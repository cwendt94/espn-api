from datetime import datetime
from typing import Any, Callable, Dict

class Transaction(object):
    def __init__(self, data: dict, player_map: Dict[int, str], get_team_data: Callable[[int], Any]):
        self.team_id = data['teamId']
        self.team = get_team_data(self.team_id)
        self.type = data['type']
        self.status = data.get('status')
        self.scoring_period = data['scoringPeriodId']
        raw_date = data.get('processDate') or data.get('proposedDate')
        self.date = datetime.fromtimestamp(raw_date / 1000) if raw_date else None
        self.bid_amount = data.get('bidAmount')
        self.is_pending = data.get('isPending', self.status == 'PENDING')
        self.rating = data.get('rating')
        self.execution_type = data.get('executionType')
        self.related_transaction_id = data.get('relatedTransactionId')
        self.comment = data.get('comment')
        self.member_id = data.get('memberId')
        self.items = []
        for item in data.get('items', []):
            self.items.append(TransactionItem(item, player_map))

    def __repr__(self):
        items = ', '.join([str(item) for item in self.items])
        team_name = self.team.team_name if self.team else f'Team({self.team_id})'
        return f'Transaction({team_name} {self.type} {items})'

class TransactionItem(object):
    def __init__(self, data, player_map):
        self.type = data['type']
        self.player_name = player_map.get(data['playerId'], 'Unknown')
        self.from_team_id = data.get('fromTeamId')
        self.to_team_id = data.get('toTeamId')
        self.from_lineup_slot_id = data.get('fromLineupSlotId')
        self.to_lineup_slot_id = data.get('toLineupSlotId')
        self.is_keeper = data.get('isKeeper', False)
        self.overall_pick_number = data.get('overallPickNumber')

    def __repr__(self):
        return f'{self.type} {self.player_name}'
