class BaseSettings(object):
    '''Creates Settings object'''
    def __init__(self, data):
        self.reg_season_count = data['scheduleSettings']['matchupPeriodCount']
        self.matchup_periods = data['scheduleSettings']['matchupPeriods']
        self.veto_votes_required = data['tradeSettings']['vetoVotesRequired']
        self.team_count = data['size']
        self.playoff_team_count = data['scheduleSettings']['playoffTeamCount']
        self.keeper_count = data['draftSettings']['keeperCount']
        self.trade_deadline = 0
        self.division_map = {}
        if 'deadlineDate' in data['tradeSettings']:
            self.trade_deadline = data['tradeSettings']['deadlineDate']
        self.name = data['name']
        self.tie_rule = data['scoringSettings']['matchupTieRule']
        self.playoff_tie_rule = data['scoringSettings']['playoffMatchupTieRule']
        self.playoff_matchup_period_length = data.get('scheduleSettings', {}).get('playoffMatchupPeriodLength', 0)
        self.playoff_seed_tie_rule = data['scheduleSettings']['playoffSeedingRule']
        self.scoring_type = data.get('scoringSettings', {}).get('scoringType')
        self.faab = data['acquisitionSettings']['isUsingAcquisitionBudget']
        divisions = data.get('scheduleSettings', {}).get('divisions', [])
        for division in divisions: self.division_map[division.get('id', 0)] = division.get('name')

    def __repr__(self):
        return f'Settings({self.name})'