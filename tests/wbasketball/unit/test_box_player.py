from unittest import TestCase

from espn_api.wbasketball.box_player import BoxPlayer
from espn_api.wbasketball.constant import POSITION_MAP


def _make_box_player_data(
    full_name="Test Player",
    player_id=101,
    pro_team_id=3,
    lineup_slot_id=1,
    stats=None,
):
    return {
        "fullName": full_name,
        "id": player_id,
        "defaultPositionId": 1,
        "lineupSlotId": lineup_slot_id,
        "eligibleSlots": [lineup_slot_id],
        "acquisitionType": "DRAFT",
        "acquisitionDate": 1700000000000,
        "proTeamId": pro_team_id,
        "injuryStatus": "ACTIVE",
        "playerPoolEntry": {
            "player": {
                "fullName": full_name,
                "id": player_id,
                "proTeamId": pro_team_id,
                "injuryStatus": "ACTIVE",
                "injured": False,
                "stats": stats or [],
            }
        },
    }


class BoxPlayerTest(TestCase):
    def test_box_player_defaults(self):
        player = BoxPlayer(_make_box_player_data(), {}, 2023)

        self.assertEqual(player.slot_position, POSITION_MAP[1])
        self.assertEqual(player.pro_opponent, "None")
        self.assertEqual(player.game_played, 100)
        self.assertEqual(player.points, 0)
        self.assertEqual(player.points_breakdown, {})

    def test_box_player_maps_points_and_applied_stats(self):
        data = _make_box_player_data(
            stats=[
                {
                    "id": "0010",
                    "appliedTotal": 18.567,
                    "appliedStats": {"0": 18, "3": 4},
                }
            ]
        )

        player = BoxPlayer(data, {}, 2023)

        self.assertEqual(player.points, 18.57)
        self.assertEqual(player.points_breakdown, {"PTS": 18, "AST": 4})

    def test_box_player_uses_stats_when_applied_stats_missing(self):
        data = _make_box_player_data(
            stats=[{"id": "0010", "appliedTotal": 12, "stats": {"0": 12, "6": 5}}]
        )

        player = BoxPlayer(data, {}, 2023)

        self.assertEqual(player.points_breakdown, {"PTS": 12, "REB": 5})

    def test_box_player_resolves_finished_game_opponent(self):
        data = _make_box_player_data(pro_team_id=3)

        player = BoxPlayer(data, {3: (5, 0)}, 2023)

        self.assertEqual(player.pro_opponent, "Ind")
        self.assertEqual(player.game_played, 100)

    def test_box_player_repr(self):
        player = BoxPlayer(_make_box_player_data(full_name="A'ja Wilson"), {}, 2023)

        self.assertEqual(repr(player), "Player(A'ja Wilson, points:0)")
