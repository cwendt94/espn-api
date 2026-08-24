from unittest import TestCase
from espn_api.basketball.activity import Activity
from espn_api.basketball.constant import ACTIVITY_MAP, POSITION_MAP


class ActivityTest(TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.player_map = {
            1001: "Player One",
            1002: "Player Two",
            1003: "Player Three",
        }

        self.team_data = {
            "team1": "Team One",
            "team2": "Team Two",
            "team3": "Team Three",
        }

        self.get_team_data = lambda team_id: self.team_data.get(team_id, "")

    def test_activity_init_empty_messages(self):
        """Test Activity initialization with empty messages"""
        data = {"date": "2023-01-01", "messages": []}

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(activity.date, "2023-01-01")
        self.assertEqual(len(activity.actions), 0)

    def test_activity_init_with_fa_added(self):
        """Test Activity with FA_ADDED message (type 178)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 178,
                    "from": "team1",
                    "to": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(team, "Team One")
        self.assertEqual(action, "FA ADDED")
        self.assertEqual(player, "Player One")
        self.assertEqual(position, "")

    def test_activity_init_with_waiver_added(self):
        """Test Activity with WAIVER_ADDED message (type 180)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 180,
                    "to": "team1",
                    "targetId": 1002,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(team, "Team One")
        self.assertEqual(action, "WAIVER ADDED")
        self.assertEqual(player, "Player Two")

    def test_activity_init_with_dropped(self):
        """Test Activity with DROPPED message (type 179)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 179,
                    "to": "team2",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(team, "Team Two")
        self.assertEqual(action, "DROPPED")
        self.assertEqual(player, "Player One")

    def test_activity_init_with_traded(self):
        """Test Activity with TRADED message (type 244)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 244,
                    "from": "team1",
                    "targetId": 1003,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(team, "Team One")
        self.assertEqual(action, "TRADED")
        self.assertEqual(player, "Player Three")

    def test_activity_init_with_moved_no_include(self):
        """Test Activity with MOVED message (type 188) when include_moved=False"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 188,
                    "to": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(
            data, self.player_map, self.get_team_data, include_moved=False
        )

        # With include_moved=False and type 188, action should be UNKNOWN
        self.assertEqual(len(activity.actions), 0)

    def test_activity_init_with_moved_include(self):
        """Test Activity with MOVED message (type 188) when include_moved=True"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 188,
                    "to": 4,  # Position ID that's in POSITION_MAP
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(
            data, self.player_map, self.get_team_data, include_moved=True
        )

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(action, "MOVED")
        self.assertEqual(position, "C")  # Position ID 4 maps to 'C'

    def test_activity_init_with_unknown_player(self):
        """Test Activity with player not in player_map"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 178,
                    "from": "team1",
                    "to": "team1",
                    "targetId": 9999,  # Player not in map
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(player, "")

    def test_activity_init_with_unknown_message_type(self):
        """Test Activity with unknown message type"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 999,  # Unknown message type
                    "to": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        # Unknown message type should result in no actions added
        self.assertEqual(len(activity.actions), 0)

    def test_activity_repr_with_actions(self):
        """Test Activity __repr__ with actions"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 178,
                    "from": "team1",
                    "to": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        repr_str = repr(activity)
        self.assertIn("Activity", repr_str)
        self.assertIn("Team One", repr_str)
        self.assertIn("FA ADDED", repr_str)
        self.assertIn("Player One", repr_str)

    def test_activity_repr_empty_actions(self):
        """Test Activity __repr__ with no actions"""
        data = {"date": "2023-01-01", "messages": []}

        activity = Activity(data, self.player_map, self.get_team_data)

        repr_str = repr(activity)
        self.assertEqual(repr_str, "")

    def test_activity_multiple_messages(self):
        """Test Activity with multiple messages"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 178,
                    "from": "team1",
                    "to": "team1",
                    "targetId": 1001,
                },
                {
                    "messageTypeId": 179,
                    "to": "team2",
                    "targetId": 1002,
                },
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 2)
        self.assertEqual(activity.actions[0][1], "FA ADDED")
        self.assertEqual(activity.actions[1][1], "DROPPED")

    def test_activity_with_position_map_invalid_position(self):
        """Test Activity with MOVED message with invalid position"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 188,
                    "to": 999,  # Position not in POSITION_MAP
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(
            data, self.player_map, self.get_team_data, include_moved=True
        )

        # Action should still be added but position will be empty
        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(action, "MOVED")
        self.assertEqual(position, "")

    def test_activity_with_type_239_dropped(self):
        """Test Activity with type 239 (another DROPPED type)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 239,
                    "for": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(action, "DROPPED")

    def test_activity_with_type_181_dropped(self):
        """Test Activity with type 181 (another DROPPED type)"""
        data = {
            "date": "2023-01-01",
            "messages": [
                {
                    "messageTypeId": 181,
                    "to": "team1",
                    "targetId": 1001,
                }
            ],
        }

        activity = Activity(data, self.player_map, self.get_team_data)

        self.assertEqual(len(activity.actions), 1)
        team, action, player, position = activity.actions[0]
        self.assertEqual(action, "DROPPED")
