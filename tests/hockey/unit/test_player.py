import json
from unittest import TestCase

from espn_api.hockey import Player


class TestPlayer(TestCase):

    def setUp(self) -> None:
        with open('tests/hockey/unit/data/league_data.json') as data:
            self.roster_data = json.loads(data.read())['teams'][0]['roster']['entries']

    def test_player(self):
        player_input = self.roster_data[0]
        actual_player = Player(player_input)

        self.assertEqual('Player(Taylor Hall)', repr(actual_player))
        self.assertEqual(actual_player.position, 'Left Wing')





