import json
from unittest import TestCase, mock

from espn_api.base_league import BaseLeague
from espn_api.hockey import League as HockeyLeague, Team
from espn_api.requests.espn_requests import EspnFantasyRequests


class BaseLeagueTest(TestCase):
    def setUp(self) -> None:
        self.league_id = 1
        self.season = 2020
        self.league = BaseLeague(self.league_id, self.season, sport= 'nhl')

        with open('tests/hockey/unit/data/league_data.json') as data:
                self.league_data = json.loads(data.read())


    def test_base_league(self):
        self.assertEqual(self.league.league_id, 1)
        self.assertEqual(self.league.year, self.season)
        self.assertEqual(self.league.teams, [])
        self.assertEqual(self.league.draft, [])
        self.assertEqual(self.league.player_map, {})

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_base_league_fetch_league(self, mock_get_league_request):
        mock_get_league_request.return_value = self.league_data

        self.league._fetch_league()
        mock_get_league_request.assert_called_once()

        self.assertIsNotNone(self.league.currentMatchupPeriod)

    @mock.patch.object(EspnFantasyRequests, 'get_pro_players')
    def test_base_league_fetch_players(self, mock_get_players):
        with open('tests/hockey/unit/data/player_data.json') as data:
            player_data = json.loads(data.read())
        mock_get_players.return_value = player_data

        self.league._fetch_players()

        self.assertEqual(self.league.player_map['Charlie  Coyle'], 2555315)
        self.assertEqual(self.league.player_map[2555315], 'Charlie  Coyle')
        mock_get_players.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'get_pro_schedule')
    def test_base_league_fetch_schedule(self, mock_get_pro_schedule):
        with open('tests/hockey/unit/data/pro_schedule.json') as data:
            schedule_data = json.loads(data.read())
        mock_get_pro_schedule.return_value = schedule_data

        schedule = self.league._get_pro_schedule(scoringPeriodId=35)

        self.assertEqual(schedule[11], (13, 1613520000000))
        mock_get_pro_schedule.assert_called_once()

    def test_base_league_standings(self):
        expected_standings = ["Team(Barkko Ruutu)",
                              "Team(2 Minutes for.. Rooping?)",
                              "Team(Tyutin in  the Staal)",
                              "Team(Turds of  Misery)",
                              "Team(Fast and Fleuryious)",
                              "Team(The Return of the Captain)",
                              "Team(Eichel Scott Paper Company )",
                              "Team(Took a Dump and Chased)",
                              "Team(Lafleur Power   -)",
                              "Team(Drop Trou and Shattenkirk)"]
        self.league._fetch_teams(self.league_data, TeamClass= Team)
        actual_standings = self.league.standings()

        for i, actual_team in enumerate(actual_standings):
            self.assertEqual(repr(actual_team), expected_standings[i])



class HockeyLeagueTest(BaseLeagueTest):

    def setUp(self):
        super().setUp()

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league(self, mock_league_request):
        mock_league_request.return_value = self.league_data

        league = HockeyLeague(self.league_id, self.season)
        self.assertEqual(league.scoringPeriodId, 265)
        self.assertEqual(league.currentMatchupPeriod, 13)
        self.assertEqual(league.current_week, 264)
        self.assertEqual(league.year, self.season)
        mock_league_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_teams(self, mock_league_request):
        mock_league_request.return_value = self.league_data
        expected_teams = set(["Team(Barkko Ruutu)",
                              "Team(2 Minutes for.. Rooping?)",
                              "Team(Tyutin in  the Staal)",
                              "Team(Turds of  Misery)",
                              "Team(Fast and Fleuryious)",
                              "Team(The Return of the Captain)",
                              "Team(Eichel Scott Paper Company )",
                              "Team(Took a Dump and Chased)",
                              "Team(Lafleur Power   -)",
                              "Team(Drop Trou and Shattenkirk)"])
        league = HockeyLeague(self.league_id, self.season)

        actual_teams = set(league.teams)

        for actual_team in actual_teams:
            self.assertIn(repr(actual_team), expected_teams)
        mock_league_request.assert_called_once()\

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_scoreboard(self, mock_get_league_request, mock_league_get_request):
        with open('tests/hockey/unit/data/matchup_data.json') as file:
            matchup_data = json.loads(file.read())
        mock_get_league_request.return_value = self.league_data
        mock_league_get_request.return_value = matchup_data
        league = HockeyLeague(self.league_id, self.season)

        first_expected_matchup = 'Matchup(Team(Drop Trou and Shattenkirk) 9.0 - 1.0 Team(Eichel Scott Paper Company ))'

        actual_matchups = league.scoreboard()

        self.assertEqual(first_expected_matchup, repr(actual_matchups[0]))

        mock_get_league_request.assert_called_once()
        mock_league_get_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_get_team_data(self, mock_get_league_request):
        mock_get_league_request.return_value = self.league_data
        league = HockeyLeague(self.league_id, self.season)

        expected_team = 'Team(The Return of the Captain)'
        actual_team = league.get_team_data(9)

        self.assertEqual(expected_team, repr(actual_team))

        mock_get_league_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_free_agency(self, mock_get_league_request, mock_league_get_request):
        with open('tests/hockey/unit/data/free_agent_data.json') as file:
            free_agents_data = json.loads(file.read())
        mock_get_league_request.return_value = self.league_data
        mock_league_get_request.return_value = free_agents_data
        league = HockeyLeague(self.league_id, self.season)

        first_expected_free_agent = 'Player(Brendan  Gallagher)'

        actual_free_agents = league.free_agents()

        self.assertEqual(first_expected_free_agent, repr(actual_free_agents[0]))

        mock_get_league_request.assert_called_once()
        mock_league_get_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_recent_activity(self, mock_get_league_request, mock_league_get_request):
        with open('tests/hockey/unit/data/recent_activity_data.json') as file:
            activity_data = json.loads(file.read())
        mock_get_league_request.return_value = self.league_data
        mock_league_get_request.return_value = activity_data
        league = HockeyLeague(self.league_id, self.season)

        first_expected_activity = 'Activity((Team(2 Minutes for.. Rooping?),FA ADDED,Jake DeBrusk))'

        actual_activities = league.recent_activity()

        self.assertEqual(first_expected_activity, repr(actual_activities[0]))

        mock_get_league_request.assert_called_once()
        mock_league_get_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league_box_scores(self, mock_get_league_request, mock_league_get_request):
        with open('tests/hockey/unit/data/box_score_data.json') as file:
            box_score_data = json.loads(file.read())
        mock_get_league_request.return_value = self.league_data
        mock_league_get_request.return_value = box_score_data
        league = HockeyLeague(self.league_id, self.season)

        first_box_score = 'Box Score(12 at Team(2 Minutes for.. Rooping?))'

        actual_box_scores = league.box_scores()

        self.assertEqual(len(actual_box_scores), 6)
        self.assertEqual(first_box_score, repr(actual_box_scores[0]))

        mock_get_league_request.assert_called_once()
        mock_league_get_request.assert_called_once()
