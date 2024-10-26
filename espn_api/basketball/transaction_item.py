class TransactionItem(object):
    def __init__(self, data, player_map):
        self.type = data['type']
        self.player = player_map[data['playerId']]

    def __repr__(self):
        return f'{self.type} {self.player}'
