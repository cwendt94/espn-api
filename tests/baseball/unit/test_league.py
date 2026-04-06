import json
from unittest import TestCase, mock

from espn_api.baseball import League
from espn_api.baseball.activity import Activity
from espn_api.baseball.box_score import RotoBoxScore
from espn_api.baseball.matchup import Matchup
from espn_api.baseball.player import Player
from espn_api.baseball.constant import POSITION_MAP
from espn_api.requests.espn_requests import EspnFantasyRequests


def _make_matchup_data(matchup_period_id=3, home_team_id=1, away_team_id=2):
    return {
        'matchupPeriodId': matchup_period_id,
        'home': {'teamId': home_team_id, 'totalPoints': 10.0},
        'away': {'teamId': away_team_id, 'totalPoints': 8.0},
        'winner': 'HOME',
    }


def _make_player_card_data(player_id=1001):
    return {
        'keeperValue': 5,
        'keeperValueFuture': 10,
        'lineupLocked': False,
        'rosterLocked': False,
        'tradeLocked': False,
        'onTeamId': 1,
        'player': {
            'fullName': 'Test Player',
            'id': player_id,
            'defaultPositionId': 1,
            'eligibleSlots': [0],
            'firstName': 'Test',
            'lastName': 'Player',
            'injuryStatus': 'ACTIVE',
            'injured': False,
            'active': True,
            'droppable': True,
            'jersey': '42',
            'laterality': 'RIGHT',
            'stance': 'RIGHT',
            'lastNewsDate': None,
            'seasonOutlook': '',
            'proTeamId': 10,
            'ownership': {
                'percentOwned': 50.0,
                'percentStarted': 30.0,
            },
            'draftRanksByRankType': {},
            'stats': [],
        },
    }


