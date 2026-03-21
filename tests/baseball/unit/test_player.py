from unittest import TestCase

from espn_api.baseball.constant import DEFAULT_POSITION_MAP, POSITION_MAP
from espn_api.baseball.player import Player


def _make_player_data(default_position_id, lineup_slot_id=0, eligible_slots=None):
    """Minimal data structure that Player.__init__ expects."""
    return {
        'defaultPositionId': default_position_id,
        'lineupSlotId': lineup_slot_id,
        'eligibleSlots': eligible_slots or [lineup_slot_id],
        'acquisitionType': 'DRAFT',
        'proTeamId': 10,
        'injuryStatus': 'ACTIVE',
        'status': 'ONTEAM',
        'playerPoolEntry': {
            'player': {
                'fullName': 'Test Player',
                'id': 1234,
                'injuryStatus': 'ACTIVE',
                'injured': False,
                'ownership': {'percentOwned': 50.0, 'percentStarted': 30.0},
                'stats': [],
            }
        },
    }


class PlayerPositionTest(TestCase):
    """Tests that Player.position uses DEFAULT_POSITION_MAP (defaultPositionId),
    not POSITION_MAP (lineupSlotId)."""

    def test_sp_default_position(self):
        """defaultPositionId=1 should resolve to 'SP', not 'C' (the old off-by-one bug)."""
        data = _make_player_data(default_position_id=1)
        player = Player(data, year=2021)
        self.assertEqual(player.position, 'SP')

    def test_catcher_default_position(self):
        data = _make_player_data(default_position_id=2)
        player = Player(data, year=2021)
        self.assertEqual(player.position, 'C')

    def test_rp_default_position(self):
        data = _make_player_data(default_position_id=11)
        player = Player(data, year=2021)
        self.assertEqual(player.position, 'RP')

    def test_unknown_default_position_returns_string_id(self):
        """Unknown defaultPositionId should return a string of the ID, not crash."""
        data = _make_player_data(default_position_id=99)
        player = Player(data, year=2021)
        self.assertEqual(player.position, '99')

    def test_lineup_slot_uses_position_map(self):
        """lineupSlot should still use POSITION_MAP (lineup slot IDs)."""
        data = _make_player_data(default_position_id=1, lineup_slot_id=14)
        player = Player(data, year=2021)
        self.assertEqual(player.lineupSlot, 'SP')

    def test_all_default_positions_covered(self):
        """Every entry in DEFAULT_POSITION_MAP should resolve correctly."""
        for pos_id, expected in DEFAULT_POSITION_MAP.items():
            with self.subTest(defaultPositionId=pos_id):
                data = _make_player_data(default_position_id=pos_id)
                player = Player(data, year=2021)
                self.assertEqual(player.position, expected)
