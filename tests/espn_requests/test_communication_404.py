from unittest import TestCase

import requests_mock

from espn_api.requests.espn_requests import EspnFantasyRequests, ESPNInvalidLeague


class Communication404Test(TestCase):
    def setUp(self):
        self.req = EspnFantasyRequests(sport="nfl", year=2022, league_id=123456)

    def test_communication_404_returns_empty_topics(self):
        response = self.req.checkRequestStatus(404, extend="/communication/")
        self.assertEqual(response, {"topics": []})

    def test_communication_404_without_trailing_slash(self):
        response = self.req.checkRequestStatus(404, extend="/communication")
        self.assertEqual(response, {"topics": []})

    def test_league_404_still_invalid(self):
        with self.assertRaises(ESPNInvalidLeague) as excinfo:
            self.req.checkRequestStatus(404)
        self.assertIn("does not exist", str(excinfo.exception))

    @requests_mock.Mocker()
    def test_league_get_communication_404(self, mock_request):
        mock_request.get(
            self.req.LEAGUE_ENDPOINT + "/communication/",
            status_code=404,
            json={
                "messages": [{"message": "COMMUNICATION_GROUP_NOT_FOUND"}],
            },
        )
        self.assertEqual(self.req.league_get(extend="/communication/"), {"topics": []})

    @requests_mock.Mocker()
    def test_message_board_communication_404(self, mock_request):
        mock_request.get(
            self.req.ENDPOINT + "/segments/0/leagues/123456/communication",
            status_code=404,
            json={
                "messages": ["This Communication Group does not exist."],
                "details": [{"type": "COMMUNICATION_GROUP_NOT_FOUND"}],
            },
        )
        self.assertEqual(self.req.get_league_message_board(), {"topics": []})

    @requests_mock.Mocker()
    def test_get_404_outside_communication_still_invalid(self, mock_request):
        mock_request.get(self.req.ENDPOINT + "/players", status_code=404)
        with self.assertRaises(ESPNInvalidLeague):
            self.req.get(extend="/players")
