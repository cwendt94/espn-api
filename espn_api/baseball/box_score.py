from abc import ABC, abstractmethod
from .box_player import BoxPlayer

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
        away_team = self.away_team or "BYE"
        home_team = self.home_team or "BYE"
        return f'Box Score({away_team} at {home_team})'


class H2HCategoryBoxScore(BoxScore):
    '''Boxscore class for head to head categories leagues'''
    def __init__(self, data, pro_schedule, year, scoring_period = 0):
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
    def __init__(self, data, pro_schedule, year, scoring_period = 0):
        super().__init__(data)

        (self.home_team, self.home_score, self.home_projected, self.home_lineup) = self._get_team_data('home', data, pro_schedule, scoring_period, year)

        (self.away_team, self.away_score, self.away_projected, self.away_lineup) = self._get_team_data('away', data, pro_schedule, scoring_period, year)

    def _process_team(self, team_data, is_home_team):
        super()._process_team(team_data, is_home_team)
        # TODO implement setting the scores

    def _get_team_data(self, team, data, pro_schedule, week, year):
      if team not in data:
        return (0, 0, -1, [])

      team_id = data[team]['teamId']
      team_projected = -1
      if 'totalPointsLive' in data[team]:
        team_score = round(data[team]['totalPointsLive'], 2)
        team_projected = round(data[team].get('totalProjectedPointsLive', -1), 2)
      else:
        team_score = round(data[team]['totalPoints'], 2)
      team_roster = data[team].get('rosterForCurrentScoringPeriod', {}).get('entries', [])
      team_lineup = [BoxPlayer(player, pro_schedule, week, year) for player in team_roster]

      return (team_id, team_score, team_projected, team_lineup)
