WINNERS_BRACKET = 'WINNERS_BRACKET'


class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.data = data
        self._fetch_matchup_info()

    def __repr__(self):
        return 'Matchup(%s, %s)' % (self.home_team, self.away_team, )

    def is_playoff(self):
        return WINNERS_BRACKET == self.playoff_tier_type

    def _fetch_matchup_info(self):
        '''Fetch info for matchup'''
        self.home_team = self.data['home']['teamId']
        self.home_score = self.data['home']['totalPoints']

        # For Leagues with bye weeks
        self.away_team = 0
        self.away_score = 0
        if 'away' in self.data:
            self.away_team = self.data['away']['teamId']
            self.away_score = self.data['away']['totalPoints']
        self.playoff_tier_type = self.data.get('playoffTierType', 'regular')
        self.winner = self.home_team if self.data['winner'] == 'HOME' else self.away_team
