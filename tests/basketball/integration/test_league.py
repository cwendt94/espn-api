from unittest import TestCase
import unittest
from espn_api.basketball import League

# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(411647, 2019)

        self.assertEqual(league.scoringPeriodId, 178)

    def test_league_scoreboard(self):
        league = League(411647, 2019)
        scores = league.scoreboard()

        self.assertEqual(scores[0].home_final_score, 4240.0)
        self.assertEqual(scores[0].away_final_score, 2965.0)
    
    def test_league_players(self):
        league = League(411647, 2019)
        # set size=1000 to get all players (doesn't have to be 1000, just needs to be large)
        free_agents = league.players(size=1000, types=["FREEAGENT"])
        waivers = league.players(size=1000, types=["WAIVERS"])
        on_team = league.players(size=1000, types=["ONTEAM"])
        all1 = league.players(size=1000, types=["FREEAGENT", "WAIVERS", "ONTEAM"])
        all2 = league.players(size=1000)

        self.assertNotEqual(len(free_agents), 0)
        
        self.assertNotEqual(len(on_team), 0)
        
        self.assertEqual(len(all1), len(all2))
        self.assertNotEqual(len(all2), 0)
        
        self.assertEqual(len(free_agents)+len(waivers)+len(on_team), len(all2))

    def test_league_box_scores(self):
        league = League(411647, 2019)
        final_matchup = league.box_scores()[0]
        middle_matchup = league.box_scores(matchup_period=7)[0]
        # same matchup period but single scoring period
        scoring_period_matchup = league.box_scores(scoring_period=48, matchup_total=False)[0]

        self.assertEqual(final_matchup.home_score, 4240.0)
        self.assertEqual(final_matchup.away_lineup[0].points, 156.0)

        self.assertEqual(middle_matchup.home_score, 1234.0)
        self.assertEqual(middle_matchup.away_lineup[0].points, 12.5)

        self.assertEqual(scoring_period_matchup.home_score, 234.0)
        self.assertEqual(scoring_period_matchup.away_lineup[0].points, 0)

    def test_past_league(self):
        league = League(411647, 2017)
        
        self.assertEqual(league.scoringPeriodId, 170)

    def test_past_league_scoreboard(self):
        league = League(411647, 2017)
        scores = league.scoreboard()

        self.assertTrue(scores[0].home_final_score > 0)
        self.assertTrue(scores[0].away_final_score > 0)