from typing import Any, Optional


class BasePick(object):
    """Pick represents a pick in draft"""

    def __init__(
        self,
        team: Optional[Any],
        playerId: Optional[int],
        playerName: str,
        round_num: Optional[int],
        round_pick: Optional[int],
        bid_amount: Optional[int],
        keeper_status: Optional[bool],
        nominatingTeam: Optional[Any],
    ) -> None:
        self.team = team
        self.playerId = playerId
        self.playerName = playerName
        self.round_num = round_num
        self.round_pick = round_pick
        self.bid_amount = bid_amount
        self.keeper_status = keeper_status
        self.nominatingTeam = nominatingTeam

    def __repr__(self) -> str:
        return "Pick(R:%s P:%s, %s, %s)" % (
            self.round_num,
            self.round_pick,
            self.playerName,
            self.team,
        )

    def auction_repr(self) -> str:
        return ", ".join(
            map(
                str,
                [
                    self.team,
                    self.playerId,
                    self.playerName,
                    self.bid_amount,
                    self.keeper_status,
                ],
            )
        )
