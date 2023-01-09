from .constant import STATS_MAP

class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.winner = data['winner']
        (self.home_team, self.home_final_score, self.home_team_cats,
            self.home_team_live_score) = self._fetch_matchup_info(data, 'home')
        (self.away_team, self.away_final_score, self.away_team_cats,
            self.away_team_live_score) = self._fetch_matchup_info(data, 'away')

    def __repr__(self):
        # TODO: use final score when that's available?
        # writing this too early to see if data['home']['totalPoints'] is final score
        # it might also be used for points leagues instead of category leagues
        if not self.away_team_live_score:
            return f'Matchup({self.home_team}, {self.away_team})'
        else:
            return f'Matchup({self.home_team} {round(self.home_team_live_score, 1)} - {round(self.away_team_live_score, 1)} {self.away_team})'

    def _fetch_matchup_info(self, data, team):
        '''Fetch info for matchup'''
        if team not in data:
            return (0, 0, None, None)
        team_id = data[team]['teamId']
        final_score = data[team]['totalPoints']
        team_cats = None
        team_live_score = None

        # if stats are available
        if 'cumulativeScore' in data[team].keys() and data[team]['cumulativeScore']['scoreByStat']:

            team_live_score = (data[team]['cumulativeScore']['wins'] +
                               data[team]['cumulativeScore']['ties']/2)

            team_cats = { STATS_MAP.get(i, i): {'score': data[team]['cumulativeScore']['scoreByStat'][i]['score'],
                                                   'result': data[team]['cumulativeScore']['scoreByStat'][i]['result']} for i in data[team]['cumulativeScore']['scoreByStat'].keys()}

        return (team_id, final_score, team_cats, team_live_score)

