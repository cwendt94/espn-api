from .player import Player
from .matchup import Matchup
from .constant import STATS_MAP

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
        self.points_against = data['record']['overall']['pointsAgainst']
        self.streak_length = data['record']['overall']['streakLength']
        self.streak_type = data['record']['overall']['streakType']
        self.home_wins = data['record']['home']['wins']
        self.home_losses = data['record']['home']['losses']
        self.home_ties = data['record']['home']['ties']
        self.away_wins = data['record']['away']['wins']
        self.away_losses = data['record']['away']['losses']
        self.away_ties = data['record']['away']['ties']
        self.division_wins = data['record']['division']['wins']
        self.division_losses = data['record']['division']['losses']
        self.division_ties = data['record']['division']['ties']
        self.current_projected_rank = data.get('currentProjectedRank')
        self.waiver_rank = data.get('waiverRank')
        self.points = data.get('points', 0)
        self.logo_url = ''
        self.standing = data['playoffSeed']
        self.final_standing = data.get('rankFinal') or data.get('rankCalculatedFinal')
        self.roster = []
        self.schedule = []
        if 'logo' in data:    
            self.logo_url = data['logo']
        
        self._fetch_roster(roster, year)
        self._fetch_schedule(schedule)
        self.owners = kwargs.get('owners', [])
        
    def __repr__(self):
        return f'Team({self.team_name})'
    

    def _fetch_roster(self, data, year):
        '''Fetch teams roster'''
        self.roster.clear()
        roster = data['entries']

        for player in roster:
            self.roster.append(Player(player, year))


    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''
        for match in data:
            if 'away' in match.keys():
                if match['away']['teamId'] == self.team_id:
                    new_match = Matchup(match)
                    setattr(new_match, 'away_team', self)
                    self.schedule.append(new_match)
                elif match['home']['teamId'] == self.team_id:
                    new_match = Matchup(match)
                    setattr(new_match, 'home_team', self)
                    self.schedule.append(new_match)
