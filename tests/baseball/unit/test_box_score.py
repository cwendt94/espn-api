from unittest import TestCase, mock

from espn_api.baseball.box_score import BoxScore, H2HPointsBoxScore, RotoBoxScore
from espn_api.baseball.constant import STATS_MAP


def _make_roto_team(team_id, total_points=50.0, stat_scores=None, entries=None):
    """Build a single team entry as returned by the ESPN ROTO schedule API."""
    stat_scores = stat_scores or {5: (10.0, 8.0), 20: (5.0, 6.0)}  # stat_id: (score, rank)
    score_by_stat = {
        str(stat_id): {'score': score, 'rank': rank, 'result': None, 'ineligible': False}
        for stat_id, (score, rank) in stat_scores.items()
    }
    return {
        'teamId': team_id,
        'totalPoints': total_points,
        'cumulativeScore': {'scoreByStat': score_by_stat},
        'rosterForCurrentScoringPeriod': {'entries': entries or []},
    }


def _make_roto_data(matchup_period=1, teams=None):
    """Build a roto schedule entry (one per matchup period, all teams included)."""
    if teams is None:
        teams = [_make_roto_team(1), _make_roto_team(2, total_points=40.0)]
    return {'matchupPeriodId': matchup_period, 'teams': teams}


class RotoBoxScoreInitTest(TestCase):
    def setUp(self):
        self.data = _make_roto_data()
        self.roto = RotoBoxScore(self.data, pro_schedule={}, year=2026)

    def test_matchup_period_set(self):
        self.assertEqual(self.roto.matchup_period, 1)

    def test_teams_length(self):
        self.assertEqual(len(self.roto.teams), 2)

    def test_team_ids_stored(self):
        ids = [e['team'] for e in self.roto.teams]
        self.assertIn(1, ids)
        self.assertIn(2, ids)

    def test_total_points(self):
        entry = next(e for e in self.roto.teams if e['team'] == 1)
        self.assertEqual(entry['total_points'], 50.0)

    def test_stats_dict_keyed_by_name(self):
        entry = self.roto.teams[0]
        # stat id 5 → 'HR', stat id 20 → 'R' per STATS_MAP
        for stat_name in entry['stats']:
            self.assertIsInstance(stat_name, str)

    def test_stat_has_score_and_rank(self):
        entry = self.roto.teams[0]
        for stat in entry['stats'].values():
            self.assertIn('score', stat)
            self.assertIn('rank', stat)

    def test_stat_values_correct(self):
        entry = next(e for e in self.roto.teams if e['team'] == 1)
        hr_name = STATS_MAP[5]
        self.assertEqual(entry['stats'][hr_name]['score'], 10.0)
        self.assertEqual(entry['stats'][hr_name]['rank'], 8.0)

    def test_lineup_is_list(self):
        for entry in self.roto.teams:
            self.assertIsInstance(entry['lineup'], list)

    def test_repr(self):
        self.assertEqual(repr(self.roto), 'Roto Box Score(period:1)')

    def test_inherits_from_box_score(self):
        self.assertIsInstance(self.roto, BoxScore)

    def test_home_away_winner_are_none(self):
        # Roto has no head-to-head concept; these stub fields exist only so
        # that isinstance() checks and attribute access don't crash.
        self.assertIsNone(self.roto.home_team)
        self.assertIsNone(self.roto.away_team)
        self.assertIsNone(self.roto.winner)


class RotoBoxScoreTotalPointsLiveTest(TestCase):
    def test_live_score_takes_precedence(self):
        team = _make_roto_team(1, total_points=40.0)
        team['totalPointsLive'] = 55.5
        data = _make_roto_data(teams=[team])
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        self.assertEqual(roto.teams[0]['total_points'], 55.5)

    def test_falls_back_to_total_points(self):
        team = _make_roto_team(1, total_points=40.0)
        # no totalPointsLive key
        data = _make_roto_data(teams=[team])
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        self.assertEqual(roto.teams[0]['total_points'], 40.0)


class RotoBoxScoreInfinityTest(TestCase):
    def test_infinity_string_converted_to_float_inf(self):
        team = _make_roto_team(1, stat_scores={41: ('Infinity', 5.0)})  # 41 → WHIP
        data = _make_roto_data(teams=[team])
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        whip_name = STATS_MAP[41]
        score = roto.teams[0]['stats'][whip_name]['score']
        self.assertEqual(score, float('inf'))

    def test_normal_score_unchanged(self):
        team = _make_roto_team(1, stat_scores={5: (12.0, 9.0)})
        data = _make_roto_data(teams=[team])
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        hr_name = STATS_MAP[5]
        self.assertEqual(roto.teams[0]['stats'][hr_name]['score'], 12.0)


class RotoBoxScoreEmptyTeamsTest(TestCase):
    def test_empty_teams_list(self):
        data = _make_roto_data(teams=[])
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        self.assertEqual(roto.teams, [])

    def test_missing_teams_key(self):
        data = {'matchupPeriodId': 1}
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        self.assertEqual(roto.teams, [])

    def test_missing_matchup_period(self):
        data = _make_roto_data(teams=[])
        del data['matchupPeriodId']
        roto = RotoBoxScore(data, pro_schedule={}, year=2026)
        self.assertIsNone(roto.matchup_period)


class RotoBoxScoreProcessTeamTest(TestCase):
    def test_process_team_noop(self):
        # _process_team is required by the abstract base but unused — calling it
        # directly should be a no-op and leave instance state untouched.
        roto = RotoBoxScore(_make_roto_data(teams=[]), pro_schedule={}, year=2026)
        self.assertIsNone(roto._process_team({'teamId': 99}, True))
        self.assertIsNone(roto.home_team)
        self.assertIsNone(roto.away_team)


class H2HPointsBoxScoreByeWeekTest(TestCase):
    def test_missing_away_returns_bye_defaults(self):
        data = {
            'winner': 'HOME',
            'home': {
                'teamId': 1,
                'totalPoints': 42.5,
                'rosterForCurrentScoringPeriod': {'entries': []},
            },
        }
        box = H2HPointsBoxScore(data, pro_schedule={}, year=2026)
        self.assertEqual(box.away_team, 0)
        self.assertEqual(box.away_score, 0)
        self.assertEqual(box.away_projected, -1)
        self.assertEqual(box.away_lineup, [])
