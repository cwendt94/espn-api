class Trade(object):
    def __init__(self, team1, team2, data):
        self.team_1 = team1.team_name
        self.team_1_players = []
        self.team_2 = team2.team_name
        self.team_2_players = []
        for players in data['pendingMoveItems']:
            if players['fromTeamId'] == team1.team_id:
                player1_name = team1.get_player_name(players['playerId'])
                if players['moveTypeId'] == 3:
                    player1_name = "Drop " + player1_name
                self.team_1_players.append(player1_name)
            else:
                player2_name = team2.get_player_name(players['playerId'])
                if players['moveTypeId'] == 3:
                    player2_name = "Drop " + player2_name
                self.team_2_players.append(player2_name)