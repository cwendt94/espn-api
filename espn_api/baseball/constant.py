POSITION_MAP = {
    0: 'C',
    1: '1B',
    2: '2B',
    3: '3B',
    4: 'SS',
    5: 'OF',
    6: '2B/SS',
    7: '1B/3B',
    8: 'LF',
    9: 'CF', # For unknown use stat number
    10: 'RF',
    11: 'DH',
    12: 'UTIL',
    13: 'P',
    14: 'SP',
    15: 'RP',
    16: 'BE',
    17: 'IL',
    18: '18',
    19: 'IF', # 1B/2B/SS/3B
    22: '22', # Josh Fleming (2020)
    # reverse TODO
}

PRO_TEAM_MAP = {
    0: 'FA',
    1: 'Bal',
    2: 'Bos',
    3: 'LAA',
    4: 'ChW',
    5: 'Cle',
    6: 'Det',
    7: 'KC',
    8: 'Mil',
    9: 'Min',
    10: 'NYY',
    11: 'Oak',
    12: 'Sea',
    13: 'Tex',
    14: 'Tor',
    15: 'Atl',
    16: 'ChC',
    17: 'Cin',
    18: 'Hou',
    19: 'LAD',
    20: 'Wsh',
    21: 'NYM',
    22: 'Phi',
    23: 'Pit',
    24: 'StL',
    25: 'SD',
    26: 'SF',
    27: 'Col',
    28: 'Mia',
    29: 'Ari',
    30: 'TB',
}

STATS_MAP = {
    0: 'AB',WPTG baseball
    1: 'H',
    2: 'AVG',
    3: '2B',
    4: '3B',
    5: 'HR',
    6: 'XBH', # 2B + 3B + HR
    7: '1B',
    8: 'TB', # 1 * COUNT(1B) + 2 * COUNT(2B) + 3 * COUNT(3B) + 4 * COUNT(4B)
    9: 'SLG',
    10: 'BB',
    11: 'B_IBB',
    12: 'HBP',
    13: 'SF', # Sacrifice Fly
    14: 'SH', # Sacrifice Hit - i.e. Sacrifice Bunt
    15: 'SAC' # Total Sacrifices = SF + SH
    16: 'PA',
    17: 'B_OBP',
    18: 'OPS', # OBP + SLG
    19: 'RC' # Runs Created =  TB * (H + BB) / (AB + BB)
    20: 'R',
    21: 'RBI',
    # 22: '',
    23: 'SB',
    24: 'CS',
    25: 'SB-CS', # Not sure what this is called / how to abbreviate
    26: 'GDP',
    27: 'B_SO', # batter strike-outs
    28: 'PS', # pitches seen
    29: 'PPA', # pitches per plate appearance = PS / PA
    # 30: '',
    31: 'CYC',
    32: 'P_G', # pitcher Games pitched
    33: 'GS', # games started
    34: 'OUTS',
    35: 'BATTERS',
    36: 'PITCHES',
    37: 'P_H',
    38: 'BAA', # Batting average against
    39: 'P_BB',
    40: 'P_IBB', # Intentional Walks given
    41: 'WHIP',
    42: 'HBP',
    43: 'P_OBP' # On-base percentage against
    44: 'P_R',
    45: 'ER',
    46: 'P_HR',
    47: 'ERA',
    48: 'K',
    49: 'K9',
    50: 'WP',
    51: 'BALK',
    52: 'PK', # pickoff
    53: 'QS',
    54: 'L',
    55: 'WPCT', # Win Percentage
    56: 'SVO', # Save opportunity
    57: 'SV',
    58: 'BS', # Blown Save
    59: 'SV%', # Save percentage
    60: 'HD',
    # 61: '',
    62: 'CG',
    63: 'W',
    # 64: '',
    65: 'NH', # No-hitters
    66: 'PG', # Perfect Games
    67: 'TC', # Total Chances = PO + A + E
    68: 'PO', # Put Outs
    69: 'A', # Assists
    70: 'OFA', # Outfield Assists
    71 'FPCT', # Fielding Percentage
    72: 'E',
    73: 'DP', # Double plays turned
    # Not sure what to call the next four
    # 74 is games played where the player's team won
    # 75 is the same except when the team lost
    # 76 and 77 are the same except for pitchers
    74: 'B_G_W', 
    75: 'B_G_L',
    76: 'P_G_W',
    77: 'P_G_L',
    # 78: ,
    # 79: ,
    # 80: ,
    81: 'G', # Games Played
    82: 'KBB', # Strikeout to Walk Ratio
    99: 'STARTER',
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
