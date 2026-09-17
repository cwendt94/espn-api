from unittest import TestCase, mock

from espn_api.requests.espn_requests import EspnFantasyRequests


class PlayerPoolIdsTest(TestCase):
    def setUp(self):
        self.request = EspnFantasyRequests(sport="nfl", year=2022, league_id=1)

    def test_collects_ids_from_wrap_and_inner_player(self):
        self.request.league_get = mock.Mock(
            return_value={
                "players": [
                    {"id": 1001},
                    {"player": {"id": 1002}},
                    {"id": 0},
                    {"player": {"id": 1001}},
                ]
            }
        )

        ids = self.request.get_player_pool_ids(18)

        self.assertEqual(ids, [1001, 1002])
        self.request.league_get.assert_called_once()

    def test_paginates_until_short_page(self):
        first = [{"id": i} for i in range(1, 4)]
        second = [{"id": 4}]
        self.request.league_get = mock.Mock(
            side_effect=[
                {"players": first},
                {"players": second},
            ]
        )

        ids = self.request.get_player_pool_ids(18, page_size=3)

        self.assertEqual(ids, [1, 2, 3, 4])
        self.assertEqual(self.request.league_get.call_count, 2)

    def test_stops_on_empty_page(self):
        self.request.league_get = mock.Mock(return_value={"players": []})

        self.assertEqual(self.request.get_player_pool_ids(18), [])
        self.request.league_get.assert_called_once()
