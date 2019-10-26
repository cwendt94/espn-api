from .constant import STATS_MAP

class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.data = data
        self._fetch_matchup_info()

    def __repr__(self):
        # TODO: use final score when that's available?
        # writing this too early to see if data['home']['totalPoints'] is final score
        # it might also be used for points leagues instead of category leagues
        if 'cumulativeScore' not in self.data['home'].keys():
            return 'Matchup(%s, %s)' % (self.home_team, self.away_team, )
        else:
            return 'Matchup(%s %s - %s %s)' % (self.home_team,
                                               str(round(self.home_team_live_score, 1)),
                                               str(round(self.away_team_live_score, 1)),
                                               self.away_team)

    def _fetch_matchup_info(self):
        '''Fetch info for matchup'''
        self.home_team = self.data['home']['teamId']
        self.home_team_live_score = None
        self.home_final_score = self.data['home']['totalPoints']
        self.away_team = self.data['away']['teamId']
        self.away_team_live_score = None
        self.away_final_score = self.data['away']['totalPoints']
        self.winner = self.data['winner']
        self.home_team_cats = None
        self.away_team_cats = None
        
        # if stats are available
        if 'cumulativeScore' in self.data['home'].keys():

            self.home_team_live_score = (self.data['home']['cumulativeScore']['wins'] +
                                         self.data['home']['cumulativeScore']['ties']/2)
            self.away_team_live_score = (self.data['away']['cumulativeScore']['wins'] +
                                         self.data['away']['cumulativeScore']['ties']/2)
            
            self.home_team_cats = { STATS_MAP[i]: {'score': self.data['home']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': self.data['home']['cumulativeScore']['scoreByStat'][i]['result']} for i in self.data['home']['cumulativeScore']['scoreByStat'].keys()}
            
            self.away_team_cats = { STATS_MAP[i]: {'score': self.data['away']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': self.data['away']['cumulativeScore']['scoreByStat'][i]['result']} for i in self.data['away']['cumulativeScore']['scoreByStat'].keys()}
        
