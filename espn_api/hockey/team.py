from .member import Member
from .record import Record
from .player import Player
import pandas as pd

class Team(object):
    
    def __init__(self, data, members_list):
        self.team_id = data['id']
        self.team_abbrev = data['abbrev']
        self.team_name = data['location'] + data['nickname']
        self.primary_owner = ''
        for mem in members_list:
            if(mem.id == data['primaryOwner']):
                self.primary_owner = mem
                break
        self.away = Record(data['record']['away'])
        self.home = Record(data['record']['home'])
        self.division = Record(data['record']['division'])
        self.overall = Record(data['record']['overall'])
        self.roster = []
        for player in data['roster']['entries']:
            self.roster.append(Player(player))
            
    def get_owner_name(self):
        return self.primary_owner.full_name
    
    def get_basic_roster_information(self):
        roster_data = list(map(lambda player: [player.full_name, player.pro_team, player.position, player.injury_status], self.roster))
        return pd.DataFrame(data = roster_data, columns = ['Player', 'NHL Team', 'Position', 'Injury Status'])
