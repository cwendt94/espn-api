from datetime import datetime
from unittest import TestCase

from espn_api.base_offer import Offer


class OfferTest(TestCase):
    def _make_offer(
        self,
        status="EXECUTED",
        bid_amount=20,
        player_id=1001,
        team_id=3,
        process_date=1700000000000,
        add_item=True,
        drop_player_id=999,
    ):
        data = {
            "status": status,
            "id": 42,
            "bidAmount": bid_amount,
            "teamId": team_id,
            "processDate": process_date,
            "items": [],
        }
        if add_item:
            data["items"].append({"type": "ADD", "playerId": player_id})
        if drop_player_id is not None:
            data["items"].append({"type": "DROP", "playerId": drop_player_id})
        return Offer(data, {}, lambda *_: None)

    def test_processed_offer_sets_expected_attributes(self):
        offer = self._make_offer(
            status="EXECUTED", bid_amount=25, player_id=1001, team_id=7
        )

        self.assertEqual(offer.id, 42)
        self.assertEqual(offer.result, "Processed")
        self.assertEqual(offer.amount, 25)
        self.assertEqual(offer.teamId, 7)
        self.assertEqual(offer.player, 1001)
        self.assertEqual(offer.droppedPlayer, 999)
        self.assertEqual(offer.dateTime, datetime.fromtimestamp(1700000000))
        self.assertIn("Offer(Date:", repr(offer))

    def test_result_mapping_for_statuses(self):
        expected = {
            "CANCELED": "Canceled",
            "EXECUTED": "Processed",
            "FAILED_INVALIDPLAYERSOURCE": "Outbid",
            "FAILED_AUCTIONBUDGETEXCEEDED": "Budget Exceeded",
            "FAILED_POSITIONLIMIT": "Position Limit Exceeded",
            "FAILED_ROSTERLOCK": "Failed Due to Roster Lock",
            "FAILED_PLAYERALREADYDROPPED": "Player already dropped",
            "FAILED_ROSTERLIMIT": "Player already dropped",
            "PENDING": "Player already dropped",
        }

        for status, expected_result in expected.items():
            with self.subTest(status=status):
                offer = self._make_offer(status=status)
                self.assertEqual(offer.result, expected_result)

    def test_offer_ordering_uses_status_then_bid_amount(self):
        processed = self._make_offer(status="EXECUTED", bid_amount=30)
        outbid = self._make_offer(status="FAILED_INVALIDPLAYERSOURCE", bid_amount=20)
        canceled = self._make_offer(status="CANCELED", bid_amount=15)

        ordered = sorted([processed, outbid, canceled])
        self.assertEqual(
            [offer.result for offer in ordered], ["Canceled", "Outbid", "Processed"]
        )

    def test_repr_for_canceled_offer(self):
        offer = self._make_offer(status="CANCELED", bid_amount=12, drop_player_id=None)
        self.assertEqual(repr(offer), "Canceled bid")

    def test_missing_items_does_not_raise(self):
        data = {
            "status": "EXECUTED",
            "id": 7,
            "bidAmount": 5,
            "teamId": 2,
            "processDate": 1700000000000,
        }
        offer = Offer(data, {}, lambda *_: None)
        self.assertEqual(offer.result, "Processed")
        self.assertIsNone(offer.player)
        self.assertIsNone(offer.droppedPlayer)

    def test_canceled_offer_leaves_bid_fields_unset(self):
        offer = self._make_offer(status="CANCELED", drop_player_id=None)

        self.assertEqual(offer.result, "Canceled")
        self.assertIsNone(offer.dateTime)
        self.assertIsNone(offer.amount)
        self.assertIsNone(offer.teamId)
        self.assertIsNone(offer.player)
        self.assertIsNone(offer.droppedPlayer)

    def test_canceled_offers_can_be_sorted(self):
        first = self._make_offer(status="CANCELED", drop_player_id=None)
        second = self._make_offer(status="CANCELED", drop_player_id=None)

        ordered = sorted([first, second])
        self.assertEqual([offer.result for offer in ordered], ["Canceled", "Canceled"])
