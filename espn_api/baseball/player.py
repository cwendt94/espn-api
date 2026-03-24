from datetime import datetime
from .constant import DEFAULT_POSITION_MAP, POSITION_MAP, PRO_TEAM_MAP, STATS_MAP
from .utils import json_parsing

class Player(object):
    '''Player are part of team'''
    def __init__(self, data, year):
        self.name = json_parsing(data, 'fullName')
        self.playerId = json_parsing(data, 'id')
        self.position = DEFAULT_POSITION_MAP.get(json_parsing(data, 'defaultPositionId'), str(json_parsing(data, 'defaultPositionId')))
        self.lineupSlot = POSITION_MAP.get(data.get('lineupSlotId'), '')
        self.eligibleSlots = [POSITION_MAP.get(pos, pos) for pos in json_parsing(data, 'eligibleSlots')]  # if position isn't in position map, just use the position id number
        self.acquisitionType = json_parsing(data, 'acquisitionType')
        self.acquisitionDate = json_parsing(data, 'acquisitionDate')
        self.proTeam = PRO_TEAM_MAP.get(json_parsing(data, 'proTeamId'), json_parsing(data, 'proTeamId'))
        self.injuryStatus = json_parsing(data, 'injuryStatus')
        self.status = json_parsing(data, 'status')
        self.stats = {}

        # pool entry fields exist either nested under 'playerPoolEntry' (roster/free agent)
        # or at the top level (player_info card response)
        pool_entry = data.get('playerPoolEntry') or data
        self.on_team_id = pool_entry.get('onTeamId')
        self.keeper_value = pool_entry.get('keeperValue')
        self.keeper_value_future = pool_entry.get('keeperValueFuture')
        self.lineup_locked = pool_entry.get('lineupLocked', False)
        self.roster_locked = pool_entry.get('rosterLocked', False)
        self.trade_locked = pool_entry.get('tradeLocked', False)

        player = pool_entry.get('player') or data.get('player', {})
        self.injuryStatus = player.get('injuryStatus', self.injuryStatus)
        self.injured = player.get('injured', False)
        self.first_name = player.get('firstName', '')
        self.last_name = player.get('lastName', '')
        self.active = player.get('active', True)
        self.droppable = player.get('droppable', True)
        self.jersey = player.get('jersey')
        self.laterality = player.get('laterality')
        self.stance = player.get('stance')
        raw_news_date = player.get('lastNewsDate')
        self.last_news_date = datetime.fromtimestamp(raw_news_date / 1000) if raw_news_date else None
        self.season_outlook = player.get('seasonOutlook', '')

        ownership = player.get('ownership', {})
        self.percent_owned = round(ownership.get('percentOwned', -1), 2)
        self.percent_started = round(ownership.get('percentStarted', -1), 2)
        self.percent_owned_change = ownership.get('percentChange')
        self.adp = ownership.get('averageDraftPosition')
        self.adp_change = ownership.get('averageDraftPositionPercentChange')
        self.auction_value = ownership.get('auctionValueAverage')
        self.auction_value_change = ownership.get('auctionValueAverageChange')

        self.draft_ranks = {
            rank_type: {'rank': rank_data['rank'], 'auction_value': rank_data['auctionValue']}
            for rank_type, rank_data in player.get('draftRanksByRankType', {}).items()
        }

        # add available stats
        player_stats = player.get('stats', [])
        for stats in player_stats:
            stats_split_type = stats.get('statSplitTypeId')
            if stats.get('seasonId') != year or (stats_split_type != 0 and stats_split_type != 5):
                continue
            stats_breakdown = stats.get('stats') or stats.get('appliedStats', {})
            breakdown = {STATS_MAP.get(int(k), k):v for (k,v) in stats_breakdown.items()}
            points = round(stats.get('appliedTotal', 0), 2)
            scoring_period = stats.get('scoringPeriodId')
            stat_source = stats.get('statSourceId')
            (points_type, breakdown_type) = ('points', 'breakdown') if stat_source == 0 else ('projected_points', 'projected_breakdown')
            if self.stats.get(scoring_period):
                self.stats[scoring_period][points_type] = points
                self.stats[scoring_period][breakdown_type] = breakdown
            else:
                self.stats[scoring_period] = {points_type: points, breakdown_type: breakdown}

        self.total_points = self.stats.get(0, {}).get('points', 0)
        self.projected_total_points = self.stats.get(0, {}).get('projected_points', 0)

    def __repr__(self):
        return 'Player(%s)' % (self.name, )
