from abc import ABC, abstractmethod

from .constant import STATS_MAP

class BoxScore(ABC):
    ''' '''
    def __init__(self, data):
        self.winner = data['winner']
        
        self._process_team(data['home'], True)

        if 'away' in data:
            self._process_team(data['away'], False)
        else:
            self._process_team(None, False)

    @abstractmethod
    def _process_team(self, team_data, is_home_team):
        team = {}

        if team_data is not None:
            team['id'] = team_data['teamId']

        if is_home_team:
            self.home_team = team['id']
        else:
            self.away_team = team.get('id')
    
    def __repr__(self):
        away_team = self.away_team if self.away_team else "BYE"
        home_team = self.home_team if self.home_team else "BYE"
        return 'Box Score(%s at %s)' % (away_team, home_team)


class H2HCategoryBoxScore(BoxScore):
    '''Boxscore class for head to head categories leagues'''
    def __init__(self, data):
        super().__init__(data)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)

        team = {}

        if team_data is not None:
            team['wins'] = team_data['cumulativeScore']['wins']
            team['losses'] = team_data['cumulativeScore']['losses']
            team['ties'] = team_data['cumulativeScore']['ties']

            team['stats'] = {}
            for stat_key, stat_dict in team_data['cumulativeScore']['scoreByStat'].items():
                team['stats'][STATS_MAP[int(stat_key)]] = {
                    'value': stat_dict['score'],
                    'result': stat_dict['result']
                }
        
        if is_home_team:
            self.home_wins = team['wins']
            self.home_losses = team['losses']
            self.home_ties = team['ties']
            self.home_stats = team['stats']
        else:
            self.away_wins = team.get('wins')
            self.away_losses = team.get('losses')
            self.away_ties = team.get('ties')
            self.away_stats = team.get('stats')


class H2HPointsBoxScore(BoxScore):
    '''Boxscore class for head to head points leagues'''
    def __init__(self, data):
        super().__init__(data)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)
        # TODO implement setting the scores
