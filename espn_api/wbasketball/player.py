from .constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP, STAT_ID_MAP
from espn_api.utils.utils import json_parsing

class Player(object):
    '''Player are part of team'''
    def __init__(self, data, year):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP[json_parsing(data, 'defaultPositionId')]
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.stats = {}

        # add available stats

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)

        for split in player.get('stats', []):
            id = self._stat_id_pretty(split['id'])
            applied_total = split.get('appliedTotal', 0)
            applied_avg =  round(split.get('appliedAverage', 0), 2)
            self.stats[id] = dict(applied_total=applied_total, applied_avg=applied_avg)
            if 'stats' in split:
                if 'averageStats' in split.keys():
                    self.stats[id]['avg'] = {STATS_MAP[i]: split['averageStats'][i] for i in split['averageStats'].keys() if STATS_MAP[i] != ''}
                    self.stats[id]['total'] = {STATS_MAP[i]: split['stats'][i] for i in split['stats'].keys() if STATS_MAP[i] != ''}
                else:
                    self.stats[id]['avg'] = None
                    self.stats[id]['total'] = None
        self.total_points = self.stats.get(f'{year}', {}).get('applied_total', 0)
        self.avg_points = self.stats.get(f'{year}', {}).get('applied_avg', 0)
        self.projected_total_points= self.stats.get(f'{year}_projected', {}).get('applied_total', 0)
        self.projected_avg_points = self.stats.get(f'{year}_projected', {}).get('applied_avg', 0)
            
    def __repr__(self):
        return f'Player({self.name})'
    
    def _stat_id_pretty(self, id: str):
        id_type = STAT_ID_MAP.get(id[:2])
        return f'{id[2:]}_{id_type}' if id_type else id[2:]