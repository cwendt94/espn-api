import datetime
import time
import json
from typing import List, Tuple
import pdb

from ..base_league import BaseLeague
from .team import Team
from .player import Player
from .matchup import Matchup
from .constant import PRO_TEAM_MAP

class League(BaseLeague):
    '''Creates a League instance for Public/Private ESPN league'''
    def __init__(self, league_id: int, year: int, espn_s2=None, swid=None, username=None, password=None, debug=False):
        super().__init__(league_id=league_id, year=year, sport='nba', espn_s2=espn_s2, swid=swid, username=username, password=password, debug=debug)
            
        data = self._fetch_league()
        self._fetch_teams(data)

    def _fetch_league(self):
        data = super()._fetch_league()
        self.start_date = datetime.datetime.fromtimestamp(min([i[1][1]/1000 for i in self._get_pro_schedule(1).items()])).date()
        
        return(data)


    def _fetch_teams(self, data):
        '''Fetch teams in league'''        
        super()._fetch_teams(data, TeamClass=Team)

        # replace opponentIds in schedule with team instances
        for team in self.teams:
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

