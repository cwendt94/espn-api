from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
from .utils import json_parsing

class Player(object):
    '''Player are part of team'''
    def __init__(self, data, year):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.posRank = json_parsing(data, 'positionalRanking')
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.onTeamId = json_parsing(data, 'onTeamId')
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.stats = {}
        self.transactions = []

        if 'transactions' in data:
            self._set_transaction_data(data)

        # Get players main position
        for pos in json_parsing(data, 'eligibleSlots'):
            if (pos != 25 and '/' not in POSITION_MAP[pos]) or '/' in self.name:
                self.position = POSITION_MAP[pos]
                break

        # set each scoring period stat
        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)
        self.percent_owned = round(player.get('ownership', {}).get('percentOwned', -1), 2)
        self.percent_started = round(player.get('ownership', {}).get('percentStarted', -1), 2)

        self.active_status = 'bye'
        player_stats = player.get('stats', [])
        for stats in player_stats:
            if stats.get('seasonId') != year or stats.get('statSplitTypeId') == 2:
                continue
            stats_breakdown = stats.get('stats') or stats.get('appliedStats', {})
            breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}
            points = round(stats.get('appliedTotal', 0), 2)
            avg_points =  round(stats.get('appliedAverage', 0), 2)
            scoring_period = stats.get('scoringPeriodId')
            stat_source = stats.get('statSourceId')
            (points_type, breakdown_type, avg_type) = ('points', 'breakdown', 'avg_points') if stat_source == 0 else ('projected_points', 'projected_breakdown', 'projected_avg_points')
            if self.stats.get(scoring_period):
                self.stats[scoring_period][points_type] = points
                self.stats[scoring_period][breakdown_type] = breakdown
                self.stats[scoring_period][avg_type] = avg_points
            else:
                self.stats[scoring_period] = {points_type: points, breakdown_type: breakdown, avg_type: avg_points}
            if not stat_source:
                if not self.stats[scoring_period][breakdown_type]:
                    self.active_status = 'inactive'
                else:
                    self.active_status = 'active'
        self.total_points = self.stats.get(0, {}).get('points', 0)
        self.projected_total_points = self.stats.get(0, {}).get('projected_points', 0)
        self.avg_points = self.stats.get(0, {}).get('avg_points', 0)
        self.projected_avg_points = self.stats.get(0, {}).get('projected_avg_points', 0)

    def __repr__(self):
        return f'Player({self.name})'
    
    def _set_transaction_data(self, data):
        transactions = data.get('transactions', [])
        for transaction in transactions:
            bid_amount = transaction.get('bidAmount', 0)
            type = transaction.get('type', '')
            team = transaction.get('teamId', 0)
            date = transaction.get('proposedDate')
            items = transaction.get('items', [])
            self.transactions.append({'bid_amount': bid_amount, 'type': type, 'team': team, 'date': date, 'items': items})
