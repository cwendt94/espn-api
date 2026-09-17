from unittest import TestCase, mock
from espn_api.wbasketball.box_score import BoxScore


def _make_box_score_data(
    home_team_id=1,
    away_team_id=2,
    winner="UNDECIDED",
    home_score=100.0,
    away_score=95.0,
    by_matchup=True,
    home_projected=105.0,
    away_projected=98.0,
    include_away=True,
):
    """Helper function to create box score data"""
    data = {
        "winner": winner,
        "home": {
            "teamId": home_team_id,
            "rosterForMatchupPeriod": {"appliedStatTotal": home_score, "entries": []},
            "totalPointsLive": home_score if by_matchup else None,
            "totalProjectedPointsLive": home_projected if by_matchup else None,
        },
    }

    if include_away:
        data["away"] = {
            "teamId": away_team_id,
            "rosterForMatchupPeriod": {"appliedStatTotal": away_score, "entries": []},
            "totalPointsLive": away_score if by_matchup else None,
            "totalProjectedPointsLive": away_projected if by_matchup else None,
        }

    return data


class BoxScoreTest(TestCase):

    def test_box_score_init_basic(self):
        """Test basic BoxScore initialization"""
        data = _make_box_score_data()
        pro_schedule = {}

        box_score = BoxScore(data, pro_schedule, True, 2023)

        self.assertEqual(box_score.home_team, 1)
        self.assertEqual(box_score.away_team, 2)
        self.assertEqual(box_score.winner, "UNDECIDED")

    def test_box_score_home_team_id(self):
        """Test home team ID is set correctly"""
        data = _make_box_score_data(home_team_id=5)

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.home_team, 5)

    def test_box_score_away_team_id(self):
        """Test away team ID is set correctly"""
        data = _make_box_score_data(away_team_id=8)

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.away_team, 8)

    def test_box_score_winner(self):
        """Test winner field is set correctly"""
        data = _make_box_score_data(winner="HOME")

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.winner, "HOME")

    def test_box_score_scores_by_matchup(self):
        """Test scores when by_matchup is True"""
        data = _make_box_score_data(home_score=100.0, away_score=95.0, by_matchup=True)

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.home_score, 100.0)
        self.assertEqual(box_score.away_score, 95.0)

    def test_box_score_scores_not_by_matchup(self):
        """Test scores when by_matchup is False"""
        data = {
            "winner": "UNDECIDED",
            "home": {
                "teamId": 1,
                "rosterForCurrentScoringPeriod": {
                    "appliedStatTotal": 102.5,
                    "entries": [],
                },
            },
            "away": {
                "teamId": 2,
                "rosterForCurrentScoringPeriod": {
                    "appliedStatTotal": 98.5,
                    "entries": [],
                },
            },
        }

        box_score = BoxScore(data, {}, False, 2023)

        self.assertEqual(box_score.home_score, 102.5)
        self.assertEqual(box_score.away_score, 98.5)

    def test_box_score_projected_scores_by_matchup(self):
        """Test projected scores when by_matchup is True"""
        data = _make_box_score_data(
            home_projected=105.5, away_projected=98.2, by_matchup=True
        )

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.home_projected, 105.5)
        self.assertEqual(box_score.away_projected, 98.2)

    def test_box_score_projected_scores_default_not_by_matchup(self):
        """Test projected scores default to -1 when by_matchup is False"""
        data = {
            "winner": "UNDECIDED",
            "home": {
                "teamId": 1,
                "rosterForCurrentScoringPeriod": {
                    "appliedStatTotal": 100.0,
                    "entries": [],
                },
            },
            "away": {
                "teamId": 2,
                "rosterForCurrentScoringPeriod": {
                    "appliedStatTotal": 95.0,
                    "entries": [],
                },
            },
        }

        box_score = BoxScore(data, {}, False, 2023)

        self.assertEqual(box_score.home_projected, -1)
        self.assertEqual(box_score.away_projected, -1)

    def test_box_score_no_away_team_bye_week(self):
        """Test BoxScore with no away team (bye week)"""
        data = _make_box_score_data(include_away=False)

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.away_team, 0)
        self.assertEqual(box_score.away_score, 0)
        self.assertEqual(box_score.away_projected, -1)
        self.assertEqual(len(box_score.away_lineup), 0)

    def test_box_score_home_lineup_empty(self):
        """Test BoxScore home lineup is empty when no entries"""
        data = _make_box_score_data()

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(len(box_score.home_lineup), 0)

    def test_box_score_away_lineup_empty(self):
        """Test BoxScore away lineup is empty when no entries"""
        data = _make_box_score_data()

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(len(box_score.away_lineup), 0)

    def test_box_score_repr_with_both_teams(self):
        """Test BoxScore repr with both home and away teams"""
        data = _make_box_score_data(home_team_id=5, away_team_id=8, include_away=True)

        box_score = BoxScore(data, {}, True, 2023)

        repr_str = repr(box_score)
        self.assertIn("Box Score", repr_str)
        self.assertIn("8", repr_str)  # Away team
        self.assertIn("5", repr_str)  # Home team
        self.assertIn("at", repr_str)

    def test_box_score_repr_with_bye_week(self):
        """Test BoxScore repr when away team is bye"""
        data = _make_box_score_data(include_away=False)

        box_score = BoxScore(data, {}, True, 2023)

        repr_str = repr(box_score)
        self.assertIn("BYE", repr_str)
        self.assertIn("at", repr_str)

    def test_box_score_score_rounding(self):
        """Test that scores are rounded to 2 decimals"""
        data = {
            "winner": "UNDECIDED",
            "home": {
                "teamId": 1,
                "rosterForMatchupPeriod": {
                    "appliedStatTotal": 100.12345,
                    "entries": [],
                },
                "totalPointsLive": 100.12345,
            },
            "away": {
                "teamId": 2,
                "rosterForMatchupPeriod": {"appliedStatTotal": 95.98765, "entries": []},
                "totalPointsLive": 95.98765,
            },
        }

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.home_score, 100.12)
        self.assertEqual(box_score.away_score, 95.99)

    def test_box_score_default_winner(self):
        """Test default winner when not provided"""
        data = {
            "home": {
                "teamId": 1,
                "rosterForMatchupPeriod": {"appliedStatTotal": 100.0, "entries": []},
                "totalPointsLive": 100.0,
            },
            "away": {
                "teamId": 2,
                "rosterForMatchupPeriod": {"appliedStatTotal": 95.0, "entries": []},
                "totalPointsLive": 95.0,
            },
        }

        box_score = BoxScore(data, {}, True, 2023)

        self.assertEqual(box_score.winner, "UNDECIDED")

    def test_box_score_home_projected_default(self):
        """Test home projected defaults to -1"""
        data = {
            "winner": "UNDECIDED",
            "home": {
                "teamId": 1,
                "rosterForMatchupPeriod": {"appliedStatTotal": 100.0, "entries": []},
            },
            "away": {
                "teamId": 2,
                "rosterForMatchupPeriod": {"appliedStatTotal": 95.0, "entries": []},
            },
        }

        box_score = BoxScore(data, {}, False, 2023)

        self.assertEqual(box_score.home_projected, -1)

    def test_box_score_away_projected_default(self):
        """Test away projected defaults to -1"""
        data = {
            "winner": "UNDECIDED",
            "home": {
                "teamId": 1,
                "rosterForMatchupPeriod": {"appliedStatTotal": 100.0, "entries": []},
            },
            "away": {
                "teamId": 2,
                "rosterForMatchupPeriod": {"appliedStatTotal": 95.0, "entries": []},
            },
        }

        box_score = BoxScore(data, {}, False, 2023)

        self.assertEqual(box_score.away_projected, -1)
