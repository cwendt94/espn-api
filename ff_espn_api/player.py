from .constant import POSITION_MAP

class Player(object):
    '''Player are part of team'''
    def __init__(self, data):
        player = data['playerPoolEntry']['player']
        self.name = player['fullName']
        self.playerId = data['playerId']
        if 'ratings' in data['playerPoolEntry']:
            self.posRank = data['playerPoolEntry']['ratings']['0']['positionalRanking']
        else:
            self.posRank = 0
        self.position = ''
        self.acquisitionType = data['acquisitionType']

        # Get players main position
        for pos in player['eligibleSlots']:
            if '/' not in POSITION_MAP[pos] or '/' in self.name:
                self.position = POSITION_MAP[pos]
                break
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
        
