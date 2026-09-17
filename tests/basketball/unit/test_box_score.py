from datetime import datetime, timedelta
from unittest import TestCase

from espn_api.basketball.box_player import BoxPlayer
from espn_api.basketball.box_score import (
    BoxScore,
    H2HCategoryBoxScore,
    H2HPointsBoxScore,
    get_box_scoring_type_class,
)


def _make_box_player_data(
    player_id=101,
    pro_team_id=1,
    lineup_slot_id=0,
    default_position_id=1,
    points=18.5,
    breakdown=None,
):
    if breakdown is None:
        breakdown = {"0": points, "3": 4}
    return {
        "fullName": "Test Player",
        "id": player_id,
        "defaultPositionId": default_position_id,
        "lineupSlotId": lineup_slot_id,
        "eligibleSlots": [lineup_slot_id],
        "acquisitionType": "DRAFT",
        "proTeamId": pro_team_id,
        "injuryStatus": "ACTIVE",
        "positionalRanking": 50,
        "expectedReturnDate": None,
        "playerPoolEntry": {
            "player": {
                "id": player_id,
                "fullName": "Test Player",
                "proTeamId": pro_team_id,
                "injuryStatus": "ACTIVE",
                "injured": False,
                "stats": [
                    {
                        "seasonId": 2023,
                        "id": "0010",
                        "scoringPeriodId": 1,
                        "appliedTotal": points,
                        "appliedStats": breakdown,
                        "stats": breakdown,
                    }
                ],
            }
        },
    }


class BoxPlayerTest(TestCase):
    def test_box_player_sets_points_and_opponent(self):
        pro_schedule = {
            1: {
                "1": [
                    {
                        "awayProTeamId": 2,
                        "homeProTeamId": 1,
                        "date": (datetime.now() - timedelta(days=2)).timestamp() * 1000,
                    }
                ]
            }
        }

        player = BoxPlayer(_make_box_player_data(points=22.5), pro_schedule, 2023, 1)

        self.assertEqual(player.slot_position, "PG")
        self.assertEqual(player.pro_opponent, "BOS")
        self.assertEqual(player.game_played, 100)
        self.assertEqual(player.points, 22.5)
        self.assertEqual(player.points_breakdown["PTS"], 22.5)
        self.assertIn("Player(", repr(player))

    def test_box_player_without_schedule_uses_default_values(self):
        player = BoxPlayer(_make_box_player_data(), {}, 2023, 1)

        self.assertEqual(player.slot_position, "PG")
        self.assertEqual(player.pro_opponent, "None")
        self.assertEqual(player.game_played, 100)
        self.assertEqual(player.points, 18.5)


class BoxScoreTest(TestCase):
    def test_box_score_repr_uses_byes_when_missing(self):
        score = BoxScore(
            {"winner": "HOME", "home": {"teamId": 0}, "away": {"teamId": 0}}, 1
        )
        self.assertEqual(repr(score), "Box Score(BYE at BYE)")

    def test_get_player_lineup_from_roster(self):
        data = {
            "home": {
                "rosterForCurrentScoringPeriod": {
                    "entries": [_make_box_player_data(player_id=201)]
                }
            },
            "away": {"teamId": 2},
        }

        score = BoxScore({"home": {"teamId": 1}, "away": {"teamId": 2}}, 1)
        lineup = score._get_player_lineup("home", data, {}, False, 2023)

        self.assertEqual(len(lineup), 1)
        self.assertIsInstance(lineup[0], BoxPlayer)
        self.assertEqual(lineup[0].playerId, 201)

    def test_h2h_points_box_score_sets_team_scores(self):
        data = {
            "home": {
                "teamId": 1,
                "rosterForCurrentScoringPeriod": {"appliedStatTotal": 101.25},
            },
            "away": {
                "teamId": 2,
                "rosterForCurrentScoringPeriod": {"appliedStatTotal": 97.5},
            },
        }

        score = H2HPointsBoxScore(data, {}, False, 2023, scoring_period=1)

        self.assertEqual(score.home_score, 101.25)
        self.assertEqual(score.away_score, 97.5)
        self.assertEqual(score.home_projected, -1)
        self.assertEqual(score.away_projected, -1)

    def test_h2h_category_box_score_maps_stat_results(self):
        data = {
            "home": {
                "teamId": 1,
                "cumulativeScore": {
                    "wins": 2,
                    "ties": 1,
                    "losses": 0,
                    "scoreByStat": {"0": {"score": 100, "result": "W"}},
                },
            },
            "away": {
                "teamId": 2,
                "cumulativeScore": {
                    "wins": 1,
                    "ties": 0,
                    "losses": 1,
                    "scoreByStat": {"0": {"score": 95, "result": "L"}},
                },
            },
        }

        score = H2HCategoryBoxScore(data, {}, False, 2023, scoring_period=1)

        self.assertEqual(score.home_wins, 2)
        self.assertEqual(score.home_ties, 1)
        self.assertEqual(score.home_losses, 0)
        self.assertEqual(score.home_stats["PTS"]["value"], 100)
        self.assertEqual(score.home_stats["PTS"]["result"], "W")
        self.assertEqual(score.away_stats["PTS"]["value"], 95)

    def test_get_box_scoring_type_class_returns_expected_class(self):
        self.assertIs(get_box_scoring_type_class("H2H_POINTS"), H2HPointsBoxScore)
        self.assertIs(get_box_scoring_type_class("H2H_CATEGORY"), H2HCategoryBoxScore)
        self.assertIs(get_box_scoring_type_class("UNKNOWN"), H2HPointsBoxScore)
