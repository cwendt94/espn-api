from unittest import TestCase
from ff_espn_api import League

# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(1234, 2018)

        self.assertEqual(league.current_week, 15)

    def test_past_league(self):
        league = League(12345, 2017)

        self.assertEqual(league.nfl_week, 18)
    
    def test_private_league(self):
        with self.assertRaises(Exception):
            League(368876, 2018)

    def test_unknown_league(self):
        with self.assertRaises(Exception):
            League(2, 2018)
    
    def test_box_scores(self):
        league = League(1234, 2018)
        
        box_scores = league.box_scores(5)

        self.assertEqual(repr(box_scores[1].away_team), 'Team(Team 5)')
        self.assertEqual(repr(box_scores[1].away_lineup[1]), 'Player(Keenan Allen, points:9, projected:10)')