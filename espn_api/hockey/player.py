from espn_api.utils.utils import json_parsing
from .constant import POSITION_MAP, STATS_MAP, PRO_TEAM_MAP, STATS_IDENTIFIER


class Player(object):

    def __init__(self, data):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = POSITION_MAP.get(json_parsing(data, 'defaultPositionId') - 1
                                         if json_parsing(data, 'defaultPositionId') and json_parsing(data, 'defaultPositionId') <= 3 
                                         else json_parsing(data, 'defaultPositionId'), '')
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP.get(pos, '') for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP.get(json_parsing(data, 'proTeamId'), 'Unknown Team')
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.stats = {}

        '''
        Options
        1. Today
        2. This season (2021) 002021
        3. Last 7             012021
        4. Last 15            022021
        5. Last 30            032021
        6. Last season (2020) 002020
        7. 2021 Projections   102021
        '''
        player = data.get('playerPoolEntry', {}).get('player') or data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)

        for split in player.get('stats', []):
            if split['stats']:
                id = split['id']
                stat_key = get_stat_key(id)

                self.stats[stat_key] = {}

                if 'stats' in split.keys():
                    self.stats[stat_key]['total'] = {STATS_MAP[i]: split['stats'][i] for i in split['stats'].keys()
                                                        if STATS_MAP[i] != ''}
                else:
                    self.stats[stat_key]['total'] = None

    def __repr__(self):
        return 'Player(%s)' % (self.name,)

def get_stat_key(id: str) -> str:
    if id[:2] in STATS_IDENTIFIER:
        stat_type = STATS_IDENTIFIER[id[:2]]
        return stat_type + ' ' + id[2:]

    return id
