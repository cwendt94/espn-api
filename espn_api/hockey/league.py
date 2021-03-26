from ..base_league import BaseLeague
from .member import Member
from .team import Team
from .record import Record
from .player import Player
import pandas as pd

class League(BaseLeague):
    
    def __init__(self, league_id, year, espn_s2 = None, swid = None, username = None, password = None, testing = False, test_data = None):
        if(testing):
            self.data = test_data
        else:
            super().__init__(league_id=league_id, year=year, sport='nhl', espn_s2=espn_s2, swid=swid, username=username, password=password)
            self.data = self._fetch_league()
        member_list = []
        for member in self.data['members']:
            member_list.append(Member(member))
        self.member_list = member_list
        team_list = []
        for team in self.data['teams']:
            team_list.append(Team(team, member_list))
        self.team_list = team_list
        
    def get_league_players(self):
        player_array = []
        for team in self.team_list:
            for player in team.roster:
                player_array.append([player.full_name,player.pro_teamID, player.pro_team])
        return pd.DataFrame(data = player_array, columns = ['player_name', 'pro_teamID', 'pro_team'])
    
    def get_league_records(self):
        team_records = []
        for team in self.team_list:
            team_records.append([team.get_owner_name(), 'Away', team.away.wins, team.away.losses, team.away.ties])
            team_records.append([team.get_owner_name(), 'Home', team.home.wins, team.home.losses, team.home.ties])
            team_records.append([team.get_owner_name(), 'Division', team.division.wins, team.division.losses, team.division.ties])
            team_records.append([team.get_owner_name(), 'Overall', team.overall.wins, team.overall.losses, team.overall.ties])
        return pd.DataFrame(data = team_records, columns = ['team_owner', 'record_type', 'wins', 'losses', 'ties'])
    
    def get_standings(self):
        standings = list(map(lambda team: [team.get_owner_name(), team.overall.wins, team.overall.losses, team.overall.ties], self.team_list))
        #return standings
        return pd.DataFrame(data = standings, columns = ['team_owner', 'wins', 'losses', 'ties']).sort_values(by = ['wins', 'ties'], ascending = [False,False]).reset_index(drop = True)
      
    def get_team_by_owner_name(self, owner_name):
        for team in self.team_list:
            if(team.get_owner_name() == owner_name):
                return team
        print(f'No Team Found with {owner_name} as owner')
        
    def get_league_player_stats(self):
        des_columns = ['Owner_Name','Player_Name','statSourceId', 'seasonID', 'proTeamID', 'scoringPeriodID',
       'statSplitTypeID', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
        '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
         '36', '37', '38', '39', '99']

        df = pd.DataFrame(columns = des_columns)

        for team in self.team_list:
            for player in team.roster:
                #columns.append(list(player.stats.columns))
                stats = player.stats.copy()
                stats['Owner_Name'] = team.get_owner_name()
                stats['Player_Name'] = player.full_name
                #stats.columns = des_columns
                df =  df.append(stats)
        return df.reindex(columns = des_columns)
        
        
