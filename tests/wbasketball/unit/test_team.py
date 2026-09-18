from unittest import TestCase

from espn_api.wbasketball.player import Player
from espn_api.wbasketball.team import Team


def _make_team_data(
    team_id=1,
    name="Liberty",
    abbrev="NY",
    division_id=1,
    wins=10,
    losses=5,
    ties=0,
    playoff_seed=1,
    rank_final=None,
    stats=None,
):
    data = {
        "id": team_id,
        "abbrev": abbrev,
        "name": name,
        "location": "New York",
        "nickname": "Liberty",
        "divisionId": division_id,
        "record": {"overall": {"wins": wins, "losses": losses, "ties": ties}},
        "playoffSeed": playoff_seed,
    }
    if rank_final is not None:
        data["rankFinal"] = rank_final
    if stats is not None:
        data["valuesByStat"] = stats
    return data


def _make_roster():
    return {
        "entries": [
            {
                "fullName": "Player One",
                "id": 1001,
                "defaultPositionId": 1,
                "lineupSlotId": 1,
                "eligibleSlots": [1],
                "acquisitionType": "DRAFT",
                "acquisitionDate": 1700000000000,
                "proTeamId": 3,
                "injuryStatus": "ACTIVE",
                "playerPoolEntry": {
                    "player": {
                        "fullName": "Player One",
                        "id": 1001,
                        "injuryStatus": "ACTIVE",
                        "injured": False,
                        "stats": [],
                    }
                },
            }
        ]
    }


class TeamTest(TestCase):
    def test_team_initializes_record_roster_and_defaults(self):
        team = Team(_make_team_data(), _make_roster(), [], 2023)

        self.assertEqual(team.team_id, 1)
        self.assertEqual(team.team_name, "Liberty")
        self.assertEqual(team.wins, 10)
        self.assertEqual(team.losses, 5)
        self.assertEqual(team.division_name, "")
        self.assertEqual(team.owners, [])
        self.assertIsInstance(team.roster[0], Player)
        self.assertEqual(team.roster[0].name, "Player One")

    def test_team_maps_stats_and_optional_values(self):
        data = _make_team_data(stats={"0": 150.0, "3": 20.0}, rank_final=2)

        team = Team(data, {"entries": []}, [], 2023, owners=["Owner"])

        self.assertEqual(team.stats, {"PTS": 150.0, "AST": 20.0})
        self.assertEqual(team.final_standing, 2)
        self.assertEqual(team.owners, ["Owner"])

    def test_team_builds_schedule_and_marks_self(self):
        schedule = [
            {
                "winner": "HOME",
                "home": {"teamId": 1, "totalPoints": 90},
                "away": {"teamId": 2, "totalPoints": 80},
            }
        ]

        team = Team(_make_team_data(), {"entries": []}, schedule, 2023)

        self.assertEqual(len(team.schedule), 1)
        self.assertIs(team.schedule[0].home_team, team)
        self.assertEqual(team.schedule[0].away_team, 2)

    def test_team_falls_back_to_location_and_nickname(self):
        data = _make_team_data(name="Unknown")

        team = Team(data, {"entries": []}, [], 2023)

        self.assertEqual(team.team_name, "New York Liberty")
        self.assertEqual(repr(team), "Team(New York Liberty)")
