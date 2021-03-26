import pandas as pd
from .constants import position_dict
from .constants import team_dict

class Player(object):
    
    def __init__(self, data):
        self.full_name = data['playerPoolEntry']['player']['fullName']
        self.status = data['playerPoolEntry']['status']
        self.playerID = data['playerId']
        self.acquisition_type = data['acquisitionType']
        self.injury_status = data['injuryStatus']
        self.line_up_slotID = data['lineupSlotId']
        self.line_up_lock_status = data['playerPoolEntry']['lineupLocked']
        self.on_teamID = data['playerPoolEntry']['onTeamId']
        self.trade_locked = data['playerPoolEntry']['tradeLocked']
        self.positionID = data['playerPoolEntry']['player']['defaultPositionId']
        self.position = ''
        if(position_dict[self.positionID] != None):
            self.position = position_dict[self.positionID]
        else:
            self.position = 'Unkown'
        ratings = {}
        for key in data['playerPoolEntry']['ratings'].keys():
            r = data['playerPoolEntry']['ratings'][key]
            if(not(r['positionalRanking'] == r['statCategoryRanking'] == r['totalRanking'] == r['totalRating'] == 0)):
                ratings[key] = r
        self.ratings = pd.DataFrame(ratings)
        self.pro_teamID = data['playerPoolEntry']['player']['proTeamId']
        self.pro_team = ''
        if(team_dict[self.pro_teamID] != None):
            self.pro_team = team_dict[self.pro_teamID]
        else:
            self.pro_team = 'Unkown'
        initial_stats = list(filter(lambda x: x['stats'] != {}, data['playerPoolEntry']['player']['stats']))
        stat_dict = []
        for stat in initial_stats:
            #innerDict['externalId'] = entry['playerPoolEntry']['player']['externalId']
            #['statSourceId']
            innerDict = {}
            innerDict['statSourceId'] = stat['statSourceId']
            innerDict['seasonID'] = stat['seasonId']
            innerDict['proTeamID'] = stat['proTeamId']
            innerDict['scoringPeriodID'] = stat['scoringPeriodId']
            innerDict['statSplitTypeID'] = stat['statSplitTypeId']
            #innerDict.append(stat['stats'], ignore_index=True)
            innerDict.update(stat['stats'])
            stat_dict.append(innerDict)
        self.stats = pd.DataFrame(stat_dict)
        
        
