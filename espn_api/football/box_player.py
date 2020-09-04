from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
from .player import Player
from datetime import datetime, timedelta

class BoxPlayer(Player):
    '''player with extra data from a matchup'''
    def __init__(self, data, pro_schedule, positional_rankings, week):
        super(BoxPlayer, self).__init__(data)
        self.slot_position = 'FA'
        self.points = 0
        self.projected_points = 0
        self.pro_opponent = "None" # professional team playing against
        self.pro_pos_rank = 0 # rank of professional team against player position
        self.game_played = 100 # 0-100 for percent of game played

        if 'lineupSlotId' in data:
            self.slot_position = POSITION_MAP[data['lineupSlotId']]

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        if player['proTeamId'] in pro_schedule:
            (opp_id, date) = pro_schedule[player['proTeamId']]
            self.game_played = 100 if datetime.now() > datetime.fromtimestamp(date/1000.0) + timedelta(hours=3) else 0
            posId = str(player['defaultPositionId'])
            if posId in positional_rankings:
                self.pro_opponent = PRO_TEAM_MAP[opp_id]
                self.pro_pos_rank = positional_rankings[posId][str(opp_id)] if str(opp_id) in positional_rankings[posId] else 0

        stats = self.stats.get(week)
        if stats and stats.get('stat_source') == 0:
            self.points = stats.get('points')
            self.points_breakdown = stats.get('breakdown')
        elif stats and stats.get('stat_source') == 1:
            self.projected_points = stats.get('points')
            self.projected_breakdown = stats.get('breakdown')



    def __repr__(self):
        return 'Player(%s, points:%d, projected:%d)' % (self.name, self.points, self.projected_points)
