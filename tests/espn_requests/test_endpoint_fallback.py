from unittest import TestCase

import requests
import requests_mock

from espn_api.requests.constant import FANTASY_BASE_ENDPOINT
from espn_api.requests.espn_requests import EspnFantasyRequests, ESPNAccessDenied


class EndpointFallbackTest(TestCase):
    def _endpoints(self, year):
        base = FANTASY_BASE_ENDPOINT + "ffl"
        season = f"{base}/seasons/{year}/segments/0/leagues/123456"
        history = f"{base}/leagueHistory/123456?seasonId={year}"
        return (history, season) if year < 2018 else (season, history)

    def _assert_failed_fallback(self, response, error):
        for year in (2017, 2024):
            with self.subTest(year=year), requests_mock.Mocker() as mock_request:
                request = EspnFantasyRequests(sport="nfl", year=year, league_id=123456)
                original, alternate = self._endpoints(year)
                data = {"id": 123456}
                mock_request.get(
                    original,
                    [
                        {"status_code": 401},
                        {"json": [data] if year < 2018 else data},
                    ],
                )
                mock_request.get(alternate, **response)

                with self.assertRaises(error):
                    request.league_get()

                self.assertEqual(request.LEAGUE_ENDPOINT, original)
                self.assertEqual(request.league_get(), data)
                self.assertEqual(
                    [item.url for item in mock_request.request_history],
                    [original, alternate, original],
                )

    def test_connection_error_preserves_endpoint(self):
        self._assert_failed_fallback(
            {"exc": requests.exceptions.ConnectionError("connection failed")},
            requests.exceptions.ConnectionError,
        )

    def test_timeout_preserves_endpoint(self):
        self._assert_failed_fallback(
            {"exc": requests.exceptions.Timeout("request timed out")},
            requests.exceptions.Timeout,
        )

    def test_invalid_json_preserves_endpoint(self):
        self._assert_failed_fallback(
            {"status_code": 200, "text": "<html>temporarily unavailable</html>"},
            requests.exceptions.JSONDecodeError,
        )

    def test_http_error_preserves_endpoint(self):
        self._assert_failed_fallback({"status_code": 403}, ESPNAccessDenied)

    def test_successful_fallback_is_reused(self):
        for year in (2017, 2024):
            with self.subTest(year=year), requests_mock.Mocker() as mock_request:
                request = EspnFantasyRequests(sport="nfl", year=year, league_id=123456)
                original, alternate = self._endpoints(year)
                data = {"id": 123456}
                mock_request.get(original, status_code=401)
                mock_request.get(alternate, json=data if year < 2018 else [data])

                self.assertEqual(request.league_get(), data)
                self.assertEqual(request.LEAGUE_ENDPOINT, alternate)
                self.assertEqual(request.league_get(), data)
                self.assertEqual(
                    [item.url for item in mock_request.request_history],
                    [original, alternate, alternate],
                )
