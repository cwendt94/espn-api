from unittest import TestCase

from espn_api.football.player import Player
from espn_api.football.transaction import Transaction
from espn_api.utils.trade_fill import (
    best_player_transactions,
    chunked,
    fill_trade_accept_from_players,
    player_card_transactions,
    transaction_trade_legs,
)
from tests.football.unit.test_player import _card_player


def _empty_trade(txn_id="weekly-1", related="rel-1", team_id=2, week=6):
    return Transaction(
        {
            "id": txn_id,
            "teamId": team_id,
            "type": "TRADE_ACCEPT",
            "status": "EXECUTED",
            "scoringPeriodId": week,
            "relatedTransactionId": related,
            "items": [],
        },
        {},
        lambda _: None,
    )


def _card_trade(
    txn_id="card-1", related="rel-1", player_id=1001, week=6, extra_items=None
):
    items = [
        {
            "type": "TRADE",
            "playerId": player_id,
            "fromTeamId": 2,
            "toTeamId": 3,
        }
    ]
    if extra_items:
        items.extend(extra_items)
    return {
        "id": txn_id,
        "teamId": 3,
        "type": "TRADE_ACCEPT",
        "status": "EXECUTED",
        "scoringPeriodId": week,
        "relatedTransactionId": related,
        "items": items,
    }


class TradeFillHelperTest(TestCase):
    def test_prefers_player_with_more_trade_legs(self):
        short = Player(
            _card_player([_card_trade(txn_id="a", related="rel-1", player_id=1)]), 2022
        )
        long = Player(
            _card_player(
                [
                    _card_trade(
                        txn_id="b",
                        related="rel-1",
                        player_id=1,
                        extra_items=[
                            {
                                "type": "TRADE",
                                "playerId": 2,
                                "fromTeamId": 3,
                                "toTeamId": 2,
                            }
                        ],
                    )
                ]
            ),
            2022,
        )
        best = best_player_transactions([short, long])
        self.assertEqual(len(transaction_trade_legs(best["rel-1"])), 2)

    def test_fills_empty_weekly_row_from_player_transactions(self):
        weekly = [_empty_trade()]
        player = Player(
            _card_player([_card_trade()]), 2022, player_map={1001: "Justin Jefferson"}
        )
        fill_trade_accept_from_players(weekly, [player], scoring_period=6)
        self.assertEqual(len(transaction_trade_legs(weekly[0])), 1)
        self.assertEqual(weekly[0].items[0].playerId, 1001)
        self.assertEqual(weekly[0].team_id, 2)

    def test_appends_card_only_trade_for_requested_week(self):
        weekly = []
        player = Player(_card_player([_card_trade(related="rel-new", week=6)]), 2022)
        fill_trade_accept_from_players(weekly, [player], scoring_period=6)
        self.assertEqual(len(weekly), 1)
        self.assertEqual(weekly[0].related_transaction_id, "rel-new")

    def test_skips_card_trade_for_other_weeks(self):
        weekly = []
        player = Player(_card_player([_card_trade(related="rel-new", week=9)]), 2022)
        fill_trade_accept_from_players(weekly, [player], scoring_period=6)
        self.assertEqual(weekly, [])

    def test_does_not_duplicate_related_id_already_in_weekly(self):
        weekly = [_empty_trade()]
        player = Player(_card_player([_card_trade()]), 2022)
        fill_trade_accept_from_players(weekly, [player], scoring_period=6)
        self.assertEqual(len(weekly), 1)

    def test_chunked_splits_evenly(self):
        self.assertEqual(list(chunked([1, 2, 3, 4, 5], 2)), [[1, 2], [3, 4], [5]])
        self.assertEqual(list(chunked([], 40)), [])

    def test_player_card_transactions_reads_wrap_or_inner_player(self):
        wrap = {"transactions": [{"type": "DRAFT"}]}
        self.assertEqual(player_card_transactions(wrap)[0]["type"], "DRAFT")
        nested = {"player": {"transactions": [{"type": "WAIVER"}]}}
        self.assertEqual(player_card_transactions(nested)[0]["type"], "WAIVER")
        self.assertEqual(player_card_transactions({}), [])
