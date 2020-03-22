from .constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP
from .utils import json_parsing
import pdb

class Player(object):
    '''Player are part of team'''
    def __init__(self, data):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP[json_parsing(data, 'defaultPositionId') - 1]
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.stats = {}

        # add available stats

        # 0020XX is full season stats for 20XX
        # 1020XX is projected season stats for 20XX
        # I think 0120XX, 0220XX, and 0320XX are last 7, last 15, and last 30
        # but I haven't figured out which yet (too season in season!)

        if 'stats' in data['playerPoolEntry']['player'].keys():
            for split in data['playerPoolEntry']['player']['stats']:
                
                if split['stats']:
                    self.stats[split['id']] = {}
                    if 'averageStats' in split.keys():
                        self.stats[split['id']]['avg'] = {STATS_MAP[i]: split['averageStats'][i] for i in split['averageStats'].keys() if STATS_MAP[i] != ''}
                        self.stats[split['id']]['total'] = {STATS_MAP[i]: split['stats'][i] for i in split['stats'].keys() if STATS_MAP[i] != ''}
                    else:
                        self.stats[split['id']]['avg'] = None
                        self.stats[split['id']]['total'] = None
            
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
        
