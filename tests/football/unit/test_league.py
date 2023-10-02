from unittest import mock, TestCase
from espn_api.football import League, BoxPlayer
import requests_mock
import json
import io

class LeagueTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2018
        self.espn_endpoint = "https://fantasy.espn.com/apis/v3/games/FFL/seasons/" + str(self.season) + "/segments/0/leagues/" + str(self.league_id)
        self.players_endpoint = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + str(self.season) + '/players?view=players_wl'
        with open('tests/football/unit/data/league_2018_data.json') as data:
            self.league_data = json.loads(data.read())
        with open('tests/football/unit/data/league_draft_2018.json') as data:
            self.draft_data = json.loads(data.read())
        with open('tests/football/unit/data/league_players_2018.json') as data:
            self.players_data = json.loads(data.read())
        with open('tests/football/unit/data/league_2019_playerCard.json') as data:
            self.player_card_data = json.loads(data.read())
    
    def mock_setUp(self, m):
        m.get(self.espn_endpoint + '?view=mTeam&view=mRoster&view=mMatchup&view=mSettings', status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mDraftDetail', status_code=200, json=self.draft_data)
        m.get(self.players_endpoint, status_code=200, json=self.players_data)

    @requests_mock.Mocker()        
    def test_error_status(self, m):
        m.get(self.espn_endpoint, status_code=501, json=self.league_data)
        with self.assertRaises(Exception):
            League(self.league_id, self.season)
    
    @requests_mock.Mocker()        
    def test_unknown_error_status(self, m):
        m.get(self.espn_endpoint, status_code=300, json=self.league_data)
        with self.assertRaises(Exception):
            League(self.league_id, self.season)

    @requests_mock.Mocker()        
    def test_create_object(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)
        self.assertEqual(repr(league), 'League(123, 2018)')
        self.assertEqual(repr(league.settings), 'Settings(FXBG League)')
        self.assertEqual(league.settings.scoring_format[0]['abbr'], 'BLKKRTD')
        self.assertEqual(league.current_week, 16)
        self.assertEqual(len(league.teams), 10)

        league.refresh()
        self.assertEqual(repr(league), 'League(123, 2018)')
        self.assertEqual(repr(league.settings), 'Settings(FXBG League)')
        self.assertEqual(league.current_week, 16)
        self.assertEqual(len(league.teams), 10)

    @requests_mock.Mocker()        
    def test_load_roster_week(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)
        
        with open('tests/football/unit/data/league_roster_week1.json') as f:
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
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        standings = league.standings()
        self.assertEqual(standings[0].final_standing, 1)

    @requests_mock.Mocker()        
    def test_top_scorer(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.top_scorer()
        self.assertEqual(team.team_id, 1)
    
    @requests_mock.Mocker()        
    def test_least_scorer(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.least_scorer()
        self.assertEqual(team.team_id, 10)

    @requests_mock.Mocker()        
    def test_most_pa(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.most_points_against()
        self.assertEqual(team.team_id, 2)

    @requests_mock.Mocker()        
    def test_top_scored(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.top_scored_week()
        self.assertEqual(team[0].team_id, 5)     

    @requests_mock.Mocker()
    def test_least_scored(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.least_scored_week()
        self.assertEqual(team[0].team_id, 10)
    
    @requests_mock.Mocker()
    def test_get_team(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.get_team_data(8)
        self.assertEqual(team.team_id, 8) 

        team = league.get_team_data(18)
        self.assertEqual(team, None)
    
    @requests_mock.Mocker()        
    def test_get_scoreboard(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)
        
        with open('tests/football/unit/data/league_matchupScore_2018.json') as f:
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
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        team = league.teams[2]
        self.assertEqual(repr(team.roster[0]), 'Player(Drew Brees)')
        self.assertEqual(team.get_player_name(2521161), 'Zach Zenner')
        self.assertEqual(team.get_player_name(0), '')
    
    @requests_mock.Mocker()
    def test_draft(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        first_pick = league.draft[0]
        third_pick = league.draft[2]
        self.assertEqual(repr(first_pick), 'Pick(Le\'Veon Bell, Team(Rollin\' With Mahomies))')
        self.assertEqual(third_pick.round_num, 1)
        self.assertEqual(third_pick.round_pick, 3)
        self.assertEqual(third_pick.auction_repr(), 'Team(Goin\' HAM Newton), 13934, Antonio Brown, 0, False')

    # TODO need to get data for most recent season
    # @requests_mock.Mocker()        
    # def test_box_score(self, m):
    #     self.mock_setUp(m)

    #     league = League(self.league_id, self.season)
        
    #     with open('tests/unit/data/league_boxscore_2018.json') as f:
    #         data = json.loads(f.read())
    #     m.get(self.espn_endpoint + '?view=mMatchup&view=mMatchupScore&scoringPeriodId=13', status_code=200, json=data)
    #     box_scores = league.box_scores(13)

    #     self.assertEqual(repr(box_scores[0].home_team), 'Team(Rollin\' With Mahomies)')
    #     self.assertEqual(repr(box_scores[0].home_lineup[1]), 'Player(Christian McCaffrey, points:31, projected:23)')
    
    @requests_mock.Mocker()
    def test_power_rankings(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        invalid_week = league.power_rankings(0)
        current_week = league.power_rankings(league.current_week)
        self.assertEqual(invalid_week, current_week)

        empty_week = league.power_rankings()
        self.assertEqual(empty_week, current_week)

        valid_week = league.power_rankings(13)
        self.assertEqual(valid_week[0][0], '71.15')
        self.assertEqual(repr(valid_week[0][1]), 'Team(Perscription Mixon)')

    @requests_mock.Mocker()
    @mock.patch.object(League, '_get_pro_schedule')   
    @mock.patch.object(League, '_get_positional_ratings')
    @mock.patch.object(BoxPlayer, '__init__') 
    def test_free_agents(self, m, mock_boxplayer, mock_nfl_schedule, mock_pos_ratings):
        self.mock_setUp(m)
        mock_boxplayer.return_value = None
        league = League(self.league_id, self.season)
        m.get(self.espn_endpoint + '?view=kona_player_info&scoringPeriodId=16', status_code=200, json={'players': [1, 2]})
        league.year = 2019
        free_agents = league.free_agents(position='QB', position_id=0)

        self.assertEqual(len(free_agents), 2)

    @requests_mock.Mocker()        
    def test_recent_activity(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, 2018)
        
        # TODO hack until I get all mock data for 2019
        league.year = 2019 
        self.espn_endpoint = "https://fantasy.espn.com/apis/v3/games/ffl/seasons/" + str(2019) + "/segments/0/leagues/" + str(self.league_id)
        league.espn_request.LEAGUE_ENDPOINT = self.espn_endpoint

        with open('tests/football/unit/data/league_recent_activity_2019.json') as f:
            data = json.loads(f.read())
        m.get(self.espn_endpoint + '/communication/?view=kona_league_communication', status_code=200, json=data)
        m.get(self.espn_endpoint + '?view=kona_playercard', status_code=200, json=self.player_card_data)

        activity  = league.recent_activity()
        self.assertEqual(repr(activity[0].actions[0][0]), 'Team(Perscription Mixon)')
        self.assertEqual(len(repr(activity)), 2765)

    @mock.patch.object(League, '_fetch_league')
    def test_cookie_set(self, mock_fetch_league):
        league = League(league_id=1234, year=2019, espn_s2='cookie1', swid='cookie2')
        self.assertEqual(league.espn_request.cookies['espn_s2'], 'cookie1')
        self.assertEqual(league.espn_request.cookies['SWID'], 'cookie2')
    
    @requests_mock.Mocker()
    def test_player_info(self, m):
        self.mock_setUp(m)
        m.get(self.espn_endpoint + '?view=kona_playercard', status_code=200, json=self.player_card_data)

        league = League(self.league_id, self.season)
        league.year = 2019
        # Invalid name
        player = league.player_info('Test 1')
        self.assertEqual(player, None)

        player = league.player_info('James Conner')
        self.assertEqual(player.name, 'James Conner')
        self.assertEqual(player.stats[1]['points'], 10.5)
        self.assertEqual(player.percent_owned, 96.73)
        self.assertEqual(player.percent_started, 73.87)
        


