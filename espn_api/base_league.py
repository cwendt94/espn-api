from abc import ABC
from typing import List, Tuple

from .base_settings import BaseSettings
from .base_pick import BasePick
from .utils.logger import Logger
from .requests.espn_requests import EspnFantasyRequests

class BaseLeague(ABC):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, sport: str, espn_s2=None, swid=None, debug=False):
        self.logger = Logger(name=f'{sport} league', debug=debug)
        self.league_id = league_id
        self.year = year
        self.teams = []
        self.members = []
        self.draft = []
        self.player_map = {}

        cookies = None
        if espn_s2 and swid:
            cookies = {
                'espn_s2': espn_s2,
                'SWID': swid
            }
        self.espn_request = EspnFantasyRequests(sport=sport, year=year, league_id=league_id, cookies=cookies, logger=self.logger)

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self, SettingsClass = BaseSettings):
        data = self.espn_request.get_league()

        self.currentMatchupPeriod = data['status']['currentMatchupPeriod']
        self.scoringPeriodId = data['scoringPeriodId']
        self.firstScoringPeriod = data['status']['firstScoringPeriod']
        self.finalScoringPeriod = data['status']['finalScoringPeriod']
        self.previousSeasons = [
            year for year in data["status"]["previousSeasons"] if year < self.year
        ]
        if self.year < 2018:
            self.current_week = data['scoringPeriodId']
        else:
            self.current_week = self.scoringPeriodId if self.scoringPeriodId <= data['status']['finalScoringPeriod'] else data['status']['finalScoringPeriod']
        self.settings = SettingsClass(data['settings'])
        self.members = data.get('members', [])
        return data

    def _fetch_draft(self):
        '''Creates list of Pick objects from the leagues draft'''
        data = self.espn_request.get_league_draft()

        # League has not drafted yet
        if not data.get('draftDetail', {}).get('drafted'):
            return

        picks = data.get('draftDetail', {}).get('picks', [])
        for pick in picks:
            team = self.get_team_data(pick.get('teamId'))
            playerId = pick.get('playerId')
            playerName = ''
            if playerId in self.player_map:
                playerName = self.player_map[playerId]
            round_num = pick.get('roundId')
            round_pick = pick.get('roundPickNumber')
            bid_amount = pick.get('bidAmount')
            keeper_status = pick.get('keeper')
            nominatingTeam = self.get_team_data(pick.get('nominatingTeamId'))
            self.draft.append(BasePick(team, playerId, playerName, round_num, round_pick, bid_amount, keeper_status, nominatingTeam))

    def _fetch_teams(self, data, TeamClass, pro_schedule = None):
        '''Fetch teams in league'''
        self.teams = []
        teams = data['teams']
        schedule = data['schedule']
        seasonId = data['seasonId']
        members = data.get('members', [])

        team_roster = {}
        for team in data['teams']:
            team_roster[team['id']] = team.get('roster', {})

        for team in teams:
            roster = team_roster[team['id']]
            owners = [member for member in members if member.get('id') in team.get('owners', [])]
            self.teams.append(TeamClass(team, roster=roster, schedule=schedule, year=seasonId, owners=owners, pro_schedule=pro_schedule))

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
    
    def _get_all_pro_schedule(self):
        data = self.espn_request.get_pro_schedule()

        pro_teams = data['settings']['proTeams']
        pro_team_schedule = {}

        for team in pro_teams:
            pro_game = team.get('proGamesByScoringPeriod', {})
            pro_team_schedule[team['id']] = pro_game
        return pro_team_schedule

    def standings(self) -> List:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings

    def get_team_data(self, team_id: int) -> List:
        for team in self.teams:
            if team_id == team.team_id:
                return team
        return None
