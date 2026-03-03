from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
from .utils import json_parsing
from datetime import datetime

class Player(object):
    '''Player are part of team'''
    def __init__(self, data, year, pro_team_schedule = None):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.posRank = json_parsing(data, 'positionalRanking')
        self.eligibleSlots = [POSITION_MAP[pos] for pos in json_parsing(data, 'eligibleSlots')]
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.proTeam = PRO_TEAM_MAP[json_parsing(data, 'proTeamId')]
        self.jersey = json_parsing(data, 'jersey')
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.onTeamId = json_parsing(data, 'onTeamId')
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.position = ''
        self.stats = {}
        self.schedule = {}

        # Get players main position
        for pos in json_parsing(data, 'eligibleSlots'):
            if (pos != 25 and '/' not in POSITION_MAP[pos]) or '/' in self.name:
                self.position = POSITION_MAP[pos]
                break

        if pro_team_schedule:
            pro_team_id = json_parsing(data, 'proTeamId')
            pro_team = pro_team_schedule.get(pro_team_id, {})
            for key in pro_team:
                game = pro_team[key][0]
                team = game['awayProTeamId'] if game['awayProTeamId'] != pro_team_id else game['homeProTeamId']
                self.schedule[key] = { 'team': PRO_TEAM_MAP[team], 'date': datetime.fromtimestamp(game['date']/1000.0) }

        # set each scoring period stat
        player = data['playerPoolEntry']['player'] if 'playerPoolEntry' in data else data['player']
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)
        self.percent_owned = round(player.get('ownership', {}).get('percentOwned', -1), 2)
        self.percent_started = round(player.get('ownership', {}).get('percentStarted', -1), 2)

        self.active_status = 'bye'
        player_stats = player.get('stats', [])
        for stats in player_stats:
            if stats.get('seasonId') != year or stats.get('statSplitTypeId') == 2:
                continue

            # real game stats (number of yards, number of passes, etc)- PLAYER_MAP may not be quite correct
            stats_breakdown = stats.get('stats', {})
            breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}
            # fantasy stats (points per td, ppr, points per yard bucket)
            applied_stats = stats.get('appliedStats', {})
            points_breakdown = {PLAYER_STATS_MAP.get(int(k), k):v for (k,v) in applied_stats.items()}

            points = round(stats.get('appliedTotal', 0), 2)
            avg_points = round(stats.get('appliedAverage', 0), 2)
            scoring_period = stats.get('scoringPeriodId')
            stat_source = stats.get('statSourceId')
            (points_type, breakdown_type, points_breakdown_type, avg_type) = ('points', 'breakdown', 'points_breakdown', 'avg_points') if stat_source == 0 else ('projected_points', 'projected_breakdown', 'projected_points_breakdown', 'projected_avg_points')
            if self.stats.get(scoring_period):
                self.stats[scoring_period][points_type] = points
                self.stats[scoring_period][breakdown_type] = breakdown
                self.stats[scoring_period][points_breakdown_type] = points_breakdown
                self.stats[scoring_period][avg_type] = avg_points
            else:
                self.stats[scoring_period] = {points_type: points, breakdown_type: breakdown, points_breakdown_type: points_breakdown, avg_type: avg_points}
            if not stat_source:
                if not self.stats[scoring_period][breakdown_type]:
                    self.active_status = 'inactive'
                else:
                    self.active_status = 'active'
        self.total_points = self.stats.get(0, {}).get('points', 0)
        self.projected_total_points = self.stats.get(0, {}).get('projected_points', 0)
        self.avg_points = self.stats.get(0, {}).get('avg_points', 0)
        self.projected_avg_points = self.stats.get(0, {}).get('projected_avg_points', 0)

    def __repr__(self):
        return f'Player({self.name})'
