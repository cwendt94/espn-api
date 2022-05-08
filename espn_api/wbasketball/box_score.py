from .box_player import BoxPlayer

class BoxScore(object):
    ''' '''
    def __init__(self, data, pro_schedule, by_matchup, year):
        self.winner = data.get('winner', 'UNDECIDED')
        self.home_team = data['home']['teamId']
        self.home_projected = -1 # week is over/not set
        roster_key = 'rosterForMatchupPeriod' if by_matchup else 'rosterForCurrentScoringPeriod'
        # TODO combine home and away logic into common function
        home_roster =  data['home'].get(roster_key, {})
        if 'totalPointsLive' in data['home'] and by_matchup:
          self.home_score = round(data['home']['totalPointsLive'], 2)
          self.home_projected = round(data['home'].get('totalProjectedPointsLive', -1), 2)
        else:
          self.home_score = round(home_roster.get('appliedStatTotal', 0), 2)
        self.home_lineup = [BoxPlayer(player, pro_schedule, year) for player in home_roster.get('entries', [])]

        # For Leagues with bye weeks
        self.away_team = 0
        self.away_score = 0
        self.away_lineup = []
        self.away_projected = -1 # week is over/not set
        if 'away' in data:
          self.away_team = data['away']['teamId']
          away_roster = data['away'].get(roster_key, {})
          if 'totalPointsLive' in data['away'] and by_matchup:
            self.away_score = round(data['away']['totalPointsLive'], 2)
            self.away_projected = round(data['away'].get('totalProjectedPointsLive', -1), 2)
          else:
            self.away_score = round(away_roster.get('appliedStatTotal', 0), 2)
          self.away_lineup = [BoxPlayer(player, pro_schedule, year) for player in away_roster.get('entries', [])]

    def __repr__(self):
        away_team = self.away_team or "BYE"
        home_team = self.home_team or "BYE"
        return f'Box Score({away_team} at {home_team})'
