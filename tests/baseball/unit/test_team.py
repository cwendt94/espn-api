from unittest import TestCase, mock

from espn_api.baseball.team import Team


def _make_record(wins=5, losses=3, ties=0, points_for=100.0, points_against=80.0,
                 streak_length=2, streak_type='WIN'):
    return {
        'wins': wins, 'losses': losses, 'ties': ties,
        'pointsFor': points_for, 'pointsAgainst': points_against,
        'streakLength': streak_length, 'streakType': streak_type,
        'gamesBack': 0.0, 'percentage': 0.625,
    }


def _make_team_data(team_id=1, wins=5, losses=3):
    return {
        'id': team_id,
        'abbrev': 'TST',
        'name': 'Test Team',
        'divisionId': 0,
        'playoffSeed': 1,
        'rankCalculatedFinal': 1,
        'currentProjectedRank': 2,
        'waiverRank': 4,
        'points': 55.5,
        'record': {
            'overall': _make_record(wins=wins, losses=losses),
            'home': _make_record(wins=3, losses=1),
            'away': _make_record(wins=2, losses=2),
            'division': _make_record(wins=1, losses=1),
        },
    }


def _make_team(data=None):
    data = data or _make_team_data()
    roster = {'entries': []}
    schedule = []
    with mock.patch('espn_api.baseball.team.Player'), \
         mock.patch('espn_api.baseball.team.Matchup'):
        return Team(data, roster, schedule, year=2026)


class TeamRecordTest(TestCase):
    def setUp(self):
        self.team = _make_team()

    def test_overall_record(self):
        self.assertEqual(self.team.wins, 5)
        self.assertEqual(self.team.losses, 3)
        self.assertEqual(self.team.ties, 0)

    def test_points_for_and_against(self):
        self.assertAlmostEqual(self.team.points_for, 100.0)
        self.assertAlmostEqual(self.team.points_against, 80.0)

    def test_streak(self):
        self.assertEqual(self.team.streak_length, 2)
        self.assertEqual(self.team.streak_type, 'WIN')

    def test_home_record(self):
        self.assertEqual(self.team.home_wins, 3)
        self.assertEqual(self.team.home_losses, 1)
        self.assertEqual(self.team.home_ties, 0)

    def test_away_record(self):
        self.assertEqual(self.team.away_wins, 2)
        self.assertEqual(self.team.away_losses, 2)
        self.assertEqual(self.team.away_ties, 0)

    def test_division_record(self):
        self.assertEqual(self.team.division_wins, 1)
        self.assertEqual(self.team.division_losses, 1)
        self.assertEqual(self.team.division_ties, 0)


class TeamMetadataTest(TestCase):
    def setUp(self):
        self.team = _make_team()

    def test_current_projected_rank(self):
        self.assertEqual(self.team.current_projected_rank, 2)

    def test_waiver_rank(self):
        self.assertEqual(self.team.waiver_rank, 4)

    def test_points(self):
        self.assertAlmostEqual(self.team.points, 55.5)

    def test_optional_fields_default_to_none(self):
        data = _make_team_data()
        del data['currentProjectedRank']
        del data['waiverRank']
        team = _make_team(data)
        self.assertIsNone(team.current_projected_rank)
        self.assertIsNone(team.waiver_rank)

    def test_points_defaults_to_zero(self):
        data = _make_team_data()
        del data['points']
        team = _make_team(data)
        self.assertEqual(team.points, 0)
