import requests
import json
from .constant import FANTASY_BASE_ENDPOINT, FANTASY_SPORTS
from ..utils.logger import Logger
from typing import List


class ESPNAccessDenied(Exception):
    pass


class ESPNInvalidLeague(Exception):
    pass


class ESPNUnknownError(Exception):
    pass


def checkRequestStatus(status: int, cookies=None, league_id=None) -> None:
    if cookies is None:
        cookies = {}
    if league_id is None:
        league_id = ""
    if status == 401:
        raise ESPNAccessDenied(f"League {league_id} cannot be accessed with espn_s2={cookies.get('espn_s2')} and swid={cookies.get('SWID')}")

    elif status == 404:
        raise ESPNInvalidLeague(f"League {league_id} does not exist")

    elif status != 200:
        raise ESPNUnknownError(f"ESPN returned an HTTP {status}")


class EspnFantasyRequests(object):
    def __init__(self, sport: str, year: int, league_id: int, cookies: dict = None, logger: Logger = None):
        if sport not in FANTASY_SPORTS:
            raise Exception(f'Unknown sport: {sport}, available options are {FANTASY_SPORTS.keys()}')
        self.year = year
        self.league_id = league_id
        self.ENDPOINT = FANTASY_BASE_ENDPOINT + FANTASY_SPORTS[sport] + '/seasons/' + str(self.year)
        self.cookies = cookies
        self.logger = logger

        self.LEAGUE_ENDPOINT = FANTASY_BASE_ENDPOINT + FANTASY_SPORTS[sport]
        # older season data is stored at a different endpoint
        if year < 2018:
            self.LEAGUE_ENDPOINT += "/leagueHistory/" + str(league_id) + "?seasonId=" + str(year)
        else:
            self.LEAGUE_ENDPOINT += "/seasons/" + str(year) + "/segments/0/leagues/" + str(league_id)
        
        # Try the first endpoint and fall back to the second if the first fails
        self.check_league_endpoint()
    def league_get(self, params: dict = None, headers: dict = None, extend: str = ''):
        endpoint = self.LEAGUE_ENDPOINT + extend
        r = requests.get(endpoint, params=params, headers=headers, cookies=self.cookies)
        checkRequestStatus(r.status_code, cookies=self.cookies, league_id=self.league_id)

        if self.logger:
            self.logger.log_request(endpoint=endpoint, params=params, headers=headers, response=r.json())
        return r.json() if self.year > 2017 else r.json()[0]

    def get(self, params: dict = None, headers: dict = None, extend: str = ''):
        endpoint = self.ENDPOINT + extend
        r = requests.get(endpoint, params=params, headers=headers, cookies=self.cookies)
        checkRequestStatus(r.status_code)

        if self.logger:
            self.logger.log_request(endpoint=endpoint, params=params, headers=headers, response=r.json())
        return r.json()

    def get_league(self):
        '''Gets all of the leagues initial data (teams, roster, matchups, settings)'''
        params = {
            'view': ['mTeam', 'mRoster', 'mMatchup', 'mSettings', 'mStandings']
        }
        data = self.league_get(params=params)
        return data

    def get_pro_schedule(self):
        '''Gets the current sports professional team schedules'''
        params = {
            'view': 'proTeamSchedules_wl'
        }
        data = self.get(params=params)
        return data

    def get_pro_players(self):
        '''Gets the current sports professional players'''
        params = {
            'view': 'players_wl'
        }
        filters = {"filterActive": {"value": True}}
        headers = {'x-fantasy-filter': json.dumps(filters)}
        data = self.get(extend='/players', params=params, headers=headers)
        return data

    def get_league_draft(self):
        '''Gets the leagues draft'''
        params = {
            'view': 'mDraftDetail',
        }
        data = self.league_get(params=params)
        return data

    def get_league_message_board(self, msg_types = None):
        '''Gets league message board and can filter by msg types'''
        params = {
            'view': 'kona_league_messageboard'
        }
        headers = None
        if msg_types is not None:
            filters = { "topicsByType": {} }
            base_filter = {"sortMessageDate":{"sortPriority":1,"sortAsc":False}}
            for msg_type in msg_types:
                filters['topicsByType'][msg_type] = base_filter
            headers = {'x-fantasy-filter': json.dumps(filters)}

        extend = "/segments/0/leagues/" + str(self.league_id) + '/communication'

        data = self.get(params=params, extend=extend, headers=headers)
        return data

    def get_player_card(self, playerIds: List[int], max_scoring_period: int, additional_filters: List = None):
        '''Gets the player card'''
        params = { 'view': 'kona_playercard' }

        additional_value = ["00{}".format(self.year), "10{}".format(self.year)]
        if additional_filters : additional_value += additional_filters

        filters = {'players':{'filterIds':{'value': playerIds}, 'filterStatsForTopScoringPeriodIds':{'value': max_scoring_period, 'additionalValue': additional_value}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        data = self.league_get(params=params, headers=headers)
        return data
        
    def check_league_endpoint(self):
        # First, try the current LEAGUE_ENDPOINT
        r = requests.get(self.LEAGUE_ENDPOINT, cookies=self.cookies)

        # If the response is 401 Unauthorized, switch to the other endpoint
        if r.status_code == 401:
            # If the current LEAGUE_ENDPOINT was using the /leagueHistory/ endpoint, switch to the /seasons/{year}/segments/0 endpoint
            if "/leagueHistory/" in self.LEAGUE_ENDPOINT:
                alternate_endpoint = self.LEAGUE_ENDPOINT.replace("/leagueHistory/", "/seasons/" + str(self.year) + "/segments/0/leagues/")
            else:
                # Otherwise, switch to the /leagueHistory/{league_id}?seasonId={year} endpoint
                alternate_endpoint = self.LEAGUE_ENDPOINT.replace("/seasons/" + str(self.year) + "/segments/0/leagues/", "/leagueHistory/") + "?seasonId=" + str(self.year)

            # Try the alternate endpoint
            r = requests.get(alternate_endpoint, cookies=self.cookies)
            
            # If the alternate endpoint works (status 200), update the LEAGUE_ENDPOINT
            if r.status_code == 200:
                self.LEAGUE_ENDPOINT = alternate_endpoint
                if self.logger:
                    self.logger.logging.info(f"Switched to alternate endpoint: {self.LEAGUE_ENDPOINT}")
            else:
                # If both endpoints fail, log the error and raise an exception
                if self.logger:
                    self.logger.logging.error(f"Both endpoints failed with status: {r.status_code}")
                raise Exception(f"Both endpoints for league {self.league_id} failed with status {r.status_code}")

    # Username and password no longer works using their API without using google recaptcha
    # Possibly revisit in future if anything changes
 
    # def authentication(self, username: str, password: str):
    #     url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
    #     url_login = 'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US'

    #     # Make request to get the API-Key
    #     headers = {'Content-Type': 'application/json'}
    #     response = requests.post(url_api_key, headers=headers)
    #     if response.status_code != 200 or 'api-key' not in response.headers:
    #         print('Unable to access API-Key')
    #         print('Retry the authentication or continuing without private league access')
    #         return
    #     api_key = response.headers['api-key']

    #     # Utilize API-Key and login information to get the swid and s2 keys
    #     headers['authorization'] = 'APIKEY ' + api_key
    #     payload = {'loginValue': username, 'password': password}
    #     response = requests.post(url_login, headers=headers, json=payload)
    #     if response.status_code != 200:
    #         print('Authentication unsuccessful - check username and password input')
    #         print('Retry the authentication or continuing without private league access')
    #         return
    #     data = response.json()
    #     if data['error'] is not None:
    #         print('Authentication unsuccessful - error:' + str(data['error']))
    #         print('Retry the authentication or continuing without private league access')
    #         return
    #     self.cookies = {
    #         "espn_s2": data['data']['s2'],
    #         "swid": data['data']['profile']['swid']
    #     }
