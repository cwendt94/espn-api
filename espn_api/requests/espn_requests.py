import requests
import json
from .constant import FANTASY_BASE_ENDPOINT, NEWS_BASE_ENDPOINT, FANTASY_SPORTS
from ..utils.logger import Logger
from typing import List


class ESPNAccessDenied(Exception):
    pass


class ESPNInvalidLeague(Exception):
    pass


class ESPNUnknownError(Exception):
    pass


class EspnFantasyRequests(object):
    def __init__(self, sport: str, year: int, league_id: int, cookies: dict = None, logger: Logger = None):
        if sport not in FANTASY_SPORTS:
            raise Exception(f'Unknown sport: {sport}, available options are {FANTASY_SPORTS.keys()}')
        self.year = year
        self.league_id = league_id
        self.ENDPOINT = FANTASY_BASE_ENDPOINT + FANTASY_SPORTS[sport] + '/seasons/' + str(self.year)
        self.NEWS_ENDPOINT = NEWS_BASE_ENDPOINT + FANTASY_SPORTS[sport] + '/news/' + 'players'
        self.cookies = cookies
        self.logger = logger

        self.LEAGUE_ENDPOINT = FANTASY_BASE_ENDPOINT + FANTASY_SPORTS[sport]
        # older season data is stored at a different endpoint
        if year < 2018:
            self.LEAGUE_ENDPOINT += "/leagueHistory/" + str(league_id) + "?seasonId=" + str(year)
        else:
            self.LEAGUE_ENDPOINT += "/seasons/" + str(year) + "/segments/0/leagues/" + str(league_id)

    def checkRequestStatus(self, status: int, extend: str = "", params: dict = None, headers: dict = None) -> dict:
        '''Handles ESPN API response status codes and endpoint format switching'''
        if status == 401:
            # Try the alternate endpoint without changing state until it succeeds.
            if "/leagueHistory/" in self.LEAGUE_ENDPOINT:
                base_endpoint = self.LEAGUE_ENDPOINT.split("/leagueHistory/")[0]
                alternate_endpoint = f"{base_endpoint}/seasons/{self.year}/segments/0/leagues/{self.league_id}"
            else:
                base_endpoint = self.LEAGUE_ENDPOINT.split(f"/seasons/")[0]
                alternate_endpoint = f"{base_endpoint}/leagueHistory/{self.league_id}?seasonId={self.year}"

            r = requests.get(alternate_endpoint + extend, params=params, headers=headers, cookies=self.cookies)

            if r.status_code == 200:
                response = r.json()
                self.LEAGUE_ENDPOINT = alternate_endpoint
                return response

            # If all endpoints failed, raise the corresponding error
            if not self.cookies or 'espn_s2' not in self.cookies or 'SWID' not in self.cookies:
                raise ESPNAccessDenied("espn_s2 and swid are required")

            raise ESPNAccessDenied(f"League {self.league_id} cannot be accessed with the provided credentials")

        elif status == 404:
            # Historical leagues often 404 on /communication/ with
            # COMMUNICATION_GROUP_NOT_FOUND. The league itself is valid;
            # recent_activity() should return no topics.
            if extend and 'communication' in extend:
                return {"topics": []}
            raise ESPNInvalidLeague(f"League {self.league_id} does not exist")

        elif status != 200:
            raise ESPNUnknownError(f"ESPN returned an HTTP {status}")

        # If no issues with the status code, return None
        return None

    def league_get(self, params: dict = None, headers: dict = None, extend: str = ''):
        endpoint = self.LEAGUE_ENDPOINT + extend
        r = requests.get(endpoint, params=params, headers=headers, cookies=self.cookies)
        alternate_response = self.checkRequestStatus(r.status_code, extend=extend, params=params, headers=headers)


        response = alternate_response if alternate_response else r.json()

        if self.logger:
            self.logger.log_request(endpoint=self.LEAGUE_ENDPOINT + extend, params=params, headers=headers, response=response)

        return response[0] if isinstance(response, list) else response

    def get(self, params: dict = None, headers: dict = None, extend: str = ''):
        endpoint = self.ENDPOINT + extend
        r = requests.get(endpoint, params=params, headers=headers, cookies=self.cookies)
        self.checkRequestStatus(r.status_code)

        if self.logger:
            self.logger.log_request(endpoint=endpoint, params=params, headers=headers, response=r.json())
        return r.json()

    def news_get(self, params: dict = None, headers: dict = None, extend: str = ''):
        endpoint = self.NEWS_ENDPOINT + extend
        r = requests.get(endpoint, params=params, headers=headers, cookies=self.cookies)

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

    def get_league_offers(self, week: int):
        '''Gets the league offers reports'''
        params = {
            'scoringPeriodId': week,
            'view': 'mTransactions2'
        }

        filters = {"transactions": {"filterType": {"value": ["WAIVER", "WAIVER_ERROR"]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        data = self.league_get(params=params, headers=headers)
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

    def get_player_pool_ids(self, week: int, page_size: int = 500) -> List[int]:
        '''Player ids in the league pool (rostered, FA, waivers) for card fetches.'''
        found = []
        seen = set()
        offset = 0
        while True:
            filters = {
                'players': {
                    'filterStatus': {'value': ['FREEAGENT', 'WAIVERS', 'ONTEAM']},
                    'limit': page_size,
                    'offset': offset,
                    'sortPercOwned': {'sortPriority': 1, 'sortAsc': False},
                }
            }
            headers = {'x-fantasy-filter': json.dumps(filters)}
            data = self.league_get(
                params={'view': 'kona_player_info', 'scoringPeriodId': week},
                headers=headers,
            )
            batch = data.get('players') if isinstance(data, dict) else None
            if not isinstance(batch, list) or not batch:
                break
            for wrap in batch:
                player_id = self._player_wrap_id(wrap)
                if player_id is None or player_id in seen:
                    continue
                seen.add(player_id)
                found.append(player_id)
            if len(batch) < page_size:
                break
            offset += page_size
        return found

    @staticmethod
    def _player_wrap_id(wrap):
        if not isinstance(wrap, dict):
            return None
        player_id = wrap.get('id')
        if isinstance(player_id, int) and player_id != 0:
            return player_id
        inner = wrap.get('player')
        if isinstance(inner, dict):
            inner_id = inner.get('id')
            if isinstance(inner_id, int) and inner_id != 0:
                return inner_id
        return None

    def get_player_news(self, playerId):
        '''Gets the player news'''
        params = {'playerId': playerId}
        data = self.news_get(params=params)
        return data

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
