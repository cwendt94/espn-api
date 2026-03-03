from .constant import ACTIVITY_MAP

class Activity(object):
    def __init__(self, data, player_map, get_team_data, player_info):
        self.actions = [] # List of tuples (Team, action, Player)
        self.date = data['date']
        for msg in data['messages']:
            msg_id = msg['messageTypeId']

            # Trades: emit two rows — TRADE_SENT (from) + TRADE_RECEIVED (to)
            if msg_id == 244:
                from_team = get_team_data(msg['from'])
                to_team = get_team_data(msg.get('to'))

                player = None
                if from_team:
                    for team_player in from_team.roster:
                        if team_player.playerId == msg['targetId']:
                            player = team_player
                            break
                if not player and to_team:
                    for team_player in to_team.roster:
                        if team_player.playerId == msg['targetId']:
                            player = team_player
                            break
                if not player:
                    player = player_info(playerId=msg['targetId'])
                if not player:
                    player = msg.get('targetId', 'Unknown')

                self.actions.append((from_team, 'TRADE_SENT', player, 0))
                if to_team:
                    self.actions.append((to_team, 'TRADE_RECEIVED', player, 0))
                continue

            # Non-trade messages
            team = ''
            action = 'UNKNOWN'
            player = None
            bid_amount = 0
            if msg_id == 239:
                team = get_team_data(msg['for'])
            else:
                team = get_team_data(msg['to'])
            if msg_id in ACTIVITY_MAP:
                action = ACTIVITY_MAP[msg_id]
            if action == 'WAIVER ADDED':
                bid_amount = msg.get('from', 0)
            if team:
                for team_player in team.roster:
                    if team_player.playerId == msg['targetId']:
                        player = team_player
                        break
            if not player:
                player = player_info(playerId=msg['targetId'])
            if not player:
                player = msg.get('targetId', 'Unknown')
            self.actions.append((team, action, player, bid_amount))

    def __repr__(self):
        return 'Activity(' + ' '.join("(%s,%s,%s)" % tup[0:3] for tup in self.actions) + ')'





