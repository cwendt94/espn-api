from unittest import mock, TestCase
from espn_api.football import League, BoxPlayer
from espn_api.requests.constant import FANTASY_BASE_ENDPOINT
from espn_api.football.helper import (
    build_division_record_dict,
    build_h2h_dict,
    sort_by_coin_flip,
    sort_by_division_record,
    sort_by_head_to_head,
    sort_by_points_against,
    sort_by_points_for,
    sort_by_win_pct,
)
import requests_mock
import json
import io


class LeagueTest(TestCase):
    def setUp(self):
        self.league_id = 123
        self.season = 2018
        self.espn_endpoint = FANTASY_BASE_ENDPOINT + 'FFL/seasons/' + str(self.season) + '/segments/0/leagues/' + str(self.league_id)
        self.players_endpoint = FANTASY_BASE_ENDPOINT + 'ffl/seasons/' + str(self.season) + '/players?view=players_wl'
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
        m.get(self.espn_endpoint + '?view=proTeamSchedules_wl', status_code=200, json={})

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
    def test_standings_weekly(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        # Test various weeks
        week1_standings = [team.team_id for team in league.standings_weekly(1)]
        self.assertEqual(week1_standings, [3, 11, 2, 10, 7, 8, 4, 5, 9, 1])

        week4_standings = [team.team_id for team in league.standings_weekly(4)]
        self.assertEqual(week4_standings, [2, 7, 11, 4, 3, 9, 1, 8, 5, 10])

        # # Does not work with the playoffs
        # week13_standings = [team.team_id for team in league.standings_weekly(13)]
        # final_standings = [team.team_id for team in league.standings()]
        # self.assertEqual(week13_standings, final_standings)

        # Test invalid playoff seeding rule
        with self.assertRaises(Exception):
            league.settings.playoff_seed_tie_rule = "NOT_A_REAL_RULE"
            league.standings(week=1)

    def get_list_of_team_data(self, league: League, week: int):
        list_of_team_data = []
        for team in league.teams:
            team_data = {
                "team": team,
                "team_id": team.team_id,
                "division_id": team.division_id,
                "wins": sum([1 for outcome in team.outcomes[:week] if outcome == "W"]),
                "ties": sum([1 for outcome in team.outcomes[:week] if outcome == "T"]),
                "losses": sum(
                    [1 for outcome in team.outcomes[:week] if outcome == "L"]
                ),
                "points_for": sum(team.scores[:week]),
                "points_against": sum(
                    [team.schedule[w].scores[w] for w in range(week)]
                ),
                "schedule": team.schedule[:week],
                "outcomes": team.outcomes[:week],
            }
            team_data["win_pct"] = (team_data["wins"] + team_data["ties"] / 2) / sum(
                [1 for outcome in team.outcomes[:week] if outcome in ["W", "T", "L"]]
            )
            list_of_team_data.append(team_data)
        return list_of_team_data

    @requests_mock.Mocker()
    def test_build_h2h_dict(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        # Test build_h2h_dict and build_division_record_dict
        # Week 1
        ## Get data for teams 1 and 7
        week1_teams_data = self.get_list_of_team_data(league, 1)
        list_of_team_data = [
            team for team in week1_teams_data if team["team_id"] in (1, 7)
        ]
        h2h_dict = build_h2h_dict(list_of_team_data)

        self.assertEqual(h2h_dict[1][7]["h2h_wins"], 0)  # Team 1 is 0/1 vs Team 7
        self.assertEqual(h2h_dict[7][1]["h2h_wins"], 1)  # Team 7 is 1/1 vs Team 1
        self.assertEqual(h2h_dict[1][7]["h2h_games"], 1)  # Team 1 is 0/1 vs Team 7
        self.assertEqual(h2h_dict[7][1]["h2h_games"], 1)  # Team 7 is 1/1 vs Team 1

        ## Test 3 teams head-to-head
        list_of_team_data = [
            team for team in week1_teams_data if team["team_id"] in (1, 2, 3)
        ]
        h2h_dict = build_h2h_dict(list_of_team_data)
        self.assertEqual(h2h_dict[1][2]["h2h_games"], 0)  # Teams have not played
        self.assertEqual(h2h_dict[1][3]["h2h_games"], 0)  # Teams have not played
        self.assertEqual(h2h_dict[2][3]["h2h_games"], 0)  # Teams have not played

        # Week 10
        ## Get data for teams 1 and 7
        week10_teams_data = self.get_list_of_team_data(league, 10)
        list_of_team_data = [
            team for team in week10_teams_data if team["team_id"] in (1, 7)
        ]
        h2h_dict = build_h2h_dict(list_of_team_data)

        self.assertEqual(h2h_dict[1][7]["h2h_wins"], 1)  # Team 1 is 1/2 vs Team 7
        self.assertEqual(h2h_dict[7][1]["h2h_wins"], 1)  # Team 7 is 1/2 vs Team 1
        self.assertEqual(h2h_dict[1][7]["h2h_games"], 2)  # Team 1 is 0/1 vs Team 7
        self.assertEqual(h2h_dict[7][1]["h2h_games"], 2)  # Team 7 is 1/1 vs Team 1

        # Test 3 teams head-to-head
        list_of_team_data = [
            team for team in week10_teams_data if team["team_id"] in (1, 2, 3)
        ]
        h2h_dict = build_h2h_dict(list_of_team_data)
        self.assertEqual(h2h_dict[1][2]["h2h_games"], 1)  # Teams have played 1x
        self.assertEqual(h2h_dict[1][3]["h2h_games"], 1)  # Teams have played 1x
        self.assertEqual(h2h_dict[2][3]["h2h_games"], 1)  # Teams have played 1x

    @requests_mock.Mocker()
    def test_build_division_records_dict(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        # Test build_h2h_dict and build_division_record_dict
        # Week 1 - get data for teams 1 and 7
        week1_teams_data = self.get_list_of_team_data(league, 1)
        list_of_team_data = [
            team for team in week1_teams_data if team["team_id"] in (1, 7)
        ]
        division_record_dict = build_division_record_dict(list_of_team_data)

        self.assertEqual(division_record_dict[1], 0)
        self.assertEqual(
            division_record_dict[7],
            [
                team_data["win_pct"]
                for team_data in list_of_team_data
                if team_data["team_id"] == 7
            ][0],
        )

        # Week 10 - get data for teams 1 and 7
        week10_teams_data = self.get_list_of_team_data(league, 10)
        list_of_team_data = [
            team for team in week10_teams_data if team["team_id"] in (1, 7)
        ]
        division_record_dict = build_division_record_dict(week10_teams_data)

        self.assertEqual(division_record_dict[1], 0.6)
        self.assertEqual(
            division_record_dict[7],
            [
                team_data["win_pct"]
                for team_data in list_of_team_data
                if team_data["team_id"] == 7
            ][0],
        )

    @requests_mock.Mocker()
    def test_sort_functions(self, m):
        self.mock_setUp(m)

        league = League(self.league_id, self.season)

        week1_teams_data = self.get_list_of_team_data(league, 1)
        week10_teams_data = self.get_list_of_team_data(league, 10)
        division_record_dict = build_division_record_dict(week10_teams_data)

        # Assert that sort_by_win_pct is correct
        sorted_list_of_team_data = sort_by_win_pct(week10_teams_data)
        for i in range(len(sorted_list_of_team_data) - 1):
            self.assertGreaterEqual(
                sorted_list_of_team_data[i]["win_pct"],
                sorted_list_of_team_data[i + 1]["win_pct"],
            )

        # Assert that sort_by_points_for is correct
        sorted_list_of_team_data = sort_by_points_for(week10_teams_data)
        for i in range(len(sorted_list_of_team_data) - 1):
            self.assertGreaterEqual(
                sorted_list_of_team_data[i]["points_for"],
                sorted_list_of_team_data[i + 1]["points_for"],
            )

        # Assert that sort_by_head_to_head is correct - 1 team
        sorted_list_of_team_data = sort_by_head_to_head(week10_teams_data[:1].copy())
        self.assertEqual(sorted_list_of_team_data == week10_teams_data[:1], True)

        # Assert that sort_by_head_to_head is correct - 2 teams
        sorted_list_of_team_data = sort_by_head_to_head(
            [team for team in week10_teams_data if team["team_id"] in (1, 2)]
        )
        self.assertEqual(sorted_list_of_team_data[0]["team_id"], 1)

        # Assert that sort_by_head_to_head is correct - 3 teams, valid
        sorted_list_of_team_data = sort_by_head_to_head(
            [team for team in week10_teams_data if team["team_id"] in (1, 2, 3)]
        )
        self.assertEqual(sorted_list_of_team_data[0]["team_id"], 1)
        self.assertEqual(sorted_list_of_team_data[1]["team_id"], 3)
        self.assertEqual(sorted_list_of_team_data[2]["team_id"], 2)

        # Assert that sort_by_head_to_head is correct - 3 teams, invalid
        sorted_list_of_team_data = sort_by_head_to_head(
            [team for team in week1_teams_data if team["team_id"] in (1, 2, 3)]
        )
        self.assertEqual(sorted_list_of_team_data[0]["h2h_wins"], 0)
        self.assertEqual(sorted_list_of_team_data[1]["h2h_wins"], 0)
        self.assertEqual(sorted_list_of_team_data[2]["h2h_wins"], 0)

        # Assert that sort_by_division_record is correct
        sorted_list_of_team_data = sort_by_division_record(week10_teams_data)
        for i in range(len(sorted_list_of_team_data) - 1):
            self.assertGreaterEqual(
                division_record_dict[sorted_list_of_team_data[i]["team_id"]],
                division_record_dict[sorted_list_of_team_data[i + 1]["team_id"]],
            )

        # Assert that sort_by_points_against is correct
        sorted_list_of_team_data = sort_by_points_against(week10_teams_data)
        for i in range(len(sorted_list_of_team_data) - 1):
            self.assertGreaterEqual(
                sorted_list_of_team_data[i]["points_against"],
                sorted_list_of_team_data[i + 1]["points_against"],
            )

        # Assert that sort_by_coin_flip is not deterministic
        standings_list = []
        for i in range(5):
            sorted_list_of_team_data = sort_by_coin_flip(week10_teams_data)
            standings_list.append(
                (team["team_id"] for team in sorted_list_of_team_data)
            )
        self.assertGreater(len(set(standings_list)), 1)

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
        self.assertEqual(repr(first_pick), 'Pick(R:1 P:1, Le\'Veon Bell, Team(Rollin\' With Mahomies))')
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
        self.espn_endpoint = FANTASY_BASE_ENDPOINT + 'ffl/seasons/' + str(2019) + '/segments/0/leagues/' + str(self.league_id)
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
        


