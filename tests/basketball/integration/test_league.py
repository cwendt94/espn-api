from unittest import TestCase
from espn_api.basketball import League

# Integration test to make sure ESPN's API didn't change
class LeagueTest(TestCase):
    def setUp(self):
        self.league = League(411647, 2019)

    def test_league_init(self):

        self.assertEqual(self.league.scoringPeriodId, 178)
        player = self.league.teams[0].roster[0]
        self.assertEqual(player.schedule['2']['team'], 'BKN')
        self.assertEqual(player.total_points, 3583.0)
        self.assertEqual(player.avg_points, 45.35)

    def test_league_scoreboard(self):
        scores = self.league.scoreboard()

        self.assertEqual(scores[0].home_final_score, 4240.0)
        self.assertEqual(scores[0].away_final_score, 2965.0)

    def test_league_draft(self):
        draft = self.league.draft

        self.assertEqual(draft[1].playerName, 'LeBron James')
        self.assertEqual(draft[1].round_num, 1)
        self.assertEqual(draft[2].round_pick, 3)
        self.assertEqual(draft[2].team.team_name, 'Denver  Nuggets ')

    def test_league_free_agents(self):
        free_agents = self.league.free_agents()

        self.assertNotEqual(len(free_agents), 0)
    def test_player_info(self):
        player_id = self.league.teams[0].roster[0].playerId

        player = self.league.player_info(playerId=player_id)

        self.assertEqual(player.__repr__(), 'Player(Andre Drummond)')
        self.assertEqual(player.schedule['2']['team'], 'BKN')
        self.assertEqual(player.stats['2']['team'], 'BKN')
        self.assertEqual(player.stats['2']['total']['PTS'], 24.0)
        self.assertEqual(player.nine_cat_averages,
            {
                'PTS': 17.3,
                'BLK': 1.7,
                'STL': 1.7,
                'AST': 1.4,
                'REB': 15.6,
                'TO': 2.2,
                '3PTM': 0.1,
                'FG%': 0.533,
                'FT%': 0.59
            }
        )

    def test_league_box_scores(self):
        final_matchup = self.league.box_scores()[0]
        middle_matchup = self.league.box_scores(matchup_period=7)[0]
        # same matchup period but single scoring period
        scoring_period_matchup = self.league.box_scores(scoring_period=48, matchup_total=False)[0]

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
