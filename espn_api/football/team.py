from .player import Player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, roster, schedule, year, **kwargs):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        self.team_name = data.get('name', 'Unknown')
        if self.team_name == 'Unknown':
            self.team_name = "%s %s" % (data.get('location', 'Unknown'), data.get('nickname', 'Unknown'))
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
        self.owners = kwargs.get('owners', [])

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
            home_team = matchup.get('home', {})
            away_team = matchup.get('away', {})
            home_id = home_team.get('teamId', -1)
            away_id = away_team.get('teamId', -1)

            if self.team_id in (home_id, away_id):
                # find if current team is home or away
                (current_team, opponent_id, away) = (home_team, away_id, False) if home_id == self.team_id else (away_team, home_id, True)
                # if bye week set opponent id to self
                if opponent_id == -1: opponent_id = self.team_id

                score = current_team.get('totalPoints')
                self.outcomes.append(self._get_winner(matchup['winner'], away))
                self.scores.append(score)
                self.schedule.append(opponent_id)
    
    def _get_winner(self, winner: str, is_away: bool) -> str:
        if winner == 'UNDECIDED':
            return 'U'
        elif winner == 'TIE':
            return 'T'
        elif (is_away and winner == 'AWAY') or (not is_away and winner == 'HOME'):
            return 'W'
        else:
            return 'L'

    def get_player_name(self, playerId: int) -> str:
        for player in self.roster:
            if player.playerId == playerId:
                return player.name
        return ''
