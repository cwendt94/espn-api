from .player import Player

class Team(object):
    '''Teams are part of the league'''
    def __init__(self, data, roster, member, schedule):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        self.team_name = "%s %s" % (data['location'], data['nickname'])
        self.division_id = data['divisionId']
        self.wins = data['record']['overall']['wins']
        self.losses = data['record']['overall']['losses']
        self.points_for = data['record']['overall']['pointsFor']
        self.points_against = round(data['record']['overall']['pointsAgainst'], 2)
        self.owner = "%s %s" % (member['firstName'],
                                member['lastName'])
        self.streak_length = data['record']['overall']['streakLength']
        self.streak_type = data['record']['overall']['streakType']
        self.standing = data['rankFinal']
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
        self._fetch_roster(roster)

    def __repr__(self):
        return 'Team(%s)' % (self.team_name, )
    
    def _fetch_roster(self, data):
        self.roster.clear()
        position_map = {
                      0: 'QB',
                      1: 'TQB',
                      2: 'RB',
                      3: 'RB/WR',
                      4: 'WR',
                      5: 'WR/TE',
                      6: 'TE',
                      7: 'OP',
                      8: 'DT',
                      9: 'DE',
                      10: 'LB',
                      11: 'DL',
                      12: 'CB',
                      13: 'S',
                      14: 'DB',
                      15: 'DP',
                      16: 'D/ST',
                      17: 'K',
                      18: 'P',
                      19: 'HC',
                      20: 'BE',
                      21: 'IR',
                      22: '',
                      23: 'RB/WR/TE'
                      }
        '''Fetch teams roster'''
        roster = data['entries']

        for player in roster:
            #if 'playerPoolEntry' in player:
            self.roster.append(Player(player, position_map))

    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''

        for matchup in data:
            if 'away' in matchup.keys():
                if matchup['away']['teamId'] == self.team_id:
                    score = matchup['away']['totalPoints']
                    opponentId = matchup['home']['teamId']
                    self.outcomes.append(matchup['winner'])
                    self.scores.append(score)
                    self.schedule.append(opponentId)
                elif matchup['home']['teamId'] == self.team_id:
                    score = matchup['home']['totalPoints']
                    opponentId = matchup['away']['teamId']
                    self.outcomes.append(matchup['winner'])
                    self.scores.append(score)
                    self.schedule.append(opponentId)
            elif matchup['home']['teamId'] == self.team_id:
                score = matchup['home']['totalPoints']
                opponentId = matchup['home']['teamId']
                self.outcomes.append(matchup['winner'])
                self.scores.append(score)
                self.schedule.append(opponentId)
    
    def get_player_name(self, playerId: int) -> str:
        for player in self.roster:
            if player.playerId == playerId:
                return player.name
        return ''
