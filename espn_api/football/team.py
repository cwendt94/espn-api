from .player import Player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, roster, member, schedule, year, **kwargs):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        self.team_name = "%s %s" % (data['location'], data['nickname'])
        self.division_id = data['divisionId']
        self.division_name = '' # set by caller
        self.wins = data['record']['overall']['wins']
        self.losses = data['record']['overall']['losses']
        self.ties = data['record']['overall']['ties']
        self.points_for = data['record']['overall']['pointsFor']
        self.points_against = round(data['record']['overall']['pointsAgainst'], 2)
        self.acquisitions = data.get('transactionCounter', {}).get('acquisitions', 0)
        self.acquisition_budget_spent = data.get('transactionCounter', {}).get('acquisitionBudgetSpent', 0)
        self.drops = data.get('transactionCounter', {}).get('drops', 0)
        self.trades = data.get('transactionCounter', {}).get('trades', 0)
        self.playoff_pct = data.get('currentSimulationResults', {}).get('playoffPct', 0) * 100
        self.draft_projected_rank = data.get('draftDayProjectedRank', 0)
        self.owner = 'None'
        if member:
            self.owner = "%s %s" % (member['firstName'],
                                    member['lastName'])
        self.streak_length = data['record']['overall']['streakLength']
        self.streak_type = data['record']['overall']['streakType']
        self.standing = data['playoffSeed']
        self.final_standing = data['rankCalculatedFinal']
        if 'logo' in data:    
            self.logo_url = data['logo']
        else:
            self.logo_url = ''
        self.roster = []
        self.schedule = []
        self.scores = []
        self.outcomes = []
        self.mov = []
        self._fetch_schedule(schedule)
        self._fetch_roster(roster, year)

    def __repr__(self):
        return 'Team(%s)' % (self.team_name, )
    
    def _fetch_roster(self, data, year):
        '''Fetch teams roster'''
        self.roster.clear()
        roster = data.get('entries', [])

        for player in roster:
            self.roster.append(Player(player, year))

    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''

        for matchup in data:
            if 'away' in matchup.keys():
                if matchup['away']['teamId'] == self.team_id:
                    score = matchup['away']['totalPoints']
                    opponentId = matchup['home']['teamId']
                    self.outcomes.append(self._get_winner(matchup['winner'], True))
                    self.scores.append(score)
                    self.schedule.append(opponentId)
                elif matchup['home']['teamId'] == self.team_id:
                    score = matchup['home']['totalPoints']
                    opponentId = matchup['away']['teamId']
                    self.outcomes.append(self._get_winner(matchup['winner'], False))
                    self.scores.append(score)
                    self.schedule.append(opponentId)
            elif matchup['home']['teamId'] == self.team_id:
                score = matchup['home']['totalPoints']
                opponentId = matchup['home']['teamId']
                self.outcomes.append(self._get_winner(matchup['winner'], False))
                self.scores.append(score)
                self.schedule.append(opponentId)
    
    def _get_winner(self, winner: str, is_away: bool) -> str:
        if winner == 'UNDECIDED':
            return 'U'
        elif (is_away and winner == 'AWAY') or (not is_away and winner == 'HOME'):
            return 'W'
        else:
            return 'L'

    def get_player_name(self, playerId: int) -> str:
        for player in self.roster:
            if player.playerId == playerId:
                return player.name
        return ''
