from unittest import TestCase

from espn_api.utils.utils import json_parsing


class JsonParsingTest(TestCase):
    def test_returns_first_matching_scalar(self):
        data = {"player": {"fullName": "LeBron James", "id": 1966}}
        self.assertEqual(json_parsing(data, "fullName"), "LeBron James")
        self.assertEqual(json_parsing(data, "id"), 1966)

    def test_missing_key_returns_empty_list(self):
        self.assertEqual(json_parsing({"player": {"id": 1}}, "fullName"), [])

    def test_returns_list_of_scalars(self):
        data = {"player": {"eligibleSlots": [0, 1, 2]}}
        self.assertEqual(json_parsing(data, "eligibleSlots"), [0, 1, 2])

    def test_returns_first_match_from_list_of_objects(self):
        data = [{"id": 1}, {"id": 2}]
        self.assertEqual(json_parsing(data, "id"), 1)

    def test_dict_valued_key_is_walked_not_captured(self):
        data = {"player": {"fullName": "A"}}
        self.assertEqual(json_parsing(data, "player"), [])
