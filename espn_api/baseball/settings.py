from ..base_settings import BaseSettings
from .constant import POSITION_MAP


class Settings(BaseSettings):
    def __init__(self, data):
        super().__init__(data)
        lineup_slot_counts = data.get('rosterSettings', {}).get('lineupSlotCounts', {})
        # slot IDs not in POSITION_MAP (e.g. bench, IR) are intentionally excluded
        self.position_slot_counts = {
            POSITION_MAP[int(slot_id)]: count
            for slot_id, count in lineup_slot_counts.items()
            if int(slot_id) in POSITION_MAP
        }
