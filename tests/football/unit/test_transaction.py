from types import SimpleNamespace
from unittest import TestCase

from espn_api.football.transaction import Transaction


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
