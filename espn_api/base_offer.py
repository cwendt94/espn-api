from datetime import datetime


class Offer(object):
    def __init__(self, data, player_map, get_team_data):
        status = data['status']
        self.id = data['id']
        self.time = None
        if status == 'CANCELED':
            self.result = 'Canceled'
        else:
            if status == 'EXECUTED':
                self.result = 'Processed'
            elif status == 'FAILED_INVALIDPLAYERSOURCE':
                self.result = 'Outbid'
            elif status == 'FAILED_AUCTIONBUDGETEXCEEDED':
                self.result = 'Budget Exceeded'
            elif status == 'FAILED_POSITIONLIMIT':
                self.result = 'Position Limit Exceeded'
            elif status == 'FAILED_ROSTERLOCK':
                self.result = 'Failed Due to Roster Lock'
            elif status == 'FAILED_PLAYERALREADYDROPPED' or status == 'FAILED_ROSTERLIMIT' or status == 'PENDING':
                self.result = 'Player already dropped'
            else:
                self.result = status
            # fixes bug with unprocessed waivers stuck on "PENDING" status
            if 'processDate' in data:
                self.time = datetime.fromtimestamp(int(data['processDate'] / 1000))  # convert from milliseconds to seconds
            self.amount = data['bidAmount']
            self.teamId = data['teamId']
            self.dropped_player = None
            for item in data['items']:
                if item['type'] == 'ADD':
                    self.player = item['playerId']
                elif item['type'] == 'DROP' and self.result == 'Processed':
                    self.dropped_player = item['playerId']

    def __lt__(self, other):
        # sort by status, then bid amount
        result_ranking = {'Processed': 7,
                          'Outbid': 6,
                          'Player already dropped': 5,
                          'Budget Exceeded': 4,
                          'Position Limit Exceeded': 3,
                          'Failed Due to Roster Lock': 2,
                          'CANCELLED': 1,
                          'PENDING': 0}
        if result_ranking[self.result] != result_ranking[other.result]:
            return result_ranking[self.result] < result_ranking[other.result]
        else:
            # sort by bid amount
            return self.amount < other.amount

    def __repr__(self):
        if self.result == 'Canceled':
            return 'Canceled bid'
        else:
            ret_string = 'Offer(Date:{0}, Player:{1}, Team:{2}, Result:{3}, Bid:{4}'.format(self.time, self.player, self.teamId,
                                                                                self.result, self.amount)
            if self.dropped_player:
                ret_string += ', Dropped:{0})'.format(self.dropped_player)
            else:
                ret_string += ')'
            return ret_string