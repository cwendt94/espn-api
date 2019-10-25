from .constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP
from .utils import json_parsing

class Player(object):
    '''Player are part of team'''
    def __init__(self, data):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP[json_parsing(data, 'defaultPositionId') - 1]
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.stats = {'current': {'avg': None, 'tot': None},
                      'last': {'avg': None, 'tot': None},
                      'projected': {'avg': None, 'tot': None},
                      }
        
        # add current season's stats
        cys = data['playerPoolEntry']['player']['stats'][0]
        if cys['stats']:
            self.stats['current']['avg'] = {STATS_MAP[i]: cys['averageStats'][i] for i in cys['averageStats'].keys() if STATS_MAP[i] != ''}
            self.stats['current']['tot'] = {STATS_MAP[i]: cys['stats'][i] for i in cys['stats'].keys() if STATS_MAP[i] != ''}            

        # add last season's stats
        try:
            lys = data['playerPoolEntry']['player']['stats'][6]
        except IndexError:
            lys = None        
        if lys:  # rookies don't have last season stats
            if lys['stats']: # players hurt the whole season don't have stats either
                self.stats['last']['avg'] = {STATS_MAP[i]: lys['averageStats'][i] for i in lys['averageStats'].keys() if STATS_MAP[i] != ''}
                self.stats['last']['tot'] = {STATS_MAP[i]: lys['stats'][i] for i in lys['stats'].keys() if STATS_MAP[i] != ''}

        # add current season projected stats
        pys = data['playerPoolEntry']['player']['stats'][4]
        if pys['stats']:
            self.stats['projected']['avg'] = {STATS_MAP[i]: pys['averageStats'][i] for i in pys['averageStats'].keys() if STATS_MAP[i] != ''}
            self.stats['projected']['tot'] = {STATS_MAP[i]: pys['stats'][i] for i in pys['stats'].keys() if STATS_MAP[i] != ''}            

            
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
        
