from types import SimpleNamespace
from unittest import TestCase, mock

from espn_api.football.league import League
from espn_api.football.transaction import Transaction
from tests.football.unit.test_player import _card_player


class TransactionTest(TestCase):
    def _transaction(self, data=None, player_map=None, team=None):
        payload = {
            'teamId': 1,
            'type': 'TRADE_ACCEPT',
            'status': 'EXECUTED',
            'scoringPeriodId': 6,
            'processDate': 1700000000000,
            'relatedTransactionId': 'abc-related',
            'memberId': '{swid}',
            'items': [
                {
                    'type': 'TRADE',
                    'playerId': 1001,
                    'fromTeamId': 1,
                    'toTeamId': 2,
                }
            ],
        }
        if data:
            payload.update(data)
        return Transaction(
            payload,
            player_map if player_map is not None else {1001: 'Justin Jefferson'},
            lambda _: team if team is not None else SimpleNamespace(team_name='Vikes'),
        )

    def test_trade_fields(self):
        transaction = self._transaction()

        self.assertEqual(transaction.team_id, 1)
        self.assertEqual(transaction.related_transaction_id, 'abc-related')
        self.assertEqual(transaction.member_id, '{swid}')
        self.assertEqual(transaction.date, 1700000000000)
        self.assertEqual(transaction.items[0].player, 'Justin Jefferson')
        self.assertEqual(transaction.items[0].playerId, 1001)
        self.assertEqual(transaction.items[0].from_team_id, 1)
        self.assertEqual(transaction.items[0].to_team_id, 2)
        self.assertEqual(
            repr(transaction),
            'Transaction(Vikes TRADE_ACCEPT TRADE Justin Jefferson)',
        )

    def test_date_falls_back_to_accepted_then_proposed(self):
        transaction = self._transaction({'processDate': None, 'acceptedDate': 11})
        self.assertEqual(transaction.date, 11)

        transaction = self._transaction({
            'processDate': None,
            'acceptedDate': None,
            'proposedDate': 22,
        })
        self.assertEqual(transaction.date, 22)

    def test_missing_items_and_unknown_player(self):
        transaction = self._transaction({'items': None}, player_map={})
        self.assertEqual(transaction.items, [])

        transaction = Transaction(
            {
                'teamId': 4,
                'type': 'FREEAGENT',
                'status': 'EXECUTED',
                'scoringPeriodId': 1,
                'items': [{'type': 'ADD', 'playerId': 9}],
            },
            {},
            lambda _: None,
        )
        self.assertEqual(transaction.items[0].player, 'Unknown')
        self.assertIsNone(transaction.items[0].from_team_id)
        self.assertIsNone(transaction.items[0].to_team_id)
        self.assertEqual(repr(transaction), 'Transaction(Team(4) FREEAGENT ADD Unknown)')


def _empty_trade(txn_id='weekly-1', related='rel-1', team_id=2, week=6):
    return {
        'id': txn_id,
        'teamId': team_id,
        'type': 'TRADE_ACCEPT',
        'status': 'EXECUTED',
        'scoringPeriodId': week,
        'relatedTransactionId': related,
        'items': [],
    }


def _card_trade(player_id=1001, related='rel-1', week=6):
    return {
        'id': 'card-1',
        'teamId': 3,
        'type': 'TRADE_ACCEPT',
        'status': 'EXECUTED',
        'scoringPeriodId': week,
        'relatedTransactionId': related,
        'items': [{
            'type': 'TRADE',
            'playerId': player_id,
            'fromTeamId': 2,
            'toTeamId': 3,
        }],
    }


