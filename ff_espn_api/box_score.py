from .box_player import BoxPlayer

class BoxScore(object):
    ''' '''
    def __init__(self, data):
        self.home_team = data['home']['teamId']
        self.home_score = data['home']['totalPoints']
        self.away_team = data['away']['teamId']
        self.away_score = data['away']['totalPoints']

        home_roster = data['home']['rosterForCurrentScoringPeriod']['entries']
        self.home_lineup = [BoxPlayer(player) for player in home_roster]
        
        away_roster = data['away']['rosterForCurrentScoringPeriod']['entries']
        self.away_lineup = [BoxPlayer(player) for player in away_roster]
