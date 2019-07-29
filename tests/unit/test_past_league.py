from unittest import mock, TestCase
from ff_espn_api import League
import requests_mock
import json



class LeaguePastTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2015
        self.espn_endpoint = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(self.league_id) + "?seasonId=2015"
        with open('tests/unit/league_2015.json') as data:
            self.league_data = json.loads(data.read())
        with open('tests/unit/league_team_2015.json') as data:
            self.team_data = json.loads(data.read())
        with open('tests/unit/league_settings_2015.json') as data:
            self.settings_data = json.loads(data.read())
        with open('tests/unit/league_matchup_2015.json') as data:
            self.matchup_data = json.loads(data.read())
        with open('tests/unit/league_roster_2015.json') as data:
            self.roster_data = json.loads(data.read())

    @requests_mock.Mocker()        
    def test_create_object(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '&view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '&view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '&view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '&view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        self.assertEqual(league.nfl_week, 18)
        self.assertEqual(len(league.teams), 8)

    @requests_mock.Mocker()        
    def test_get_scoreboard(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '&view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '&view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '&view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '&view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)
        
        with open('tests/unit/league_matchupScore_2015.json') as f:
            data = json.loads(f.read())
        m.get(self.espn_endpoint + '&view=mMatchupScore', status_code=200, json=data)

        scoreboard = league.scoreboard(1)
        self.assertEqual(repr(scoreboard[1]), 'Matchup(Team(Go Deep Jack ), Team(Last Place))')
        self.assertEqual(scoreboard[0].home_score, 133)

        scoreboard = league.scoreboard()
        self.assertEqual(repr(scoreboard[-1]), 'Matchup(Team(Go Deep Jack ), Team(Last Place))')
        self.assertEqual(scoreboard[-1].away_score, 123)