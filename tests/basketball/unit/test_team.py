from unittest import TestCase
from espn_api.basketball.team import Team
from espn_api.basketball.player import Player


def _make_team_data(
    team_id=1,
    abbrev="LAL",
    name="Lakers",
    location="Los Angeles",
    nickname="Lakers",
    division_id=1,
    wins=10,
    losses=5,
    ties=0,
    points_for=1000.0,
    points_against=950.0,
    playoff_seed=1,
    rank_final=None,
    acquisitions=5,
    drops=3,
    trades=1,
    acquisition_budget_spent=50,
    logo_url=None,
    stats_data=None,
):
    """Helper function to create team data"""
    data = {
        "id": team_id,
        "abbrev": abbrev,
        "name": name,
        "location": location,
        "nickname": nickname,
        "divisionId": division_id,
        "record": {
            "overall": {
                "wins": wins,
                "losses": losses,
                "ties": ties,
                "pointsFor": points_for,
                "pointsAgainst": points_against,
            }
        },
        "playoffSeed": playoff_seed,
        "rankCalculatedFinal": rank_final,
        "transactionCounter": {
            "acquisitions": acquisitions,
            "acquisitionBudgetSpent": acquisition_budget_spent,
            "drops": drops,
            "trades": trades,
        },
    }

    if logo_url:
        data["logo"] = logo_url

    if stats_data:
        data["valuesByStat"] = stats_data

    return data


