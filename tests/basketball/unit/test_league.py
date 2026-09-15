from unittest import TestCase, mock
from espn_api.basketball.league import League
from espn_api.basketball.team import Team
from espn_api.basketball.matchup import Matchup
from tests.basketball.unit.test_player import _make_player_data


class LeagueTest(TestCase):
    
    def test_league_init_no_fetch(self):
        """Test League initialization without fetching"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            # Verify that fetch_league was not called by checking that teams doesn't exist
            self.assertFalse(hasattr(league, 'teams') or league.__dict__.get('teams') is not None)

    def test_league_map_matchup_ids_empty_schedule(self):
        """Test _map_matchup_ids with empty schedule"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            schedule = []
            league._map_matchup_ids(schedule)
            
            self.assertEqual(league.matchup_ids, {})

    def test_league_map_matchup_ids_single_matchup(self):
        """Test _map_matchup_ids with single matchup"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            schedule = [
                {
                    'matchupPeriodId': 1,
                    'home': {
                        'pointsByScoringPeriod': {
                            '1': 100.0,
                            '2': 95.0
                        }
                    }
                }
            ]
            
            league._map_matchup_ids(schedule)
            
            self.assertEqual(league.matchup_ids[1], ['1', '2'])

    def test_league_map_matchup_ids_multiple_periods(self):
        """Test _map_matchup_ids with multiple matchup periods"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            schedule = [
                {
                    'matchupPeriodId': 1,
                    'home': {
                        'pointsByScoringPeriod': {
                            '1': 100.0,
                            '2': 95.0
                        }
                    }
                },
                {
                    'matchupPeriodId': 2,
                    'home': {
                        'pointsByScoringPeriod': {
                            '3': 98.0,
                            '4': 92.0
                        }
                    }
                }
            ]
            
            league._map_matchup_ids(schedule)
            
            self.assertEqual(league.matchup_ids[1], ['1', '2'])
            self.assertEqual(league.matchup_ids[2], ['3', '4'])

    def test_league_map_matchup_ids_duplicate_periods(self):
        """Test _map_matchup_ids handles duplicate scoring periods"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            schedule = [
                {
                    'matchupPeriodId': 1,
                    'home': {
                        'pointsByScoringPeriod': {
                            '1': 100.0,
                            '2': 95.0
                        }
                    }
                },
                {
                    'matchupPeriodId': 1,
                    'home': {
                        'pointsByScoringPeriod': {
                            '2': 98.0,
                            '3': 92.0
                        }
                    }
                }
            ]
            
            league._map_matchup_ids(schedule)
            
            # Should merge and deduplicate
            self.assertEqual(league.matchup_ids[1], ['1', '2', '3'])

    def test_league_map_matchup_ids_empty_scoring_periods(self):
        """Test _map_matchup_ids skips matchups with no scoring periods"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            schedule = [
                {
                    'matchupPeriodId': 1,
                    'home': {
                        'pointsByScoringPeriod': {}  # Empty
                    }
                }
            ]
            
            league._map_matchup_ids(schedule)
            
            self.assertEqual(league.matchup_ids, {})

    def test_league_standings_sorting(self):
        """Test standings are sorted by final_standing"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            # Create mock teams
            team1 = mock.MagicMock()
            team1.final_standing = 2
            team1.standing = 5
            
            team2 = mock.MagicMock()
            team2.final_standing = 1
            team2.standing = 3
            
            team3 = mock.MagicMock()
            team3.final_standing = 3
            team3.standing = 4
            
            league.teams = [team1, team2, team3]
            
            standings = league.standings()
            
            # Should be sorted by final_standing
            self.assertEqual(standings[0].final_standing, 1)
            self.assertEqual(standings[1].final_standing, 2)
            self.assertEqual(standings[2].final_standing, 3)

    def test_league_standings_fallback_to_standing(self):
        """Test standings fallback to standing when final_standing is 0"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            
            # Create mock teams with zero final_standing
            team1 = mock.MagicMock()
            team1.final_standing = 0
            team1.standing = 2
            
            team2 = mock.MagicMock()
            team2.final_standing = 0
            team2.standing = 1
            
            league.teams = [team1, team2]
            
            standings = league.standings()
            
            # Should be sorted by standing when final_standing is 0
            self.assertEqual(standings[0].standing, 1)
            self.assertEqual(standings[1].standing, 2)

    def test_league_recent_activity_year_check(self):
        """Test recent_activity raises exception for years before 2019"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2018, fetch_league=False)
            league.year = 2018
            
            with self.assertRaises(Exception) as context:
                league.recent_activity()
            
            self.assertIn('Cant use recent activity before 2019', str(context.exception))

    def test_league_transactions_valid_types(self):
        """Test transactions with valid types"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            league.scoringPeriodId = 1
            league.espn_request = mock.MagicMock()
            league.espn_request.league_get.return_value = {'transactions': []}
            league.player_map = {}
            league.get_team_data = lambda x: ''
            
            # Valid types should not raise exception
            result = league.transactions(types={"WAIVER", "FREEAGENT"})
            
            # Should call espn_request
            league.espn_request.league_get.assert_called_once()
            league.espn_request.get_player_card.assert_not_called()

    def test_league_transactions_fill_empty_trade_accept(self):
        """Empty TRADE_ACCEPT rows are filled from player cards."""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2023, fetch_league=False)
            league.year = 2023
            league.scoringPeriodId = 4
            league.finalScoringPeriod = 20
            league.teams = []
            league.player_map = {3003: 'Stephen Curry'}
            league.get_team_data = lambda _: None
            league.espn_request = mock.MagicMock()
            league.espn_request.league_get.return_value = {
                'transactions': [{
                    'id': 'weekly-1',
                    'teamId': 3,
                    'type': 'TRADE_ACCEPT',
                    'status': 'EXECUTED',
                    'scoringPeriodId': 4,
                    'relatedTransactionId': 'rel-1',
                    'items': [],
                }]
            }
            wrap = _make_player_data(full_name='Stephen Curry', player_id=3003)
            wrap['transactions'] = [{
                'id': 'card-1',
                'teamId': 8,
                'type': 'TRADE_ACCEPT',
                'status': 'EXECUTED',
                'scoringPeriodId': 4,
                'relatedTransactionId': 'rel-1',
                'items': [{
                    'type': 'TRADE',
                    'playerId': 3003,
                    'fromTeamId': 3,
                    'toTeamId': 8,
                }],
            }]
            league.espn_request.get_player_card.return_value = {'players': [wrap]}

            result = league.transactions(
                types={"TRADE_ACCEPT"},
                fill_trade_items=True,
                player_ids=[3003],
            )

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].items[0].playerId, 3003)
            self.assertEqual(result[0].items[0].from_team_id, 3)
            league.espn_request.get_player_card.assert_called()

    def test_league_free_agents_year_check(self):
        """Test free_agents raises exception for years before 2019"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2018, fetch_league=False)
            league.year = 2018
            
            with self.assertRaises(Exception) as context:
                league.free_agents()
            
            self.assertIn('Cant use free agents before 2019', str(context.exception))

    def test_league_box_scores_year_check(self):
        """Test box_scores raises exception for years before 2019"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None):
            league = League(411647, 2018, fetch_league=False)
            league.year = 2018
            
            with self.assertRaises(Exception) as context:
                league.box_scores()
            
            self.assertIn('Cant use box score before 2019', str(context.exception))

    def test_league_init_with_espn_s2_swid(self):
        """Test League initialization with espn_s2 and swid"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None) as mock_init:
            league = League(411647, 2023, espn_s2='test_s2', swid='test_swid', fetch_league=False)
            
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs['league_id'], 411647)
            self.assertEqual(call_kwargs['year'], 2023)
            self.assertEqual(call_kwargs['sport'], 'nba')
            self.assertEqual(call_kwargs['espn_s2'], 'test_s2')
            self.assertEqual(call_kwargs['swid'], 'test_swid')
            self.assertFalse(call_kwargs['debug'])

    def test_league_init_debug_mode(self):
        """Test League initialization with debug mode"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None) as mock_init:
            league = League(411647, 2023, debug=True, fetch_league=False)
            
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args[1]
            self.assertTrue(call_kwargs['debug'])

    def test_league_sport_is_nba(self):
        """Test that League always uses 'nba' as the sport"""
        with mock.patch('espn_api.basketball.league.BaseLeague.__init__', return_value=None) as mock_init:
            league = League(411647, 2023, fetch_league=False)
            
            call_kwargs = mock_init.call_args[1]
            self.assertEqual(call_kwargs['sport'], 'nba')