class LeagueTradeFillTest(TestCase):
    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2022)
        self.league.scoringPeriodId = 6
        self.league.finalScoringPeriod = 18
        self.league.player_map = {1001: 'Justin Jefferson'}
        self.league.teams = []
        self.league.espn_request = mock.Mock()

    def test_skips_player_cards_by_default(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }

        result = self.league.transactions(types={'TRADE_ACCEPT'})

        self.assertEqual(result[0].items, [])
        self.league.espn_request.get_player_card.assert_not_called()

    def test_fills_empty_trade_accept_from_week_rosters(self):
        teams = self.league.teams

        def league_get(params=None, headers=None, extend=''):
            if params and params.get('view') == 'mRoster':
                return {
                    'teams': [{
                        'id': 2,
                        'roster': {'entries': [{'playerId': 1001}]},
                    }]
                }
            return {'transactions': [_empty_trade()]}

        self.league.espn_request.league_get.side_effect = league_get
        self.league.espn_request.get_player_card.return_value = {
            'players': [_card_player([_card_trade()])]
        }

        result = self.league.transactions(types={'TRADE_ACCEPT'}, fill_trade_items=True)

        self.assertIs(self.league.teams, teams)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0].items), 1)
        self.assertEqual(result[0].items[0].playerId, 1001)
        self.assertEqual(result[0].items[0].from_team_id, 2)
        self.assertEqual(result[0].items[0].to_team_id, 3)
        self.league.espn_request.get_player_card.assert_called()
        self.league.espn_request.get_player_pool_ids.assert_not_called()

    def test_fills_using_explicit_player_ids(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }
        self.league.espn_request.get_player_card.return_value = {
            'players': [_card_player([_card_trade()])]
        }

        result = self.league.transactions(
            types={'TRADE_ACCEPT'},
            fill_trade_items=True,
            player_ids=[1001],
        )

        self.assertEqual(result[0].items[0].playerId, 1001)
        self.assertEqual(self.league.espn_request.league_get.call_count, 1)
        self.league.espn_request.get_player_card.assert_called()

    def test_fills_using_player_pool(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }
        self.league.espn_request.get_player_pool_ids.return_value = [1001]
        self.league.espn_request.get_player_card.return_value = {
            'players': [_card_player([_card_trade()])]
        }

        result = self.league.transactions(
            types={'TRADE_ACCEPT'},
            fill_trade_items=True,
            fill_from='pool',
        )

        self.assertEqual(result[0].items[0].playerId, 1001)
        self.league.espn_request.get_player_pool_ids.assert_called_once_with(18)
        roster_views = [
            call.kwargs.get('params', {}).get('view')
            if call.kwargs else None
            for call in self.league.espn_request.league_get.call_args_list
        ]
        self.assertNotIn('mRoster', roster_views)

    def test_fills_using_current_rosters(self):
        player = mock.Mock()
        player.playerId = 1001
        team = mock.Mock()
        team.roster = [player]
        self.league.teams = [team]
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }
        self.league.espn_request.get_player_card.return_value = {
            'players': [_card_player([_card_trade()])]
        }

        result = self.league.transactions(
            types={'TRADE_ACCEPT'},
            fill_trade_items=True,
            fill_from='roster',
        )

        self.assertEqual(result[0].items[0].playerId, 1001)
        self.league.espn_request.get_player_pool_ids.assert_not_called()

    def test_invalid_fill_from_raises(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }
        with self.assertRaises(ValueError):
            self.league.transactions(
                types={'TRADE_ACCEPT'},
                fill_trade_items=True,
                fill_from='everyone',
            )

    def test_skips_player_cards_when_fill_disabled(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_empty_trade()]
        }

        result = self.league.transactions(types={'TRADE_ACCEPT'}, fill_trade_items=False)

        self.assertEqual(result[0].items, [])
        self.league.espn_request.get_player_card.assert_not_called()
        self.league.espn_request.get_player_pool_ids.assert_not_called()

    def test_skips_player_cards_when_trade_already_has_items(self):
        self.league.espn_request.league_get.return_value = {
            'transactions': [_card_trade()]
        }

        result = self.league.transactions(types={'TRADE_ACCEPT'})

        self.assertEqual(len(result[0].items), 1)
        self.league.espn_request.get_player_card.assert_not_called()
        self.league.espn_request.get_player_pool_ids.assert_not_called()

    def test_waiver_calls_do_not_fetch_player_cards(self):
        self.league.espn_request.league_get.return_value = {'transactions': []}

        self.league.transactions(types={'WAIVER'})

        self.league.espn_request.get_player_card.assert_not_called()
        self.league.espn_request.get_player_pool_ids.assert_not_called()
