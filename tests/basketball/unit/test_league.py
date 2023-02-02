from unittest import mock, TestCase
from espn_api.basketball import League
import requests_mock
import json
import io

class LeagueTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2023
        self.base_endpoint = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + str(self.season)
        self.espn_endpoint = self.base_endpoint + "/segments/0/leagues/" + str(self.league_id)
        self.players_endpoint = self.base_endpoint + '/players?view=players_wl'
        with open('tests/basketball/unit/data/league_2023_data.json') as data:
            self.league_data = json.loads(data.read())
        with open('tests/basketball/unit/data/league_2023_draft.json') as data:
            self.draft_data = json.loads(data.read())
        with open('tests/basketball/unit/data/league_players_2023.json') as data:
            self.players_data = json.loads(data.read())
        with open('tests/basketball/unit/data/league_2023_playerCard.json') as data:
            self.player_card_data = json.loads(data.read())
        with open('tests/basketball/unit/data/league_2023_pro_schedule.json') as data:
            self.pro_schedule = json.loads(data.read())
    
    def mock_setUp(self, m):
        m.get(self.espn_endpoint + '?view=mTeam&view=mRoster&view=mMatchup&view=mSettings', status_code=200, json=self.league_data)
        m.get(self.espn_endpoint + '?view=mDraftDetail', status_code=200, json=self.draft_data)
        m.get(self.players_endpoint, status_code=200, json=self.players_data)
        m.get(self.base_endpoint + '?view=proTeamSchedules_wl', status_code=200, json=self.pro_schedule)

    @requests_mock.Mocker()        
    def test_create_object(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)
        self.assertEqual(repr(league), 'League(123, 2023)')
        self.assertEqual(repr(league.settings), 'Settings(Orlando Beginner H2H Points League)')
        self.assertEqual(league.settings.scoring_type, 'H2H_POINTS')
        self.assertEqual(league.current_week, 108)
        self.assertEqual(len(league.teams), 10)
    
    @requests_mock.Mocker()
    def test_draft(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        first_pick = league.draft[0]
        third_pick = league.draft[2]
        self.assertEqual(repr(first_pick), 'Pick(R:1 P:1, Nikola Jokic, Team(Team P))')
        self.assertEqual(third_pick.round_num, 1)
        self.assertEqual(third_pick.round_pick, 3)
        self.assertEqual(third_pick.auction_repr(), 'J G, 4065648, Jayson Tatum, 0, False')

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
    def test_player_info(self, m):
        self.mock_setUp(m)
        m.get(self.espn_endpoint + '?view=kona_playercard', status_code=200, json=self.player_card_data)

        league = League(self.league_id, self.season)
        # Invalid name
        player = league.player_info('Test 1')
        self.assertEqual(player, None)

        player = league.player_info('Jalen Brunson')
        self.assertEqual(player.name, 'Jalen Brunson')
        print(player.stats)
        self.assertEqual(player.stats['107']['total']['PTS'], 37.0)
        self.assertEqual(player.total_points, 1929.0)
        self.assertEqual(player.avg_points, 39.37)
        


