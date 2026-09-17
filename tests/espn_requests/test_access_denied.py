from unittest import TestCase, mock
from espn_api.requests.espn_requests import EspnFantasyRequests, ESPNAccessDenied


class DummyLogger:
    def log_request(self, **kwargs):
        pass


class TestAccessDenied(TestCase):
    def test_access_denied_no_cookies(self):
        req = EspnFantasyRequests(
            sport="nfl", year=2024, league_id=123456, cookies=None, logger=DummyLogger()
        )
        with self.assertRaises(ESPNAccessDenied) as excinfo:
            req.checkRequestStatus(401)
        self.assertIn("espn_s2 and swid are required", str(excinfo.exception))

    def test_access_denied_missing_espn_s2(self):
        cookies = {"SWID": "some_swid"}
        req = EspnFantasyRequests(
            sport="nfl",
            year=2024,
            league_id=123456,
            cookies=cookies,
            logger=DummyLogger(),
        )
        with self.assertRaises(ESPNAccessDenied) as excinfo:
            req.checkRequestStatus(401)
        self.assertIn("espn_s2 and swid are required", str(excinfo.exception))

    def test_access_denied_missing_swid(self):
        cookies = {"espn_s2": "some_s2"}
        req = EspnFantasyRequests(
            sport="nfl",
            year=2024,
            league_id=123456,
            cookies=cookies,
            logger=DummyLogger(),
        )
        with self.assertRaises(ESPNAccessDenied) as excinfo:
            req.checkRequestStatus(401)
        self.assertIn("espn_s2 and swid are required", str(excinfo.exception))

    @mock.patch("requests.get")
    def test_access_denied_with_cookies(self, mock_get):
        cookies = {"espn_s2": "some_s2", "SWID": "some_swid"}
        req = EspnFantasyRequests(
            sport="nfl",
            year=2024,
            league_id=123456,
            cookies=cookies,
            logger=DummyLogger(),
        )

        class DummyResponse:
            status_code = 401

            def json(self):
                return {}

        mock_get.return_value = DummyResponse()
        with self.assertRaises(ESPNAccessDenied) as excinfo:
            req.checkRequestStatus(401)
        self.assertIn(
            f"League {req.league_id} cannot be accessed", str(excinfo.exception)
        )
