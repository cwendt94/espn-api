class Transaction(object):
    def __init__(self, data, player_map, get_team_data):
        self.team_id = data['teamId']
        self.team = get_team_data(self.team_id)
        self.type = data['type']
        self.status = data['status']
        self.scoring_period = data['scoringPeriodId']
        self.date = data.get('processDate') or data.get('acceptedDate') or data.get('proposedDate')
        self.bid_amount = data.get('bidAmount')
        self.related_transaction_id = data.get('relatedTransactionId')
        self.member_id = data.get('memberId')
        self.items = []
        for item in data.get('items') or []:
            self.items.append(TransactionItem(item, player_map))

    def __repr__(self):
        items = ', '.join([str(item) for item in self.items])
        team_name = self.team.team_name if self.team else f'Team({self.team_id})'
        return f'Transaction({team_name} {self.type} {items})'

class TransactionItem(object):
    def __init__(self, data, player_map):
        self.type = data['type']
        self.playerId = data['playerId']
        self.player = player_map.get(data['playerId'], 'Unknown')
        self.from_team_id = data.get('fromTeamId')
        self.to_team_id = data.get('toTeamId')

    def __repr__(self):
        return f'{self.type} {self.player}'
