from unittest import TestCase
from espn_api.hockey import League


# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):
    def test_league_init(self):
        league = League(77421173, 2021)

        self.assertEqual(league.start_date.year, 2021)
        self.assertEqual(league.start_date.month, 1)
        self.assertEqual(league.start_date.day, 13)

    def test_blank_league_init(self):
        blank_league = League(77421173, 2021, fetch_league=False)
        self.assertEqual(len(blank_league.teams), 0)
