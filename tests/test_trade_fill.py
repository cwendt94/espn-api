from unittest import TestCase, mock

from espn_api.base_league import BaseLeague
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

    def test_best_player_transactions_ignores_incomplete_or_unexecuted_cards(self):
        valid = Player(
            _card_player([_card_trade(related="rel-2", player_id=50)]),
            2022,
            player_map={50: "A"},
        )
        valid.transactions[0].status = "EXECUTED"
        invalid = Player(
            _card_player([_card_trade(related="rel-2", player_id=51)]), 2022
        )
        invalid.transactions[0].status = "PENDING"

        best = best_player_transactions([valid, invalid])
        self.assertIn("rel-2", best)
        self.assertEqual(best["rel-2"].items[0].playerId, 50)

    def test_fill_trade_accept_from_players_appends_card_only_trade_when_week_matches(
        self,
    ):
        weekly = []
        player = Player(
            _card_player([_card_trade(related="rel-card", week=7, player_id=900)]),
            2022,
            player_map={900: "Card Player"},
        )
        player.transactions[0].scoring_period = 7

        fill_trade_accept_from_players(weekly, [player], scoring_period=7)

        self.assertEqual(len(weekly), 1)
        self.assertEqual(weekly[0].related_transaction_id, "rel-card")

    def test_fill_trade_accept_from_players_skips_mismatched_card_week(self):
        weekly = []
        player = Player(
            _card_player([_card_trade(related="rel-card", week=7, player_id=901)]),
            2022,
            player_map={901: "Card Player"},
        )
        player.transactions[0].scoring_period = 8

        fill_trade_accept_from_players(weekly, [player], scoring_period=7)

        self.assertEqual(weekly, [])


class BaseLeagueCoverageTest(TestCase):
    def _league(self):
        league = object.__new__(BaseLeague)
        league.teams = []
        league.year = 2023
        league.player_map = {}
        league.finalScoringPeriod = 17
        league.espn_request = mock.MagicMock()
        return league

    def test_base_league_roster_entry_player_id_variants(self):
        self.assertEqual(BaseLeague._roster_entry_player_id({"playerId": 12}), 12)
        self.assertEqual(
            BaseLeague._roster_entry_player_id({"playerPoolEntry": {"id": 22}}), 22
        )
        self.assertEqual(
            BaseLeague._roster_entry_player_id(
                {"playerPoolEntry": {"player": {"id": 33}}}
            ),
            33,
        )
        self.assertIsNone(BaseLeague._roster_entry_player_id({"playerId": "12"}))
        self.assertIsNone(
            BaseLeague._roster_entry_player_id({"playerPoolEntry": {"id": 0}})
        )

    def test_base_league_scoring_period_roster_ids_uses_team_rosters(self):
        league = self._league()
        league.espn_request.league_get.return_value = {
            "teams": [
                {
                    "roster": {
                        "entries": [
                            {"playerId": 1},
                            {"playerPoolEntry": {"id": 2}},
                            {"playerId": 0},
                        ]
                    }
                },
                {
                    "roster": {
                        "entries": [
                            {"playerPoolEntry": {"player": {"id": 3}}},
                            {"playerPoolEntry": {"id": "bad"}},
                        ]
                    }
                },
            ]
        }

        self.assertEqual(league._scoring_period_roster_ids(5), {1, 2, 3})
        league.espn_request.league_get.assert_called_once_with(
            params={"view": "mRoster", "scoringPeriodId": 5}
        )

    def test_base_league_trade_fill_player_ids_routes_by_source(self):
        league = self._league()
        league._scoring_period_roster_ids = mock.Mock(return_value={1, 2})
        league._roster_player_ids = mock.Mock(return_value={3, 4})
        league.espn_request.get_player_pool_ids.return_value = [5, 6]

        self.assertEqual(
            league._trade_fill_player_ids(7, player_ids=[1, 0, "x", 8]), {1, 8}
        )
        self.assertEqual(league._trade_fill_player_ids(7), {1, 2})
        self.assertEqual(league._trade_fill_player_ids(7, fill_from="roster"), {3, 4})
        self.assertEqual(league._trade_fill_player_ids(7, fill_from="pool"), {5, 6})
        with self.assertRaises(ValueError):
            league._trade_fill_player_ids(7, fill_from="bad")

    def test_base_league_fill_trade_accept_from_player_cards_uses_card_data(self):
        league = self._league()
        league.player_map = {44: "Player 44"}
        league.get_team_data = lambda _: None
        league.espn_request.get_player_card.return_value = {
            "players": [
                {
                    "id": 44,
                    "fullName": "Player 44",
                    "positionalRanking": 5,
                    "eligibleSlots": [0],
                    "acquisitionType": "DRAFT",
                    "proTeamId": 1,
                    "lineupSlotId": 0,
                    "injuryStatus": "ACTIVE",
                    "playerPoolEntry": {
                        "player": {
                            "fullName": "Player 44",
                            "id": 44,
                            "injuryStatus": "ACTIVE",
                            "injured": False,
                            "stats": [],
                        }
                    },
                    "transactions": [
                        {
                            "id": "card-1",
                            "teamId": 7,
                            "type": "TRADE_ACCEPT",
                            "status": "EXECUTED",
                            "scoringPeriodId": 3,
                            "relatedTransactionId": "rel-1",
                            "items": [
                                {
                                    "type": "TRADE",
                                    "playerId": 44,
                                    "fromTeamId": 1,
                                    "toTeamId": 7,
                                }
                            ],
                        }
                    ],
                }
            ]
        }

        txn = _empty_trade(txn_id="weekly-1", related="rel-1", team_id=1, week=3)
        result = league._fill_trade_accept_from_player_cards(
            [txn],
            3,
            {"TRADE_ACCEPT"},
            fill_trade_items=True,
            player_ids=[44],
            player_class=Player,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].items[0].playerId, 44)
        self.assertEqual(result[0].related_transaction_id, "rel-1")
