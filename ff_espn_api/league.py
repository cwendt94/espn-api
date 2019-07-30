import requests
import datetime
import time
from typing import List, Tuple


from .team import Team
from .trade import Trade
from .settings import Settings
from .matchup import Matchup
from .pick import Pick


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
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None):
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
        self.current_week = 0
        self.nfl_week = 0
        if self.espn_s2 and self.swid:
            self.cookies = {
                'espn_s2': self.espn_s2,
                'SWID': self.swid
            }
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
                # get member info
                if member['id'] == team['owners'][0]:
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
            playerName = self.player_map[playerId]
            round_num = pick['roundId']
            round_pick = pick['roundPickNumber']

            self.draft.append(Pick(team, playerId, playerName, round_num, round_pick))

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
        standings = sorted(self.teams, key=lambda x: x.final_standing, reverse=False)
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
    
    # TODO League Trades, checks if any trades happened recently
    def league_trades(self):
        pass

    def scoreboard(self, week=None):
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
