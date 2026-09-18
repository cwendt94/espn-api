from unittest import TestCase, mock

from espn_api.wbasketball.league import League


class LeagueTest(TestCase):
    def _make_league(self, year=2023):
        with mock.patch("espn_api.wbasketball.league.BaseLeague.__init__", return_value=None):
            league = League(411647, year, fetch_league=False)
        league.year = year
        return league

    def test_league_initialization_uses_wnba(self):
        with mock.patch(
            "espn_api.wbasketball.league.BaseLeague.__init__", return_value=None
        ) as base_init:
            League(411647, 2023, espn_s2="s2", swid="swid", fetch_league=False, debug=True)

        call_kwargs = base_init.call_args.kwargs
        self.assertEqual(call_kwargs["sport"], "wnba")
        self.assertEqual(call_kwargs["league_id"], 411647)
        self.assertTrue(call_kwargs["debug"])

    def test_map_matchup_ids_merges_and_sorts_periods(self):
        league = self._make_league()

        league._map_matchup_ids(
            [
                {"matchupPeriodId": 1, "home": {"pointsByScoringPeriod": {"2": 95, "1": 100}}},
                {"matchupPeriodId": 1, "home": {"pointsByScoringPeriod": {"3": 92, "2": 98}}},
                {"matchupPeriodId": 2, "home": {"pointsByScoringPeriod": {}}},
            ]
        )

        self.assertEqual(league.matchup_ids, {1: ["1", "2", "3"]})

    def test_standings_use_final_standing_or_standing(self):
        league = self._make_league()
        first = mock.Mock(final_standing=0, standing=2)
        second = mock.Mock(final_standing=1, standing=1)
        league.teams = [first, second]

        self.assertEqual(league.standings(), [second, first])

    def test_recent_activity_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use recent activity before 2019"):
            league.recent_activity()

    def test_free_agents_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use free agents before 2019"):
            league.free_agents()

    def test_box_scores_rejects_old_seasons(self):
        league = self._make_league(year=2018)

        with self.assertRaisesRegex(Exception, "Cant use box score before 2019"):
            league.box_scores()
