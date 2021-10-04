import json
from unittest import TestCase

from espn_api.hockey import Team


class TestHockeyTeam(TestCase):
    def setUp(self) -> None:
        with open('tests/hockey/unit/data/league_data.json') as file:
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

        self.assertEqual(len(team.roster), 25)
        self.assertEqual(team.roster[0].name, 'Thomas Chabot')

