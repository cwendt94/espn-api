class Matchup(object):
    '''Creates Matchup instance'''
    def __init__(self, data):
        self.matchup_type = data.get('playoffTierType', 'NONE')
        self.is_playoff = self.matchup_type != 'NONE'
        (self.home_team, self.home_score) = self._fetch_matchup_info(data, 'home')
        (self.away_team, self.away_score) = self._fetch_matchup_info(data, 'away')

    def __repr__(self):
        return f'Matchup({self.home_team}, {self.away_team})'

    def _fetch_matchup_info(self, data, team):
        '''Fetch info for matchup'''
        if team not in data:
            return (0, 0)
        team_id = data[team]['teamId']
        team_score = data[team]['totalPoints']

        return (team_id, team_score)
