import datetime
import time
import json
import math
from typing import List, Tuple, Union
import pdb

from ..base_league import BaseLeague
from .team import Team
from .player import Player
from .matchup import Matchup
from .box_score import BoxScore, H2HCategoryBoxScore, H2HPointsBoxScore
from.activity import Activity
from .constant import POSITION_MAP, ACTIVITY_MAP

class League(BaseLeague):
    '''Creates a League instance for Public/Private ESPN league'''

    ScoreTypes = {'H2H_CATEGORY': H2HCategoryBoxScore, 'H2H_POINTS': H2HPointsBoxScore}

    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, fetch_league=True, debug=False):
        super().__init__(league_id=league_id, year=year, sport='mlb', espn_s2=espn_s2, swid=swid, debug=debug)

        self._set_scoring_class = lambda scoring_type: League.ScoreTypes.get(scoring_type, BoxScore)

        self.scoring_type = None
        self._box_score_class = None

        if fetch_league:
            self.fetch_league()
        if self._box_score_class is None:
            self._box_score_class = self._set_scoring_class(self.scoring_type)

    def fetch_league(self):
        data = self._fetch_league()
        self.scoring_type = data['settings']['scoringSettings']['scoringType']
        self._fetch_teams(data)
        self._box_score_class = self._set_scoring_class(self.scoring_type)
        super()._fetch_draft()

    def _fetch_league(self):
        data = super()._fetch_league()
        self._fetch_players()
        return data

    def _fetch_teams(self, data):
        '''Fetch teams in league'''
        super()._fetch_teams(data, TeamClass=Team)

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            team.division_name = self.settings.division_map.get(team.division_id, '')
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup.away_team == opponent.team_id:
                        matchup.away_team = opponent
                    if matchup.home_team == opponent.team_id:
                        matchup.home_team = opponent

    def standings(self) -> List[Team]:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings

    def scoreboard(self, matchupPeriod: int = None) -> List[Matchup]:
        '''Returns list of matchups for a given matchup period'''
        if not matchupPeriod:
            matchupPeriod=self.currentMatchupPeriod

        params = {
            'view': 'mMatchup',
        }
        data = self.espn_request.league_get(params=params)
        schedule = data['schedule']
        matchups = [Matchup(matchup) for matchup in schedule if matchup['matchupPeriodId'] == matchupPeriod]

        for team in self.teams:
            for matchup in matchups:
                if matchup.home_team == team.team_id:
                    matchup.home_team = team
                elif matchup.away_team == team.team_id:
                    matchup.away_team = team

        return matchups

    def recent_activity(self, size: int = 25, msg_type: str = None, offset: int = 0) -> List[Activity]:
        '''Returns a list of recent league activities (Add, Drop, Trade)'''
        if self.year < 2019:
            raise Exception('Cant use recent activity before 2019')

        msg_types = [178,180,179,239,181,244]
        if msg_type in ACTIVITY_MAP:
            msg_types = [ACTIVITY_MAP[msg_type]]
        params = {
            'view': 'kona_league_communication'
        }

        filters = {"topics":{"filterType":{"value":["ACTIVITY_TRANSACTIONS"]},"limit":size,"limitPerMessageSet":{"value":25},"offset":offset,"sortMessageDate":{"sortPriority":1,"sortAsc":False},"sortFor":{"sortPriority":2,"sortAsc":False},"filterIncludeMessageTypeIds":{"value":msg_types}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(extend='/communication/', params=params, headers=headers)
        data = data['topics']
        
        # Pass self.player_info to the Activity constructor
        activity = [Activity(topic, self.player_map, self.get_team_data, self.player_info) for topic in data]

        return activity


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

        return [Player(player, self.year) for player in players]

    def box_scores(self, matchup_period: int = None, scoring_period: int = None) -> List[Union[BoxScore, H2HCategoryBoxScore]]:
        '''Returns list of box score for a given matchup or scoring period'''
        if self.year < 2019:
            raise Exception('Cant use box score before 2019')

        matchup_id = self.currentMatchupPeriod
        scoring_id = self.current_week
        if matchup_period and scoring_period:
            matchup_id = matchup_period
            scoring_id = scoring_period
        elif matchup_period and matchup_period < matchup_id:
            matchup_id = matchup_period

        params = {
            'view': ['mMatchupScore', 'mScoreboard'],
            'scoringPeriodId': scoring_id
        }

        filters = {"schedule":{"filterMatchupPeriodIds":{"value":[matchup_id]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.espn_request.league_get(params=params, headers=headers)
        pro_schedule = self._get_pro_schedule(scoring_id)

        schedule = data['schedule']
        box_data = [self._box_score_class(matchup, pro_schedule, self.year, scoring_id) for matchup in schedule]

        for team in self.teams:
            for matchup in box_data:
                if matchup.home_team == team.team_id:
                    matchup.home_team = team
                elif matchup.away_team == team.team_id:
                    matchup.away_team = team
        return box_data
    
    def player_info(self, name: str = None, playerId: Union[int, list] = None) -> Union[Player, List[Player]]:
        '''Returns Player class if name found'''

        if name:
            playerId = self.player_map.get(name)
        if playerId is None or isinstance(playerId, str):
            return None
        if not isinstance(playerId, list):
            playerId = [playerId]

        data = self.espn_request.get_player_card(playerId, self.finalScoringPeriod)
        pro_schedule = self._get_all_pro_schedule()

        # Adjust the Player constructor call here
        if len(data['players']) == 1:
            return Player(data['players'][0], self.year)  # Remove pro_schedule here
        if len(data['players']) > 1:
            return [Player(player, self.year) for player in data['players']]  # Remove pro_schedule here
