from ..base_settings import BaseSettings
from .constant import SETTINGS_SCORING_FORMAT_MAP, POSITION_MAP

class Settings(BaseSettings):
    def __init__(self, data):
        super().__init__(data)
        self.scoring_format = []
        scoring_items = data['scoringSettings'].get('scoringItems', [])
        lineup_slot_counts = data['rosterSettings'].get('lineupSlotCounts', {})
        position_labels = list(POSITION_MAP.values())[:len(lineup_slot_counts)]
        self.position_slot_counts = dict(zip(position_labels,list(lineup_slot_counts.values())))

        for scoring_item in scoring_items:
            stat_id = scoring_item['statId']
            points_override = scoring_item.get('pointsOverrides', {}).get('16')

            scoring_type = SETTINGS_SCORING_FORMAT_MAP.get(stat_id, { 'abbr': 'Unknown', 'label': 'Unknown' })
            scoring_type['id'] = stat_id
            scoring_type['points'] = points_override or scoring_item.get('points', 0)
            self.scoring_format.append(scoring_type)