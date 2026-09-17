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
        self.assertEqual(transaction.team_id, 1)
        self.assertEqual(transaction.type, "FREEAGENT")
        self.assertEqual(transaction.status, "EXECUTED")
        self.assertEqual(transaction.bid_amount, 3)
        self.assertEqual(transaction.date, 1700000000000)
        self.assertEqual(transaction.items[0].player, "LeBron James")
        self.assertEqual(transaction.items[0].playerId, 1001)
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

    def test_trade_item_teams_and_related_id(self):
        transaction = Transaction(
            {
                "teamId": 3,
                "type": "TRADE_ACCEPT",
                "status": "EXECUTED",
                "scoringPeriodId": 4,
                "acceptedDate": 99,
                "relatedTransactionId": "rel-1",
                "items": [
                    {
                        "type": "TRADE",
                        "playerId": 3003,
                        "fromTeamId": 3,
                        "toTeamId": 8,
                    }
                ],
            },
            {3003: "Stephen Curry"},
            lambda _: SimpleNamespace(team_name="Warriors"),
        )

        self.assertEqual(transaction.related_transaction_id, "rel-1")
        self.assertEqual(transaction.date, 99)
        self.assertEqual(transaction.items[0].from_team_id, 3)
        self.assertEqual(transaction.items[0].to_team_id, 8)

    def test_unknown_player_and_missing_team(self):
        transaction = Transaction(
            {
                "teamId": 9,
                "type": "WAIVER",
                "status": "EXECUTED",
                "scoringPeriodId": 1,
                "items": [{"type": "ADD", "playerId": 404}],
            },
            {},
            lambda _: None,
        )

        self.assertEqual(transaction.items[0].player, "Unknown")
        self.assertEqual(repr(transaction), "Transaction(Team(9) WAIVER ADD Unknown)")
