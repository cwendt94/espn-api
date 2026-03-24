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
            'revisionHours': 48,
        },
        'draftSettings': {
            'keeperCount': 0,
        },
        'acquisitionSettings': {
            'isUsingAcquisitionBudget': True,
            'acquisitionBudget': 100,
            'acquisitionLimit': 50,
            'matchupAcquisitionLimit': 5,
            'matchupLimitPerScoringPeriod': True,
            'minimumBid': 1,
            'waiverProcessDays': ['MONDAY', 'THURSDAY'],
            'waiverProcessHour': 3,
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


class SettingsAcquisitionTest(TestCase):
    def setUp(self):
        self.settings = Settings(_make_settings_data())

    def test_faab(self):
        self.assertTrue(self.settings.faab)

    def test_acquisition_budget(self):
        self.assertEqual(self.settings.acquisition_budget, 100)

    def test_acquisition_limit(self):
        self.assertEqual(self.settings.acquisition_limit, 50)

    def test_matchup_acquisition_limit(self):
        self.assertEqual(self.settings.matchup_acquisition_limit, 5)

    def test_matchup_limit_per_scoring_period(self):
        self.assertTrue(self.settings.matchup_limit_per_scoring_period)

    def test_minimum_bid(self):
        self.assertEqual(self.settings.minimum_bid, 1)

    def test_waiver_process_days(self):
        self.assertEqual(self.settings.waiver_process_days, ['MONDAY', 'THURSDAY'])

    def test_waiver_process_hour(self):
        self.assertEqual(self.settings.waiver_process_hour, 3)

    def test_trade_revision_hours(self):
        self.assertEqual(self.settings.trade_revision_hours, 48)

    def test_missing_acquisition_fields_default_to_none(self):
        data = _make_settings_data()
        data['acquisitionSettings'] = {'isUsingAcquisitionBudget': False, 'acquisitionBudget': 0}
        data['tradeSettings'] = {'vetoVotesRequired': 4}
        settings = Settings(data)
        self.assertIsNone(settings.acquisition_limit)
        self.assertIsNone(settings.matchup_acquisition_limit)
        self.assertIsNone(settings.waiver_process_hour)
        self.assertIsNone(settings.trade_revision_hours)
        self.assertEqual(settings.waiver_process_days, [])
