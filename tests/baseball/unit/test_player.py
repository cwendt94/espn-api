from datetime import datetime
from unittest import TestCase

from espn_api.baseball.constant import DEFAULT_POSITION_MAP, POSITION_MAP
from espn_api.baseball.player import Player


def _make_player_data(default_position_id=1, lineup_slot_id=0, eligible_slots=None,
                      ownership=None, pool_entry_extras=None, player_extras=None):
    """Roster-style data: pool entry nested under 'playerPoolEntry'."""
    return {
        'defaultPositionId': default_position_id,
        'lineupSlotId': lineup_slot_id,
        'eligibleSlots': eligible_slots or [lineup_slot_id],
        'acquisitionType': 'DRAFT',
        'acquisitionDate': 1700000000000,
        'proTeamId': 10,
        'injuryStatus': 'ACTIVE',
        'status': 'ONTEAM',
        'playerPoolEntry': {
            'keeperValue': 5,
            'keeperValueFuture': 10,
            'lineupLocked': False,
            'rosterLocked': False,
            'tradeLocked': False,
            'onTeamId': 3,
            **(pool_entry_extras or {}),
            'player': {
                'fullName': 'Test Player',
                'id': 1234,
                'firstName': 'Test',
                'lastName': 'Player',
                'injuryStatus': 'ACTIVE',
                'injured': False,
                'active': True,
                'droppable': True,
                'jersey': '42',
                'laterality': 'RIGHT',
                'stance': 'RIGHT',
                'lastNewsDate': 1700000000000,
                'seasonOutlook': 'Looking good.',
                'ownership': {
                    'percentOwned': 50.0,
                    'percentStarted': 30.0,
                    'percentChange': 1.5,
                    'averageDraftPosition': 100.0,
                    'averageDraftPositionPercentChange': 0.5,
                    'auctionValueAverage': 12.0,
                    'auctionValueAverageChange': -1.0,
                    **(ownership or {}),
                },
                'draftRanksByRankType': {
                    'STANDARD': {'rank': 50, 'auctionValue': 20, 'rankSourceId': 0, 'rankType': 'STANDARD', 'slotId': 0, 'published': True},
                    'ROTO': {'rank': 45, 'auctionValue': 18, 'rankSourceId': 0, 'rankType': 'ROTO', 'slotId': 0, 'published': True},
                },
                'stats': [],
                **(player_extras or {}),
            },
        },
    }


def _make_player_card_data(player_id=4424862):
    """Player card style: flat structure, no 'playerPoolEntry' wrapper."""
    return {
        'keeperValue': 7,
        'keeperValueFuture': 14,
        'lineupLocked': True,
        'rosterLocked': False,
        'tradeLocked': True,
        'onTeamId': 5,
        'player': {
            'fullName': 'Card Player',
            'id': player_id,
            'defaultPositionId': 1,
            'eligibleSlots': [0],
            'firstName': 'Card',
            'lastName': 'Player',
            'injuryStatus': 'ACTIVE',
            'injured': False,
            'active': True,
            'droppable': False,
            'jersey': '99',
            'laterality': 'LEFT',
            'stance': 'SWITCH',
            'lastNewsDate': 1700000000000,
            'seasonOutlook': 'Card outlook.',
            'proTeamId': 15,
            'ownership': {
                'percentOwned': 75.0,
                'percentStarted': 60.0,
                'percentChange': 2.0,
                'averageDraftPosition': 50.0,
                'averageDraftPositionPercentChange': 1.0,
                'auctionValueAverage': 25.0,
                'auctionValueAverageChange': 3.0,
            },
            'draftRanksByRankType': {
                'STANDARD': {'rank': 20, 'auctionValue': 30, 'rankSourceId': 0, 'rankType': 'STANDARD', 'slotId': 0, 'published': True},
            },
            'stats': [],
        },
    }


class PlayerPositionTest(TestCase):
    """Tests that Player.position uses DEFAULT_POSITION_MAP (defaultPositionId),
    not POSITION_MAP (lineupSlotId)."""

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


class PlayerMetadataTest(TestCase):
    def setUp(self):
        self.player = Player(_make_player_data(), year=2021)

    def test_basic_identity(self):
        self.assertEqual(self.player.name, 'Test Player')
        self.assertEqual(self.player.first_name, 'Test')
        self.assertEqual(self.player.last_name, 'Player')

    def test_active_and_droppable(self):
        self.assertTrue(self.player.active)
        self.assertTrue(self.player.droppable)

    def test_jersey(self):
        self.assertEqual(self.player.jersey, '42')

    def test_laterality_and_stance(self):
        self.assertEqual(self.player.laterality, 'RIGHT')
        self.assertEqual(self.player.stance, 'RIGHT')

    def test_last_news_date_is_datetime(self):
        self.assertIsInstance(self.player.last_news_date, datetime)

    def test_last_news_date_none_when_missing(self):
        data = _make_player_data()
        del data['playerPoolEntry']['player']['lastNewsDate']
        player = Player(data, year=2021)
        self.assertIsNone(player.last_news_date)

    def test_season_outlook(self):
        self.assertEqual(self.player.season_outlook, 'Looking good.')

    def test_acquisition_date(self):
        self.assertEqual(self.player.acquisitionDate, 1700000000000)


