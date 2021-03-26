import json
import numpy as np
from unittest import TestCase

from espn_api.hockey import League

#Load League Data
jsonFile = open('tests/hockey/data.json', "r+")
data = json.load(jsonFile)
jsonFile.close()

class LeagueTest(TestCase):
    
    def test_league_init(self):
        league = League(
                          league_id = 1
                        , year = 2020
                        , espn_s2= 'espn_s2'
                        , swid = 'swid'
                        , username = 'username'
                        , password = 'password'
                        , testing = True
                        , test_data = data
                    )
        players = league.get_league_players()
        self.assertEqual(
                          players.iloc[0]['player_name'], "Taylor Hall")
    
    
    def test_league_stats(self):
        league = League(
                          league_id = 1
                        , year = 2020
                        , espn_s2= 'espn_s2'
                        , swid = 'swid'
                        , username = 'username'
                        , password = 'password'
                        , testing = True
                        , test_data = data
                    )
        stats = league.get_league_player_stats()

        self.assertEqual(stats.iloc[0]['Owner_Name'],"firstName7 lastName7")
        self.assertEqual(stats.iloc[0]['statSourceId'], 2)
        self.assertEqual(stats.iloc[0]['seasonID'], 2020)
