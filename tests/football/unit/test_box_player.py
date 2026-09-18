from unittest import TestCase

from espn_api.football.box_player import BoxPlayer


def _make_box_player_data(
    player_id=1001,
    full_name="Justin Jefferson",
    pro_team_id=16,
    default_position_id=4,
    lineup_slot_id=4,
    week=7,
    actual_stats=None,
    projected_stats=None,
):
    stats = []
    if actual_stats is not None:
        stats.append(
            {
                "seasonId": 2023,
                "scoringPeriodId": week,
                "statSourceId": 0,
                "proTeamId": pro_team_id,
                "appliedTotal": actual_stats,
                "appliedAverage": actual_stats,
                "stats": {"42": 100},
                "appliedStats": {"42": actual_stats},
            }
        )
    if projected_stats is not None:
        stats.append(
            {
                "seasonId": 2023,
                "scoringPeriodId": week,
                "statSourceId": 1,
                "proTeamId": pro_team_id,
                "appliedTotal": projected_stats,
                "appliedAverage": projected_stats,
                "stats": {"42": 120},
                "appliedStats": {"42": projected_stats},
            }
        )

    return {
        "id": player_id,
        "fullName": full_name,
        "defaultPositionId": default_position_id,
        "eligibleSlots": [default_position_id, lineup_slot_id],
        "acquisitionType": "DRAFT",
        "proTeamId": pro_team_id,
        "jersey": "18",
        "injuryStatus": "ACTIVE",
        "onTeamId": 1,
        "positionalRanking": 5,
        "lineupSlotId": lineup_slot_id,
        "playerPoolEntry": {
            "player": {
                "id": player_id,
                "fullName": full_name,
                "defaultPositionId": default_position_id,
                "proTeamId": pro_team_id,
                "injuryStatus": "ACTIVE",
                "injured": False,
                "ownership": {"percentOwned": 99, "percentStarted": 90},
                "stats": stats,
            }
        },
    }


class BoxPlayerTest(TestCase):
    def test_box_player_maps_weekly_points_breakdowns_and_opponent_rank(self):
        data = _make_box_player_data(actual_stats=18.567, projected_stats=20.25)

        player = BoxPlayer(
            data,
            {16: (11, 0)},
            {"4": {"11": 3}},
            7,
            2023,
        )

        self.assertEqual(player.slot_position, "WR")
        self.assertEqual(player.pro_opponent, "IND")
        self.assertEqual(player.pro_pos_rank, 3)
        self.assertEqual(player.game_played, 100)
        self.assertEqual(player.points, 18.57)
        self.assertEqual(player.projected_points, 20.25)
        self.assertEqual(player.points_breakdown, {"receivingYards": 18.567})
        self.assertEqual(player.projected_breakdown, {"receivingYards": 120})

    def test_box_player_prefers_actual_week_team_and_updates_cache(self):
        data = _make_box_player_data(pro_team_id=16, actual_stats=10)
        data["playerPoolEntry"]["player"]["stats"][0]["proTeamId"] = 11
        team_cache = {}

        player = BoxPlayer(data, {11: (12, 0)}, {"4": {"12": 3}}, 7, 2023, team_cache)

        self.assertEqual(player.proTeam, "IND")
        self.assertEqual(team_cache[1001], 11)
        self.assertFalse(player.on_bye_week)

    def test_box_player_uses_cached_team_on_bye_week(self):
        data = _make_box_player_data(pro_team_id=16, actual_stats=None)
        team_cache = {1001: 11}

        player = BoxPlayer(data, {11: (12, 0)}, {"4": {"12": 3}}, 7, 2023, team_cache)

        self.assertEqual(player.proTeam, "IND")
        self.assertEqual(player.pro_opponent, "KC")
        self.assertFalse(player.on_bye_week)
        self.assertEqual(player.points, 0)

    def test_box_player_marks_missing_schedule_as_bye(self):
        player = BoxPlayer(_make_box_player_data(actual_stats=10), {}, {}, 7, 2023)

        self.assertTrue(player.on_bye_week)
        self.assertEqual(player.pro_opponent, "None")
        self.assertEqual(player.pro_pos_rank, 0)

    def test_box_player_repr_includes_actual_and_projected_points(self):
        player = BoxPlayer(
            _make_box_player_data(actual_stats=12, projected_stats=15), {}, {}, 7, 2023
        )

        self.assertEqual(repr(player), "Player(Justin Jefferson, points:12, projected:15)")
