class Record(object):
    
    def __init__(self, data):
        self.games_back = data['gamesBack']
        self.losses = data['losses']
        self.points_against = data['pointsAgainst']
        self.points_for = data['pointsFor']
        self.ties = data['ties']
        self.wins = data['wins']
        
    def __add__(self, otherRecord):
        data = {}
        data['gamesBack'] = self.games_back + otherRecord.games_back
        data['losses'] = self.losses + otherRecord.losses
        data['pointsAgainst'] = self.points_against + otherRecord.points_against
        data['pointsFor'] = self.points_for + otherRecord.points_for
        data['ties'] = self.ties + otherRecord.ties
        data['wins'] = self.wins + otherRecord.wins
        return Record(data)
        
    def get_standing_str(self):
        docstring = f"Wins: {self.wins} \nLosses: {self.losses} \nTies: {self.ties}"
        return docstring
