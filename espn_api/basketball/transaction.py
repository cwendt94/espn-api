from .transaction_item import TransactionItem

class Transaction(object):
    def __init__(self, data, player_map, get_team_data):
        self.team = get_team_data(data['teamId'])
        self.type = data['type']
        self.status = data['status']
        self.scoring_period = data['scoringPeriodId']
        self.date = data['processDate']
        self.bid_amount = data['bidAmount']
        self.items = []
        for item in data['items']:
            self.items.append(TransactionItem(item, player_map))

    def __repr__(self):
        items = ', '.join([str(item) for item in self.items])
        return f'Transaction({self.team.team_name} {self.type} {items})'
