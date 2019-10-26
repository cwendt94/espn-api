from .constant import STATS_MAP

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
        self.winner = self.data['winner']
        self.home_team_cats = None
        self.away_team_cats = None
        
        # load category scores
        if 'cumulativeScore' in self.data['home'].keys():
            self.home_team_cats = { STATS_MAP[i]: {'score': self.data['home']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': self.data['home']['cumulativeScore']['scoreByStat'][i]['result']} for i in self.data['home']['cumulativeScore']['scoreByStat'].keys()}
            
            self.away_team_cats = { STATS_MAP[i]: {'score': self.data['away']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': self.data['away']['cumulativeScore']['scoreByStat'][i]['result']} for i in self.data['away']['cumulativeScore']['scoreByStat'].keys()}
        
