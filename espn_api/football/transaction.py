class Transaction(object):
    def __init__(self, data, player_map, get_team_data):
        self.team = get_team_data(data['teamId'])
        self.type = data['type']
        self.status = data['status']
        self.scoring_period = data['scoringPeriodId']
        self.date = data.get('processDate')
        if not self.date:
            self.date = data.get('proposedDate')
        self.bid_amount = data.get('bidAmount')
        self.items = []
        for item in data['items']:
            self.items.append(TransactionItem(item, player_map))

    def __repr__(self):
        items = ', '.join([str(item) for item in self.items])
        return f'Transaction({self.team.team_name} {self.type} {items})'

class TransactionItem(object):
    def __init__(self, data, player_map):
        self.type = data['type']
        self.player = player_map[data['playerId']]

    def __repr__(self):
        return f'{self.type} {self.player}'