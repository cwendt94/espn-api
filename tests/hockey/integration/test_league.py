from unittest import TestCase
from espn_api.hockey import League


# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):

    def test_league_init(self):
        league = League(77421173, 2021)

        self.assertEqual(league.start_date.year, 2021)
        self.assertEqual(league.start_date.month, 1)
        self.assertEqual(league.start_date.day, 13)

