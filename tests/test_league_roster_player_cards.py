from copy import deepcopy
from unittest import TestCase, mock

from espn_api.base_league import BaseLeague
from espn_api.baseball.league import League as BaseballLeague
from espn_api.baseball.player import Player as BaseballPlayer
from espn_api.baseball.team import Team as BaseballTeam
from espn_api.basketball.player import Player as BasketballPlayer
from espn_api.basketball.team import Team as BasketballTeam
from espn_api.football.player import Player as FootballPlayer
from espn_api.football.team import Team as FootballTeam
from espn_api.hockey.league import League as HockeyLeague
from espn_api.hockey.player import Player as HockeyPlayer
from espn_api.hockey.team import Team as HockeyTeam
from espn_api.wbasketball.league import League as WBasketballLeague
from espn_api.wbasketball.player import Player as WBasketballPlayer
from espn_api.wbasketball.team import Team as WBasketballTeam

YEAR = 2025
SCORING_PERIOD = 7


def _player_data(player_id, stats=None, pro_team_id=1):
    return {
        "id": player_id,
        "fullName": f"Player {player_id}",
        "defaultPositionId": 1,
        "eligibleSlots": [0],
        "proTeamId": pro_team_id,
        "injuryStatus": "ACTIVE",
        "injured": False,
        "stats": stats or [],
    }


def _roster_entry(
    player_id, pro_team_id=1, lineup_slot_id=0, acquisition_type="DRAFT"
):
    player = _player_data(player_id, pro_team_id=pro_team_id)
    return {
        "id": player_id,
        "playerId": player_id,
        "fullName": player["fullName"],
        "defaultPositionId": player["defaultPositionId"],
        "lineupSlotId": lineup_slot_id,
        "eligibleSlots": player["eligibleSlots"],
        "acquisitionType": acquisition_type,
        "proTeamId": player["proTeamId"],
        "injuryStatus": player["injuryStatus"],
        "playerPoolEntry": {"id": player_id, "player": player},
    }


def _player_card(player_id, pro_team_id=1):
    player = _player_data(
        player_id,
        [
            {
                "id": f"00{YEAR}",
                "seasonId": YEAR,
                "scoringPeriodId": 0,
                "statSplitTypeId": 0,
                "statSourceId": 0,
                "appliedTotal": 22.5,
                "appliedAverage": 2.25,
                "stats": {"0": 22.5},
                "averageStats": {"0": 2.25},
            }
        ],
        pro_team_id=pro_team_id,
    )
    return {"id": player_id, "player": player}


def _team_data(team_id):
    record = {
        "wins": 1,
        "losses": 0,
        "ties": 0,
        "pointsFor": 10,
        "pointsAgainst": 5,
        "streakLength": 1,
        "streakType": "WIN",
    }
    return {
        "id": team_id,
        "abbrev": f"T{team_id}",
        "name": f"Team {team_id}",
        "divisionId": 0,
        "playoffSeed": team_id,
        "record": {
            "overall": record,
            "home": record,
            "away": record,
            "division": record,
        },
    }


def _league_data(entries):
    return {
        "seasonId": YEAR,
        "status": {"finalScoringPeriod": SCORING_PERIOD},
        "schedule": [],
        "teams": [
            {
                **_team_data(1),
                "roster": {"entries": entries},
            }
        ],
    }


class RosterTeam:
    def __init__(self, data, roster, schedule, year, **kwargs):
        self.team_id = data["id"]
        self.roster = list(roster.get("entries", []))


