import datetime
import time
import json
from typing import List, Tuple
import pdb

from ..utils.logger import Logger
from ..requests.espn_requests import EspnFantasyRequests
from .team import Team
from .player import Player
from .matchup import Matchup
from .constant import PRO_TEAM_MAP

class League(object):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        self.logger = Logger(name='Basketball League', debug=debug)
        self.league_id = league_id
        self.year = year
        self.teams = []
        cookies = None

        if espn_s2 and swid:
            cookies = {
                'espn_s2': espn_s2,
                'SWID': swid
            }
        self.espn_request = EspnFantasyRequests(sport='nba', year=year, league_id=league_id, cookies=cookies, logger=self.logger)
        if username and password:
            self.espn_request.authentication(username, password)
            
        data = self._fetch_league()
        self._fetch_teams(data)

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):
        
        params = {
            'view': ['mTeam', 'mRoster', 'mMatchup',]
        }
        data = self.espn_request.league_get(params=params)

        self.currentMatchupPeriod = data['status']['currentMatchupPeriod']
        self.scoringPeriodId = data['scoringPeriodId']
        self.firstScoringPeriod = data['status']['firstScoringPeriod']
        self.start_date = datetime.datetime.fromtimestamp(min([i[1][1]/1000 for i in self._get_nba_schedule(1).items()])).date()
        
        return(data)


    def _fetch_teams(self, data):
        '''Fetch teams in league'''        
        teams = data['teams']
        members = data['members']
        schedule = data['schedule']

        team_roster = {}
        for team in data['teams']:
            
            team_roster[team['id']] = team['roster']
        
        for team in teams:
            for member in members:
                # For league that is not full the team will not have a owner field
                if 'owners' not in team or not team['owners']:
                    member = None
                    break
                elif member['id'] == team['owners'][0]:
                    break
            roster = team_roster[team['id']]
            self.teams.append(Team(team, member, roster, schedule))

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup.away_team == opponent.team_id:
                        matchup.away_team = opponent
                    if matchup.home_team == opponent.team_id:
                        matchup.home_team = opponent
                        

        # sort by team ID
        self.teams = sorted(self.teams, key=lambda x: x.team_id, reverse=False)

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

    
    def _get_nba_schedule(self, scoringPeriodId: int = None):
        '''get nba schedule for a given scoring period'''
        if not scoringPeriodId:
            scoringPeriodId=self.scoringPeriodId
        params = {
            'view': 'proTeamSchedules_wl'
        }
        data = self.espn_request.get(params=params)
        
        pro_teams = data['settings']['proTeams']
        pro_team_schedule = {}

        for team in pro_teams:
            if team['id'] != 0 and str(scoringPeriodId) in team['proGamesByScoringPeriod'].keys():
                game_data = team['proGamesByScoringPeriod'][str(scoringPeriodId)][0]
                pro_team_schedule[PRO_TEAM_MAP[team['id']]] = (PRO_TEAM_MAP[game_data['homeProTeamId']], game_data['date'])  if team['id'] == game_data['awayProTeamId'] else (PRO_TEAM_MAP[game_data['awayProTeamId']], game_data['date'])
        return pro_team_schedule

