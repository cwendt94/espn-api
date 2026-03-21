import json
from unittest import TestCase, mock

from espn_api.baseball import League
from espn_api.baseball.constant import POSITION_MAP
from espn_api.requests.espn_requests import EspnFantasyRequests


class FreeAgentsPositionFilterTest(TestCase):
    """Tests that free_agents(position=...) correctly filters by slot ID."""

    def setUp(self):
        with mock.patch.object(League, 'fetch_league'):
            self.league = League(league_id=1, year=2021)
        self.league.current_week = 1

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_position_string_builds_correct_slot_filter(self, mock_league_get):
        """Passing position='SP' should send slotId 14, not an empty filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents(position='SP')

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [14])  # 14 is the int key for 'SP' in POSITION_MAP

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_no_position_sends_empty_slot_filter(self, mock_league_get):
        """Calling free_agents() with no position should send an empty slot filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents()

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_invalid_position_sends_empty_slot_filter(self, mock_league_get):
        """An unrecognized position string should not crash and should send an empty filter."""
        mock_league_get.return_value = {'players': []}

        self.league.free_agents(position='INVALID')

        call_kwargs = mock_league_get.call_args
        headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
        sent_filter = json.loads(headers['x-fantasy-filter'])
        slot_ids = sent_filter['players']['filterSlotIds']['value']

        self.assertEqual(slot_ids, [])

    @mock.patch.object(EspnFantasyRequests, 'league_get')
    def test_all_position_strings_resolve_to_their_int_id(self, mock_league_get):
        """Every position name in POSITION_MAP should resolve to its correct int slot ID."""
        mock_league_get.return_value = {'players': []}

        for slot_id, pos_name in POSITION_MAP.items():
            if not isinstance(slot_id, int):
                continue
            with self.subTest(position=pos_name):
                self.league.free_agents(position=pos_name)
                call_kwargs = mock_league_get.call_args
                headers = call_kwargs.kwargs.get('headers') or call_kwargs[1].get('headers')
                sent_filter = json.loads(headers['x-fantasy-filter'])
                slot_ids = sent_filter['players']['filterSlotIds']['value']
                self.assertEqual(slot_ids, [slot_id])
