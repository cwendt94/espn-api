from .player import Player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, member, roster):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        self.team_name = "%s %s" % (data['location'], data['nickname'])
        self.division_id = data['divisionId']
        self.wins = data['record']['overall']['wins']
        self.losses = data['record']['overall']['losses']
        self.owner = 'None'
        if member:
            self.owner = "%s %s" % (member['firstName'],
                                    member['lastName'])
        if 'logo' in data:    
            self.logo_url = data['logo']
        else:
            self.logo_url = ''
        self.roster = []
        self.schedule = []
        self.scores = []
        self.outcomes = []
        self.mov = []
        self._fetch_roster(roster)

    def __repr__(self):
        return 'Team(%s)' % (self.team_name, )
    

    def _fetch_roster(self, data):
        '''Fetch teams roster'''
        self.roster.clear()
        roster = data['entries']

        for player in roster:
            self.roster.append(Player(player))

