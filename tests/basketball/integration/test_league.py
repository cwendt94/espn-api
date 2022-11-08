from unittest import TestCase
from espn_api.basketball import League

# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(411647, 2019)

        self.assertEqual(league.scoringPeriodId, 178)
        player = league.teams[0].roster[0]
        self.assertEqual(player.schedule['2']['team'], 'BKN')
        self.assertEqual(player.total_points, 3583.0)
        self.assertEqual(player.avg_points, 45.35)

    def test_league_scoreboard(self):
        league = League(411647, 2019)
        scores = league.scoreboard()

        self.assertEqual(scores[0].home_final_score, 4240.0)
        self.assertEqual(scores[0].away_final_score, 2965.0)
    
    def test_league_free_agents(self):
        league = League(411647, 2019)
        free_agents = league.free_agents()

        self.assertNotEqual(len(free_agents), 0)
    def test_player_info(self):
        league = League(411647, 2019)
        player_id = league.teams[0].roster[0].playerId

        player = league.player_info(playerId=player_id)

        self.assertEqual(player.__repr__(), 'Player(Andre Drummond)')
        self.assertEqual(player.schedule['2']['team'], 'BKN')
        self.assertEqual(player.stats['2']['team'], 'BKN')
        self.assertEqual(player.stats['2']['total']['PTS'], 24.0)

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
    
    def test_league_box_scores_category(self):
        league = League(1631984064, 2023)

        score = league.box_scores(matchup_period=3, scoring_period=21)

        self.assertEqual(score[0].__repr__(), 'Box Score(Team(Team McWilliams) at Team(Team Wendt))')
        self.assertEqual(score[0].away_lineup[0].name, 'Stephen Curry')
        # comment for now until matchup week is over
        self.assertEqual(score[0].away_stats['PTS'], { 'value': 733.0, 'result': 'WIN' })

    def test_past_league(self):
        league = League(411647, 2017)
        
        self.assertEqual(league.scoringPeriodId, 170)

    def test_past_league_scoreboard(self):
        league = League(411647, 2017)
        scores = league.scoreboard()

        self.assertTrue(scores[0].home_final_score > 0)
        self.assertTrue(scores[0].away_final_score > 0)
    
    def test_blank_league_init(self):
        blank_league = League(411647, 2019, fetch_league=False)
        self.assertEqual(len(blank_league.teams), 0)
