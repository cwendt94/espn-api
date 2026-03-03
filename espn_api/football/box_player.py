from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
from .player import Player
from datetime import datetime, timedelta


class BoxPlayer(Player):
    '''player with extra data from a matchup'''
    def __init__(self, data, pro_schedule, positional_rankings, week, year, player_team_cache=None):
        super(BoxPlayer, self).__init__(data, year)
        self.slot_position = 'FA'
        self.pro_opponent = "None" # professional team playing against
        self.pro_pos_rank = 0 # rank of professional team against player position
        self.game_played = 100 # 0-100 for percent of game played
        self.on_bye_week = False

        if 'lineupSlotId' in data:
            self.slot_position = POSITION_MAP[data['lineupSlotId']]

        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']

        # ESPN's top-level proTeamId is the player's CURRENT team, not their
        # team at time of the game. Always prefer the per-week proTeamId from
        # the actual stats entry, which has the correct team per scoring period.
        pro_team_id = player['proTeamId']
        player_stats = player.get('stats', [])

        # Check for an actual (statSourceId=0) entry for this week
        found_actual = False
        for stat in player_stats:
            if (stat.get('scoringPeriodId') == week
                    and stat.get('statSourceId') == 0
                    and stat.get('proTeamId', 0) != 0):
                pro_team_id = stat['proTeamId']
                self.proTeam = PRO_TEAM_MAP.get(pro_team_id, self.proTeam)
                found_actual = True
                break

        # Bye week / no actual stats — use cached team from a prior week
        if not found_actual and player_team_cache is not None:
            cached = player_team_cache.get(self.playerId)
            if cached:
                pro_team_id = cached
                self.proTeam = PRO_TEAM_MAP.get(pro_team_id, self.proTeam)

        # Update cache with this week's resolved team
        if player_team_cache is not None and found_actual:
            player_team_cache[self.playerId] = pro_team_id

        if pro_team_id in pro_schedule:
            (opp_id, date) = pro_schedule[pro_team_id]
            self.game_date = datetime.fromtimestamp(date/1000.0)
            self.game_played = 100 if datetime.now() > self.game_date + timedelta(hours=3) else 0
            posId = str(player['defaultPositionId'])
            if posId in positional_rankings:
                self.pro_opponent = PRO_TEAM_MAP[opp_id]
                self.pro_pos_rank = positional_rankings[posId][str(opp_id)] if str(opp_id) in positional_rankings[posId] else 0
        else: # bye week
            self.on_bye_week = True

        stats = self.stats.get(week, {})
        self.points = stats.get('points', 0)
        self.breakdown = stats.get('breakdown', {})
        self.points_breakdown = stats.get('points_breakdown', {})
        self.projected_points = stats.get('projected_points', 0)
        self.projected_breakdown = stats.get('projected_breakdown', {})
        self.projected_points_breakdown = stats.get('projected_points_breakdown', {})

    def __repr__(self):
        return f'Player({self.name}, points:{self.points}, projected:{self.projected_points})'
