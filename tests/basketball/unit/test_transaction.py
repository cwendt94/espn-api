from types import SimpleNamespace
from unittest import TestCase

from espn_api.basketball.transaction import Transaction


class TransactionTest(TestCase):
    def test_transaction_builds_item_details(self):
        player_map = {1001: "LeBron James"}
        team = SimpleNamespace(team_name="Lakers")

        transaction = Transaction(
            {
                "teamId": 1,
                "type": "FREEAGENT",
                "status": "EXECUTED",
                "scoringPeriodId": 7,
                "processDate": 1700000000000,
                "bidAmount": 3,
                "items": [{"type": "ADD", "playerId": 1001}],
            },
            player_map,
            lambda _: team,
        )

        self.assertEqual(transaction.team.team_name, "Lakers")
        self.assertEqual(transaction.type, "FREEAGENT")
        self.assertEqual(transaction.status, "EXECUTED")
        self.assertEqual(transaction.bid_amount, 3)
        self.assertEqual(transaction.items[0].player, "LeBron James")
        self.assertEqual(
            repr(transaction), "Transaction(Lakers FREEAGENT ADD LeBron James)"
        )

    def test_transaction_item_repr(self):
        transaction = Transaction(
            {
                "teamId": 1,
                "type": "WAIVER",
                "status": "EXECUTED",
                "scoringPeriodId": 2,
                "items": [{"type": "ADD", "playerId": 2002}],
            },
            {2002: "Anthony Davis"},
            lambda _: SimpleNamespace(team_name="Lakers"),
        )

        self.assertEqual(repr(transaction.items[0]), "ADD Anthony Davis")
