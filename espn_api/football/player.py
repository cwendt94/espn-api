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
        self.stats = {}

        # Get players main position
        for pos in json_parsing(data, 'eligibleSlots'):
            if (pos != 25 and '/' not in POSITION_MAP[pos]) or '/' in self.name:
                self.position = POSITION_MAP[pos]
                break

        # set each scoring period stat
        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)

        player_stats = player.get('stats', [])
        for stats in player_stats:
            if stats.get('seasonId') != year:
                continue
            stats_breakdown = stats.get('stats') if stats.get('stats') else stats.get('appliedStats', {})
            breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}
            points = round(stats.get('appliedTotal', 0), 2)
            scoring_period = stats.get('scoringPeriodId')
            stat_source = stats.get('statSourceId')
            (points_type, breakdown_type) = ('points', 'breakdown') if stat_source == 0 else ('projected_points', 'projected_breakdown')
            if self.stats.get(scoring_period):
                self.stats[scoring_period][points_type] = points
                self.stats[scoring_period][breakdown_type] = breakdown
            else:
                self.stats[scoring_period] = {points_type: points, breakdown_type: breakdown}
        self.total_points = self.stats.get(0, {}).get('points', 0)
        self.projected_total_points = self.stats.get(0, {}).get('projected_points', 0)
            
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
        
