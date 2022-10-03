from unittest import TestCase
from espn_api.hockey import League


# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):

    def test_league_init(self):
        league = League(77421173, 2021)

        self.assertEqual(league.teams[0].__repr__(), 'Team(Cambridge Bay Caribou)')
        self.assertEqual(league.teams[1].roster[0].name, 'Steven Stamkos')

    def test_blank_league_init(self):
        blank_league = League(77421173, 2021, fetch_league=False)
        self.assertEqual(len(blank_league.teams), 0)