from unittest import mock, TestCase
from ff_espn_api import League
import requests_mock
import json

class LeagueTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2018
        self.espn_endpoint = "https://fantasy.espn.com/apis/v3/games/FFL/seasons/" + str(self.season) + "/segments/0/leagues/" + str(self.league_id)
        with open('tests/unit/league_2018.json') as data:
            self.league_data = json.loads(data.read())
        with open('tests/unit/league_team_2018.json') as data:
            self.team_data = json.loads(data.read())
        with open('tests/unit/league_settings_2018.json') as data:
            self.settings_data = json.loads(data.read())
        with open('tests/unit/league_matchup_2018.json') as data:
            self.matchup_data = json.loads(data.read())
        with open('tests/unit/league_roster_2018.json') as data:
            self.roster_data = json.loads(data.read())

    @requests_mock.Mocker()        
    def test_error_status(self, m):
        m.get(self.espn_endpoint, status_code=501, json=self.league_data)
        with self.assertRaises(Exception):
            League(self.league_id, self.season)
    
    @requests_mock.Mocker()        
    def test_uknown_error_status(self, m):
        m.get(self.espn_endpoint, status_code=300, json=self.league_data)
        with self.assertRaises(Exception):
            League(self.league_id, self.season)

    @requests_mock.Mocker()        
    def test_create_object(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)
        self.assertEqual(repr(league), 'League(123, 2018)')
        self.assertEqual(repr(league.settings), 'Settings(FXBG League)')
        self.assertEqual(league.current_week, 16)
        self.assertEqual(len(league.teams), 10)
    
    @requests_mock.Mocker()        
    def test_load_roster_week(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)
        
        with open('tests/unit/league_roster_week1.json') as f:
            data = json.loads(f.read())
        m.get(self.espn_endpoint + '?view=mRoster&scoringPeriodId=1', status_code=200, json=data)
        league.load_roster_week(1)

        # check player that I know is on roster
        name = ''
        team = league.teams[1]
        for player in team.roster:
            if player.name == "Le'Veon Bell":
                name = player.name
        self.assertEqual(name, "Le'Veon Bell")
    
    @requests_mock.Mocker()        
    def test_league_standings(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        standings = league.standings()
        self.assertEqual(standings[0].final_standing, 1)

    @requests_mock.Mocker()        
    def test_top_scorer(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.top_scorer()
        self.assertEqual(team.team_id, 1)
    
    @requests_mock.Mocker()        
    def test_least_scorer(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.least_scorer()
        self.assertEqual(team.team_id, 10)

    @requests_mock.Mocker()        
    def test_most_pa(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.most_points_against()
        self.assertEqual(team.team_id, 2)

    @requests_mock.Mocker()        
    def test_top_scored(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.top_scored_week()
        self.assertEqual(team[0].team_id, 5)     

    @requests_mock.Mocker()
    def test_least_scored(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.least_scored_week()
        self.assertEqual(team[0].team_id, 10)
    
    @requests_mock.Mocker()
    def test_get_team(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.get_team_data(8)
        self.assertEqual(team.team_id, 8) 

        team = league.get_team_data(18)
        self.assertEqual(team, None)
    
    @requests_mock.Mocker()        
    def test_get_scoreboard(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)
        
        with open('tests/unit/league_matchupScore_2018.json') as f:
            data = json.loads(f.read())
        m.get(self.espn_endpoint + '?view=mMatchupScore', status_code=200, json=data)

        scoreboard = league.scoreboard(1)
        self.assertEqual(repr(scoreboard[1]), 'Matchup(Team(Watch What  You Saquon), Team(Feel the  Brees))')
        self.assertEqual(scoreboard[0].home_score, 125.5)

        scoreboard = league.scoreboard()
        self.assertEqual(repr(scoreboard[-1]), 'Matchup(Team(Jacking Goff  On Sundays), Team(Feel the  Brees))')
        self.assertEqual(scoreboard[-1].away_score, 108.64)
    
    @requests_mock.Mocker()
    def test_player(self, m):
        m.get(self.espn_endpoint, status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mTeam', status_code=200, json=self.team_data)
        m.get(self.espn_endpoint + '?view=mSettings', status_code=200, json=self.settings_data)
        m.get(self.espn_endpoint + '?view=mMatchup', status_code=200, json=self.matchup_data)
        m.get(self.espn_endpoint + '?view=mRoster', status_code=200, json=self.roster_data)

        league = League(self.league_id, self.season)

        team = league.teams[2]
        self.assertEqual(repr(team.roster[0]), 'Player(Drew Brees)')
        self.assertEqual(team.get_player_name(2521161), 'Zach Zenner')
        self.assertEqual(team.get_player_name(0), '')

