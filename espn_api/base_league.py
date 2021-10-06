from abc import ABC
from typing import List, Tuple

from .base_settings import BaseSettings
from .utils.logger import Logger
from .requests.espn_requests import EspnFantasyRequests

class BaseLeague(ABC):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, sport: str, espn_s2=None, swid=None, username=None, password=None, debug=False):
        self.logger = Logger(name=f'{sport} league', debug=debug)
        self.league_id = league_id
        self.year = year
        self.teams = []
        self.draft = []
        self.player_map = {}

        cookies = None
        if espn_s2 and swid:
            cookies = {
                'espn_s2': espn_s2,
                'SWID': swid
            }
        self.espn_request = EspnFantasyRequests(sport=sport, year=year, league_id=league_id, cookies=cookies, logger=self.logger)
        if username and password:
            self.espn_request.authentication(username, password)

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self, SettingsClass = BaseSettings):
        data = self.espn_request.get_league()

        self.currentMatchupPeriod = data['status']['currentMatchupPeriod']
        self.scoringPeriodId = data['scoringPeriodId']
        self.firstScoringPeriod = data['status']['firstScoringPeriod']
        if self.year < 2018:
            self.current_week = data['scoringPeriodId']
        else:
            self.current_week = self.scoringPeriodId if self.scoringPeriodId <= data['status']['finalScoringPeriod'] else data['status']['finalScoringPeriod']
        self.settings = SettingsClass(data['settings'])
        return data

    def _fetch_teams(self, data, TeamClass):
        '''Fetch teams in league'''
        self.teams = []
        teams = data['teams']
        members = data['members']
        schedule = data['schedule']
        seasonId = data['seasonId']

        team_roster = {}
        for team in data['teams']:
            team_roster[team['id']] = team.get('roster', {})

        for team in teams:
            for member in members:
                # For league that is not full the team will not have a owner field
                if 'owners' not in team or not team['owners']:
                    member = None
                    break
                elif member['id'] == team['owners'][0]:
                    break
            roster = team_roster[team['id']]
            self.teams.append(TeamClass(team, roster=roster, member=member, schedule=schedule, year=seasonId))

        # sort by team ID
        self.teams = sorted(self.teams, key=lambda x: x.team_id, reverse=False)

    def _fetch_players(self):
        data = self.espn_request.get_pro_players()
        # Map all player id's to player name
        for player in data:
            # two way map to find playerId's by name
            self.player_map[player['id']] = player['fullName']
            # if two players have the same fullname use first one for now TODO update for multiple player names
            if player['fullName'] not in self.player_map:
                self.player_map[player['fullName']] = player['id']

    def _get_pro_schedule(self, scoringPeriodId: int = None):
        data = self.espn_request.get_pro_schedule()

        pro_teams = data['settings']['proTeams']
        pro_team_schedule = {}

        for team in pro_teams:
            pro_game = team.get('proGamesByScoringPeriod', {})
            if team['id'] != 0 and (str(scoringPeriodId) in pro_game.keys() and pro_game[str(scoringPeriodId)]):
                game_data = pro_game[str(scoringPeriodId)][0]
                pro_team_schedule[team['id']] = (game_data['homeProTeamId'], game_data['date'])  if team['id'] == game_data['awayProTeamId'] else (game_data['awayProTeamId'], game_data['date'])
        return pro_team_schedule

    def standings(self) -> List:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings