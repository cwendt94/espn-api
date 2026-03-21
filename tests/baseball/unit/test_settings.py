from unittest import TestCase

from espn_api.baseball.settings import Settings


def _make_settings_data(lineup_slot_counts=None, scoring_type='H2H_CATEGORY',
                         scoring_enhancement_type='NONE'):
    return {
        'name': 'Test League',
        'size': 10,
        'scoringSettings': {
            'scoringType': scoring_type,
            'scoringEnhancementType': scoring_enhancement_type,
            'matchupTieRule': 'NONE',
            'playoffMatchupTieRule': 'NONE',
        },
        'scheduleSettings': {
            'matchupPeriodCount': 20,
            'matchupPeriods': {},
            'playoffTeamCount': 4,
            'playoffMatchupPeriodLength': 1,
            'playoffSeedingRule': 'WINS',
            'divisions': [],
        },
        'tradeSettings': {
            'vetoVotesRequired': 4,
        },
        'draftSettings': {
            'keeperCount': 0,
        },
        'acquisitionSettings': {
            'isUsingAcquisitionBudget': False,
            'acquisitionBudget': 0,
        },
        'rosterSettings': {
            'lineupSlotCounts': lineup_slot_counts or {},
        },
    }


class SettingsPositionSlotCountsTest(TestCase):
    def test_known_slots_are_mapped(self):
        data = _make_settings_data(lineup_slot_counts={
            '14': 2,  # SP
            '15': 3,  # RP
            '0': 1,   # C
        })
        settings = Settings(data)
        self.assertEqual(settings.position_slot_counts['SP'], 2)
        self.assertEqual(settings.position_slot_counts['RP'], 3)
        self.assertEqual(settings.position_slot_counts['C'], 1)

    def test_unknown_slot_ids_are_excluded(self):
        """Slot IDs not in POSITION_MAP (e.g. 18, 21) should be silently dropped."""
        data = _make_settings_data(lineup_slot_counts={'18': 1, '14': 1})
        settings = Settings(data)
        self.assertNotIn(18, settings.position_slot_counts)
        self.assertIn('SP', settings.position_slot_counts)

    def test_empty_roster_settings(self):
        data = _make_settings_data(lineup_slot_counts={})
        settings = Settings(data)
        self.assertEqual(settings.position_slot_counts, {})
