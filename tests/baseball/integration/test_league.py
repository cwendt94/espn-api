from unittest import TestCase
from espn_api.baseball import League

# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(81134470, 2021)

        self.assertEqual(len(league.teams), 8)

   #  def test_league_scoreboard(self):
   #      league = League(81134470, 2021)
   #      scores = league.scoreboard()

   #      self.assertEqual(scores[0].home_final_score, 4240.0)
   #      self.assertEqual(scores[0].away_final_score, 2965.0)
    
    def test_league_free_agents(self):
        league = League(81134470, 2021)
        free_agents = league.free_agents()

        self.assertNotEqual(len(free_agents), 0)