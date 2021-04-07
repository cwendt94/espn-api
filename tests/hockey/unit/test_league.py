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
        assert(self.league.league_id == 1)
        assert(self.league.year == self.season)
        assert(self.league.teams == [])
        assert(self.league.draft == [])
        assert(self.league.player_map == {})

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_base_league_fetch_league(self, mock_get_league_request):
        mock_get_league_request.return_value = self.league_data

        self.league._fetch_league()
        mock_get_league_request.assert_called_once()

        assert(self.league.currentMatchupPeriod)

    @mock.patch.object(EspnFantasyRequests, 'get_pro_players')
    def test_base_league_fetch_players(self, mock_get_players):
        with open('tests/hockey/unit/data/player_data.json') as data:
            player_data = json.loads(data.read())
        mock_get_players.return_value = player_data

        self.league._fetch_players()

        assert(self.league.player_map['Charlie  Coyle'] == 2555315)
        assert(self.league.player_map[2555315] == 'Charlie  Coyle')
        mock_get_players.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'get_pro_schedule')
    def test_base_league_fetch_schedule(self, mock_get_pro_schedule):
        with open('tests/hockey/unit/data/pro_schedule.json') as data:
            schedule_data = json.loads(data.read())
        mock_get_pro_schedule.return_value = schedule_data

        schedule = self.league._get_pro_schedule(scoringPeriodId=35)

        assert (schedule[11] == (13, 1613520000000))
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
            assert(repr(actual_team) == expected_standings[i])



class HockeyLeagueTest(BaseLeagueTest):

    def setUp(self):
        super().setUp()

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league(self, mock_league_request):
        mock_league_request.return_value = self.league_data

        league = HockeyLeague(self.league_id, self.season)
        assert(league.scoringPeriodId == 265)
        assert(league.currentMatchupPeriod == 24)
        assert(league.current_week == 264)
        assert(league.year == self.season)
        mock_league_request.assert_called_once()

    @mock.patch.object(EspnFantasyRequests, 'get_league')
    def test_league(self, mock_league_request):
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
            assert(repr(actual_team) in expected_teams)
        mock_league_request.assert_called_once()