class LeagueRosterPlayerCardTest(TestCase):
    def test_one_batched_card_request_enriches_multi_team_rosters_for_all_sports(self):
        sports = [
            ("mlb", BaseballLeague, BaseballTeam, BaseballPlayer),
            ("nba", BaseLeague, BasketballTeam, BasketballPlayer),
            ("nfl", BaseLeague, FootballTeam, FootballPlayer),
            ("nhl", BaseLeague, HockeyTeam, HockeyPlayer),
            ("wnba", BaseLeague, WBasketballTeam, WBasketballPlayer),
        ]
        expected_lineup_slots = {
            "mlb": ["C", "1B", "2B", "3B"],
            "nba": ["PG", "SG", "SF", "PF"],
            "nfl": ["QB", "TQB", "RB", "RB/WR"],
            "nhl": ["Center", "Left Wing", "Right Wing", "Forward"],
            "wnba": ["", "G", "F", "C"],
        }

        for sport, league_class, team_class, player_class in sports:
            with self.subTest(sport=sport):
                if sport == "mlb":
                    league = league_class(1, YEAR, fetch_league=False)
                    league.settings = mock.Mock(division_map={})
                else:
                    league = league_class(1, YEAR, sport=sport)
                league.espn_request = mock.Mock()
                league.espn_request.get_player_card.return_value = {
                    "players": [
                        _player_card(101, pro_team_id=3 if sport == "wnba" else 1),
                        _player_card(102, pro_team_id=3 if sport == "wnba" else 1),
                        _player_card(103, pro_team_id=3 if sport == "wnba" else 1),
                    ]
                }

                pro_team_id = 3 if sport == "wnba" else 1
                first_team_entries = [
                    _roster_entry(101, pro_team_id, 0, "DRAFT"),
                    _roster_entry(102, pro_team_id, 1, "WAIVER"),
                ]
                second_team_entries = [
                    _roster_entry(103, pro_team_id, 2, "TRADE"),
                    _roster_entry(101, pro_team_id, 3, "FREEAGENT"),
                ]
                data = _league_data([])
                data["teams"] = [
                    {
                        **_team_data(1),
                        "roster": {"entries": first_team_entries},
                    },
                    {
                        **_team_data(2),
                        "roster": {"entries": second_team_entries},
                    },
                ]
                if sport == "mlb":
                    league._fetch_teams(data)
                else:
                    league._fetch_teams(data, TeamClass=team_class, pro_schedule={})

                league.espn_request.get_player_card.assert_called_once()
                call_args = league.espn_request.get_player_card.call_args
                self.assertEqual(call_args.args[:2], ([101, 102, 103], SCORING_PERIOD))
                if sport == "mlb":
                    self.assertEqual(
                        call_args.kwargs["additional_filters"],
                        ["012025", "022025", "032025"],
                    )
                else:
                    self.assertEqual(call_args.kwargs, {})

                self.assertEqual(len(league.teams), 2)
                self.assertEqual(
                    [
                        [player.playerId for player in team.roster]
                        for team in league.teams
                    ],
                    [[101, 102], [103, 101]],
                )
                for team_index, team in enumerate(league.teams):
                    for roster_index, player in enumerate(team.roster):
                        with self.subTest(
                            sport=sport, team=team.team_id, player=player.playerId
                        ):
                            self.assertIsInstance(player, player_class)
                            self.assertEqual(
                                player.name, f"Player {player.playerId}"
                            )
                            self.assertEqual(
                                player.acquisitionType,
                                (
                                    first_team_entries[roster_index]["acquisitionType"]
                                    if team_index == 0
                                    else second_team_entries[roster_index][
                                        "acquisitionType"
                                    ]
                                ),
                            )
                            self.assertEqual(
                                player.lineupSlot,
                                expected_lineup_slots[sport][
                                    roster_index + (2 if team_index else 0)
                                ],
                            )
                            if sport == "mlb":
                                points = player.stats_splits["season"][0]["points"]
                            elif sport == "nba":
                                points = player.stats["2025_total"]["applied_total"]
                            elif sport == "nfl":
                                points = player.stats[0]["points"]
                            elif sport == "nhl":
                                points = player.stats["Total 2025"]["total"]["GS"]
                            else:
                                points = player.stats["2025"]["total"]["PTS"]
                            self.assertEqual(points, 22.5)

    def test_missing_cards_keep_roster_entries_and_empty_rosters_skip_request(self):
        league = BaseLeague(1, YEAR, sport="nba")
        league.espn_request = mock.Mock()
        league.espn_request.get_player_card.return_value = {
            "players": [_player_card(101)]
        }
        original_entries = [_roster_entry(101), _roster_entry(102)]

        league._fetch_teams(_league_data(original_entries), TeamClass=RosterTeam)

        self.assertEqual(
            league.teams[0].roster[0]["playerPoolEntry"]["player"]["stats"][0][
                "appliedTotal"
            ],
            22.5,
        )
        self.assertEqual(league.teams[0].roster[1], original_entries[1])
        self.assertEqual(original_entries[0]["playerPoolEntry"]["player"]["stats"], [])

        league.espn_request.get_player_card.reset_mock()
        league._fetch_teams(
            {
                **_league_data([]),
                "teams": [{**_team_data(1)}],
            },
            TeamClass=RosterTeam,
        )

        league.espn_request.get_player_card.assert_not_called()
        self.assertEqual(league.teams[0].roster, [])

    def test_roster_projections_survive_card_stats_enrichment(self):
        league = BaseLeague(1, YEAR, sport="nfl")
        league.espn_request = mock.Mock()
        roster_entry = _roster_entry(101)
        roster_projection = {
            "seasonId": YEAR,
            "scoringPeriodId": 18,
            "statSourceId": 1,
            "statSplitTypeId": 0,
            "appliedTotal": 15.7,
            "appliedAverage": 1.1,
            "stats": {"1": 8},
            "appliedStats": {"1": 2},
        }
        roster_actual = {
            "seasonId": YEAR,
            "scoringPeriodId": 17,
            "statSourceId": 0,
            "statSplitTypeId": 0,
            "appliedTotal": 2.0,
            "appliedAverage": 0.2,
            "stats": {"1": 3, "2": 4},
        }
        roster_other_source = {
            **roster_actual,
            "statSourceId": 1,
            "appliedTotal": 5.0,
            "stats": {"1": 5},
        }
        roster_other_split = {
            **roster_actual,
            "statSplitTypeId": 1,
            "appliedTotal": 3.0,
            "stats": {"1": 99},
        }
        roster_other_season = {
            **roster_actual,
            "seasonId": YEAR - 1,
            "appliedTotal": 4.0,
            "stats": {"1": 100},
        }
        roster_player = roster_entry["playerPoolEntry"]["player"]
        roster_player.update(
            seasonOutlook="Roster outlook",
            ownership={"percentOwned": 42.0, "percentStarted": 13.0},
        )
        roster_player["stats"] = [
            roster_projection,
            roster_other_split,
            roster_actual,
            roster_other_source,
            roster_other_season,
        ]
        data = _league_data([roster_entry])
        original_data = deepcopy(data)

        card = _player_card(101)
        card["player"]["stats"] = [
            {
                "seasonId": YEAR,
                "scoringPeriodId": 18,
                "statSourceId": 0,
                "statSplitTypeId": 0,
                "appliedTotal": 12.0,
                "appliedAverage": 0.75,
                "stats": {"1": 12},
                "appliedStats": {"1": 12},
            },
            {
                "seasonId": YEAR,
                "scoringPeriodId": 17,
                "statSourceId": 0,
                "statSplitTypeId": 0,
                "appliedTotal": 0.0,
                "appliedAverage": 0.0,
                "stats": {"2": 0},
            },
            {
                "seasonId": YEAR,
                "scoringPeriodId": 16,
                "statSourceId": 0,
                "statSplitTypeId": 0,
                "appliedTotal": 6.0,
                "appliedAverage": 0.4,
                "stats": {"1": 6},
            },
        ]
        original_card = deepcopy(card)
        league.espn_request.get_player_card.return_value = {"players": [card]}

        league._fetch_teams(data, TeamClass=RosterTeam)

        enriched_entry = league.teams[0].roster[0]
        player = FootballPlayer(enriched_entry, YEAR)
        self.assertEqual(enriched_entry["lineupSlotId"], 0)
        self.assertEqual(enriched_entry["acquisitionType"], "DRAFT")
        self.assertEqual(player.stats[18]["points"], 12.0)
        self.assertEqual(player.stats[18]["projected_points"], 15.7)
        self.assertEqual(player.stats[18]["projected_avg_points"], 1.1)
        self.assertEqual(
            player.stats[18]["projected_breakdown"], {"passingCompletions": 8}
        )
        self.assertEqual(
            player.stats[18]["projected_points_breakdown"],
            {"passingCompletions": 2},
        )
        self.assertEqual(player.stats[17]["points"], 0.0)
        self.assertEqual(player.stats[17]["breakdown"]["passingCompletions"], 3)
        self.assertEqual(player.stats[17]["breakdown"]["passingIncompletions"], 0)
        self.assertEqual(player.stats[16]["points"], 6.0)
        self.assertEqual(player.stats[16]["breakdown"]["passingCompletions"], 6)
        self.assertEqual(
            enriched_entry["playerPoolEntry"]["player"]["seasonOutlook"],
            "Roster outlook",
        )
        self.assertEqual(
            enriched_entry["playerPoolEntry"]["player"]["ownership"],
            {"percentOwned": 42.0, "percentStarted": 13.0},
        )
        merged_stats = enriched_entry["playerPoolEntry"]["player"]["stats"]
        self.assertEqual(
            {
                (
                    stat["seasonId"],
                    stat["scoringPeriodId"],
                    stat["statSourceId"],
                    stat["statSplitTypeId"],
                )
                for stat in merged_stats
            },
            {
                (YEAR, 18, 1, 0),
                (YEAR, 18, 0, 0),
                (YEAR, 17, 0, 0),
                (YEAR, 17, 0, 1),
                (YEAR, 17, 1, 0),
                (YEAR - 1, 17, 0, 0),
                (YEAR, 16, 0, 0),
            },
        )
        self.assertEqual(len(merged_stats), 7)
        matching_stats = [
            stat
            for stat in merged_stats
            if (
                stat["seasonId"],
                stat["scoringPeriodId"],
                stat["statSourceId"],
                stat["statSplitTypeId"],
            )
            == (YEAR, 17, 0, 0)
        ]
        self.assertEqual(len(matching_stats), 1)
        self.assertEqual(matching_stats[0]["appliedTotal"], 0.0)
        self.assertEqual(matching_stats[0]["appliedAverage"], 0.0)
        self.assertEqual(matching_stats[0]["stats"], {"1": 3, "2": 0})
        self.assertEqual(data, original_data)
        self.assertEqual(card, original_card)

    def test_base_player_info_supports_hockey_and_womens_basketball(self):
        sports = [
            (HockeyLeague, HockeyPlayer, "nhl", 1),
            (WBasketballLeague, WBasketballPlayer, "wnba", 3),
        ]

        for league_class, player_class, sport, pro_team_id in sports:
            with self.subTest(sport=sport):
                league = league_class(1, YEAR, fetch_league=False)
                league.finalScoringPeriod = SCORING_PERIOD
                league.player_map = {"Player 101": 101}
                league.espn_request = mock.Mock()
                league.espn_request.get_player_card.return_value = {
                    "players": [_player_card(101, pro_team_id=pro_team_id)]
                }

                player = league.player_info(name="Player 101")

                self.assertIsInstance(player, player_class)
                league.espn_request.get_player_card.assert_called_once_with(
                    [101], SCORING_PERIOD
                )
