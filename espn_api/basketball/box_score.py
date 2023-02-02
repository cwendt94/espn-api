from abc import ABC
from .constant import STATS_MAP

from .box_player import BoxPlayer

class BoxScore(ABC):
  ''' '''
  def __init__(self, data):
      self.winner = data.get('winner', 'UNDECIDED')
      self.home_team = data.get('home', {}).get('teamId', 0)
      self.away_team = data.get('away', {}).get('teamId', 0)

  def __repr__(self):
    away_team = self.away_team or "BYE"
    home_team = self.home_team or "BYE"
    return f'Box Score({away_team} at {home_team})'

class H2HPointsBoxScore(BoxScore):
  def __init__(self, data, pro_schedule, by_matchup, year):
    super().__init__(data)

    (self.home_score, self.home_projected, self.home_lineup) = self._get_team_data('home', data, pro_schedule, by_matchup, year)

    (self.away_score, self.away_projected, self.away_lineup) = self._get_team_data('away', data, pro_schedule, by_matchup, year)

  def _get_team_data(self, team, data, pro_schedule, by_matchup, year):
    if team not in data:
      return (0, -1, [])
    
    team_projected = -1
    roster_key = 'rosterForMatchupPeriod' if by_matchup else 'rosterForCurrentScoringPeriod'
    team_roster = data[team].get(roster_key, {})
    if 'totalPointsLive' in data[team] and by_matchup:
      team_score = round(data[team]['totalPointsLive'], 2)
      team_projected = round(data[team].get('totalProjectedPointsLive', -1), 2)
    else:
      team_score = round(team_roster.get('appliedStatTotal', 0), 2)
    lineup = get_player_lineup(data[team], pro_schedule, by_matchup, year)

    return (team_score, team_projected, lineup)

class H2HCategoryBoxScore(BoxScore):
  def __init__(self, data, pro_schedule, by_matchup, year):
    super().__init__(data)

    (self.home_wins, self.home_ties, self.home_losses, self.home_stats, self.home_lineup) = self._get_team_data('home', data, pro_schedule, by_matchup, year)

    (self.away_wins, self.away_ties, self.away_losses, self.away_stats, self.away_lineup) = self._get_team_data('away', data, pro_schedule, by_matchup, year)
  
  def _get_team_data(self, team, data, pro_schedule, by_matchup, year):
    if team not in data:
      return (0, 0, 0, {}, [])
    cumulative_score = data[team].get('cumulativeScore', {})
    team_wins = cumulative_score.get('wins', 0)
    team_ties = cumulative_score.get('ties', 0)
    team_losses = cumulative_score.get('losses', 0)

    team_stats = {}
    for stat_key, stat_dict in cumulative_score.get('scoreByStat', {}).items():
      team_stats[STATS_MAP.get(stat_key, stat_key)] = {
        'value': stat_dict['score'],
        'result': stat_dict['result']
      }

    lineup = get_player_lineup(data[team], pro_schedule, by_matchup, year)

    return (team_wins, team_ties, team_losses, team_stats, lineup)

class RotoBoxScore():
  def __init__(self, data, pro_schedule, by_matchup, year):
    self.teams = [self._get_team_data(team, pro_schedule, by_matchup, year) for team in data.get('teams', [])]
  
  def _get_team_data(self, team_data, pro_schedule, by_matchup, year):
    team = team_data.get('teamId', 0)
    cumulative_score = team_data.get('cumulativeScore', {})
    wins = cumulative_score.get('wins', 0)
    ties = cumulative_score.get('ties', 0)
    losses = cumulative_score.get('losses', 0)
    points = team.get('totalPointsLive') if 'totalPointsLive' in team else team.get('totalPoints', 0)

    stats = {}
    for stat_key, stat_dict in cumulative_score.get('scoreByStat', {}).items():
      stats[STATS_MAP.get(stat_key, stat_key)] = {
        'value': stat_dict.get('score'),
        'result': stat_dict.get('result'),
        'rank': stat_dict.get('rank')
      }
    lineup = get_player_lineup(team_data, pro_schedule, by_matchup, year)

    return { team, wins, ties, losses, points, stats, lineup  }



def get_player_lineup(team_data, pro_schedule, by_matchup, year):
  '''Helper function to get teams line up '''
  roster_key = 'rosterForMatchupPeriod' if by_matchup else 'rosterForCurrentScoringPeriod'
  roster =  team_data.get(roster_key, {})
  lineup = [BoxPlayer(player, pro_schedule, year) for player in roster.get('entries', [])]

  return lineup

# helper function to get correct box score class
ScoringType = {'H2H_POINTS': H2HPointsBoxScore, 'H2H_CATEGORY': H2HCategoryBoxScore, 'H2H_MOST_CATEGORIES': H2HCategoryBoxScore, 'ROTO': RotoBoxScore}
get_box_scoring_type_class = lambda scoring_type: ScoringType.get(scoring_type, H2HPointsBoxScore)
