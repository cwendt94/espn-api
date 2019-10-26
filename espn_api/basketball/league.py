import requests
import datetime
import time
import json
from typing import List, Tuple

from .logger import setup_logger
from .team import Team
from .player import Player


def checkRequestStatus(status: int) -> None:
    if 500 <= status <= 503:
            raise Exception(status)
    if status == 401:
        raise Exception("Access Denied")

    elif status == 404:
        raise Exception("Invalid League")

    elif status != 200:
        raise Exception('Unknown %s Error' % status)

class League(object):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        self.logger = setup_logger(debug=debug)
        self.league_id = league_id
        self.year = year
        # older season data is stored at a different endpoint 
        if year < 2018:
            self.ENDPOINT = "https://fantasy.espn.com/apis/v3/games/fba/leagueHistory/" + str(league_id) + "?seasonId=" + str(year)
        else:
            self.ENDPOINT = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + str(year) + "/segments/0/leagues/" + str(league_id)
        self.teams = []
        self.espn_s2 = espn_s2
        self.swid = swid
        self.cookies = None
        self.username = username
        self.password = password
        self.current_week = 0
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
        elif self.username and self.password:
            self.authentication()
            
        data = self._fetch_league()
        self._fetch_teams(data)

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):
        
        params = {
            'view': ['mTeam', 'mRoster', 'mMatchup']
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        self.logger.debug(f'ESPN API Request: {self.ENDPOINT} \nESPN API Response: {r.json()}\n')
        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]

        if self.year < 2018:
            self.current_week = data['scoringPeriodId']
        else:
            self.current_week = data['status']['currentMatchupPeriod']

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



    def authentication(self):
        url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
        url_login = 'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US'

        # Make request to get the API-Key
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url_api_key, headers=headers)
        if response.status_code != 200 or 'api-key' not in response.headers:
            print('Unable to access API-Key')
            print('Retry the authentication or continuing without private league access')
            return
        api_key = response.headers['api-key']

        # Utilize API-Key and login information to get the swid and s2 keys
        headers['authorization'] = 'APIKEY ' + api_key
        payload = {'loginValue': self.username, 'password': self.password}
        response = requests.post(url_login, headers=headers, json=payload)
        if response.status_code != 200:
            print('Authentication unsuccessful - check username and password input')
            print('Retry the authentication or continuing without private league access')
            return
        data = response.json()
        if data['error'] is not None:
            print('Authentication unsuccessful - error:' + str(data['error']))
            print('Retry the authentication or continuing without private league access')
            return
        self.cookies = {
            "espn_s2": data['data']['s2'],
            "swid": data['data']['profile']['swid']
        }

