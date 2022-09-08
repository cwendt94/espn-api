from unittest import TestCase
from espn_api.football import League

# Integration test to make sure ESPN's API didnt change
class LeagueTest(TestCase):

    def test_league_init(self):
        league = League(1234, 2018)

        self.assertEqual(league.current_week, 17)

    def test_past_league(self):
        league = League(12345, 2017)

        self.assertEqual(league.nfl_week, 18)

    def test_private_league(self):
        with self.assertRaises(Exception):
            League(368876, 2018)

    def test_unknown_league(self):
        with self.assertRaises(Exception):
            League(2, 2018)

    def test_bad_box_scores(self):
        league = League(1234, 2018)

        with self.assertRaises(Exception):
            league.box_scores()

    def test_bad_free_agents(self):
        league = League(1234, 2018)

        with self.assertRaises(Exception):
            league.free_agents()

    def test_box_scores(self):
        league = League(48153503, 2019)

        box_scores = league.box_scores(week=2)

        self.assertEqual(repr(box_scores[1].away_team), 'Team(TEAM BERRY)')
        self.assertEqual(repr(box_scores[1].away_lineup[1]), 'Player(Odell Beckham Jr., points:29.0, projected:16.72)')
        self.assertEqual(repr(box_scores[1]), 'Box Score(Team(TEAM BERRY) at Team(TEAM HOLLAND))')
        self.assertEqual(box_scores[0].is_playoff, False)

        box_scores = league.box_scores()
        self.assertEqual(box_scores[0].is_playoff, True)

    def test_player_info(self):
        league = League(48153503, 2019)

        # Single ID
        player = league.player_info(playerId=3139477)
        self.assertEqual(player.name, 'Patrick Mahomes')

        # Two ID
        players = league.player_info(playerId=[3139477, 3068267])
        self.assertEqual(len(players), 2)
        self.assertEqual(players[0].name, 'Patrick Mahomes')
        self.assertEqual(players[1].name, 'Austin Ekeler')

    def test_blank_league_init(self):
        blank_league = League(48153503, 2019, fetch_league=False)
        self.assertEqual(len(blank_league.teams), 0)