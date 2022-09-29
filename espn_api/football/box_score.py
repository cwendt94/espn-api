from .box_player import BoxPlayer

class BoxScore(object):
    ''' '''
    def __init__(self, data, pro_schedule, positional_rankings, week, year):
        self.matchup_type = data.get('playoffTierType', 'NONE') 
        self.is_playoff = self.matchup_type != 'NONE'
        
        (self.home_team, self.home_score, self.home_projected, self.home_lineup) = self._get_team_data('home', data, pro_schedule, positional_rankings, week, year)
        self.home_projected = self._get_projected_score(self.home_projected, self.home_lineup)

        (self.away_team, self.away_score, self.away_projected, self.away_lineup) = self._get_team_data('away', data, pro_schedule, positional_rankings, week, year)
        self.away_projected = self._get_projected_score(self.away_projected, self.away_lineup)

    def __repr__(self):
        away_team = self.away_team or "BYE"
        home_team = self.home_team or "BYE"
        return f'Box Score({away_team} at {home_team})'
    
    def _get_projected_score(self, projected_score, lineup):
      if projected_score != -1:
        return projected_score
      projected_score = 0
      for player in lineup:
        if player.slot_position != 'BE' and player.slot_position != 'IR':
          projected_score += player.projected_points
      return projected_score
    
    def _get_team_data(self, team, data, pro_schedule, positional_rankings, week, year):
      if team not in data:
        return (0, 0, -1, [])

      team_id = data[team]['teamId']
      team_projected = -1
      if 'totalPointsLive' in data[team]:
        team_score = round(data[team]['totalPointsLive'], 2)
        team_projected = round(data[team].get('totalProjectedPointsLive', -1), 2)
      else:
        team_score = round(data[team]['rosterForCurrentScoringPeriod']['appliedStatTotal'], 2)
      team_roster = data[team]['rosterForCurrentScoringPeriod']['entries']
      team_lineup = [BoxPlayer(player, pro_schedule, positional_rankings, week, year) for player in team_roster]

      return (team_id, team_score, team_projected, team_lineup)