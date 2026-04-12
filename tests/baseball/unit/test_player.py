from datetime import datetime
from unittest import TestCase

from espn_api.baseball.constant import DEFAULT_POSITION_MAP, POSITION_MAP, STAT_SPLIT_MAP
from espn_api.baseball.player import Player


def _make_player_data(default_position_id=2, lineup_slot_id=0, eligible_slots=None,
                      ownership=None, pool_entry_extras=None, player_extras=None):
    """Roster-style data: pool entry nested under 'playerPoolEntry'. Default position is C (catcher, ID=2)."""
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
        from datetime import datetime
        self.assertIsInstance(self.player.acquisitionDate, datetime)


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


def _make_stat(split_type_id, scoring_period=0, season_id=2021,
               stat_source_id=0, applied_total=10.0, stats=None):
    return {
        'statSplitTypeId': split_type_id,
        'scoringPeriodId': scoring_period,
        'seasonId': season_id,
        'statSourceId': stat_source_id,
        'appliedTotal': applied_total,
        'stats': stats or {'5': 1.0},  # stat key '5' = HR
    }


class PlayerStatSplitsTest(TestCase):
    def _player_with_stats(self, stat_list):
        data = _make_player_data(player_extras={'stats': stat_list})
        return Player(data, year=2021)

    def test_stats_splits_keys_present(self):
        player = self._player_with_stats([])
        for label in STAT_SPLIT_MAP.values():
            self.assertIn(label, player.stats_splits)

    def test_season_split_populates_stats(self):
        player = self._player_with_stats([_make_stat(0, applied_total=50.0)])
        self.assertIn(0, player.stats['season'] if 'season' in player.stats else player.stats)
        self.assertIn(0, player.stats_splits['season'])
        self.assertEqual(player.stats_splits['season'][0]['points'], 50.0)

    def test_season_split_also_in_stats_dict(self):
        """split_type=0 (season) must still appear in player.stats for backwards compat."""
        player = self._player_with_stats([_make_stat(0, applied_total=30.0)])
        self.assertIn(0, player.stats)
        self.assertEqual(player.stats[0]['points'], 30.0)

    def test_box_score_split_in_stats_dict(self):
        """split_type=5 (box_score) must still appear in player.stats."""
        player = self._player_with_stats([_make_stat(5, scoring_period=3, applied_total=7.0)])
        self.assertIn(3, player.stats)
        self.assertEqual(player.stats[3]['points'], 7.0)

    def test_last7_split_not_in_stats_dict(self):
        """split_type=1 (last_7) should NOT appear in player.stats."""
        player = self._player_with_stats([_make_stat(1, applied_total=20.0)])
        self.assertNotIn(0, player.stats)
        self.assertIn(0, player.stats_splits['last_7'])

    def test_last15_and_last30_splits(self):
        player = self._player_with_stats([
            _make_stat(2, applied_total=15.0),
            _make_stat(3, applied_total=30.0),
        ])
        self.assertEqual(player.stats_splits['last_15'][0]['points'], 15.0)
        self.assertEqual(player.stats_splits['last_30'][0]['points'], 30.0)

    def test_wrong_season_ignored(self):
        player = self._player_with_stats([_make_stat(0, season_id=2020, applied_total=99.0)])
        self.assertEqual(player.stats, {})
        for split in player.stats_splits.values():
            self.assertEqual(split, {})

    def test_projected_split(self):
        player = self._player_with_stats([_make_stat(0, stat_source_id=1, applied_total=25.0)])
        self.assertIn(0, player.stats_splits['season'])
        self.assertEqual(player.stats_splits['season'][0]['projected_points'], 25.0)
        self.assertNotIn('points', player.stats_splits['season'][0])

    def test_breakdown_keys_mapped(self):
        player = self._player_with_stats([_make_stat(0, stats={'5': 2.0})])
        self.assertEqual(player.stats_splits['season'][0]['breakdown']['HR'], 2.0)

    def test_total_points_from_season_stats(self):
        player = self._player_with_stats([_make_stat(0, applied_total=42.0)])
        self.assertAlmostEqual(player.total_points, 42.0)

    def test_projected_total_points_from_projected_split(self):
        player = self._player_with_stats([_make_stat(0, stat_source_id=1, applied_total=38.5)])
        self.assertAlmostEqual(player.projected_total_points, 38.5)

    def test_total_points_zero_when_no_stats(self):
        player = self._player_with_stats([])
        self.assertEqual(player.total_points, 0)

    def test_batter_stats_filtered_for_pitchers(self):
        """Pitcher (SP, ID=1) should not include batter-only stats like HR (ID=5)."""
        pitcher_data = _make_player_data(default_position_id=1, eligible_slots=[14], player_extras={'stats': [_make_stat(0, stats={'5': 2.0, '48': 10.0})]})
        pitcher = Player(pitcher_data, year=2021)
        breakdown = pitcher.stats_splits['season'][0]['breakdown']
        self.assertNotIn('HR', breakdown)  # HR is a batter-only stat
        self.assertIn('K', breakdown)  # K (strikeout) is a pitcher stat

    def test_pitcher_stats_filtered_for_batters(self):
        """Batter (C, ID=2) should not include pitcher-only stats like ERA (ID=47)."""
        batter_data = _make_player_data(default_position_id=2, eligible_slots=[0], player_extras={'stats': [_make_stat(0, stats={'5': 2.0, '47': 3.45})]})
        batter = Player(batter_data, year=2021)
        breakdown = batter.stats_splits['season'][0]['breakdown']
        self.assertIn('HR', breakdown)  # HR is a batter stat
        self.assertNotIn('ERA', breakdown)  # ERA is a pitcher-only stat

    def test_multi_position_player_keeps_all_stats(self):
        """Ohtani-like player (eligible for both SP and DH) should keep both pitcher and batter stats."""
        multi_data = _make_player_data(eligible_slots=[0, 14], player_extras={'stats': [_make_stat(0, stats={'5': 2.0, '48': 10.0})]})
        multi = Player(multi_data, year=2021)
        breakdown = multi.stats_splits['season'][0]['breakdown']
        self.assertIn('HR', breakdown)  # HR is a batter stat
        self.assertIn('K', breakdown)  # K is a pitcher stat


class PlayerMiscTest(TestCase):
    def test_repr(self):
        player = Player(_make_player_data(), year=2021)
        self.assertEqual(repr(player), 'Player(Test Player)')

    def test_eligible_slots_mapped(self):
        data = _make_player_data(eligible_slots=[0, 14])
        player = Player(data, year=2021)
        self.assertIn('C', player.eligibleSlots)
        self.assertIn('SP', player.eligibleSlots)

    def test_status_field(self):
        player = Player(_make_player_data(), year=2021)
        self.assertEqual(player.status, 'ONTEAM')

    def test_pro_team_mapped(self):
        from espn_api.baseball.constant import PRO_TEAM_MAP
        for pro_id, pro_name in PRO_TEAM_MAP.items():
            with self.subTest(pro_id=pro_id):
                data = _make_player_data(player_extras={'proTeamId': pro_id})
                # proTeamId in player_extras goes into player dict, but proTeam reads from
                # the outer roster entry's proTeamId — patch that instead
                data['proTeamId'] = pro_id
                player = Player(data, year=2021)
                self.assertEqual(player.proTeam, pro_name)
