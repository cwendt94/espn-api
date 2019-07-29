class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.data = data
        self._fetch_matchup_info()

    def __repr__(self):
        return 'Matchup(%s, %s)' % (self.home_team, self.away_team, )

    def _fetch_matchup_info(self):
        '''Fetch info for matchup'''
        self.home_team = self.data['home']['teamId']
        self.home_score = self.data['home']['totalPoints']
        self.away_team = self.data['away']['teamId']
        self.away_score = self.data['away']['totalPoints']
        # if self.data['teams'][0]['home'] and not self.data['bye']:
        #     self.home_team = self.data['teams'][0]['teamId']
        #     self.home_score = self.data['teams'][0]['score']
        #     self.away_team = self.data['teams'][1]['teamId']
        #     self.away_score = self.data['teams'][1]['score']
        # elif self.data['teams'][0]['home'] and not self.data['bye']:
        #     self.home_team = self.data['teams'][1]['teamId']
        #     self.home_score = self.data['teams'][1]['score']
        #     self.away_team = self.data['teams'][0]['teamId']
        #     self.away_score = self.data['teams'][0]['score']
        # else:
        #     self.home_team = self.data['teams'][0]['teamId']
        #     self.home_score = self.data['teams'][0]['score']
        #     self.away_team = None
        #     self.away_score = None
