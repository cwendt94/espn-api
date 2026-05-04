# Maps defaultPositionId (a player's natural position) to a position string.
# This is a DIFFERENT numbering system from lineupSlotId (see POSITION_MAP).
DEFAULT_POSITION_MAP = {
    1: 'SP',
    2: 'C',
    3: '1B',
    4: '2B',
    5: '3B',
    6: 'SS',
    7: 'LF',
    8: 'CF',
    9: 'RF',
    10: 'DH',
    11: 'RP',
}

# Maps lineupSlotId (where a player sits in the lineup) to a slot string.
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
    9: 'CF',
    10: 'RF',
    11: 'DH',
    12: 'UTIL',
    13: 'P',
    14: 'SP',
    15: 'RP',
    16: 'BE',
    17: 'IL',
    19: 'IF', # 1B/2B/SS/3B
    # 18, 21, 22 have appeared but unknown what position they correspond to
    # reverse mapping — used by free_agents() to translate position name → slot ID filter
    'C': 0,
    '1B': 1,
    '2B': 2,
    '3B': 3,
    'SS': 4,
    'OF': 5,
    '2B/SS': 6,
    '1B/3B': 7,
    'LF': 8,
    'CF': 9,
    'RF': 10,
    'DH': 11,
    'UTIL': 12,
    'P': 13,
    'SP': 14,
    'RP': 15,
    'BE': 16,
    'IL': 17,
    'IF': 19,
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

# where batter and pitcher stats have the same abbreviation and both are commonly used
# B_ = batter stat
# P_ = pitcher stat

STATS_MAP = {
    0: 'AB',
    1: 'H',
    2: 'AVG',
    3: '2B',
    4: '3B',
    5: 'HR',
    6: 'XBH', # 2B + 3B + HR
    7: '1B',
    8: 'TB', # 1 * COUNT(1B) + 2 * COUNT(2B) + 3 * COUNT(3B) + 4 * COUNT(HR)
    9: 'SLG',
    10: 'B_BB',
    11: 'B_IBB',
    12: 'HBP',
    13: 'SF', # Sacrifice Fly
    14: 'SH', # Sacrifice Hit - i.e. Sacrifice Bunt
    15: 'SAC', # total sacrifices = SF + SH
    16: 'PA',
    17: 'OBP',
    18: 'OPS', # OBP + SLG
    19: 'RC', # Runs Created = TB * (H + BB) / (AB + BB)
    20: 'R',
    21: 'RBI',
    # 22: '',
    23: 'SB',
    24: 'CS',
    25: 'SB-CS', # net steals
    26: 'GDP',
    27: 'B_SO', # batter strike-outs
    28: 'PS', # pitches seen
    29: 'PPA', # pitches per plate appearance = PS / PA
    # 30: '',
    31: 'CYC',
    32: 'GP', # pitcher games pitched
    33: 'GS', # games started
    34: 'OUTS',  # divide by 3 for IP
    35: 'TBF',
    36: 'P',  # pitches
    37: 'P_H',
    38: 'OBA', # Opponent Batting Average
    39: 'P_BB',
    40: 'P_IBB', # intentional walks allowed
    41: 'WHIP',
    42: 'HBP',
    43: 'OOBP', # Opponent On-Base Percentage
    44: 'P_R',
    45: 'ER',
    46: 'P_HR',
    47: 'ERA',
    48: 'K',
    49: 'K/9',
    50: 'WP',
    51: 'BLK',
    52: 'PK', # pickoff
    53: 'W',
    54: 'L',
    55: 'WPCT', # Win Percentage
    56: 'SVO', # Save opportunity
    57: 'SV',
    58: 'BLSV', # BLown SaVe
    59: 'SV%', # Save percentage
    60: 'HLD',
    # 61: '',
    62: 'CG',
    63: 'QS', # Quality Starts
    # 64: '',
    65: 'NH', # No-hitters
    66: 'PG', # Perfect Games
    67: 'TC', # Total Chances = PO + A + E
    68: 'PO', # Put Outs
    69: 'A', # Assists
    70: 'OFA', # Outfield Assists
    71: 'FPCT', # Fielding Percentage
    72: 'E',
    73: 'DP', # Double plays turned
    # Not sure what to call the next four
    # 74 is games played where the batter's team won
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
    82: 'K/BB', # Strikeout to Walk Ratio
    83: 'SVHD', # Saves + Holds
    99: 'STARTER',
}

STAT_SPLIT_MAP = {
    0: 'season',
    1: 'last_7',
    2: 'last_15',
    3: 'last_30',
    5: 'box_score',
}

# Stat IDs that apply only to pitchers
PITCHER_ONLY_STATS = {
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 62, 63, 65, 66, 76, 77, 82, 83
}

# Stat IDs that apply only to batters (excludes shared fielding stats and games played)
BATTER_ONLY_STATS = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    23, 24, 25, 26, 27, 28, 29, 31, 74, 75
}

# Eligibility-slot names used to classify a player as a pitcher or batter
# when filtering stats by role (e.g. dropping batter-only stats from a pitcher).
PITCHER_POSITIONS = {'SP', 'RP', 'P'}
BATTER_POSITIONS = {'C', '1B', '2B', '3B', 'SS', 'OF', 'LF', 'CF', 'RF', 'DH', 'UTIL', '2B/SS', '1B/3B'}

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

TRANSACTION_TYPES = {
    'DRAFT', 'TRADE_ACCEPT', 'WAIVER', 'TRADE_VETO', 'FUTURE_ROSTER',
    'ROSTER', 'RETRO_ROSTER', 'TRADE_PROPOSAL', 'TRADE_UPHOLD',
    'FREEAGENT', 'TRADE_DECLINE', 'WAIVER_ERROR', 'TRADE_ERROR'
}
