from datetime import datetime, date
from unittest import TestCase
from espn_api.basketball.player import Player
from espn_api.basketball.constant import POSITION_MAP, PRO_TEAM_MAP


def _make_player_data(full_name='Test Player', player_id=1234, default_position_id=1,
                      lineup_slot_id=0, eligible_slots=None, pro_team_id=1,
                      acquisition_type='DRAFT', injury_status='ACTIVE', pos_rank=50,
                      expected_return_date=None, stats=None, player_extras=None):
    """Helper function to create player data"""
    if eligible_slots is None:
        eligible_slots = [lineup_slot_id]
    if stats is None:
        stats = []
    
    return {
        'fullName': full_name,
        'id': player_id,
        'defaultPositionId': default_position_id,
        'lineupSlotId': lineup_slot_id,
        'eligibleSlots': eligible_slots,
        'acquisitionType': acquisition_type,
        'acquisitionDate': 1700000000000,
        'proTeamId': pro_team_id,
        'injuryStatus': injury_status,
        'positionalRanking': pos_rank,
        'expectedReturnDate': expected_return_date,
        'playerPoolEntry': {
            'player': {
                'fullName': full_name,
                'id': player_id,
                'injuryStatus': injury_status,
                'injured': False,
                'stats': stats,
                **(player_extras or {})
            }
        }
    }


