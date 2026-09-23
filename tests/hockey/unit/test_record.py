from unittest import TestCase, mock

from espn_api.hockey import League, Record


class TestRecord(TestCase):
    def test_record_init_and_standing_string(self):
        record = Record(
            {
                "gamesBack": 1.5,
                "losses": 2,
                "pointsAgainst": 120,
                "pointsFor": 150,
                "ties": 1,
                "wins": 7,
            }
        )

        self.assertEqual(record.games_back, 1.5)
        self.assertEqual(record.losses, 2)
        self.assertEqual(record.points_against, 120)
        self.assertEqual(record.points_for, 150)
        self.assertEqual(record.ties, 1)
        self.assertEqual(record.wins, 7)
        self.assertEqual(record.get_standing_str(), "Wins: 7 \nLosses: 2 \nTies: 1")

    def test_record_add(self):
        left = Record(
            {
                "gamesBack": 1.0,
                "losses": 2,
                "pointsAgainst": 80,
                "pointsFor": 100,
                "ties": 1,
                "wins": 3,
            }
        )
        right = Record(
            {
                "gamesBack": 2.0,
                "losses": 4,
                "pointsAgainst": 50,
                "pointsFor": 60,
                "ties": 2,
                "wins": 5,
            }
        )

        combined = left + right

        self.assertEqual(combined.games_back, 3.0)
        self.assertEqual(combined.losses, 6)
        self.assertEqual(combined.points_against, 130)
        self.assertEqual(combined.points_for, 160)
        self.assertEqual(combined.ties, 3)
        self.assertEqual(combined.wins, 8)

    def test_hockey_league_map_matchup_ids(self):
        with mock.patch("espn_api.hockey.league.BaseLeague.__init__", return_value=None):
            league = League(123, 2024, fetch_league=False)

            schedule = [
                {
                    "matchupPeriodId": 1,
                    "home": {"pointsByScoringPeriod": {"1": 10.0, "2": 12.0}},
                },
                {
                    "matchupPeriodId": 1,
                    "home": {"pointsByScoringPeriod": {"2": 15.0, "3": 20.0}},
                },
                {
                    "matchupPeriodId": 2,
                    "home": {"pointsByScoringPeriod": {}},
                },
            ]

            league._map_matchup_ids(schedule)

            self.assertEqual(league.matchup_ids[1], ["1", "2", "3"])
            self.assertNotIn(2, league.matchup_ids)
