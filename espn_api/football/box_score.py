from .box_player import BoxPlayer

class BoxScore(object):
    ''' '''
    def __init__(self, data, pro_schedule, positional_rankings, week, year):
        self.home_team = data['home']['teamId']
        self.home_score = round(data['home']['rosterForCurrentScoringPeriod']['appliedStatTotal'], 2)
        home_roster = data['home']['rosterForCurrentScoringPeriod']['entries']
        self.home_lineup = [BoxPlayer(player, pro_schedule, positional_rankings, week, year) for player in home_roster]

        # For Leagues with bye weeks
        self.away_team = 0
        self.away_score = 0
        self.away_lineup = []
        if 'away' in data:
            self.away_team = data['away']['teamId']
            self.away_score =  round(data['away']['rosterForCurrentScoringPeriod']['appliedStatTotal'], 2)
            away_roster = data['away']['rosterForCurrentScoringPeriod']['entries']
            self.away_lineup = [BoxPlayer(player, pro_schedule, positional_rankings, week, year) for player in away_roster]

    def __repr__(self):
        away_team = self.away_team if self.away_team else "BYE"
        home_team = self.home_team if self.home_team else "BYE"
        return 'Box Score(%s at %s)' % (away_team, home_team)
