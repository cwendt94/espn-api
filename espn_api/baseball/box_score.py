from .constant import STATS_MAP

class BoxScore(object):
    ''' '''
    def __init__(self, data):
        self.winner = data['winner']
        
        home_team = self._process_team(data['home'])

        self.home_team = home_team['id']
        self.home_wins = home_team['wins']
        self.home_losses = home_team['losses']
        self.home_ties = home_team['ties']
        self.home_stats = home_team['stats']

        if 'away' in data:
            away_team = self._process_team(data['away'])

            self.away_team = away_team['id']
            self.away_wins = away_team['wins']
            self.away_losses = away_team['losses']
            self.away_ties = away_team['ties']
            self.away_stats = away_team['stats']
        else:
            self.away_team = None
            self.away_wins = None
            self.away_losses = None
            self.away_ties = None
            self.away_stats = None
    
    @staticmethod
    def _process_team(team_data):
        team = {}

        team['id'] = team_data['teamId']
        team['wins'] = team_data['cumulativeScore']['wins']
        team['losses'] = team_data['cumulativeScore']['losses']
        team['ties'] = team_data['cumulativeScore']['ties']

        team['stats'] = {}
        for stat_key, stat_dict in team_data['cumulativeScore']['scoreByStat'].items():
            team['stats'][STATS_MAP[int(stat_key)]] = {
                'value': stat_dict['score'],
                'result': stat_dict['result']
            }
        
        return team

    def __repr__(self):
        away_team = self.away_team if self.away_team else "BYE"
        home_team = self.home_team if self.home_team else "BYE"
        return 'Box Score(%s at %s)' % (away_team, home_team)
