import datetime
import time
import json
from typing import List, Tuple

from ..base_league import BaseLeague
from .team import Team
from .matchup import Matchup
from .pick import Pick
from .box_score import BoxScore
from .box_player import BoxPlayer
from .player import Player
from .activity import Activity
from .utils import power_points, two_step_dominance
from .constant import POSITION_MAP, ACTIVITY_MAP

class League(BaseLeague):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, sport='nfl', espn_s2=espn_s2, swid=swid, username=username, password=password, debug=debug)
        self._fetch_league()

    def _fetch_league(self):
        data = super()._fetch_league()

        self.nfl_week = data['status']['latestScoringPeriod']
        self._fetch_players()
        self._fetch_teams(data)
        self._fetch_draft()

    def _fetch_teams(self, data):
        '''Fetch teams in league'''
        super()._fetch_teams(data, TeamClass=Team)

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            team.division_name = self.settings.division_map.get(team.division_id, '')
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams:
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

    def _fetch_draft(self):
        '''Creates list of Pick objects from the leagues draft'''
        data = self.espn_request.get_league_draft()
        
        # League has not drafted yet
        if not data['draftDetail']['drafted']:
            return
        
        picks = data['draftDetail']['picks']
        for pick in picks:
            team = self.get_team_data(pick['teamId'])
            playerId = pick['playerId']
            playerName = ''
            if playerId in self.player_map:
                playerName = self.player_map[playerId]
            round_num = pick['roundId']
            round_pick = pick['roundPickNumber']
            bid_amount = pick['bidAmount']
            keeper_status = pick['keeper']

            self.draft.append(Pick(team, playerId, playerName, round_num, round_pick, bid_amount, keeper_status))
    
    def _get_positional_ratings(self, week: int):
        params = {
            'view': 'mPositionalRatings',
            'scoringPeriodId': week,
        }
        data = self.espn_request.league_get(params=params)
        ratings = data['positionAgainstOpponent']['positionalRatings']

        positional_ratings = {}
        for pos, rating in ratings.items():
            teams_rating = {}
            for team, data in rating['ratingsByOpponent'].items():
                teams_rating[team] = data['rank']
            positional_ratings[pos] = teams_rating
        return positional_ratings

    def refresh(self):
        '''Gets latest league data. This can be used instead of creating a new League class each week'''
        data = super()._fetch_league()

        self.nfl_week = data['status']['latestScoringPeriod']
        self._fetch_teams(data)
    def load_roster_week(self, week: int) -> None:
        '''Sets Teams Roster for a Certain Week'''
        params = {
            'view': 'mRoster',
            'scoringPeriodId': week
        }
        data = self.espn_request.league_get(params=params)

        team_roster = {}
        for team in data['teams']:
            team_roster[team['id']] = team['roster']
        
        for team in self.teams:
            roster = team_roster[team.team_id]
            team._fetch_roster(roster, self.year)

    def standings(self) -> List[Team]:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings

    def top_scorer(self) -> Team:
        most_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=True)
        return most_pf[0]
    
    def least_scorer(self) -> Team:
        least_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=False)
        return least_pf[0]

    def most_points_against(self) -> Team:
        most_pa = sorted(self.teams, key=lambda x: x.points_against, reverse=True)
        return most_pa[0]

    def top_scored_week(self) -> Tuple[Team, int]:
        top_week_points = []
        for team in self.teams:
            top_week_points.append(max(team.scores[:self.current_week]))
        top_scored_tup = [(i, j) for (i, j) in zip(self.teams, top_week_points)]
        top_tup = sorted(top_scored_tup, key=lambda tup: int(tup[1]), reverse=True)
        return top_tup[0]
    
    def least_scored_week(self) -> Tuple[Team, int]:
        least_week_points = []
        for team in self.teams:
            least_week_points.append(min(team.scores[:self.current_week]))
        least_scored_tup = [(i, j) for (i, j) in zip(self.teams, least_week_points)]
        least_tup = sorted(least_scored_tup, key=lambda tup: int(tup[1]), reverse=False)
        return least_tup[0]

    def get_team_data(self, team_id: int) -> Team:
        for team in self.teams:
            if team_id == team.team_id:
                return team
        return None
    
    def recent_activity(self, size: int = 25, msg_type: str = None) -> List[Activity]:
        '''Returns a list of recent league activities (Add, Drop, Trade)'''
        if self.year < 2019:
            raise Exception('Cant use recent activity before 2019')

        msg_types = [178,180,179,239,181,244]
        if msg_type in ACTIVITY_MAP:
            msg_types = [ACTIVITY_MAP[msg_type]]
        params = {
            'view': 'kona_league_communication'
        }
        
        filters = {"topics":{"filterType":{"value":["ACTIVITY_TRANSACTIONS"]},"limit":size,"limitPerMessageSet":{"value":25},"offset":0,"sortMessageDate":{"sortPriority":1,"sortAsc":False},"sortFor":{"sortPriority":2,"sortAsc":False},"filterIncludeMessageTypeIds":{"value":msg_types}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(extend='/communication/', params=params, headers=headers)
        data = data['topics']
        activity = [Activity(topic, self.player_map, self.get_team_data, self.player_info) for topic in data]

        return activity

    def scoreboard(self, week: int = None) -> List[Matchup]:
        '''Returns list of matchups for a given week'''
        if not week:
            week = self.current_week

        params = {
            'view': 'mMatchupScore',
        }
        data = self.espn_request.league_get(params=params)

        schedule = data['schedule']
        matchups = [Matchup(matchup) for matchup in schedule if matchup['matchupPeriodId'] == week]

        for team in self.teams:
            for matchup in matchups:
                if matchup.home_team == team.team_id:
                    matchup.home_team = team
                elif matchup.away_team == team.team_id:
                    matchup.away_team = team
        
        return matchups

    def box_scores(self, week: int = None) -> List[BoxScore]:
        '''Returns list of box score for a given week\n
        Should only be used with most recent season'''
        if self.year < 2019:
            raise Exception('Cant use box score before 2019')
        if not week or week > self.current_week:
            week = self.current_week

        params = {
            'view': ['mMatchupScore', 'mScoreboard'],
            'scoringPeriodId': week,
        }
        
        filters = {"schedule":{"filterMatchupPeriodIds":{"value":[week]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(params=params, headers=headers)

        schedule = data['schedule']
        pro_schedule = self._get_pro_schedule(week)
        positional_rankings = self._get_positional_ratings(week)
        box_data = [BoxScore(matchup, pro_schedule, positional_rankings, week, self.year) for matchup in schedule]

        for team in self.teams:
            for matchup in box_data:
                if matchup.home_team == team.team_id:
                    matchup.home_team = team
                elif matchup.away_team == team.team_id:
                    matchup.away_team = team
        return box_data
        
    def power_rankings(self, week: int=None):
        '''Return power rankings for any week'''

        if not week or week <= 0 or week > self.current_week:
            week = self.current_week
        # calculate win for every week
        win_matrix = []
        teams_sorted = sorted(self.teams, key=lambda x: x.team_id,
                              reverse=False)

        for team in teams_sorted:
            wins = [0]*len(teams_sorted) 
            for mov, opponent in zip(team.mov[:week], team.schedule[:week]):
                opp = teams_sorted.index(opponent)
                if mov > 0:
                    wins[opp] += 1
            win_matrix.append(wins)
        dominance_matrix = two_step_dominance(win_matrix)
        power_rank = power_points(dominance_matrix, teams_sorted, week)
        return power_rank

    def free_agents(self, week: int=None, size: int=50, position: str=None, position_id: int=None) -> List[Player]:
        '''Returns a List of Free Agents for a Given Week\n
        Should only be used with most recent season'''

        if self.year < 2019:
            raise Exception('Cant use free agents before 2019')
        if not week:
            week = self.current_week
        
        slot_filter = []
        if position and position in POSITION_MAP:
            slot_filter = [POSITION_MAP[position]]
        if position_id:
            slot_filter.append(position_id)

        
        params = {
            'view': 'kona_player_info',
            'scoringPeriodId': week,
        }
        filters = {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"filterSlotIds":{"value":slot_filter},"limit":size,"sortPercOwned":{"sortPriority":1,"sortAsc":False},"sortDraftRanks":{"sortPriority":100,"sortAsc":True,"value":"STANDARD"}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        data = self.espn_request.league_get(params=params, headers=headers)

        players = data['players']
        pro_schedule = self._get_pro_schedule(week)
        positional_rankings = self._get_positional_ratings(week)

        return [BoxPlayer(player, pro_schedule, positional_rankings, week, self.year) for player in players]

    def player_info(self, name: str = None, playerId: int = None):
        ''' Returns Player class if name found '''

        if name:
            playerId = self.player_map.get(name)
        if playerId is None or isinstance(playerId, str):
            return None
        params = { 'view': 'kona_playercard' }
        filters = {'players':{'filterIds':{'value':[playerId]}, 'filterStatsForTopScoringPeriodIds':{'value':16, "additionalValue":["00{}".format(self.year), "10{}".format(self.year)]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        data = self.espn_request.league_get(params=params, headers=headers)
        
        if len(data['players']) > 0:
            return Player(data['players'][0], self.year)

