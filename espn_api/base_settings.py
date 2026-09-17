from typing import Any, Dict, List, Optional


class BaseSettings(object):
    """Creates Settings object"""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.reg_season_count: int = data["scheduleSettings"]["matchupPeriodCount"]
        self.matchup_periods: Any = data["scheduleSettings"]["matchupPeriods"]
        self.veto_votes_required: int = data["tradeSettings"]["vetoVotesRequired"]
        self.team_count: int = data["size"]
        self.playoff_team_count: int = data["scheduleSettings"]["playoffTeamCount"]
        self.keeper_count: int = data["draftSettings"]["keeperCount"]
        self.trade_deadline: int = 0
        self.division_map: Dict[Any, Any] = {}
        if "deadlineDate" in data["tradeSettings"]:
            self.trade_deadline = data["tradeSettings"]["deadlineDate"]
        self.name: str = data["name"]
        self.tie_rule: str = data["scoringSettings"]["matchupTieRule"]
        self.playoff_tie_rule: str = data["scoringSettings"]["playoffMatchupTieRule"]
        self.playoff_matchup_period_length: int = data.get("scheduleSettings", {}).get(
            "playoffMatchupPeriodLength", 0
        )
        self.playoff_seed_tie_rule: str = data["scheduleSettings"]["playoffSeedingRule"]
        self.scoring_type: Optional[str] = data.get("scoringSettings", {}).get(
            "scoringType"
        )
        self.median_scoring: bool = (
            data.get("scoringSettings", {}).get("scoringEnhancementType")
            == "WIN_BONUS_TOP_HALF"
        )
        self._raw_scoring_settings: Dict[str, Any] = data.get("scoringSettings", {})
        self._raw_schedule_settings: Dict[str, Any] = data.get("scheduleSettings", {})
        self.faab: bool = data["acquisitionSettings"]["isUsingAcquisitionBudget"]
        self.acquisition_budget: int = data.get("acquisitionSettings", {}).get(
            "acquisitionBudget", 0
        )
        self.acquisition_limit: Optional[int] = data.get("acquisitionSettings", {}).get(
            "acquisitionLimit"
        )
        self.matchup_acquisition_limit: Optional[int] = data.get(
            "acquisitionSettings", {}
        ).get("matchupAcquisitionLimit")
        self.matchup_limit_per_scoring_period: Optional[bool] = data.get(
            "acquisitionSettings", {}
        ).get("matchupLimitPerScoringPeriod")
        self.minimum_bid: int = data.get("acquisitionSettings", {}).get("minimumBid", 0)
        self.waiver_process_days: List[str] = list(
            data.get("acquisitionSettings", {}).get("waiverProcessDays", [])
        )
        self.waiver_process_hour: Optional[int] = data.get("acquisitionSettings", {}).get(
            "waiverProcessHour"
        )
        self.trade_revision_hours: Optional[int] = data.get("tradeSettings", {}).get(
            "revisionHours"
        )
        divisions = data.get("scheduleSettings", {}).get("divisions", [])
        for division in divisions:
            self.division_map[division.get("id", 0)] = division.get("name")

    def __repr__(self) -> str:
        return f"Settings({self.name})"
