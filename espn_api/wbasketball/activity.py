from .constant import ACTIVITY_MAP

class Activity(object):
    def __init__(self, data, player_map, get_team_data):
        self.actions = [] # List of tuples (Team, action, player)
        self.date = data['date']
        for msg in data['messages']:
            team = ''
            action = 'UNKNOWN'
            player = ''
            msg_id = msg['messageTypeId']
            if msg_id == 244:
                team = get_team_data(msg['from'])
            elif msg_id == 239:
                team = get_team_data(msg['for'])
            else:
                team = get_team_data(msg['to'])
            if msg_id in ACTIVITY_MAP:
                action = ACTIVITY_MAP[msg_id]
            if msg['targetId'] in player_map:
                player = player_map[msg['targetId']]
            self.actions.append((team, action, player))
    
    def __repr__(self):
        return 'Activity(' + ' '.join("(%s,%s,%s)" % tup for tup in self.actions) + ')'





