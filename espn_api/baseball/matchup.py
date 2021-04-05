import pdb

from .constant import STATS_MAP

class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.home_team_live_score = None
        self.away_team_live_score = None
        self._fetch_matchup_info(data)

    def __repr__(self):
        # TODO: use final score when that's available?
        # writing this too early to see if data['home']['totalPoints'] is final score
        # it might also be used for points leagues instead of category leagues
        if not self.away_team_live_score:
            return 'Matchup(%s, %s)' % (self.home_team, self.away_team, )
        else:
            return 'Matchup(%s %s - %s %s)' % (self.home_team,
                                               str(round(self.home_team_live_score, 1)),
                                               str(round(self.away_team_live_score, 1)),
                                               self.away_team)

    def _fetch_matchup_info(self, data):
        '''Fetch info for matchup'''
        self.home_team = data['home']['teamId']
        self.home_final_score = data['home']['totalPoints']
        self.away_team = data['away']['teamId']
        self.away_final_score = data['away']['totalPoints']
        self.winner = data['winner']
        self.home_team_cats = None
        self.away_team_cats = None

        # if stats are available
        if 'cumulativeScore' in data['home'].keys() and data['home']['cumulativeScore']['scoreByStat']:

            self.home_team_live_score = (data['home']['cumulativeScore']['wins'] +
                                         data['home']['cumulativeScore']['ties']/2)
            self.away_team_live_score = (data['away']['cumulativeScore']['wins'] +
                                         data['away']['cumulativeScore']['ties']/2)

            self.home_team_cats = { STATS_MAP[i]: {'score': data['home']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': data['home']['cumulativeScore']['scoreByStat'][i]['result']} for i in data['home']['cumulativeScore']['scoreByStat'].keys()}

            self.away_team_cats = { STATS_MAP[i]: {'score': data['away']['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': data['away']['cumulativeScore']['scoreByStat'][i]['result']} for i in data['away']['cumulativeScore']['scoreByStat'].keys()}

