from unittest import mock, TestCase
import requests_mock
import io
from espn_api.requests.espn_requests import EspnFantasyRequests

class EspnRequestsTest(TestCase):

    @requests_mock.Mocker()
    @mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_stub(self, mock_request, mock_stdout):
        url_api_key = 'https://registerdisney.go.com/jgc/v5/client/ESPN-FANTASYLM-PROD/api-key?langPref=en-US'
        mock_request.post(url_api_key, status_code=400)

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