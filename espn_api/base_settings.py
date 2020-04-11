class BaseSettings(object):
    '''Creates Settings object'''
    def __init__(self, data):
        self.reg_season_count = data['scheduleSettings']['matchupPeriodCount']
        self.veto_votes_required = data['tradeSettings']['vetoVotesRequired']
        self.team_count = data['size']
        self.playoff_team_count = data['scheduleSettings']['playoffTeamCount']
        self.keeper_count = data['draftSettings']['keeperCount']
        self.trade_deadline = 0
        if 'deadlineDate' in data['tradeSettings']:
            self.trade_deadline = data['tradeSettings']['deadlineDate']
        self.name = data['name']
        self.tie_rule = data['scoringSettings']['matchupTieRule']
        self.playoff_seed_tie_rule = data['scoringSettings']['playoffMatchupTieRule']

    def __repr__(self):
        return 'Settings(%s)' % (self.name)