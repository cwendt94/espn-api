from .constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP
from .utils import json_parsing
import pdb

class Player(object):
    '''Player are part of team'''
    def __init__(self, data):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP.get(json_parsing(data, 'defaultPositionId') - 1, json_parsing(data, 'defaultPositionId') - 1)
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP.get(pos, pos) for pos in json_parsing(data, 'eligibleSlots')]  # if position isn't in position map, just use the position id number
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP.get(json_parsing(data, 'proTeamId'), json_parsing(data, 'proTeamId'))
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.stats = {}

        # add available stats
        player = data.get('playerPoolEntry', {}).get('player') or data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)
            
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
