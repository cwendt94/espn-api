from datetime import datetime
from typing import Any, Callable, Dict, Optional


class Offer(object):
    def __init__(
        self, data: Dict[str, Any], player_map: Any, get_team_data: Callable[..., Any]
    ) -> None:
        status = data["status"]
        self.id: Any = data["id"]
        self.dateTime: Optional[datetime] = None
        self.amount: Optional[int] = None
        self.teamId: Optional[int] = None
        self.player: Optional[int] = None
        self.droppedPlayer: Optional[int] = None
        if status == "CANCELED":
            self.result: str = "Canceled"
        else:
            if status == "EXECUTED":
                self.result = "Processed"
            elif status == "FAILED_INVALIDPLAYERSOURCE":
                self.result = "Outbid"
            elif status == "FAILED_AUCTIONBUDGETEXCEEDED":
                self.result = "Budget Exceeded"
            elif status == "FAILED_POSITIONLIMIT":
                self.result = "Position Limit Exceeded"
            elif status == "FAILED_ROSTERLOCK":
                self.result = "Failed Due to Roster Lock"
            elif (
                status == "FAILED_PLAYERALREADYDROPPED"
                or status == "FAILED_ROSTERLIMIT"
                or status == "PENDING"
            ):
                self.result = "Player already dropped"
            else:
                self.result = status
            # fixes bug with unprocessed waivers stuck on "PENDING" status
            if "processDate" in data:
                self.dateTime = datetime.fromtimestamp(
                    int(data["processDate"] / 1000)
                )  # convert from milliseconds to seconds
            self.amount = data["bidAmount"]
            self.teamId = data["teamId"]
            for item in data.get("items") or []:
                if item["type"] == "ADD":
                    self.player = item["playerId"]
                elif item["type"] == "DROP" and self.result == "Processed":
                    self.droppedPlayer = item["playerId"]

    def __lt__(self, other: "Offer") -> bool:
        # sort by status, then bid amount
        result_ranking = {
            "Processed": 7,
            "Outbid": 6,
            "Player already dropped": 5,
            "Budget Exceeded": 4,
            "Position Limit Exceeded": 3,
            "Failed Due to Roster Lock": 2,
            "Canceled": 1,
            "CANCELLED": 1,
            "PENDING": 0,
        }
        if result_ranking[self.result] != result_ranking[other.result]:
            return result_ranking[self.result] < result_ranking[other.result]
        else:
            # sort by bid amount
            left = self.amount if self.amount is not None else 0
            right = other.amount if other.amount is not None else 0
            return left < right

    def __repr__(self) -> str:
        if self.result == "Canceled":
            return "Canceled bid"
        else:
            ret_string = (
                "Offer(Date:{0}, Player:{1}, Team:{2}, Result:{3}, Bid:{4}".format(
                    self.dateTime, self.player, self.teamId, self.result, self.amount
                )
            )
            if self.droppedPlayer:
                ret_string += ", Dropped:{0})".format(self.droppedPlayer)
            else:
                ret_string += ")"
            return ret_string
