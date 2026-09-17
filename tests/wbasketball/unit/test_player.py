from unittest import TestCase
from espn_api.wbasketball.player import Player
from espn_api.wbasketball.constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP


def _make_player_data(
    full_name="Test Player",
    player_id=1234,
    default_position_id=1,
    lineup_slot_id=0,
    eligible_slots=None,
    pro_team_id=3,
    acquisition_type="DRAFT",
    injury_status="ACTIVE",
    stats=None,
    player_extras=None,
):
    """Helper function to create player data"""
    if eligible_slots is None:
        eligible_slots = [lineup_slot_id]
    if stats is None:
        stats = []

    return {
        "fullName": full_name,
        "id": player_id,
        "defaultPositionId": default_position_id,
        "lineupSlotId": lineup_slot_id,
        "eligibleSlots": eligible_slots,
        "acquisitionType": acquisition_type,
        "acquisitionDate": 1700000000000,
        "proTeamId": pro_team_id,
        "injuryStatus": injury_status,
        "playerPoolEntry": {
            "player": {
                "fullName": full_name,
                "id": player_id,
                "injuryStatus": injury_status,
                "injured": False,
                "stats": stats,
                **(player_extras or {}),
            }
        },
    }


class PlayerTest(TestCase):

    def test_player_basic_init(self):
        """Test basic Player initialization"""
        data = _make_player_data(
            full_name="Breanna Stewart", player_id=1001, default_position_id=2
        )

        player = Player(data, 2023)

        self.assertEqual(player.name, "Breanna Stewart")
        self.assertEqual(player.playerId, 1001)
        self.assertEqual(player.position, POSITION_MAP[2])

    def test_player_position_mapping(self):
        """Test that player positions are correctly mapped"""
        # Test various positions
        positions = [1, 2, 3, 4, 5]

        for pos_id in positions:
            data = _make_player_data(default_position_id=pos_id)
            player = Player(data, 2023)
            self.assertEqual(player.position, POSITION_MAP[pos_id])

    def test_player_pro_team_mapping(self):
        """Test that pro teams are correctly mapped"""
        # Test a few team IDs that are in wbasketball PRO_TEAM_MAP
        pro_team_data = [(3, "Dal"), (5, "Ind"), (6, "LA"), (8, "Min")]

        for team_id, expected_team in pro_team_data:
            data = _make_player_data(pro_team_id=team_id)
            player = Player(data, 2023)
            self.assertEqual(player.proTeam, expected_team)

    def test_player_acquisition_type(self):
        """Test player acquisition type"""
        data = _make_player_data(acquisition_type="WAIVER")
        player = Player(data, 2023)
        self.assertEqual(player.acquisitionType, "WAIVER")

    def test_player_injury_status(self):
        """Test player injury status"""
        data = _make_player_data(injury_status="OUT")
        player = Player(data, 2023)
        self.assertEqual(player.injuryStatus, "OUT")

    def test_player_eligible_slots(self):
        """Test player eligible slots"""
        data = _make_player_data(eligible_slots=[1, 2, 3])
        player = Player(data, 2023)
        self.assertEqual(len(player.eligibleSlots), 3)

    def test_player_lineup_slot(self):
        """Test player lineup slot"""
        data = _make_player_data(lineup_slot_id=5)
        player = Player(data, 2023)
        self.assertEqual(player.lineupSlot, POSITION_MAP.get(5, ""))

    def test_player_initial_empty_stats(self):
        """Test that player initializes with empty stats dict"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.stats, {})

    def test_player_total_points_zero(self):
        """Test player total points when no stats"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.total_points, 0)

    def test_player_avg_points_zero(self):
        """Test player average points when no stats"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.avg_points, 0)

    def test_player_projected_points_zero(self):
        """Test player projected points when no stats"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.projected_total_points, 0)
        self.assertEqual(player.projected_avg_points, 0)

    def test_player_repr(self):
        """Test player string representation"""
        data = _make_player_data(full_name="Jewell Loyd")
        player = Player(data, 2023)
        self.assertEqual(repr(player), "Player(Jewell Loyd)")

    def test_player_with_stats(self):
        """Test player with stats for the same year"""
        stats = [
            {
                "id": "0010",
                "appliedTotal": 50.0,
                "appliedAverage": 25.0,
                "stats": {"0": 100, "1": 5},
                "averageStats": {"0": 50, "1": 2.5},
            }
        ]

        data = _make_player_data(stats=stats)
        player = Player(data, 2023)

        self.assertIn("10", player.stats)
        self.assertEqual(player.stats["10"]["applied_total"], 50.0)

    def test_player_injured_flag(self):
        """Test player injured flag"""
        data = _make_player_data(player_extras={"injured": True})
        player = Player(data, 2023)
        self.assertTrue(player.injured)

    def test_player_not_injured(self):
        """Test player not injured"""
        data = _make_player_data(player_extras={"injured": False})
        player = Player(data, 2023)
        self.assertFalse(player.injured)

    def test_player_stat_id_pretty_total(self):
        """Test stat ID pretty formatting for total"""
        data = _make_player_data()
        player = Player(data, 2023)

        # Test ID '0010' -> '10'
        self.assertEqual(player._stat_id_pretty("0010"), "10")

    def test_player_stat_id_pretty_projected(self):
        """Test stat ID pretty formatting for projected"""
        data = _make_player_data()
        player = Player(data, 2023)

        # Test ID '1010' -> '10_projected'
        self.assertEqual(player._stat_id_pretty("1010"), "10_projected")

    def test_player_stat_id_pretty_unknown(self):
        """Test stat ID pretty formatting for unknown type"""
        data = _make_player_data()
        player = Player(data, 2023)

        # Test unknown ID format
        self.assertEqual(player._stat_id_pretty("9910"), "10")

    def test_player_with_pool_entry_nested(self):
        """Test player with playerPoolEntry nested data"""
        nested_data = {
            "fullName": "Test Player",
            "id": 1234,
            "defaultPositionId": 1,
            "lineupSlotId": 0,
            "eligibleSlots": [0],
            "acquisitionType": "DRAFT",
            "acquisitionDate": 1700000000000,
            "proTeamId": 3,
            "injuryStatus": "ACTIVE",
            "playerPoolEntry": {
                "player": {
                    "fullName": "Test Player",
                    "id": 1234,
                    "injuryStatus": "ACTIVE",
                    "injured": False,
                    "stats": [],
                }
            },
        }

        player = Player(nested_data, 2023)
        self.assertEqual(player.name, "Test Player")
        self.assertEqual(player.playerId, 1234)

    def test_player_with_player_directly_in_data(self):
        """Test player when 'player' is directly in data (not nested in playerPoolEntry)"""
        data = {
            "fullName": "Direct Player",
            "id": 5678,
            "defaultPositionId": 2,
            "lineupSlotId": 1,
            "eligibleSlots": [1],
            "acquisitionType": "WAIVER",
            "acquisitionDate": 1700000000000,
            "proTeamId": 5,
            "injuryStatus": "ACTIVE",
            "player": {
                "fullName": "Direct Player",
                "id": 5678,
                "injuryStatus": "ACTIVE",
                "injured": False,
                "stats": [],
            },
        }

        player = Player(data, 2023)
        self.assertEqual(player.name, "Direct Player")
        self.assertEqual(player.playerId, 5678)

    def test_player_stats_with_no_average_stats(self):
        """Test player stats without averageStats key"""
        stats = [
            {
                "id": "0010",
                "appliedTotal": 50.0,
                "appliedAverage": 25.0,
                "stats": {"0": 100, "1": 5},
            }
        ]

        data = _make_player_data(stats=stats)
        player = Player(data, 2023)

        self.assertIn("10", player.stats)
        self.assertIsNone(player.stats["10"].get("avg"))
        self.assertIsNone(player.stats["10"].get("total"))
