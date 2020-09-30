from .constant import ACTIVITY_MAP

class Activity(object):
    def __init__(self, data, player_map, get_team_data, player_info):
        self.actions = [] # List of tuples (Team, action, Player)
        self.date = data['date']
        for msg in data['messages']:
            team = ''
            action = 'UNKNOWN'
            player = None
            msg_id = msg['messageTypeId']
            if msg_id == 244:
                team = get_team_data(msg['from'])
            elif msg_id == 239:
                team = get_team_data(msg['for'])
            else:
                team = get_team_data(msg['to'])
            if msg_id in ACTIVITY_MAP:
                action = ACTIVITY_MAP[msg_id]
            if team:
                for team_player in team.roster:
                    if team_player.playerId == msg['targetId']:
                        player = team_player
                        break
            if not player:
                player = player_info(playerId=msg['targetId'])
            self.actions.append((team, action, player))
    
    def __repr__(self):
        return 'Activity(' + ' '.join("(%s,%s,%s)" % tup for tup in self.actions) + ')'





