
class Pick(object):
    ''' Pick represents a pick in draft '''
    def __init__(self, team, playerId, playerName, round_num, round_pick, bid_amount, keeper_status, nominatingTeam):
        self.team = team
        self.playerId = playerId
        self.playerName = playerName
        self.round_num = round_num
        self.round_pick = round_pick
        self.bid_amount = bid_amount
        self.keeper_status = keeper_status
        self.nominatingTeam = nominatingTeam

    def __repr__(self):
        return 'Pick(%s, %s)' % (self.playerName, self.team)

    def auction_repr(self):
        return ', '.join(map(str, [self.team.owner, self.playerId, self.playerName, self.bid_amount, self.keeper_status]))
