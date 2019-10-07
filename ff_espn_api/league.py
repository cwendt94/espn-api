import requests
import datetime
import time
import json
from typing import List, Tuple


from .team import Team
from .settings import Settings
from .matchup import Matchup
from .pick import Pick
from .box_score import BoxScore
from .box_player import BoxPlayer
from .player import Player
from .activity import Activity
from .free_agent_auction_bid import FreeAgentAuctionBid
from .utils import power_points, two_step_dominance
from .constant import POSITION_MAP


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
    def __init__(self, league_id: int, year: int,  username=None, password=None, espn_s2=None, swid=None):
        self.league_id = league_id
        self.year = year
        # older season data is stored at a different endpoint
        if year < 2018:
            self.ENDPOINT = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(league_id) + "?seasonId=" + str(year)
        else:
            self.ENDPOINT = "https://fantasy.espn.com/apis/v3/games/FFL/seasons/" + str(year) + "/segments/0/leagues/" + str(league_id)
        self.teams = []
        self.draft = []
        self.player_map = {}
        self.espn_s2 = espn_s2
        self.swid = swid
        self.cookies = None
        self.username = username
        self.password = password
        self.current_week = 0
        self.nfl_week = 0
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
        elif self.username and self.password:
            self.authentication()
        self._fetch_league()

    def __repr__(self):
        return 'League(%s, %s)' % (self.league_id, self.year, )

    def _fetch_league(self):

        r = requests.get(self.ENDPOINT, params='', cookies=self.cookies)
        self.status = r.status_code

        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
        if self.year < 2018:
            self.current_week = data['scoringPeriodId']
        else:
            self.current_week = data['status']['currentMatchupPeriod']
        self.nfl_week = data['status']['latestScoringPeriod']


        self._fetch_settings()
        self._fetch_players()
        self._fetch_teams()
        self._fetch_draft()

    def _fetch_teams(self):
        '''Fetch teams in league'''
        params = {
            'view': 'mTeam'
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code

        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
        teams = data['teams']
        members = data['members']

        params = {
            'view': 'mMatchup',
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
        schedule = data['schedule']

        params = {
            'view': 'mRoster',
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
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
            self.teams.append(Team(team, roster, member, schedule))

        # replace opponentIds in schedule with team instances
        for team in self.teams:
            for week, matchup in enumerate(team.schedule):
                for opponent in self.teams:
                    if matchup == opponent.team_id:
                        team.schedule[week] = opponent

        # calculate margin of victory
        for team in self.teams:
            for week, opponent in enumerate(team.schedule):
                mov = team.scores[week] - opponent.scores[week]
                team.mov.append(mov)

        # sort by team ID
        self.teams = sorted(self.teams, key=lambda x: x.team_id, reverse=False)

    def _fetch_settings(self):
        params = {
            'view': 'mSettings',
        }

        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code

        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
        self.settings = Settings(data['settings'])

    def _fetch_players(self):
        params = {
            'scoringPeriodId': 0,
            'view': 'players_wl',
        }

        endpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + str(self.year) + '/players'
        r = requests.get(endpoint, params=params, cookies=self.cookies)
        self.status = r.status_code

        checkRequestStatus(self.status)

        data = r.json()
        # Map all player id's to player name
        for player in data:
            self.player_map[player['id']] = player['fullName']


    def _fetch_draft(self):
        '''Creates list of Pick objects from the leagues draft'''
        params = {
            'view': 'mDraftDetail',
        }

        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code

        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]

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

    def _get_nfl_schedule(self, week: int):
        endpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + str(self.year) + '?view=proTeamSchedules_wl'
        r = requests.get(endpoint, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)

        pro_teams = r.json()['settings']['proTeams']
        pro_team_schedule = {}

        for team in pro_teams:
            if team['id'] != 0 and team['byeWeek'] != week:
                game_data = team['proGamesByScoringPeriod'][str(week)][0]
                pro_team_schedule[team['id']] = (game_data['homeProTeamId'], game_data['date'])  if team['id'] == game_data['awayProTeamId'] else (game_data['awayProTeamId'], game_data['date'])
        return pro_team_schedule

    def _get_positional_ratings(self, week: int):
        params = {
            'view': 'mPositionalRatings',
            'scoringPeriodId': week,
        }

        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)
        ratings = r.json()['positionAgainstOpponent']['positionalRatings']

        positional_ratings = {}
        for pos, rating in ratings.items():
            teams_rating = {}
            for team, data in rating['ratingsByOpponent'].items():
                teams_rating[team] = data['rank']
            positional_ratings[pos] = teams_rating
        return positional_ratings

    def load_roster_week(self, week: int) -> None:
        '''Sets Teams Roster for a Certain Week'''
        params = {
            'view': 'mRoster',
            'scoringPeriodId': week
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]
        team_roster = {}
        for team in data['teams']:
            team_roster[team['id']] = team['roster']

        for team in self.teams:
            roster = team_roster[team.team_id]
            team._fetch_roster(roster)

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

    def recent_activity(self, size: int = 25, only_trades = False) -> List[Activity]:
        '''Returns a list of recent league activities (Add, Drop, Trade)'''
        if self.year < 2019:
            raise Exception('Cant use recent activity before 2019')

        msg_types = [178,180,179,239,181,244]
        if only_trades:
            msg_types = [244]
        params = {
            'view': 'kona_league_communication'
        }

        filters = {"topics":{"filterType":{"value":["ACTIVITY_TRANSACTIONS"]},"limit":size,"limitPerMessageSet":{"value":25},"offset":0,"sortMessageDate":{"sortPriority":1,"sortAsc":False},"sortFor":{"sortPriority":2,"sortAsc":False},"filterDateRange":{"value":1564689600000,"additionalValue":1583110842000},"filterIncludeMessageTypeIds":{"value":msg_types}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        r = requests.get(self.ENDPOINT + '/communication/', params=params, cookies=self.cookies, headers=headers)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json()['topics']

        activity = [Activity(topic, self.player_map, self.get_team_data) for topic in data]

        return activity

    def get_free_agent_auction_bids(self, week: int = None) -> List[FreeAgentAuctionBid]:
        '''Returns a list of free agent auction bids'''
        if not week:
            week = self.current_week

        params = {
            'scoringPeriodId': week,
            'view': 'mTransactions2'
        }

        filters = {"transactions": {"filterType": {"value": ["WAIVER", "WAIVER_ERROR"]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies, headers=headers)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json()['transactions']

        bids = [FreeAgentAuctionBid(bid, self.player_map, self.get_team_data) for bid in data]

        return bids

    def free_agent_auction_report(self, week: int = None, report_num: int = None) -> None:
        '''Returns a human readable free agent auction report'''
        if not week:
            week = self.current_week
        bids = self.get_free_agent_auction_bids(week)
        # TODO: I don't know what ESPN returns if there are no waivers processed, don't have a league to test on
        if len(bids) == 0:
            print("There were no free agent auctions this week")
            return

        # If there are multiple waiver runs in a scoring period, ESPN API returns them all at once
        # need to determine how many waiver periods there were, and return the correct one
        reports = {bids[0].time: [bids[0]]}
        for bid in bids[1:]:
            found = False
            if bid.result != 'Canceled':
                for report_time in reports:
                    if bid.time == report_time:
                        reports[report_time].append(bid)
                        found = True
                        break
                if not found:
                    reports[bid.time] = [bid]
        reports = [report for _, report in sorted(reports.items())]
        if not report_num:
            report_num = 1
        if report_num > len(reports):
            print('ERROR: There are only {} free agent reports for week {}'.format(len(reports), week))
            return
        report = reports[report_num - 1]

        # sort by bid amount, grab largest remaining bid, and grab all other bids on that same player
        report.sort(reverse=True)
        output = []
        while len(report) > 0:
            if report[0].result == 'Processed':
                temp = '${2}: {0} to {1}'.format(self.player_map[report[0].player],
                                                  self.get_team_data(report[0].teamId).team_name,
                                                  report[0].amount)
                if report[0].dropped_player:
                    temp += ' (Dropped {})'.format(self.player_map[report[0].dropped_player])
                output.append(temp)
                for bid in list(report[1:]):  # iterate over copy of list, freeing us to modify the original
                    if bid.player == report[0].player:
                        temp = '    ${1} (${2}): {0}'.format(self.get_team_data(bid.teamId).team_name,
                                                             bid.amount,
                                                             bid.amount - report[0].amount)
                        if bid.amount > report[0].amount:
                            temp += ' (Player already dropped)'
                        output.append(temp)
                        report.remove(bid)
            else:
                temp = 'Player already dropped: ${0} {1} to {2} not processed' \
                    .format(report[0].amount,
                            self.player_map[report[0].player],
                            self.get_team_data(report[0].teamId).team_name)
                output.append(temp)
            report.remove(report[0])

        report_string = '\n'.join(output)
        return report_string

    def scoreboard(self, week: int = None) -> List[Matchup]:
        '''Returns list of matchups for a given week'''
        if not week:
            week = self.current_week

        params = {
            'view': 'mMatchupScore',
        }
        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json() if self.year > 2017 else r.json()[0]

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
            'view': 'mMatchupScore',
            'scoringPeriodId': week,
        }

        filters = {"schedule":{"filterMatchupPeriodIds":{"value":[week]}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        r = requests.get(self.ENDPOINT + '?view=mMatchup', params=params, cookies=self.cookies, headers=headers)
        self.status = r.status_code
        checkRequestStatus(self.status)

        data = r.json()

        schedule = data['schedule']
        pro_schedule = self._get_nfl_schedule(week)
        positional_rankings = self._get_positional_ratings(week)
        box_data = [BoxScore(matchup, pro_schedule, positional_rankings, week) for matchup in schedule]

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
            wins = [0]*32
            for mov, opponent in zip(team.mov[:week], team.schedule[:week]):
                opp = int(opponent.team_id)-1
                if mov > 0:
                    wins[opp] += 1
            win_matrix.append(wins)
        dominance_matrix = two_step_dominance(win_matrix)
        power_rank = power_points(dominance_matrix, teams_sorted, week)
        return power_rank

    def free_agents(self, week: int=None, size: int=50, position: str=None) -> List[Player]:
        '''Returns a List of Free Agents for a Given Week\n
        Should only be used with most recent season'''

        if self.year < 2019:
            raise Exception('Cant use free agents before 2019')
        if not week:
            week = self.current_week

        slot_filter = []
        if position and position in POSITION_MAP:
            slot_filter = [POSITION_MAP[position]]

        params = {
            'view': 'kona_player_info',
            'scoringPeriodId': week,
        }
        filters = {"players":{"filterStatus":{"value":["FREEAGENT","WAIVERS"]},"filterSlotIds":{"value":slot_filter},"limit":size,"sortPercOwned":{"sortPriority":1,"sortAsc":False},"sortDraftRanks":{"sortPriority":100,"sortAsc":True,"value":"STANDARD"}}}
        headers = {'x-fantasy-filter': json.dumps(filters)}

        r = requests.get(self.ENDPOINT, params=params, cookies=self.cookies, headers=headers)
        self.status = r.status_code
        checkRequestStatus(self.status)

        players = r.json()['players']
        pro_schedule = self._get_nfl_schedule(week)
        positional_rankings = self._get_positional_ratings(week)

        return [BoxPlayer(player, pro_schedule, positional_rankings, week) for player in players]

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
