from unittest import mock, TestCase
from espn_api.football import League
import requests_mock
import json



class LeaguePastTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2015
        self.espn_endpoint = "https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/" + str(self.league_id) + "?seasonId=2015"
        self.players_endpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + str(self.season) + '/players?view=players_wl'
        with open('tests/football/unit/data/league_2015_data.json') as data:
            self.league_data = json.loads(data.read())
        with open('tests/football/unit/data/league_draft_2015.json') as data:
            self.draft_data = json.loads(data.read())
        with open('tests/football/unit/data/league_players_2015.json') as data:
            self.players_data = json.loads(data.read())
    
    def mock_setUp(self, m):
        m.get(self.espn_endpoint + '&view=mTeam&view=mRoster&view=mMatchup&view=mSettings', status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '&view=mDraftDetail', status_code=200, json=self.draft_data)
        m.get(self.players_endpoint, status_code=200, json=self.players_data)

    @requests_mock.Mocker()        
    def test_create_object(self, m):
        self.mock_setUp(m)
        league = League(self.league_id, self.season)

        self.assertEqual(league.nfl_week, 18)
        self.assertEqual(len(league.teams), 8)

    @requests_mock.Mocker()        
    def test_get_scoreboard(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)
        
        with open('tests/football/unit/data/league_matchupScore_2015.json') as f:
            data = json.loads(f.read())
        m.get(self.espn_endpoint + '&view=mMatchupScore', status_code=200, json=data)

        scoreboard = league.scoreboard(1)
        self.assertEqual(repr(scoreboard[1]), 'Matchup(Team(Go Deep Jack ), Team(Last Place))')
        self.assertEqual(scoreboard[0].home_score, 133)

        scoreboard = league.scoreboard()
        self.assertEqual(repr(scoreboard[-1]), 'Matchup(Team(Go Deep Jack ), Team(Last Place))')
        self.assertEqual(scoreboard[-1].away_score, 123)
    
    @requests_mock.Mocker()
    def test_draft(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        first_pick = league.draft[0]
        third_pick = league.draft[2]
        self.assertEqual(repr(first_pick), 'Pick(Eddie Lacy, Team(Show Me Your TD\'s))')
        self.assertEqual(third_pick.round_num, 1)
        self.assertEqual(third_pick.round_pick, 3)
    
    @requests_mock.Mocker()
    def test_box_score_fails(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        with self.assertRaises(Exception):
            league.box_scores(1)
    
    @requests_mock.Mocker()
    def test_free_agents_fails(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        with self.assertRaises(Exception):
            league.free_agents()