class PlayerPoolEntryTest(TestCase):
    def setUp(self):
        self.player = Player(_make_player_data(), year=2021)

    def test_keeper_values(self):
        self.assertEqual(self.player.keeper_value, 5)
        self.assertEqual(self.player.keeper_value_future, 10)

    def test_lock_flags(self):
        self.assertFalse(self.player.lineup_locked)
        self.assertFalse(self.player.roster_locked)
        self.assertFalse(self.player.trade_locked)

    def test_lock_flags_true(self):
        data = _make_player_data(pool_entry_extras={
            'lineupLocked': True, 'rosterLocked': True, 'tradeLocked': True,
        })
        player = Player(data, year=2021)
        self.assertTrue(player.lineup_locked)
        self.assertTrue(player.roster_locked)
        self.assertTrue(player.trade_locked)

    def test_on_team_id(self):
        self.assertEqual(self.player.on_team_id, 3)


class PlayerOwnershipTest(TestCase):
    def setUp(self):
        self.player = Player(_make_player_data(), year=2021)

    def test_percent_owned_and_started(self):
        self.assertAlmostEqual(self.player.percent_owned, 50.0)
        self.assertAlmostEqual(self.player.percent_started, 30.0)

    def test_percent_owned_change(self):
        self.assertAlmostEqual(self.player.percent_owned_change, 1.5)

    def test_adp(self):
        self.assertAlmostEqual(self.player.adp, 100.0)

    def test_adp_change(self):
        self.assertAlmostEqual(self.player.adp_change, 0.5)

    def test_auction_value(self):
        self.assertAlmostEqual(self.player.auction_value, 12.0)

    def test_auction_value_change(self):
        self.assertAlmostEqual(self.player.auction_value_change, -1.0)

    def test_missing_ownership_fields_are_none(self):
        data = _make_player_data(ownership={
            'percentOwned': 10.0,
            'percentStarted': 5.0,
        })
        # Remove the extra ownership keys by overriding entirely
        data['playerPoolEntry']['player']['ownership'] = {
            'percentOwned': 10.0,
            'percentStarted': 5.0,
        }
        player = Player(data, year=2021)
        self.assertIsNone(player.adp)
        self.assertIsNone(player.adp_change)
        self.assertIsNone(player.auction_value)
        self.assertIsNone(player.auction_value_change)
        self.assertIsNone(player.percent_owned_change)


class PlayerDraftRanksTest(TestCase):
    def setUp(self):
        self.player = Player(_make_player_data(), year=2021)

    def test_draft_ranks_keys(self):
        self.assertIn('STANDARD', self.player.draft_ranks)
        self.assertIn('ROTO', self.player.draft_ranks)

    def test_draft_ranks_values(self):
        self.assertEqual(self.player.draft_ranks['STANDARD']['rank'], 50)
        self.assertEqual(self.player.draft_ranks['STANDARD']['auction_value'], 20)
        self.assertEqual(self.player.draft_ranks['ROTO']['rank'], 45)

    def test_empty_draft_ranks(self):
        data = _make_player_data(player_extras={'draftRanksByRankType': {}})
        player = Player(data, year=2021)
        self.assertEqual(player.draft_ranks, {})


class PlayerCardStructureTest(TestCase):
    """Player card data is flat (no playerPoolEntry wrapper) — verify fields still populate."""

    def setUp(self):
        self.player = Player(_make_player_card_data(), year=2021)

    def test_name(self):
        self.assertEqual(self.player.name, 'Card Player')

    def test_keeper_values_from_top_level(self):
        self.assertEqual(self.player.keeper_value, 7)
        self.assertEqual(self.player.keeper_value_future, 14)

    def test_lock_flags_from_top_level(self):
        self.assertTrue(self.player.lineup_locked)
        self.assertFalse(self.player.roster_locked)
        self.assertTrue(self.player.trade_locked)

    def test_on_team_id_from_top_level(self):
        self.assertEqual(self.player.on_team_id, 5)

    def test_jersey_laterality_stance(self):
        self.assertEqual(self.player.jersey, '99')
        self.assertEqual(self.player.laterality, 'LEFT')
        self.assertEqual(self.player.stance, 'SWITCH')

    def test_adp_and_auction_value(self):
        self.assertAlmostEqual(self.player.adp, 50.0)
        self.assertAlmostEqual(self.player.adp_change, 1.0)
        self.assertAlmostEqual(self.player.auction_value, 25.0)
        self.assertAlmostEqual(self.player.auction_value_change, 3.0)

    def test_draft_ranks(self):
        self.assertIn('STANDARD', self.player.draft_ranks)
        self.assertEqual(self.player.draft_ranks['STANDARD']['rank'], 20)

