from unittest import TestCase
from espn_api.baseball import League

# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):
    def setUp(self):
        self.league = League(81134470, 2021)
        self.blank_league = League(81134470, 2021, fetch_league=False)
    
    def test_league_init(self):
        self.assertEqual(len(self.league.teams), 8)

   #  def test_league_scoreboard(self):
   #      league = League(81134470, 2021)
   #      scores = league.scoreboard()

   #      self.assertEqual(scores[0].home_final_score, 4240.0)
   #      self.assertEqual(scores[0].away_final_score, 2965.0)
    
    def test_league_free_agents(self):
        free_agents = self.league.free_agents()

        self.assertNotEqual(len(free_agents), 0)
    
    def test_league_box_scores(self):
        box_scores = self.league.box_scores(1)

        self.assertNotEqual(len(box_scores), 0)

    def test_blank_league_init(self):
        self.assertEqual(len(self.blank_league.teams), 0)