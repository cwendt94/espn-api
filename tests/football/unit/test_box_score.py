from unittest import TestCase

from espn_api.football.box_score import BoxScore

from .test_box_player import _make_box_player_data


def _make_box_score_data(
    home_team_id=1,
    away_team_id=2,
    home_score=100.123,
    away_score=95.987,
    home_projected=None,
    away_projected=None,
    include_away=True,
):
    home = {
        "teamId": home_team_id,
        "totalPoints": home_score,
        "rosterForCurrentScoringPeriod": {
            "entries": [
                _make_box_player_data(
                    player_id=1001,
                    lineup_slot_id=4,
                    actual_stats=18,
                    projected_stats=home_projected,
                ),
                _make_box_player_data(
                    player_id=1002,
                    lineup_slot_id=20,
                    actual_stats=5,
                    projected_stats=99,
                ),
                _make_box_player_data(
                    player_id=1003,
                    lineup_slot_id=21,
                    actual_stats=4,
                    projected_stats=88,
                ),
            ]
        },
    }
    if home_projected is not None:
        home["totalPointsLive"] = home_score
        home["totalProjectedPointsLive"] = home_projected

    data = {"home": home, "playoffTierType": "WINNERS_BRACKET"}
    if include_away:
        data["away"] = {
            "teamId": away_team_id,
            "totalPoints": away_score,
            "rosterForCurrentScoringPeriod": {"entries": []},
        }
        if away_projected is not None:
            data["away"]["totalPointsLive"] = away_score
            data["away"]["totalProjectedPointsLive"] = away_projected
    return data


class BoxScoreTest(TestCase):
    def test_box_score_reads_live_scores_and_playoff_status(self):
        box_score = BoxScore(
            _make_box_score_data(home_projected=110.5, away_projected=101.25),
            {16: (11, 0)},
            {},
            7,
            2023,
        )

        self.assertTrue(box_score.is_playoff)
        self.assertEqual(box_score.matchup_type, "WINNERS_BRACKET")
        self.assertEqual(box_score.home_team, 1)
        self.assertEqual(box_score.away_team, 2)
        self.assertEqual(box_score.home_score, 100.12)
        self.assertEqual(box_score.away_score, 95.99)
        self.assertEqual(box_score.home_projected, 110.5)
        self.assertEqual(box_score.away_projected, 101.25)

    def test_box_score_projects_starters_but_excludes_bench_and_ir(self):
        data = _make_box_score_data(home_projected=None, away_projected=None)
        box_score = BoxScore(data, {16: (11, 0)}, {}, 7, 2023)

        self.assertEqual(box_score.home_projected, 0)
        self.assertEqual(len(box_score.home_lineup), 3)
        self.assertEqual(box_score.home_lineup[0].projected_points, 0)
        self.assertEqual(box_score.home_lineup[1].slot_position, "BE")
        self.assertEqual(box_score.home_lineup[2].slot_position, "IR")

    def test_box_score_handles_missing_away_team(self):
        box_score = BoxScore(
            _make_box_score_data(include_away=False), {}, {}, 7, 2023
        )

        self.assertIsNone(box_score.away_team)
        self.assertEqual(box_score.away_score, 0)
        self.assertEqual(box_score.away_projected, 0)
        self.assertEqual(box_score.away_lineup, [])
        self.assertEqual(repr(box_score), "Box Score(BYE at 1)")

    def test_box_score_repr_includes_both_team_ids(self):
        box_score = BoxScore(_make_box_score_data(), {}, {}, 7, 2023)

        self.assertEqual(repr(box_score), "Box Score(2 at 1)")
