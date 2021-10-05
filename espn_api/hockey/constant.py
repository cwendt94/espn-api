#Constants
POSITION_MAP = {
    # Remaining: F, IR, Util
    0 : '0' # IR?
    , 1 : 'Center'
    , 2 : 'Left Wing'
    , 3 : 'Right Wing'
    , 4 : 'Defense'
    , 5 : 'Goalie'
    , 6 : '6' # Forward ?
    , 7 : '7' # Goalie, F (Goalie Bench?)
    , 8 : '8' # Goalie, F
    , 'Center': 1
    , 'Left Wing' : 2
    , 'Right Wing' : 3
    , 'Defense' : 4
    , 'Goalie' : 5
}

STATS_IDENTIFIER = {
    '00': 'Total',
    '01': 'Last 7',
    '02': 'Last 15',
    '03': 'Last 30',
    '10': 'Projected',
    '20': '20'
}

PRO_TEAM_MAP = {
       1: 'Boston Bruins'
    ,  2: 'Buffalo Sabres'
    ,  3: 'Calgary Flames'
    ,  4: 'Chicago Blackhawks'
    ,  5: 'Detroit Red Wings'
    ,  6: 'Edmonton Oilers'
    ,  7: 'Carolina Hurricanes'
    ,  8: 'Los Angeles Kings'
    ,  9: 'Dallas Stars'
    , 10: 'Montréal Canadiens'
    , 11: 'New Jersey Devils'
    , 12: 'New York Islanders'
    , 13: 'New York Rangers'
    , 14: 'Ottawa Senators'
    , 15: 'Philadelphia Flyers'
    , 16: 'Pittsburgh Penguins'
    , 17: 'Colorado Avalanche'
    , 18: 'San Jose Sharks'
    , 19: 'St. Louis Blues'
    , 20: 'Tampa Bay Lightning'
    , 21: 'Toronto Maple Leafs'
    , 22: 'Vancouver Canucks'
    , 23: 'Washington Capitals'
    , 24: 'Arizona Coyotes'
    , 25: 'Anaheim Ducks'
    , 26: 'Florida Panthers'
    , 27: 'Nashville Predators'
    , 28: 'Winnipeg Jets'
    , 29: 'Columbus Blue Jackets'
    , 30: 'Minnesota Wild'
    , 37: 'Vegas Golden Knights'
    , 124292: 'Seattle Kraken'
}

STATS_MAP = {
    '0': 'GS',
    '1': 'W',
    '2': 'L',
    '3': 'SA',
    '4': 'GA',
    '5': '5',
    '6': 'SV',
    '7': 'SO',
    '8': 'MIN ?',
    '9': 'OTL',
    '10': 'GAA',
    '11': 'SV%',
    '12': '12',
    '13': 'G',
    '14': 'A',
    '15': '+/-',
    '16': '16',
    '17': 'PIM',
    '18': 'PPG',
    '19': '19',
    '20': 'SHG',
    '21': 'SHA',
    '22': 'GWG',
    '23': 'FOW',
    '24': 'FOL',
    '25': '25',
    '26': 'TTOI ?',
    '27': 'ATOI',
    '28': 'HAT',
    '29': 'SOG',
    '30': '30',
    '31': 'HIT',
    '32': 'BLK',
    '33': 'DEF',
    '34': 'GP',
    '35': '35',
    '36': '36',
    '37': '37',
    '38': 'PPP',
    '39': 'SHP',
    '40': '40',
    '41': '41',
    '42': '42',
    '43': '43',
    '44': '44',
    '45': '45',
    '99': '99'
    }

ACTIVITY_MAP = {
    178: 'FA ADDED',
    180: 'WAIVER ADDED',
    179: 'DROPPED',
    181: 'DROPPED',
    239: 'DROPPED',
    244: 'TRADED',
    'FA': 178,
    'WAIVER': 180,
    'TRADED': 244
}
