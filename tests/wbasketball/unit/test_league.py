from unittest import TestCase, mock

from espn_api.wbasketball.league import League


class LeagueTest(TestCase):
    def _make_league(self, year=2023):
        with mock.patch(
            "espn_api.wbasketball.league.BaseLeague.__init__", return_value=None
        ):
            league = League(411647, year, fetch_league=False)
        league.year = year
        return league

    def test_league_initialization_uses_wnba(self):
        with mock.patch(
            "espn_api.wbasketball.league.BaseLeague.__init__", return_value=None
        ) as base_init:
            League(
                411647, 2023, espn_s2="s2", swid="swid", fetch_league=False, debug=True
            )

        call_kwargs = base_init.call_args.kwargs
        self.assertEqual(call_kwargs["sport"], "wnba")
        self.assertEqual(call_kwargs["league_id"], 411647)
        self.assertTrue(call_kwargs["debug"])

    def test_map_matchup_ids_merges_and_sorts_periods(self):
        league = self._make_league()

        league._map_matchup_ids(
            [
                {
                    "matchupPeriodId": 1,
                    "home": {"pointsByScoringPeriod": {"2": 95, "1": 100}},
                },
                {
                    "matchupPeriodId": 1,
                    "home": {"pointsByScoringPeriod": {"3": 92, "2": 98}},
                },
                {"matchupPeriodId": 2, "home": {"pointsByScoringPeriod": {}}},
            ]
        )

        self.assertEqual(league.matchup_ids, {1: ["1", "2", "3"]})

    def test_fetch_league_calls_nested_fetch_steps(self):
        league = self._make_league()
        league._fetch_league = mock.Mock(return_value={"schedule": []})
        league._fetch_teams = mock.Mock()

        with mock.patch("espn_api.wbasketball.league.BaseLeague._fetch_draft") as draft:
            league.fetch_league()

        league._fetch_league.assert_called_once_with()
        league._fetch_teams.assert_called_once_with({"schedule": []})
        draft.assert_called_once_with()

    def test_fetch_league_internal_steps(self):
        league = self._make_league()
        league._fetch_players = mock.Mock()
        league._map_matchup_ids = mock.Mock()
        data = {"schedule": [{"matchupPeriodId": 2}]}

        with mock.patch(
            "espn_api.wbasketball.league.BaseLeague._fetch_league",
            return_value=data,
        ):
            result = league._fetch_league()

        self.assertEqual(result, data)
        league._fetch_players.assert_called_once_with()
        league._map_matchup_ids.assert_called_once_with(data["schedule"])

    def test_fetch_teams_replaces_opponent_ids_with_team_instances(self):
        league = self._make_league()
        league.settings = mock.Mock(division_map={10: "West"})
        home = mock.Mock(team_id=1, division_id=10)
        away = mock.Mock(team_id=2, division_id=10)
        home.schedule = [mock.Mock(away_team=2, home_team=2)]
        away.schedule = [mock.Mock(away_team=1, home_team=1)]
        league.teams = [home, away]

        with mock.patch(
            "espn_api.wbasketball.league.BaseLeague._fetch_teams",
            autospec=True,
        ) as fetch_teams:
            fetch_teams.side_effect = lambda self, data, TeamClass: setattr(
                self, "teams", [home, away]
            )
            league._fetch_teams({"teams": []})

        self.assertEqual(home.division_name, "West")
        self.assertIs(home.schedule[0].away_team, away)
        self.assertIs(home.schedule[0].home_team, away)
        self.assertIs(away.schedule[0].away_team, home)
        self.assertIs(away.schedule[0].home_team, home)

    def test_standings_use_final_standing_or_standing(self):
        league = self._make_league()
        first = mock.Mock(final_standing=0, standing=2)
        second = mock.Mock(final_standing=1, standing=1)
        league.teams = [first, second]

        self.assertEqual(league.standings(), [second, first])

    def test_scoreboard_uses_current_matchup_period_and_resolves_teams(self):
        league = self._make_league()
        home = mock.Mock(team_id=1)
        away = mock.Mock(team_id=2)
        league.teams = [home, away]
        league.currentMatchupPeriod = 3
        league.espn_request = mock.Mock()
        league.espn_request.league_get.return_value = {
            "schedule": [
                {
                    "matchupPeriodId": 3,
                    "winner": "HOME",
                    "home": {"teamId": 1, "totalPoints": 100},
                    "away": {"teamId": 2, "totalPoints": 90},
                },
                {
                    "matchupPeriodId": 4,
                    "winner": "AWAY",
                    "home": {"teamId": 1, "totalPoints": 80},
                    "away": {"teamId": 2, "totalPoints": 85},
                },
            ]
        }

        result = league.scoreboard()

        self.assertEqual(len(result), 1)
        self.assertIs(result[0].home_team, home)
        self.assertIs(result[0].away_team, away)
        league.espn_request.league_get.assert_called_once_with(
            params={"view": "mMatchup"}
        )

    def test_recent_activity_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use recent activity before 2019"):
            league.recent_activity()

    def test_recent_activity_uses_msg_type_filter_and_activity_class(self):
        league = self._make_league(year=2023)
        league.player_map = {}
        league.get_team_data = mock.Mock()
        league.espn_request = mock.Mock()
        league.espn_request.league_get.return_value = {"topics": [{"date": "today"}]}

        with mock.patch("espn_api.wbasketball.league.Activity") as activity_cls:
            result = league.recent_activity(size=5, msg_type="FA", offset=2)

        self.assertEqual(result, [activity_cls.return_value])
        call = league.espn_request.league_get.call_args
        self.assertEqual(call.kwargs["params"], {"view": "kona_league_communication"})
        self.assertEqual(call.kwargs["extend"], "/communication/")
        self.assertIn('"limit": 5', call.kwargs["headers"]["x-fantasy-filter"])
        self.assertIn('"offset": 2', call.kwargs["headers"]["x-fantasy-filter"])
        self.assertIn("178", call.kwargs["headers"]["x-fantasy-filter"])
        activity_cls.assert_called_once_with(
            {"date": "today"}, {}, league.get_team_data
        )

    def test_free_agents_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use free agents before 2019"):
            league.free_agents()

    def test_free_agents_applies_position_and_position_id_filters(self):
        league = self._make_league(year=2023)
        league.current_week = 7
        league.espn_request = mock.Mock()
        league.espn_request.league_get.return_value = {"players": [{"id": 1}]}

        with mock.patch("espn_api.wbasketball.league.Player") as player_cls:
            result = league.free_agents(week=4, size=10, position="G", position_id=4)

        self.assertEqual(result, [player_cls.return_value])
        call = league.espn_request.league_get.call_args
        self.assertEqual(
            call.kwargs["params"], {"view": "kona_player_info", "scoringPeriodId": 4}
        )
        self.assertIn(
            '"filterSlotIds": {"value": [1, 4]}',
            call.kwargs["headers"]["x-fantasy-filter"],
        )
        player_cls.assert_called_once_with({"id": 1}, league.year)

    def test_box_scores_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use box score before 2019"):
            league.box_scores()

    def test_box_scores_uses_matchup_period_history_and_resolves_teams(self):
        league = self._make_league(year=2023)
        league.year = 2023
        league.currentMatchupPeriod = 5
        league.current_week = 8
        league.matchup_ids = {3: ["5", "6"]}
        home = mock.Mock(team_id=1)
        away = mock.Mock(team_id=2)
        league.teams = [home, away]
        league.espn_request = mock.Mock()
        league.espn_request.league_get.return_value = {
            "schedule": [{"home": {"teamId": 1}, "away": {"teamId": 2}}]
        }

        with mock.patch.object(
            league, "_get_pro_schedule", return_value={}
        ), mock.patch("espn_api.wbasketball.league.BoxScore") as box_score_cls:
            box_score = mock.Mock(home_team=1, away_team=2)
            box_score_cls.return_value = box_score
            result = league.box_scores(matchup_period=3)

        self.assertEqual(result, [box_score])
        self.assertIs(box_score.home_team, home)
        self.assertIs(box_score.away_team, away)
        call = league.espn_request.league_get.call_args
        self.assertEqual(call.kwargs["params"]["scoringPeriodId"], "6")
        self.assertIn('"value": [3]', call.kwargs["headers"]["x-fantasy-filter"])
