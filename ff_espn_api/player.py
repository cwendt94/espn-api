class Player(object):
    '''Player are part of team'''
    def __init__(self, data, position_map):
        player = data['playerPoolEntry']['player']
        self.name = player['fullName']
        self.playerId = data['playerId']
        if 'ratings' in data['playerPoolEntry']:
            self.posRank = data['playerPoolEntry']['ratings']['0']['positionalRanking']
        else:
            self.posRank = 0
        self.position = ''

        # Get players main position
        for pos in player['eligibleSlots']:
            if '/' not in position_map[pos] or '/' in self.name:
                self.position = position_map[pos]
                break
    def __repr__(self):
        return 'Player(%s)' % (self.name, )
        
