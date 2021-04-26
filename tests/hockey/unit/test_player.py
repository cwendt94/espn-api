import json
from unittest import TestCase

from espn_api.hockey import Player


class TestPlayer(TestCase):

    def setUp(self) -> None:
        with open('./data/league_data.json') as data:
            self.roster_data = json.loads(data.read())['teams'][0]['roster']['entries']

    def test_player(self):
        player_input = self.roster_data[0]
        actual_player = Player(player_input)

        self.assertEqual('Player(Taylor Hall)', repr(actual_player))


    def test_player_stats_to_df(self):
        player_input = self.roster_data[0]
        actual_player = Player(player_input)

        actual_df = actual_player.to_df("Total 2020")
        # test dict
        second_df = actual_player.to_df("Total 2020")
        self.assertEqual(actual_df['G'].iloc[0], 16)
        self.assertEqual(actual_df['A'].iloc[0], 36)
        self.assertEqual(actual_df['+/-'].iloc[0], -13)
        self.assertEqual(actual_df['PIM'].iloc[0], 32)

        self.assertEqual(actual_player, second_df)





