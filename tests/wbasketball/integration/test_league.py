from unittest import TestCase
from espn_api.wbasketball import League

# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):
    
    # def test_league_init(self):
    #     league = League(1010650954, 2022)

    #     self.assertEqual(league.scoringPeriodId, 5)

    # def test_league_scoreboard(self):
    #     league = League(1010650954, 2022)
    #     scores = league.scoreboard()

    #     self.assertEqual(scores[0].home_final_score, 136.3)
    #     self.assertEqual(scores[0].away_final_score, 224.3)
    
    def test_league_free_agents(self):
        league = League(1010650954, 2022)
        free_agents = league.free_agents()

        self.assertNotEqual(len(free_agents), 0)

    # def test_league_box_scores(self):
    #     league = League(1010650954, 2022)
    #     final_matchup = league.box_scores()[0]
    #     middle_matchup = league.box_scores(matchup_period=7)[0]
    #     # same matchup period but single scoring period
    #     scoring_period_matchup = league.box_scores(scoring_period=48, matchup_total=False)[0]

    #     self.assertEqual(final_matchup.home_score, 136.3)
    #     self.assertEqual(final_matchup.away_lineup[0].points, 31.5)

    #     self.assertEqual(middle_matchup.home_score, 136.3)
    #     self.assertEqual(middle_matchup.away_lineup[0].points, 31.5)

    #     self.assertEqual(scoring_period_matchup.home_score, 0.0)
    #     self.assertEqual(scoring_period_matchup.away_lineup[0].points, 0)

    # def test_past_league(self):
    #     league = League(411647, 2017)
        
    #     self.assertEqual(league.scoringPeriodId, 170)

    # def test_past_league_scoreboard(self):
    #     league = League(411647, 2017)
    #     scores = league.scoreboard()

    #     self.assertTrue(scores[0].home_final_score > 0)
    #     self.assertTrue(scores[0].away_final_score > 0)