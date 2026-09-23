import io
from unittest import TestCase, mock

import requests_mock

from espn_api.requests.espn_requests import (
    ESPNAccessDenied,
    ESPNInvalidLeague,
    ESPNUnknownError,
    EspnFantasyRequests,
)


class EspnRequestsTest(TestCase):

    @requests_mock.Mocker()
    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_stub(self, mock_request, mock_stdout):
        url_api_key = "https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US"
        mock_request.post(url_api_key, status_code=400)

    def test_init_uses_legacy_endpoint_for_pre_2018_year(self):
        request = EspnFantasyRequests(sport="nfl", year=2017, league_id=1234)

        self.assertIn("/leagueHistory/1234?seasonId=2017", request.LEAGUE_ENDPOINT)
        self.assertIn("/seasons/2017", request.ENDPOINT)

    def test_init_uses_modern_endpoint_for_recent_year(self):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        self.assertIn("/seasons/2024/segments/0/leagues/1234", request.LEAGUE_ENDPOINT)
        self.assertIn("/seasons/2024", request.ENDPOINT)

    def test_unknown_sport_raises_exception(self):
        with self.assertRaisesRegex(Exception, "Unknown sport"):
            EspnFantasyRequests(sport="bad_sport", year=2024, league_id=1234)

    @mock.patch("requests.get")
    def test_check_request_status_401_uses_fallback_and_returns_response(
        self, mock_get
    ):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        class DummyResponse:
            status_code = 200

            def json(self):
                return {"ok": True}

        mock_get.return_value = DummyResponse()

        self.assertEqual(request.checkRequestStatus(401), {"ok": True})
        self.assertIn("/leagueHistory/1234?seasonId=2024", request.LEAGUE_ENDPOINT)

    @mock.patch("requests.get")
    def test_check_request_status_401_without_credentials_raises(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        class DummyResponse:
            status_code = 401

            def json(self):
                return {}

        mock_get.return_value = DummyResponse()

        with self.assertRaises(ESPNAccessDenied):
            request.checkRequestStatus(401)

    @mock.patch("requests.get")
    def test_check_request_status_404_communication_returns_empty_topics(
        self, mock_get
    ):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        self.assertEqual(
            request.checkRequestStatus(404, extend="/communication/"), {"topics": []}
        )
        mock_get.assert_not_called()

    @mock.patch("requests.get")
    def test_check_request_status_404_invalid_league_raises(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        with self.assertRaises(ESPNInvalidLeague):
            request.checkRequestStatus(404)

    @mock.patch("requests.get")
    def test_check_request_status_other_http_raises_unknown_error(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)
        mock_get.return_value = mock.Mock(status_code=500)

        with self.assertRaises(ESPNUnknownError):
            request.checkRequestStatus(500)

    @mock.patch("requests.get")
    def test_league_get_returns_first_item_from_list_and_logs(self, mock_get):
        request = EspnFantasyRequests(
            sport="nfl",
            year=2024,
            league_id=1234,
            logger=mock.Mock(),
        )

        class DummyResponse:
            status_code = 200

            def json(self):
                return [{"status": "ok"}]

        mock_get.return_value = DummyResponse()

        self.assertEqual(request.league_get(params={"view": "x"}), {"status": "ok"})
        request.logger.log_request.assert_called_once()

    @mock.patch("requests.get")
    def test_get_calls_endpoint_and_returns_json(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        class DummyResponse:
            status_code = 200

            def json(self):
                return {"foo": "bar"}

        mock_get.return_value = DummyResponse()

        self.assertEqual(request.get(params={"view": "x"}), {"foo": "bar"})

    @mock.patch("requests.get")
    def test_get_pro_schedule_and_get_pro_players(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        responses = [
            mock.Mock(status_code=200, json=mock.Mock(return_value={"settings": {}})),
            mock.Mock(status_code=200, json=mock.Mock(return_value={"players": []})),
        ]
        mock_get.side_effect = responses

        self.assertEqual(request.get_pro_schedule(), {"settings": {}})
        self.assertEqual(request.get_pro_players(), {"players": []})
        self.assertEqual(mock_get.call_count, 2)

    @mock.patch("requests.get")
    def test_get_league_message_board_formats_filters(self, mock_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        class DummyResponse:
            status_code = 200

            def json(self):
                return {"topics": [{"id": 1}]}

        mock_get.return_value = DummyResponse()

        self.assertEqual(
            request.get_league_message_board(msg_types=["FA", "TRADED"]),
            {"topics": [{"id": 1}]},
        )
        self.assertIn("x-fantasy-filter", mock_get.call_args.kwargs["headers"])

    @mock.patch.object(EspnFantasyRequests, "league_get")
    def test_get_league_offers_and_player_card(self, mock_league_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)

        mock_league_get.return_value = {"ok": True}

        self.assertEqual(request.get_league_offers(5), {"ok": True})
        self.assertEqual(
            request.get_player_card([1, 2], 4, additional_filters=["03"]), {"ok": True}
        )
        self.assertEqual(mock_league_get.call_count, 2)

    @mock.patch.object(EspnFantasyRequests, "news_get")
    def test_get_player_news_and_player_pool_helpers(self, mock_news_get):
        request = EspnFantasyRequests(sport="nfl", year=2024, league_id=1234)
        mock_news_get.return_value = {"news": []}

        self.assertEqual(request.get_player_news(42), {"news": []})
        self.assertEqual(request._player_wrap_id({"id": 7}), 7)
        self.assertEqual(request._player_wrap_id({"player": {"id": 9}}), 9)
        self.assertIsNone(request._player_wrap_id({"id": 0}))
        self.assertIsNone(request._player_wrap_id({"player": {"id": 0}}))
        self.assertIsNone(request._player_wrap_id("bad"))

    def test_get_player_pool_ids_handles_invalid_and_paginated_batches(self):
        request = EspnFantasyRequests(sport="nfl", year=2022, league_id=1)
        request.league_get = mock.Mock(
            side_effect=[
                {
                    "players": [
                        {"id": 1},
                        {"player": {"id": 2}},
                        {"id": 0},
                        {"bad": "value"},
                    ]
                },
                {"players": [{"id": 3}, {"player": {"id": 2}}]},
            ]
        )

        ids = request.get_player_pool_ids(18, page_size=3)

        self.assertEqual(ids, [1, 2, 3])
        self.assertEqual(request.league_get.call_count, 2)

    @mock.patch("requests.get")
    def test_league_get_uses_alternate_endpoint_when_401_and_keeps_response(
        self, mock_get
    ):
        request = EspnFantasyRequests(sport="nfl", year=2017, league_id=1234)

        class FirstResponse:
            status_code = 401

            def json(self):
                return {}

        class SecondResponse:
            status_code = 200

            def json(self):
                return {"id": 999}

        mock_get.side_effect = [FirstResponse(), SecondResponse()]

        self.assertEqual(request.league_get(), {"id": 999})
        self.assertIn("/seasons/2017/segments/0/leagues/1234", request.LEAGUE_ENDPOINT)

    @mock.patch("requests.get")
    def test_get_with_logger_writes_request_data(self, mock_get):
        logger = mock.Mock()
        request = EspnFantasyRequests(
            sport="nfl", year=2024, league_id=1234, logger=logger
        )

        class DummyResponse:
            status_code = 200

            def json(self):
                return {"done": True}

        mock_get.return_value = DummyResponse()

        self.assertEqual(request.get(params={"a": 1}), {"done": True})
        logger.log_request.assert_called_once()

    # @requests_mock.Mocker()
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # def test_authentication_api_fail(self, mock_request, mock_stdout):
    #     url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
    #     mock_request.post(url_api_key, status_code=400)
    #     request = EspnFantasyRequests(sport='nfl', league_id=1234, year=2019)
    #     request.authentication(username='user', password='pass')
    #     self.assertEqual(mock_stdout.getvalue(), 'Unable to access API-Key\nRetry the authentication or continuing without private league access\n')

    # @requests_mock.Mocker()
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # def test_authentication_login_fail(self, mock_request, mock_stdout):
    #     url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
    #     url_login = 'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US'
    #     mock_request.post(url_api_key,  headers={'api-key':'None'}, status_code=200)
    #     mock_request.post(url_login, status_code=400, json={'eror': 'error'})

    #     request = EspnFantasyRequests(sport='nfl', league_id=1234, year=2019)
    #     request.authentication(username='user', password='pass')
    #     self.assertEqual(mock_stdout.getvalue(), 'Authentication unsuccessful - check username and password input\nRetry the authentication or continuing without private league access\n')

    # @requests_mock.Mocker()
    # @mock.patch('sys.stdout', new_callable=io.StringIO)
    # def test_authentication_login_error(self, mock_request, mock_stdout):
    #     url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
    #     url_login = 'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US'
    #     mock_request.post(url_api_key,  headers={'api-key':'None'}, status_code=200)
    #     mock_request.post(url_login, status_code=200, json={'error': {}})

    #     request = EspnFantasyRequests(sport='nfl', league_id=1234, year=2019)
    #     request.authentication(username='user', password='pass')
    #     self.assertEqual(mock_stdout.getvalue(), 'Authentication unsuccessful - error:{}\nRetry the authentication or continuing without private league access\n')

    # @requests_mock.Mocker()
    # def test_authentication_pass(self, mock_request):
    #     url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
    #     url_login = 'https://ha.registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/guest/login?langPref=en-US'
    #     mock_request.post(url_api_key,  headers={'api-key':'None'}, status_code=200)
    #     mock_request.post(url_login, status_code=200, json={'error': None,'data': {'s2': 'cookie1', 'profile': {'swid': 'cookie2'}}})

    #     request = EspnFantasyRequests(sport='nfl', league_id=1234, year=2019)
    #     request.authentication(username='user', password='pass')
    #     self.assertEqual(request.cookies['espn_s2'], 'cookie1')
    #     self.assertEqual(request.cookies['swid'], 'cookie2')
