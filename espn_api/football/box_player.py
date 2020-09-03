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


        player_stats = player.get('stats')
        for stats in player_stats:
            stats_breakdown = stats.get('appliedStats') if stats.get('appliedStats') else stats.get('stats', {})
            points = round(stats.get('appliedTotal', 0), 2)
            if stats.get('statSourceId') == 0 and stats.get('scoringPeriodId') == week:
                self.points = points
                self.points_breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}
            elif stats.get('statSourceId') == 1 and stats.get('scoringPeriodId') == week:
                self.projected_points = points
                self.projected_breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}



    def __repr__(self):
        return 'Player(%s, points:%d, projected:%d)' % (self.name, self.points, self.projected_points)