class TeamTest(TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.roster_data = {
            "entries": [
                {
                    "fullName": "Player One",
                    "id": 1001,
                    "defaultPositionId": 1,
                    "lineupSlotId": 0,
                    "eligibleSlots": [0],
                    "acquisitionType": "DRAFT",
                    "acquisitionDate": 1700000000000,
                    "proTeamId": 1,
                    "injuryStatus": "ACTIVE",
                    "positionalRanking": 50,
                    "expectedReturnDate": None,
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

        self.schedule_data = []

    def test_team_basic_init(self):
        """Test basic team initialization"""
        data = _make_team_data(team_id=1, name="Lakers", abbrev="LAL")

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.team_id, 1)
        self.assertEqual(team.team_name, "Lakers")
        self.assertEqual(team.team_abbrev, "LAL")

    def test_team_record_stats(self):
        """Test team record statistics"""
        data = _make_team_data(
            wins=20, losses=10, ties=0, points_for=2000.0, points_against=1800.0
        )

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.wins, 20)
        self.assertEqual(team.losses, 10)
        self.assertEqual(team.ties, 0)
        self.assertEqual(team.points_for, 2000.0)
        self.assertEqual(team.points_against, 1800.0)

    def test_team_transaction_stats(self):
        """Test team transaction statistics"""
        data = _make_team_data(
            acquisitions=10, drops=5, trades=2, acquisition_budget_spent=100
        )

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.acquisitions, 10)
        self.assertEqual(team.drops, 5)
        self.assertEqual(team.trades, 2)
        self.assertEqual(team.acquisition_budget_spent, 100)

    def test_team_division_id(self):
        """Test team division ID"""
        data = _make_team_data(division_id=3)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.division_id, 3)

    def test_team_playoff_seed(self):
        """Test team playoff seed"""
        data = _make_team_data(playoff_seed=5)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.standing, 5)

    def test_team_final_standing(self):
        """Test team final standing"""
        data = _make_team_data(rank_final=3)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.final_standing, 3)

    def test_team_division_name_default(self):
        """Test team division name defaults to empty"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.division_name, "")

    def test_team_logo_url(self):
        """Test team logo URL"""
        logo = "https://example.com/logo.png"
        data = _make_team_data(logo_url=logo)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.logo_url, logo)

    def test_team_logo_url_default(self):
        """Test team logo URL defaults to empty"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.logo_url, "")

    def test_team_stats_mapping(self):
        """Test team stats value mapping"""
        stats_data = {"0": 150.0, "3": 20.0, "1": 10.0}  # PTS  # AST  # BLK
        data = _make_team_data(stats_data=stats_data)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertIsNotNone(team.stats)
        self.assertEqual(team.stats["PTS"], 150.0)
        self.assertEqual(team.stats["AST"], 20.0)
        self.assertEqual(team.stats["BLK"], 10.0)

    def test_team_stats_none_by_default(self):
        """Test team stats is None when not provided"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertIsNone(team.stats)

    def test_team_roster_initialization(self):
        """Test team roster initialization"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(len(team.roster), 1)
        self.assertIsInstance(team.roster[0], Player)
        self.assertEqual(team.roster[0].name, "Player One")

    def test_team_schedule_initialization(self):
        """Test team schedule initialization"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(len(team.schedule), 0)

    def test_team_repr(self):
        """Test team string representation"""
        data = _make_team_data(name="Lakers")

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(repr(team), "Team(Lakers)")

    def test_team_team_name_from_location_nickname(self):
        """Test team name constructed from location and nickname when name is not provided"""
        data = {
            "id": 1,
            "abbrev": "LAL",
            "name": "Unknown",  # Triggers fallback
            "location": "Los Angeles",
            "nickname": "Lakers",
            "divisionId": 1,
            "record": {
                "overall": {
                    "wins": 10,
                    "losses": 5,
                    "ties": 0,
                    "pointsFor": 1000.0,
                    "pointsAgainst": 950.0,
                }
            },
            "playoffSeed": 1,
            "rankCalculatedFinal": None,
            "transactionCounter": {},
        }

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.team_name, "Los Angeles Lakers")

    def test_team_owners_kwarg(self):
        """Test team owners passed via kwargs"""
        data = _make_team_data()
        owners = ["Owner One", "Owner Two"]

        team = Team(data, self.roster_data, self.schedule_data, 2023, owners=owners)

        self.assertEqual(team.owners, owners)

    def test_team_owners_default(self):
        """Test team owners defaults to empty list"""
        data = _make_team_data()

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.owners, [])

    def test_team_pro_schedule_kwarg(self):
        """Test pro schedule passed via kwargs"""
        data = _make_team_data()
        pro_schedule = {
            1: {"1": [{"awayProTeamId": 1, "homeProTeamId": 5, "date": 1700000000000}]}
        }

        team = Team(
            data, self.roster_data, self.schedule_data, 2023, pro_schedule=pro_schedule
        )

        # Player should have schedule data
        self.assertGreater(len(team.roster[0].schedule), 0)

    def test_team_multiple_roster_players(self):
        """Test team with multiple roster players"""
        roster_data = {
            "entries": [
                {
                    "fullName": "Player One",
                    "id": 1001,
                    "defaultPositionId": 1,
                    "lineupSlotId": 0,
                    "eligibleSlots": [0],
                    "acquisitionType": "DRAFT",
                    "acquisitionDate": 1700000000000,
                    "proTeamId": 1,
                    "injuryStatus": "ACTIVE",
                    "positionalRanking": 50,
                    "expectedReturnDate": None,
                    "playerPoolEntry": {
                        "player": {
                            "fullName": "Player One",
                            "id": 1001,
                            "injuryStatus": "ACTIVE",
                            "injured": False,
                            "stats": [],
                        }
                    },
                },
                {
                    "fullName": "Player Two",
                    "id": 1002,
                    "defaultPositionId": 2,
                    "lineupSlotId": 1,
                    "eligibleSlots": [1],
                    "acquisitionType": "WAIVER",
                    "acquisitionDate": 1700000000000,
                    "proTeamId": 2,
                    "injuryStatus": "ACTIVE",
                    "positionalRanking": 25,
                    "expectedReturnDate": None,
                    "playerPoolEntry": {
                        "player": {
                            "fullName": "Player Two",
                            "id": 1002,
                            "injuryStatus": "ACTIVE",
                            "injured": False,
                            "stats": [],
                        }
                    },
                },
            ]
        }
        data = _make_team_data()

        team = Team(data, roster_data, self.schedule_data, 2023)

        self.assertEqual(len(team.roster), 2)
        self.assertEqual(team.roster[0].name, "Player One")
        self.assertEqual(team.roster[1].name, "Player Two")

    def test_team_points_against_rounding(self):
        """Test team points against is rounded to 2 decimals"""
        data = _make_team_data(points_against=1234.56789)

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.points_against, 1234.57)

    def test_team_rank_calculated_final_fallback(self):
        """Test rankCalculatedFinal used when rankFinal is None"""
        data = {
            "id": 1,
            "abbrev": "LAL",
            "name": "Lakers",
            "divisionId": 1,
            "record": {
                "overall": {
                    "wins": 10,
                    "losses": 5,
                    "ties": 0,
                    "pointsFor": 1000.0,
                    "pointsAgainst": 950.0,
                }
            },
            "playoffSeed": 1,
            "rankFinal": None,
            "rankCalculatedFinal": 2,
            "transactionCounter": {},
        }

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.final_standing, 2)

    def test_team_default_transaction_counter(self):
        """Test default transaction counter when not provided"""
        data = {
            "id": 1,
            "abbrev": "LAL",
            "name": "Lakers",
            "divisionId": 1,
            "record": {
                "overall": {
                    "wins": 10,
                    "losses": 5,
                    "ties": 0,
                    "pointsFor": 1000.0,
                    "pointsAgainst": 950.0,
                }
            },
            "playoffSeed": 1,
            "rankCalculatedFinal": None,
        }

        team = Team(data, self.roster_data, self.schedule_data, 2023)

        self.assertEqual(team.acquisitions, 0)
        self.assertEqual(team.drops, 0)
        self.assertEqual(team.trades, 0)
        self.assertEqual(team.acquisition_budget_spent, 0)
