from unittest import TestCase
from espn_api.basketball import League

# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(411647, 2019)

        self.assertEqual(league.scoringPeriodId, 178)

    def test_league_scoreboard(self):
        league = League(411647, 2019)
        scores = league.scoreboard()

        self.assertEqual(scores[0].home_final_score, 4240.0)
        self.assertEqual(scores[0].away_final_score, 2965.0)

    def test_past_league(self):
        league = League(411647, 2017)
        
        self.assertEqual(league.scoringPeriodId, 170)

    def test_past_league_scoreboard(self):
        league = League(411647, 2017)
        scores = league.scoreboard()

        self.assertTrue(scores[0].home_final_score > 0)
        self.assertTrue(scores[0].away_final_score > 0)
