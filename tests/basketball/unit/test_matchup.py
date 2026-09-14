from unittest import TestCase

from espn_api.basketball.matchup import Matchup


class MatchupTest(TestCase):
    def test_matchup_fetches_category_details(self):
        data = {
            'winner': 'HOME',
            'home': {
                'teamId': 1,
                'totalPoints': 123.4,
                'cumulativeScore': {
                    'wins': 2,
                    'ties': 1,
                    'scoreByStat': {'0': {'score': 110.5, 'result': 'W'}},
                },
            },
            'away': {
                'teamId': 2,
                'totalPoints': 118.7,
                'cumulativeScore': {
                    'wins': 1,
                    'ties': 0,
                    'scoreByStat': {'0': {'score': 104.2, 'result': 'L'}},
                },
            },
        }

        matchup = Matchup(data)

        self.assertEqual(matchup.home_team, 1)
        self.assertEqual(matchup.away_team, 2)
        self.assertEqual(matchup.home_team_live_score, 2.5)
        self.assertEqual(matchup.home_team_cats['PTS']['score'], 110.5)
        self.assertEqual(matchup.away_team_cats['PTS']['result'], 'L')

    def test_matchup_repr_without_live_score(self):
        matchup = Matchup({'winner': 'HOME', 'home': {'teamId': 1, 'totalPoints': 100}, 'away': {'teamId': 2, 'totalPoints': 90}})

        self.assertEqual(repr(matchup), 'Matchup(1, 2)')

    def test_matchup_repr_with_live_score(self):
        data = {
            'winner': 'HOME',
            'home': {
                'teamId': 1,
                'totalPoints': 100,
                'cumulativeScore': {'wins': 2, 'ties': 0, 'scoreByStat': {'0': {'score': 101, 'result': 'W'}}},
            },
            'away': {
                'teamId': 2,
                'totalPoints': 90,
                'cumulativeScore': {'wins': 1, 'ties': 0, 'scoreByStat': {'0': {'score': 89, 'result': 'L'}}},
            },
        }

        matchup = Matchup(data)

        self.assertEqual(repr(matchup), 'Matchup(1 2.0 - 1.0 2)')
