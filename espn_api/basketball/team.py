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
        self.logo_url = ''
        self.stats = None
        self.standing = data['playoffSeed']
        self.final_standing = data['rankCalculatedFinal']
        self.roster = []
        self.schedule = []
        
        if 'valuesByStat' in data:
            self.stats = {STATS_MAP.get(i, i): j for i, j in data['valuesByStat'].items()}
        if 'logo' in data:    
            self.logo_url = data['logo']
        
        self._fetch_roster(roster, year, kwargs.get('pro_schedule'))
        self._fetch_schedule(schedule)
        self.owners = kwargs.get('owners', [])
        
    def __repr__(self):
        return f'Team({self.team_name})'
    

    def _fetch_roster(self, data, year, pro_schedule = None):
        '''Fetch teams roster'''
        self.roster.clear()
        roster = data['entries']

        for player in roster:
            self.roster.append(Player(player, year, pro_schedule))


    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''
        for match in data:
            if 'away' in match.keys():
                if match.get('away', {}).get('teamId', -1) == self.team_id:
                    new_match = Matchup(match)
                    setattr(new_match, 'away_team', self)
                    self.schedule.append(new_match)
                elif match.get('home', {}).get('teamId', -1) == self.team_id:
                    new_match = Matchup(match)
                    setattr(new_match, 'home_team', self)
                    self.schedule.append(new_match)
