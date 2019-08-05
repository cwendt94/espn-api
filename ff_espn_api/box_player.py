from .constant import POSITION_MAP
from .player import Player

class BoxPlayer(Player):
    '''player with extra data from a matchup'''
    def __init__(self, data):
        super(BoxPlayer, self).__init__(data)
        self.slot_position = POSITION_MAP[data['lineupSlotId']]
        self.points = 0
        self.projected_points = 0

        player_stats = data['playerPoolEntry']['player']['stats']
        if player_stats:
            self.points = round(player_stats[0]['appliedTotal'], 2)
        if len(player_stats) > 1:
            self.projected_points = round(player_stats[1]['appliedTotal'], 2)
    
    def __repr__(self):
        return 'Player(%s, points:%d, projected:%d)' % (self.name, self.points, self.projected_points)
