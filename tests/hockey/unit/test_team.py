import json
from unittest import TestCase

from espn_api.hockey import Team


class TestHockeyTeam(TestCase):
    def setUp(self) -> None:
        with open('./data/league_data.json') as file:
            self.data = json.loads(file.read())
            self.teams = self.data['teams']
            self.schedule = self.data['schedule']
            self.seasonId = self.data['seasonId']
            self.year = '2020'

            self.team = self.data['teams'][3]
            self.team_roster = self.team['roster']

    def test_team(self):
        team = Team(self.team, roster= self.team_roster, member= None, schedule= self.schedule, year= self.year)
        self.assertEqual(team.team_abbrev, 'ESPC')

    def test_team_roster_df(self):
        team = Team(self.team, roster= self.team_roster, member= None, schedule= self.schedule, year= self.year)
        df = team.get_roster_df()

        expected_players = ['Thomas Chabot',
                            'Brayden Point',
                            'Patrik Laine',
                            'Mikko Rantanen',
                            'Sidney Crosby',
                            'Dougie Hamilton',
                            'Artemi Panarin',
                            'Frederik Andersen',
                            'Teuvo Teravainen',
                            'Matt Dumba',
                            'William Nylander',
                            'Nico Hischier',
                            'Brock Boeser',
                            'Shea Theodore',
                            'Sam Reinhart',
                            'Jacob Markstrom',
                            'Evgenii Dadonov',
                            'Adam Fox',
                            'Phillip Danault',
                            'Bryan Rust',
                            'Ryan Suter',
                            'Elvis Merzlikins',
                            'Anthony Cirelli',
                            'Alexandar Georgiev',
                            'Nikita Gusev']

        self.assertListEqual(list(df.index), expected_players)