class PlayerTest(TestCase):
    
    def test_player_basic_init(self):
        """Test basic Player initialization"""
        data = _make_player_data(full_name='LeBron James', player_id=1001, default_position_id=2)
        
        player = Player(data, 2023)
        
        self.assertEqual(player.name, 'LeBron James')
        self.assertEqual(player.playerId, 1001)
        self.assertEqual(player.year, 2023)
        self.assertEqual(player.position, 'SG')  # Position ID 2 (accounting for -1) = SG

    def test_player_position_mapping(self):
        """Test that player positions are correctly mapped"""
        # Test various positions
        positions = [1, 2, 3, 4, 5]
        expected = ['PG', 'SG', 'SF', 'PF', 'C']
        
        for pos_id, expected_pos in zip(positions, expected):
            data = _make_player_data(default_position_id=pos_id)
            player = Player(data, 2023)
            self.assertEqual(player.position, expected_pos)

    def test_player_pro_team_mapping(self):
        """Test that pro teams are correctly mapped"""
        # Test a few team IDs
        pro_team_data = [(1, 'ATL'), (9, 'GSW'), (23, 'SAC'), (28, 'TOR')]
        
        for team_id, expected_team in pro_team_data:
            data = _make_player_data(pro_team_id=team_id)
            player = Player(data, 2023)
            self.assertEqual(player.proTeam, expected_team)

    def test_player_acquisition_type(self):
        """Test player acquisition type"""
        data = _make_player_data(acquisition_type='WAIVER')
        player = Player(data, 2023)
        self.assertEqual(player.acquisitionType, 'WAIVER')

    def test_player_injury_status(self):
        """Test player injury status"""
        data = _make_player_data(injury_status='OUT')
        player = Player(data, 2023)
        self.assertEqual(player.injuryStatus, 'OUT')

    def test_player_positional_ranking(self):
        """Test player positional ranking"""
        data = _make_player_data(pos_rank=15)
        player = Player(data, 2023)
        self.assertEqual(player.posRank, 15)

    def test_player_eligible_slots(self):
        """Test player eligible slots"""
        data = _make_player_data(eligible_slots=[0, 1, 2])
        player = Player(data, 2023)
        # eligible slots are mapped directly without -1 offset
        self.assertEqual(player.eligibleSlots, ['PG', 'SG', 'SF'])

    def test_player_lineup_slot(self):
        """Test player lineup slot"""
        data = _make_player_data(lineup_slot_id=5)
        player = Player(data, 2023)
        self.assertEqual(player.lineupSlot, 'G')  # Position ID 5 = G

    def test_player_expected_return_date(self):
        """Test player expected return date parsing"""
        expected_return_tuple = (2023, 12, 15, 0, 0)
        data = _make_player_data(expected_return_date=expected_return_tuple)
        player = Player(data, 2023)
        self.assertEqual(player.expected_return_date, date(2023, 12, 15))

    def test_player_expected_return_date_none(self):
        """Test player with no expected return date"""
        data = _make_player_data(expected_return_date=None)
        player = Player(data, 2023)
        self.assertIsNone(player.expected_return_date)

    def test_player_initial_empty_stats(self):
        """Test that player initializes with empty stats dict"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.stats, {})

    def test_player_initial_empty_schedule(self):
        """Test that player initializes with empty schedule dict"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.schedule, {})

    def test_player_initial_empty_news(self):
        """Test that player initializes with empty news dict"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.news, {})

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
        data = _make_player_data(full_name='Michael Jordan')
        player = Player(data, 2023)
        self.assertEqual(repr(player), 'Player(Michael Jordan)')
        self.assertEqual(player.transactions, [])

    def test_card_player_parses_transactions(self):
        data = _make_player_data(full_name='Stephen Curry', player_id=3003)
        data['transactions'] = [{
            'teamId': 8,
            'type': 'TRADE_ACCEPT',
            'status': 'EXECUTED',
            'scoringPeriodId': 4,
            'relatedTransactionId': 'rel-1',
            'items': [{
                'type': 'TRADE',
                'playerId': 3003,
                'fromTeamId': 3,
                'toTeamId': 8,
            }],
        }]
        player = Player(data, 2023, player_map={3003: 'Stephen Curry'})
        self.assertEqual(len(player.transactions), 1)
        self.assertEqual(player.transactions[0].related_transaction_id, 'rel-1')
        self.assertEqual(player.transactions[0].items[0].from_team_id, 3)

    def test_player_with_pro_schedule(self):
        """Test player schedule with pro schedule data"""
        pro_schedule = {
            1: {
                '1': [
                    {
                        'awayProTeamId': 1,
                        'homeProTeamId': 5,
                        'date': 1700000000000
                    }
                ]
            }
        }
        
        data = _make_player_data(pro_team_id=1)
        player = Player(data, 2023, pro_team_schedule=pro_schedule)
        
        self.assertIn('1', player.schedule)
        self.assertEqual(player.schedule['1']['team'], 'CLE')  # Home team ID 5 = CLE

    def test_player_with_news(self):
        """Test player news parsing"""
        news_data = {
            'news': {
                'feed': [
                    {
                        'published': '2023-01-15T10:00:00Z',
                        'headline': 'Breaking News',
                        'story': 'Player details here'
                    }
                ]
            }
        }
        
        data = _make_player_data()
        player = Player(data, 2023, news=news_data)
        
        self.assertEqual(len(player.news), 1)
        self.assertEqual(player.news[0]['headline'], 'Breaking News')

    def test_player_with_stats_same_year(self):
        """Test player with stats for same year"""
        stats = [
            {
                'seasonId': 2023,
                'id': '0010',
                'scoringPeriodId': 1,
                'appliedTotal': 50.0,
                'appliedAverage': 25.0,
                'stats': {'0': 100, '1': 5},
                'averageStats': {'0': 50, '1': 2.5}
            }
        ]
        
        data = _make_player_data(stats=stats)
        player = Player(data, 2023)
        
        self.assertIn('10_total', player.stats)
        self.assertEqual(player.stats['10_total']['applied_total'], 50.0)

    def test_player_with_stats_different_year(self):
        """Test player stats filtering by year"""
        stats = [
            {
                'seasonId': 2022,  # Different year
                'id': '0010',
                'scoringPeriodId': 1,
                'appliedTotal': 50.0,
                'appliedAverage': 25.0,
                'stats': {'0': 100, '1': 5}
            }
        ]
        
        data = _make_player_data(stats=stats)
        player = Player(data, 2023)
        
        # Stats from 2022 should not be included
        self.assertNotIn('10_total', player.stats)

    def test_player_nine_cat_averages_empty(self):
        """Test nine cat averages when no stats"""
        data = _make_player_data()
        player = Player(data, 2023)
        self.assertEqual(player.nine_cat_averages, {})

    def test_player_stat_id_pretty_total(self):
        """Test stat ID pretty formatting for total"""
        data = _make_player_data()
        player = Player(data, 2023)
        
        # Test ID '0010' -> '10_total'
        self.assertEqual(player._stat_id_pretty('0010', 1), '10_total')

    def test_player_stat_id_pretty_projected(self):
        """Test stat ID pretty formatting for projected"""
        data = _make_player_data()
        player = Player(data, 2023)
        
        # Test ID '1010' -> '10_projected'
        self.assertEqual(player._stat_id_pretty('1010', 1), '10_projected')

    def test_player_stat_id_pretty_fallback(self):
        """Test stat ID pretty formatting fallback"""
        data = _make_player_data()
        player = Player(data, 2023)
        
        # Test unknown ID format -> returns scoring period
        self.assertEqual(player._stat_id_pretty('9910', 5), '5')

    def test_player_injured_flag(self):
        """Test player injured flag"""
        data = _make_player_data(player_extras={'injured': True})
        player = Player(data, 2023)
        self.assertTrue(player.injured)

    def test_player_not_injured(self):
        """Test player not injured"""
        data = _make_player_data(player_extras={'injured': False})
        player = Player(data, 2023)
        self.assertFalse(player.injured)

    def test_player_with_pool_entry_nested(self):
        """Test player with playerPoolEntry nested data"""
        nested_data = {
            'fullName': 'Test Player',
            'id': 1234,
            'defaultPositionId': 1,
            'lineupSlotId': 0,
            'eligibleSlots': [0],
            'acquisitionType': 'DRAFT',
            'acquisitionDate': 1700000000000,
            'proTeamId': 1,
            'injuryStatus': 'ACTIVE',
            'positionalRanking': 50,
            'expectedReturnDate': None,
            'playerPoolEntry': {
                'player': {
                    'fullName': 'Test Player',
                    'id': 1234,
                    'injuryStatus': 'ACTIVE',
                    'injured': False,
                    'stats': []
                }
            }
        }
        
        player = Player(nested_data, 2023)
        self.assertEqual(player.name, 'Test Player')
        self.assertEqual(player.playerId, 1234)