class FreeAgentsPositionFilterTest(TestCase):
    """Tests that free_agents(position=...) correctly filters by slot ID."""

    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.current_week = 1

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_position_string_builds_correct_slot_filter(self, mock_league_get):
        """Passing position='SP' should send slotId 14, not an empty filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents(position='SP')

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [14])  # 14 is the int key for 'SP' in POSITION_MAP

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_no_position_sends_empty_slot_filter(self, mock_league_get):
        """Calling free_agents() with no position should send an empty slot filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents()

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_invalid_position_sends_empty_slot_filter(self, mock_league_get):
        """An unrecognized position string should not crash and should send an empty filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents(position='INVALID')

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_all_position_strings_resolve_to_their_int_id(self, mock_league_get):
        """Every position name in POSITION_MAP should resolve to its correct int slot ID."""
        mock_league_get.return_value = {'players': []}

        for slot_id, pos_name in POSITION_MAP.items():
            if not isinstance(slot_id, int):
                continue
            with self.subTest(position=pos_name):
                self.league.free_agents(position=pos_name)
                call_kwargs = mock_league_get.call_args
                headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
                sent_filter = json.loads(headers['x-fantasy-filter'])
                slot_ids = sent_filter['players']['filterSlotIds']['value']
                self.assertEqual(slot_ids, [slot_id])


class ScoreboardTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.currentMatchupPeriod = 3
        self.mock_team = mock.Mock()
        self.mock_team.team_id = 1
        self.league.teams = [self.mock_team]

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_returns_matchups_filtered_by_period(self, mock_get):
        mock_get.return_value = {
            'schedule': [
                _make_matchup_data(matchup_period_id=3, home_team_id=1, away_team_id=2),
                _make_matchup_data(matchup_period_id=4, home_team_id=3, away_team_id=4),
            ]
        }
        result = self.league.scoreboard()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Matchup)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_explicit_matchup_period(self, mock_get):
        mock_get.return_value = {
            'schedule': [
                _make_matchup_data(matchup_period_id=2, home_team_id=1, away_team_id=2),
            ]
        }
        result = self.league.scoreboard(matchupPeriod=2)
        self.assertEqual(len(result), 1)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_team_substituted_for_home(self, mock_get):
        mock_get.return_value = {
            'schedule': [_make_matchup_data(matchup_period_id=3, home_team_id=1, away_team_id=2)]
        }
        result = self.league.scoreboard()
        self.assertEqual(result[0].home_team, self.mock_team)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_team_substituted_for_away(self, mock_get):
        mock_get.return_value = {
            'schedule': [_make_matchup_data(matchup_period_id=3, home_team_id=2, away_team_id=1)]
        }
        result = self.league.scoreboard()
        self.assertEqual(result[0].away_team, self.mock_team)


class RecentActivityTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.player_map = {1001: 'Mike Trout'}
        mock_team = mock.Mock()
        mock_team.team_id = 1
        self.league.teams = [mock_team]

    def test_raises_before_2019(self):
        with mock.patch.object(League, 'fetch_league'):
            old_league = League(league_id=1, year=2018)
        with self.assertRaises(Exception):
            old_league.recent_activity()

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_returns_activity_list(self, mock_get):
        mock_get.return_value = {
            'topics': [
                {
                    'date': 1234567890000,
                    'messages': [
                        {'messageTypeId': 178, 'to': 1, 'targetId': 1001}
                    ],
                }
            ]
        }
        result = self.league.recent_activity()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Activity)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_empty_topics_returns_empty_list(self, mock_get):
        mock_get.return_value = {'topics': []}
        result = self.league.recent_activity()
        self.assertEqual(result, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_msg_type_filter_applied(self, mock_get):
        mock_get.return_value = {'topics': []}
        self.league.recent_activity(msg_type='ADD')
        headers_arg = mock_get.call_args.kwargs.get('headers') or mock_get.call_args[1].get('headers')
        sent_filter = json.loads(headers_arg['x-fantasy-filter'])
        self.assertIn('filterIncludeMessageTypeIds', sent_filter['topics'])


class BoxScoresTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.currentMatchupPeriod = 3
        self.league.current_week = 5
        mock_team = mock.Mock()
        mock_team.team_id = 1
        self.league.teams = [mock_team]
        self.league._box_score_class = mock.Mock(return_value=mock.Mock(home_team=1, away_team=2))

    def test_raises_before_2019(self):
        with mock.patch.object(League, 'fetch_league'):
            old_league = League(league_id=1, year=2018)
        old_league._box_score_class = mock.Mock()
        with self.assertRaises(Exception):
            old_league.box_scores()

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_returns_box_score_list(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [{'dummy': True}]}
        result = self.league.box_scores()
        self.assertEqual(len(result), 1)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_explicit_matchup_and_scoring_period(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': []}
        self.league.box_scores(matchup_period=2, scoring_period=10)
        params = mock_get.call_args.kwargs.get('params') or mock_get.call_args[1].get('params')
        self.assertEqual(params['scoringPeriodId'], 10)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_matchup_period_only_uses_earlier_period(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': []}
        self.league.box_scores(matchup_period=1)
        filters_header = mock_get.call_args.kwargs.get('headers') or mock_get.call_args[1].get('headers')
        sent_filter = json.loads(filters_header['x-fantasy-filter'])
        self.assertEqual(sent_filter['schedule']['filterMatchupPeriodIds']['value'], [1])

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_team_substituted_in_box_score(self, mock_get, mock_pro):
        mock_team = self.league.teams[0]
        mock_box = mock.Mock()
        mock_box.home_team = 1
        mock_box.away_team = 2
        self.league._box_score_class.return_value = mock_box
        mock_get.return_value = {'schedule': [{'dummy': True}]}
        self.league.box_scores()
        self.assertEqual(mock_box.home_team, mock_team)


def _make_roto_schedule_entry(team_ids=(1, 2), matchup_period=1):
    teams = [
        {
            'teamId': tid,
            'totalPoints': 50.0,
            'cumulativeScore': {
                'scoreByStat': {
                    '5': {'score': 10.0, 'rank': float(i + 1), 'result': None, 'ineligible': False},
                }
            },
            'rosterForCurrentScoringPeriod': {'entries': []},
        }
        for i, tid in enumerate(team_ids)
    ]
    return {'matchupPeriodId': matchup_period, 'teams': teams}


class BoxScoresRotoTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.currentMatchupPeriod = 1
        self.league.current_week = 1
        self.league.scoring_type = 'ROTO'
        self.league._box_score_class = RotoBoxScore
        mock_team = mock.Mock()
        mock_team.team_id = 1
        self.league.teams = [mock_team]

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_returns_roto_box_score_instances(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [_make_roto_schedule_entry()]}
        result = self.league.box_scores()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], RotoBoxScore)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_team_id_replaced_with_team_object(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [_make_roto_schedule_entry(team_ids=(1, 2))]}
        result = self.league.box_scores()
        roto = result[0]
        mock_team = self.league.teams[0]
        matched = [e for e in roto.teams if e['team'] == mock_team]
        self.assertEqual(len(matched), 1)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_unknown_team_id_left_as_int(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [_make_roto_schedule_entry(team_ids=(1, 99))]}
        result = self.league.box_scores()
        roto = result[0]
        unmapped = [e for e in roto.teams if e['team'] == 99]
        self.assertEqual(len(unmapped), 1)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_all_teams_present_in_snapshot(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [_make_roto_schedule_entry(team_ids=(1, 2))]}
        result = self.league.box_scores()
        self.assertEqual(len(result[0].teams), 2)

    @mock.patch('espn_api.baseball.league.League._get_pro_schedule', return_value={})
    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_stats_and_rank_accessible(self, mock_get, mock_pro):
        mock_get.return_value = {'schedule': [_make_roto_schedule_entry(team_ids=(1,))]}
        result = self.league.box_scores()
        entry = result[0].teams[0]
        self.assertIn('stats', entry)
        for stat in entry['stats'].values():
            self.assertIn('score', stat)
            self.assertIn('rank', stat)


class PlayerInfoTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.player_map = {'Mike Trout': 1001}
        self.league.finalScoringPeriod = 162

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_by_name_returns_single_player(self, mock_get):
        mock_get.return_value = {'players': [_make_player_card_data(1001)]}
        result = self.league.player_info(name='Mike Trout')
        self.assertIsInstance(result, Player)

    def test_by_name_not_found_returns_none(self):
        result = self.league.player_info(name='Unknown Player')
        self.assertIsNone(result)

    def test_no_args_returns_none(self):
        result = self.league.player_info()
        self.assertIsNone(result)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_by_player_id_int_returns_single_player(self, mock_get):
        mock_get.return_value = {'players': [_make_player_card_data(1001)]}
        result = self.league.player_info(playerId=1001)
        self.assertIsInstance(result, Player)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_by_player_id_list_returns_list(self, mock_get):
        mock_get.return_value = {
            'players': [_make_player_card_data(1001), _make_player_card_data(1002)]
        }
        result = self.league.player_info(playerId=[1001, 1002])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_split_filters_included_in_request(self, mock_get):
        mock_get.return_value = {'players': [_make_player_card_data(1001)]}
        self.league.player_info(playerId=1001)
        headers = mock_get.call_args.kwargs.get('headers') or mock_get.call_args[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        additional = sent_filter['players']['filterStatsForTopScoringPeriodIds']['additionalValue']
        self.assertIn('012021', additional)
        self.assertIn('022021', additional)
        self.assertIn('032021', additional)


class RefreshTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.teams = []

    @mock.patch.object(League, '_fetch_teams')
    @mock.patch('espn_api.baseball.league.BaseLeague._fetch_league')
    def test_refresh_updates_scoring_type(self, mock_fetch_league, mock_fetch_teams):
        mock_fetch_league.return_value = {
            'settings': {'scoringSettings': {'scoringType': 'H2H_CATEGORY'}}
        }
        self.league.refresh()
        self.assertEqual(self.league.scoring_type, 'H2H_CATEGORY')

    @mock.patch.object(League, '_fetch_teams')
    @mock.patch('espn_api.baseball.league.BaseLeague._fetch_league')
    def test_refresh_calls_fetch_teams(self, mock_fetch_league, mock_fetch_teams):
        mock_fetch_league.return_value = {
            'settings': {'scoringSettings': {'scoringType': 'H2H_CATEGORY'}}
        }
        self.league.refresh()
        mock_fetch_teams.assert_called_once()


class LoadRosterWeekTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.mock_team = mock.Mock()
        self.mock_team.team_id = 1
        self.league.teams = [self.mock_team]

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_calls_fetch_roster_on_each_team(self, mock_get):
        mock_get.return_value = {
            'teams': [{'id': 1, 'roster': {'entries': []}}]
        }
        self.league.load_roster_week(week=5)
        self.mock_team._fetch_roster.assert_called_once_with({'entries': []}, 2021)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_uses_correct_scoring_period(self, mock_get):
        mock_get.return_value = {'teams': [{'id': 1, 'roster': {'entries': []}}]}
        self.league.load_roster_week(week=7)
        params = mock_get.call_args.kwargs.get('params') or mock_get.call_args[1].get('params')
        self.assertEqual(params['scoringPeriodId'], 7)


class StandingsTest(TestCase):
    def _make_team(self, team_id, final_standing, standing):
        t = mock.Mock()
        t.team_id = team_id
        t.final_standing = final_standing
        t.standing = standing
        return t

    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)

    def test_sorted_by_final_standing(self):
        t1 = self._make_team(1, final_standing=3, standing=3)
        t2 = self._make_team(2, final_standing=1, standing=1)
        t3 = self._make_team(3, final_standing=2, standing=2)
        self.league.teams = [t1, t2, t3]
        result = self.league.standings()
        self.assertEqual([t.team_id for t in result], [2, 3, 1])

    def test_zero_final_standing_falls_back_to_standing(self):
        t1 = self._make_team(1, final_standing=0, standing=2)
        t2 = self._make_team(2, final_standing=0, standing=1)
        self.league.teams = [t1, t2]
        result = self.league.standings()
        self.assertEqual(result[0].team_id, 2)

    def test_returns_all_teams(self):
        self.league.teams = [self._make_team(i, final_standing=i, standing=i) for i in range(1, 6)]
        self.assertEqual(len(self.league.standings()), 5)
