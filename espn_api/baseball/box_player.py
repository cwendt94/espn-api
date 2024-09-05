from .constant import POSITION_MAP, PRO_TEAM_MAP
from .player import Player
from datetime import datetime, timedelta


class BoxPlayer(Player):
    '''player with extra data from a matchup'''
    def __init__(self, data, pro_schedule, week, year):
        super(BoxPlayer, self).__init__(data, year)
        self.slot_position = 'FA'
        self.pro_opponent = "None" # professional team playing against
        self.pro_pos_rank = 0 # rank of professional team against player position
        self.game_played = 100 # 0-100 for percent of game played
        self.on_bye_week = False

        if 'lineupSlotId' in data:
            self.slot_position = POSITION_MAP[data['lineupSlotId']]

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        if player['proTeamId'] in pro_schedule:
            (opp_id, date) = pro_schedule[player['proTeamId']]
            self.game_date = datetime.fromtimestamp(date/1000.0)
            self.game_played = 100 if datetime.now() > self.game_date + timedelta(hours=3) else 0
            self.pro_opponent = PRO_TEAM_MAP[opp_id]
        else: # bye week
            self.on_bye_week = True

        stats = self.stats.get(week, {})
        self.points = stats.get('points', 0)
        self.points_breakdown = stats.get('breakdown', 0)
        self.projected_points = stats.get('projected_points', 0)
        self.projected_breakdown = stats.get('projected_breakdown', 0)

    def __repr__(self):
        return f'Player({self.name}, points:{self.points}, projected:{self.projected_points})'
