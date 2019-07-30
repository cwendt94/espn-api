
class Pick(object):
    ''' Pick represents a pick in draft '''
    def __init__(self, team, playerId, playerName, round_num, round_pick):
        self.team = team
        self.playerId = playerId
        self.playerName = playerName
        self.round_num = round_num
        self.round_pick = round_pick

    def __repr__(self):
        return 'Pick(%s, %s)' % (self.playerName, self.team)