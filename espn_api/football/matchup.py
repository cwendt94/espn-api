class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.data = data
        self._fetch_matchup_info()

    def __repr__(self):
        return f'Matchup({self.home_team}, {self.away_team})'

    def _fetch_matchup_info(self):
        '''Fetch info for matchup'''
        self.home_team = self.data['home']['teamId']
        self.home_score = self.data['home']['totalPoints']
        self.matchup_type = self.data.get('playoffTierType', 'NONE')
        self.is_playoff = self.matchup_type != 'NONE'

        # For Leagues with bye weeks
        self.away_team = 0
        self.away_score = 0
        if 'away' in self.data:
            self.away_team = self.data['away']['teamId']
            self.away_score = self.data['away']['totalPoints']
