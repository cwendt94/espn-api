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
    3: "passingYards",
    4: "passingTouchdowns",

    19: "passing2PtConversions",
    20: "passingInterceptions",

    24: "rushingYards",
    25: "rushingTouchdowns",
    26: "rushing2PtConversions",

    42: "receivingYards",
    43: "receivingTouchdowns",
    44: "receiving2PtConversions",
    53: "receivingReceptions",

    72: "lostFumbles",

    74: "madeFieldGoalsFrom50Plus",
    77: "madeFieldGoalsFrom40To49",
    80: "madeFieldGoalsFromUnder40",
    85: "missedFieldGoals",
    86: "madeExtraPoints",
    88: "missedExtraPoints",

    89:"defensive0PointsAllowed",
    90: "defensive1To6PointsAllowed",
    91: "defensive7To13PointsAllowed",
    92: "defensive14To17PointsAllowed",

    93: "defensiveBlockedKickForTouchdowns",
    95: "defensiveInterceptions",
    96: "defensiveFumbles",
    97: "defensiveBlockedKicks",
    98: "defensiveSafeties",
    99: "defensiveSacks",

    101: "kickoffReturnTouchdown",
    102: "puntReturnTouchdown",
    103: "fumbleReturnTouchdown",
    104: "interceptionReturnTouchdown",

    123: "defensive28To34PointsAllowed",
    124: "defensive35To45PointsAllowed",

    129: "defensive100To199YardsAllowed",
    130: "defensive200To299YardsAllowed",
    132: "defensive350To399YardsAllowed",
    133: "defensive400To449YardsAllowed",
    134: "defensive450To499YardsAllowed",
    135: "defensive500To549YardsAllowed",
    136: "defensiveOver550YardsAllowed",

    # Punter Stats
    140: "puntsInsideThe10", # PT10
    141: "puntsInsideThe20", # PT20
    148: "puntAverage44.0+", # PTA44
    149: "puntAverage42.0-43.9", #PTA42
    150: "puntAverage40.0-41.9", #PTA40

    # Head Coach stats
    161: "25+pointsWinMargin", #WM25
    162: "20-24pointWinMargin", #WM20
    163: "15-19pointWinMargin", #WM15
    164: "10-14pointWinMargin", #WM10
    165: "5-9pointWinMargin", # WM5
    166: "1-4pointWinMargin", # WM1

    155: "TeamWin", # TW

    171: "20-24pointLossMargin", # LM20
    172: "25+pointLossMargin", # LM25
}
