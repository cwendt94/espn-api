from .player import Player
from .matchup import Matchup
from .constant import STATS_MAP

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, member, roster, schedule, year, **kwargs):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        if year < 2023:
            self.team_name = "%s %s" % (data.get('location', 'Unknown'), data.get('nickname', 'Unknown'))
        else:
            self.team_name = data.get('name', 'Unknown')
        self.division_id = data['divisionId']
        self.division_name = '' # set by caller
        self.wins = data['record']['overall']['wins']
        self.losses = data['record']['overall']['losses']
        self.ties = data['record']['overall']['ties']
        self.owner = 'None'
        self.logo_url = ''
        self.stats = None
        self.standing = data['playoffSeed']
        self.final_standing = data['rankCalculatedFinal']
        self.roster = []
        self.schedule = []
        
        if 'valuesByStat' in data:
            self.stats = {STATS_MAP[i]: j for i, j in data['valuesByStat'].items()}
        if member:
            self.owner = f"{member['firstName']} {member['lastName']}"
        if 'logo' in data:    
            self.logo_url = data['logo']
        
        self._fetch_roster(roster, year)
        self._fetch_schedule(schedule)
        
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
