from .constant import ACTIVITY_MAP, POSITION_MAP

class Activity(object):
    def __init__(self, data, player_map, get_team_data, include_moved=False):
        self.actions = [] # List of tuples (Team, action, player)
        self.date = data['date']
        for msg in data['messages']:
            team = ''
            action = 'UNKNOWN'
            player = ''
            position = ''
            msg_id = msg['messageTypeId']
            if msg_id == 244:
                team = get_team_data(msg['from'])
            elif msg_id == 239:
                team = get_team_data(msg['for'])
            elif msg_id == 188 and include_moved and msg['to'] in POSITION_MAP:
                position = POSITION_MAP[msg['to']]
            else:
                team = get_team_data(msg['to'])
            if msg_id in ACTIVITY_MAP:
                if include_moved:
                    action = ACTIVITY_MAP[msg_id]
                elif msg_id != 188:
                    action = ACTIVITY_MAP[msg_id]
            if msg['targetId'] in player_map:
                player = player_map[msg['targetId']]
            if action != 'UNKNOWN':
                self.actions.append((team, action, player, position))
    
    def __repr__(self):
        def format_action(tup):
            return '(%s)' % ','.join(str(x) for x in tup if x)
        if self.actions:
            return 'Activity(' + ' '.join(format_action(tup) for tup in self.actions) + ')'
        else:
            return ''





