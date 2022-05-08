from .constant import POSITION_MAP, PRO_TEAM_MAP, STATS_MAP
from .player import Player
from datetime import datetime, timedelta

class BoxPlayer(Player):
    '''player with extra data from a matchup'''
    def __init__(self, data, pro_schedule, year):
        super(BoxPlayer, self).__init__(data, year)
        self.slot_position = 'FA'
        self.pro_opponent = "None" # professional team playing against
        self.game_played = 100 # 0-100 for percent of game played
        self.points = 0
        self.points_breakdown = {}

        if 'lineupSlotId' in data:
            self.slot_position = POSITION_MAP[data['lineupSlotId']]

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        if player['proTeamId'] in pro_schedule:
            (opp_id, date) = pro_schedule[player['proTeamId']]
            self.game_played = 100 if datetime.now() > datetime.fromtimestamp(date/1000.0) + timedelta(hours=3) else 0
            self.pro_opponent = PRO_TEAM_MAP[opp_id]
                
        player_stats = player.get('stats', [])
        for stats in player_stats:
            stats_breakdown = stats.get('appliedStats') or stats.get('stats', {})
            breakdown = {STATS_MAP.get(k, k):v for (k,v) in stats_breakdown.items()}
            points = round(stats.get('appliedTotal', 0), 2)
            self.points = points
            self.points_breakdown = breakdown

    def __repr__(self):
        return f'Player({self.name}, points:{self.points})'
