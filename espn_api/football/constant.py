POSITION_MAP = {
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
    23: 'RB/WR/TE',
    24: 'ER',
    25: 'Rookie',
    'QB': 0,
    'RB': 2,
    'WR': 4,
    'TE': 6,
    'D/ST': 16,
    'K': 17,
    'FLEX': 23,
    'DT': 8,
    'DE': 9,
    'LB': 10,
    'DL': 11,
    'CB': 12,
    'S': 13,
    'DB': 14,
    'DP': 15,
    'HC': 19
}

PRO_TEAM_MAP = {
    0 : 'None',
    1 : 'ATL',
    2 : 'BUF',
    3 : 'CHI',
    4 : 'CIN',
    5 : 'CLE',
    6 : 'DAL',
    7 : 'DEN',
    8 : 'DET',
    9 : 'GB',
    10: 'TEN',
    11: 'IND',
    12: 'KC',
    13: 'OAK',
    14: 'LAR',
    15: 'MIA',
    16: 'MIN',
    17: 'NE',
    18: 'NO',
    19: 'NYG',
    20: 'NYJ',
    21: 'PHI',
    22: 'ARI',
    23: 'PIT',
    24: 'LAC',
    25: 'SF',
    26: 'SEA',
    27: 'TB',
    28: 'WSH',
    29: 'CAR',
    30: 'JAX',
    33: 'BAL',
    34: 'HOU'
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

PLAYER_STATS_MAP = {
    # Passing Stats
    0: "passingAttempts", # PA
    1: "passingCompletions", # PC
    2: "passingIncompletions", # INC
    3: "passingYards", # PY
    4: "passingTouchdowns", # PTD
    # 5-14 appear for passing players
    # 5-7: 6 is half of 5 (integer divide by 2), 7 is half of 6 (integer divide by 2)
    # 8-10: 9 is half of 8 (integer divide by 2), 10 is half of 9 (integer divide by 2)
    # 11-12: 12 is half of 11 (integer divide by 2)
    # 13-14: 14 is half of 13 (integer divide by 2)
    15: "passing40PlusYardTD", # PTD40
    16: "passing50PlusYardTD", # PTD50
    17: "passing300To399YardGame", # P300
    18: "passing400PlusYardGame", # P400
    19: "passing2PtConversions", # 2PC
    20: "passingInterceptions", # INT
    21: "passingCompletionPercentage",
    22: "passingYards", # PY - TODO: figure out what the difference is between 22 and 3

    # Rushing Stats
    23: "rushingAttempts", # RA
    24: "rushingYards", # RY
    25: "rushingTouchdowns", # RTD
    26: "rushing2PtConversions", # 2PR
    # 27-34 appear for rushing players
    # 27-29: 28 is half of 27 (integer divide by 2), 29 is half of 28 (integer divide by 2)
    # 30-32: 31 is half of 30 (integer divide by 2), 32 is half of 31 (integer divide by 2)
    # 33-34: 34 is half of 33 (integer divide by 2)
    35: "rushing40PlusYardTD", # RTD40
    36: "rushing50PlusYardTD", # RTD50
    37: "rushing100To199YardGame", # RY100
    38: "rushing200PlusYardGame", # RY200
    39: "rushingYardsPerAttempt",
    40: "rushingYards", # RY - TODO: figure out what the difference is between 40 and 24

    # Receiving Stats
    41: "receivingReceptions", # REC
    42: "receivingYards", # REY
    43: "receivingTouchdowns", # RETD
    44: "receiving2PtConversions", # 2PRE
    45: "receiving40PlusYardTD", # RETD40
    46: "receiving50PlusYardTD", # RETD50
    # 47-52 appear for receiving players
    # 47-49: 48 is half of 47 (integer divide by 2), 49 is half of 48 (integer divide by 2)
    # 50-52: 51 is half of 50 (integer divide by 2), 52 is half of 51 (integer divide by 2)
    53: "receivingReceptions", # REC - TODO: figure out what the difference is between 53 and 41
    # 54-55 appear for receiving players
    # 54-55: 55 is half of 54 (integer divide by 2)
    56: "receiving100To199YardGame", # REY100
    57: "receiving200PlusYardGame", # REY200
    58: "receivingTargets", # RET
    59: "receivingYardsAfterCatch",
    60: "receivingYardsPerReception",
    61: "receivingYards", # REY - TODO: figure out what the difference is between 61 and 42
    62: "2PtConversions",
    63: "fumbleRecoveredForTD", # FTD
    64: "passingTimesSacked", # SK

    68: "fumbles", # FUM

    72: "lostFumbles", # FUML
    73: "turnovers",

    # Kicking Stats
    74: "madeFieldGoalsFrom50Plus", # FG50 (does not map directly to FG50 as FG50 does not include 60+)
    75: "attemptedFieldGoalsFrom50Plus", # FGA50 (does not map directly to FGA50 as FG50 does not include 60+)
    76: "missedFieldGoalsFrom50Plus", # FGM50 (does not map directly to FGM50 as FG50 does not include 60+)
    77: "madeFieldGoalsFrom40To49", # FG40
    78: "attemptedFieldGoalsFrom40To49", # FGA40
    79: "missedFieldGoalsFrom40To49", # FGM40
    80: "madeFieldGoalsFromUnder40", # FG0
    81: "attemptedFieldGoalsFromUnder40", # FGA0
    82: "missedFieldGoalsFromUnder40", # FGM0
    83: "madeFieldGoals", # FG
    84: "attemptedFieldGoals", # FGA
    85: "missedFieldGoals", # FGM
    86: "madeExtraPoints", # PAT
    87: "attemptedExtraPoints", # PATA
    88: "missedExtraPoints", # PATM

    # Defensive Stats
    89: "defensive0PointsAllowed", # PA0
    90: "defensive1To6PointsAllowed", # PA1
    91: "defensive7To13PointsAllowed", # PA7
    92: "defensive14To17PointsAllowed", # PA14
    93: "defensiveBlockedKickForTouchdowns", # BLKKRTD
    94: "defensiveTouchdowns", # Does not include defensive blocked kick for touchdowns (BLKKRTD)
    95: "defensiveInterceptions", # INT
    96: "defensiveFumbles", # FR
    97: "defensiveBlockedKicks", # BLKK
    98: "defensiveSafeties", # SF
    99: "defensiveSacks", # SK
    # 100: This appears to be defensiveSacks * 2
    101: "kickoffReturnTouchdowns", # KRTD
    102: "puntReturnTouchdowns", # PRTD
    103: "interceptionReturnTouchdowns", # INTTD
    104: "fumbleReturnTouchdowns", # FRTD
    105: "defensivePlusSpecialTeamsTouchdowns", # Includes defensive blocked kick for touchdowns (BLKKRTD) and kickoff/punt return touchdowns
    106: "defensiveForcedFumbles", # FF
    107: "defensiveAssistedTackles", # TKA
    108: "defensiveSoloTackles", # TKS
    109: "defensiveTotalTackles", # TK

    113: "defensivePassesDefensed", # PD
    114: "kickoffReturnYards", # KR
    115: "puntReturnYards", # PR

    118: "puntsReturned", # PTR

    120: "defensivePointsAllowed", # PA
    121: "defensive18To21PointsAllowed", # PA18
    122: "defensive22To27PointsAllowed", # PA22
    123: "defensive28To34PointsAllowed", # PA28
    124: "defensive35To45PointsAllowed", # PA35
    125: "defensive45PlusPointsAllowed", # PA46

    127: "defensiveYardsAllowed", # YA
    128: "defensiveLessThan100YardsAllowed", #YA100
    129: "defensive100To199YardsAllowed", # YA199
    130: "defensive200To299YardsAllowed", # YA299
    131: "defensive300To349YardsAllowed", # YA349
    132: "defensive350To399YardsAllowed", # YA399
    133: "defensive400To449YardsAllowed", # YA449
    134: "defensive450To499YardsAllowed", # YA499
    135: "defensive500To549YardsAllowed", # YA549
    136: "defensive550PlusYardsAllowed", # YA550

    # Punter Stats
    138: "netPunts", # PT
    139: "puntYards", # PTY
    140: "puntsInsideThe10", # PT10
    141: "puntsInsideThe20", # PT20
    142: "blockedPunts", # PTB
    145: "puntTouchbacks", # PTTB
    146: "puntFairCatches", #PTFC
    147: "puntAverage",
    148: "puntAverage44.0+", # PTA44
    149: "puntAverage42.0-43.9", #PTA42
    150: "puntAverage40.0-41.9", #PTA40
    151: "puntAverage38.0-39.9", #PTA38
    152: "puntAverage36.0-37.9", #PTA36
    153: "puntAverage34.0-35.9", #PTA34
    154: "puntAverage33.9AndUnder", #PTA33

    # Head Coach Stats
    155: "teamWin", # TW
    156: "teamLoss", # TL
    157: "teamTie", # TIE
    158: "pointsScored", # PTS

    160: "pointsMargin",
    161: "25+pointWinMargin", # WM25
    162: "20-24pointWinMargin", # WM20
    163: "15-19pointWinMargin", # WM15
    164: "10-14pointWinMargin", # WM10
    165: "5-9pointWinMargin", # WM5
    166: "1-4pointWinMargin", # WM1
    167: "1-4pointLossMargin", # LM1
    168: "5-9pointLossMargin", # LM5
    169: "10-14pointLossMargin", # LM10
    170: "15-19pointLossMargin", # LM15
    171: "20-24pointLossMargin", # LM20
    172: "25+pointLossMargin", # LM25
    174: "winPercentage", # Value goes from 0-1

    187: "defensivePointsAllowed", # TODO: figure out what the difference is between 187 and 120

    201: "madeFieldGoalsFrom60Plus", # FG60
    202: "attemptedFieldGoalsFrom60Plus", # FGA60
    203: "missedFieldGoalsFrom60Plus", # FGM60

    205: "defensive2PtReturns", # 2PTRET
    206: "defensive2PtReturns", # 2PTRET - TODO: figure out what the difference is between 206 and 205
}
