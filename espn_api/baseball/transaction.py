from datetime import datetime

class Transaction(object):
    def __init__(self, data, player_map, get_team_data):
        self.team = get_team_data(data['teamId'])
        self.type = data['type']
        self.status = data.get('status')
        self.scoring_period = data['scoringPeriodId']
        raw_date = data.get('processDate') or data.get('proposedDate')
        self.date = datetime.fromtimestamp(raw_date / 1000) if raw_date else None
        self.bid_amount = data.get('bidAmount')
        self.isPending = self.status == 'PENDING'
        self.rating = data.get('rating')
        self.execution_type = data.get('executionType')
        self.relatedTransactionId = data.get('relatedTransactionId')
        self.comment = data.get('comment', '')
        self.memberId = data.get('memberId', '')
        self.items = []
        for item in data['items']:
            self.items.append(TransactionItem(item, player_map))

    def __repr__(self):
        items = ', '.join([str(item) for item in self.items])
        return f'Transaction({self.team.team_name} {self.type} {items})'

class TransactionItem(object):
    def __init__(self, data, player_map):
        self.type = data['type']
        self.player = player_map.get(data['playerId'], 'Unknown')
        self.fromTeamId = data.get('fromTeamId')
        self.toTeamId = data.get('toTeamId')
        self.fromLineupSlotId = data.get('fromLineupSlotId')
        self.toLineupSlotId = data.get('toLineupSlotId')
        self.isKeeper = data.get('isKeeper', False)
        self.overallPickNumber = data.get('overallPickNumber')

    def __repr__(self):
        return f'{self.type} {self.player}'
