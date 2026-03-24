from datetime import datetime
from unittest import TestCase, mock

from espn_api.baseball import League, Transaction
from espn_api.baseball.constant import TRANSACTION_TYPES
from espn_api.requests.espn_requests import EspnFantasyRequests


def _make_transaction_data(type_='FREEAGENT', status='EXECUTED', team_id=1,
                            scoring_period=1, player_id=1001, item_type='ADD'):
    return {
        'teamId': team_id,
        'type': type_,
        'status': status,
        'scoringPeriodId': scoring_period,
        'processDate': 1234567890000,
        'bidAmount': None,
        'rating': 3,
        'executionType': 'PROCESS',
        'relatedTransactionId': None,
        'comment': '',
        'memberId': '{abc-123}',
        'items': [{
            'type': item_type,
            'playerId': player_id,
            'fromTeamId': 0,
            'toTeamId': team_id,
            'fromLineupSlotId': -1,
            'toLineupSlotId': 16,
            'isKeeper': False,
            'overallPickNumber': None,
        }],
    }


class TransactionClassTest(TestCase):
    def setUp(self):
        self.mock_team = mock.Mock()
        self.mock_team.team_name = 'Test Team'
        self.player_map = {1001: 'Mike Trout'}
        self.get_team_data = mock.Mock(return_value=self.mock_team)

    def test_basic_attributes(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.type, 'FREEAGENT')
        self.assertEqual(t.status, 'EXECUTED')
        self.assertEqual(t.scoring_period, 1)
        self.assertFalse(t.isPending)
        self.assertEqual(len(t.items), 1)

    def test_pending_status(self):
        data = _make_transaction_data(status='PENDING')
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertTrue(t.isPending)

    def test_item_player_resolved(self):
        data = _make_transaction_data(player_id=1001)
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.items[0].player, 'Mike Trout')

    def test_item_unknown_player(self):
        data = _make_transaction_data(player_id=9999)
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.items[0].player, 'Unknown')

    def test_repr(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertIn('FREEAGENT', repr(t))

    def test_date_is_datetime(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertIsInstance(t.date, datetime)

    def test_date_falls_back_to_proposed(self):
        data = _make_transaction_data()
        del data['processDate']
        data['proposedDate'] = 1234567890000
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertIsInstance(t.date, datetime)

    def test_date_none_when_missing(self):
        data = _make_transaction_data()
        del data['processDate']
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertIsNone(t.date)

    def test_rating_and_execution_type(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.rating, 3)
        self.assertEqual(t.execution_type, 'PROCESS')

    def test_rating_defaults_to_none(self):
        data = _make_transaction_data()
        del data['rating']
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertIsNone(t.rating)

    def test_item_lineup_slot_ids(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.items[0].fromLineupSlotId, -1)
        self.assertEqual(t.items[0].toLineupSlotId, 16)

    def test_item_is_keeper(self):
        data = _make_transaction_data()
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertFalse(t.items[0].isKeeper)

    def test_item_is_keeper_true(self):
        data = _make_transaction_data()
        data['items'][0]['isKeeper'] = True
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertTrue(t.items[0].isKeeper)

    def test_item_overall_pick_number(self):
        data = _make_transaction_data()
        data['items'][0]['overallPickNumber'] = 42
        t = Transaction(data, self.player_map, self.get_team_data)
        self.assertEqual(t.items[0].overallPickNumber, 42)


class LeagueTransactionsTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.scoringPeriodId = 5
        mock_team = mock.Mock()
        mock_team.team_name = 'Test Team'
        mock_team.team_id = 1
        self.league.teams = [mock_team]
        self.league.player_map = {1001: 'Mike Trout'}

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_returns_transaction_list(self, mock_get):
        mock_get.return_value = {
            'transactions': [_make_transaction_data()]
        }
        result = self.league.transactions()
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Transaction)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_empty_response(self, mock_get):
        mock_get.return_value = {}
        result = self.league.transactions()
        self.assertEqual(result, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_uses_current_scoring_period_by_default(self, mock_get):
        mock_get.return_value = {'transactions': []}
        self.league.transactions()
        params = mock_get.call_args.kwargs.get('params') or mock_get.call_args[1].get('params')
        self.assertEqual(params['scoringPeriodId'], 5)

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_explicit_scoring_period(self, mock_get):
        mock_get.return_value = {'transactions': []}
        self.league.transactions(scoring_period=3)
        params = mock_get.call_args.kwargs.get('params') or mock_get.call_args[1].get('params')
        self.assertEqual(params['scoringPeriodId'], 3)

    def test_invalid_type_raises(self):
        with self.assertRaises(Exception) as ctx:
            self.league.transactions(types={'BOGUS_TYPE'})
        self.assertIn('BOGUS_TYPE', str(ctx.exception))

    def test_valid_types_accepted(self):
        """All entries in TRANSACTION_TYPES should be accepted without error when mocked."""
        with mock.patch.object(EspnFantasyRequests, 'league_get', return_value={'transactions': []}):
            for t in TRANSACTION_TYPES:
                with self.subTest(type=t):
                    self.league.transactions(types={t})
