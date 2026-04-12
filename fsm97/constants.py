"""Shared constants for FIFA Soccer Manager 97."""
# fmt: off

# Reference: https://github.com/jiangsheng/fsm97trainer/blob/main/FSM97Lib/PositionRatings.cs

# ── Skill columns ────────────────────────────────────────────────────────────
# 23 values per player, ordered as they appear in SM97.DAT stats block [5:28]

SKILL_COLS = [
    'move_speed', 'move_agil',  'move_accl',  'move_stam', 'move_str',
    'move_fit',   'skill_shoot','skill_pass',  'skill_head','skill_ctrl',
    'skill_drib', 'cool',       'awar',        'tack_deter','tack_skill',
    'flair',      'gk_kick',    'gk_thrw',     'gk_hand',  'thrw',
    'lead',       'cons',       'deter',
]

SKILL_LABELS = {
    'move_speed':  'Speed',
    'move_agil':   'Agility',
    'move_accl':   'Acceleration',
    'move_stam':   'Stamina',
    'move_str':    'Strength',
    'move_fit':    'Fitness',
    'skill_shoot': 'Shooting',
    'skill_pass':  'Passing',
    'skill_head':  'Heading',
    'skill_ctrl':  'Control',
    'skill_drib':  'Dribbling',
    'cool':        'Cool',
    'awar':        'Awareness',
    'tack_deter':  'Tackling Determination',
    'tack_skill':  'Tackling Skill',
    'flair':       'Flair',
    'gk_kick':     'GK Kick',
    'gk_thrw':     'GK Throw',
    'gk_hand':     'GK Handling',
    'thrw':        'Throw-in',
    'lead':        'Leadership',
    'cons':        'Consistency',
    'deter':       'Determination',
}

SKILL_GROUPS = {
    'Move':  ['move_speed', 'move_agil', 'move_accl', 'move_stam', 'move_str', 'move_fit'],
    'Skill': ['skill_shoot', 'skill_pass', 'skill_head', 'skill_ctrl', 'skill_drib'],
    'Tack':  ['tack_deter', 'tack_skill'],
    'GK':    ['gk_kick', 'gk_thrw', 'gk_hand'],
}

# ── Position weight vectors ──────────────────────────────────────────────────
# Weights per skill attribute (indexed by SKILL_COLS order) for each position.
# Formula: floor(sum(weight[i] * skill[i]) / 100)
# Sourced from PositionRatings.cs (game mod), verified against in-game values.
# Weights sum to 100 for each position.

POS_WEIGHTS = {
    #           spd  agi  acc  stam str  fit  sht  pas  hd   ctr  drib cool awar tdet tskl flair gkk  gkt  gkh  thi  lead cons deter
    'GK':  [    2,   25,   0,   0,   0,   0,   0,   2,   0,   4,   0,   7,  10,   0,   0,   0,   8,   6,  30,   0,   0,   6,   0],
    'LB':  [    3,    0,   0,   0,   0,   0,   0,   7,   8,   0,   0,   7,  15,  10,  44,   0,   0,   0,   0,   0,   0,   4,   2],
    'RB':  [    3,    0,   0,   0,   0,   0,   0,   7,   8,   0,   0,   7,  15,  10,  44,   0,   0,   0,   0,   0,   0,   4,   2],
    'CD':  [    3,    0,   0,   0,   0,   0,   0,   3,  14,   0,   0,   7,   8,  10,  50,   0,   0,   0,   0,   0,   3,   2,   0],
    'RWB': [    7,    4,  11,   0,   0,   0,   0,  12,   0,   0,  26,   0,   6,   3,  26,   5,   0,   0,   0,   0,   0,   0,   0],
    'LWB': [    7,    4,  11,   0,   0,   0,   0,  12,   0,   0,  26,   0,   6,   3,  26,   5,   0,   0,   0,   0,   0,   0,   0],
    'SW':  [   12,    0,   6,   0,   0,   0,   0,  15,   3,   0,  15,   0,  20,   3,  26,   0,   0,   0,   0,   0,   0,   0,   0],
    'DM':  [    5,    0,   0,   0,   0,   0,   0,  40,   5,   0,   0,   0,  20,   3,  27,   0,   0,   0,   0,   0,   0,   0,   0],
    'RM':  [   10,    0,   5,   0,   0,   0,   3,  42,   0,   5,   5,   0,   5,   0,  20,   5,   0,   0,   0,   0,   0,   0,   0],
    'LM':  [   10,    0,   5,   0,   0,   0,   3,  42,   0,   5,   5,   0,   5,   0,  20,   5,   0,   0,   0,   0,   0,   0,   0],
    'AM':  [   10,    0,   5,   0,   0,   0,   5,  46,   0,   5,   5,   0,   5,   0,  14,   5,   0,   0,   0,   0,   0,   0,   0],
    'RW':  [   10,    3,  10,   0,   0,   0,   3,  31,   0,   3,  27,   0,   3,   0,   3,   7,   0,   0,   0,   0,   0,   0,   0],
    'LW':  [   10,    3,  10,   0,   0,   0,   3,  31,   0,   3,  27,   0,   3,   0,   3,   7,   0,   0,   0,   0,   0,   0,   0],
    'FR':  [   12,    2,   8,   0,   0,   0,   4,  14,   1,  10,  27,   0,  12,   0,   0,  10,   0,   0,   0,   0,   0,   0,   0],
    'FOR': [   10,    2,   9,   0,   0,   0,  36,   4,  10,  10,   3,   3,   4,   0,   0,   9,   0,   0,   0,   0,   0,   0,   0],
    'SS':  [    6,    2,   6,   0,   0,   0,  29,  16,   7,  13,   6,   2,   3,   0,   0,  10,   0,   0,   0,   0,   0,   0,   0],
}

# ── Position metadata ────────────────────────────────────────────────────────
# Each tuple: (abbreviation, full name, zone, sort_order)
# Index in the list matches the position index byte in SM97.DAT (0-based)

POSITIONS = [
    ('GK',  'Goalkeeper',         'Goalkeeper',  0),
    ('RB',  'Right Back',         'Defender',    6),
    ('LB',  'Left  Back',         'Defender',    2),
    ('CD',  'Central Defence',    'Defender',    4),
    ('RWB', 'Right Wing Back',    'Defender',    5),
    ('LWB', 'Left Wing Back',     'Defender',    3),
    ('SW',  'Sweeper',            'Defender',    1),
    ('DM',  'Defensive Midfield', 'Midfielder',  7),
    ('RM',  'Right Midfield',     'Midfielder',  9),
    ('LM',  'Left Midfield',      'Midfielder',  8),
    ('AM',  'Attacking Midfield', 'Midfielder', 10),
    ('RW',  'Right Winger',       'Attacker',   13),
    ('LW',  'Left Winger',        'Attacker',   12),
    ('FR',  'Free Role',          'Attacker',   11),
    ('FOR', 'Forward',            'Attacker',   15),
    ('SS',  'Support Striker',    'Attacker',   14),
]

# 0-based index → abbreviation (matches stats[2] byte in player records)
POS_ABBR = [p[0] for p in POSITIONS]

# Display order for squad tables
POS_ORDER = ['GK', 'RB', 'LB', 'CD', 'RWB', 'LWB', 'SW',
             'DM', 'RM', 'LM', 'AM', 'RW', 'LW', 'FR', 'FOR', 'SS']

# ── League code → display name ───────────────────────────────────────────────

LEAGUE_NAMES = {
    'engprem':  'English Premier League',
    'engfirst': 'English First Division',
    'engsecnd': 'English Second Division',
    'engthird': 'English Third Division',
    'scotprem': 'Scottish Premier League',
    'scofirst': 'Scottish First Division',
    'GermanB1': 'German Bundesliga 1',
    'GermanB2': 'German Bundesliga 2',
    'FrenchS1': 'French Division 1',
    'FrenchS2': 'French Division 2',
    'ItalianA': 'Italian Serie A',
    'ItalianB': 'Italian Serie B',
    'others':   'Others',
}

# ── League grouping ──────────────────────────────────────────────────────────
# Ordered list of (country, [league display names]) for the leagues index page.

LEAGUE_GROUPS = [
    ('England', ['English Premier League', 'English First Division',
                 'English Second Division', 'English Third Division']),
    ('Scotland', ['Scottish Premier League', 'Scottish First Division']),
    ('Germany', ['German Bundesliga 1', 'German Bundesliga 2']),
    ('France',  ['French Division 1', 'French Division 2']),
    ('Italy',   ['Italian Serie A', 'Italian Serie B']),
    ('Others',  ['Others']),
]

# ── Per-team league overrides ────────────────────────────────────────────────
# Maps corrected team name → correct league (applied after TEAM_NAMES).
# Use for teams the game placed in the wrong division.
TEAM_LEAGUES = {
    'Hamilton Academical': 'Others',
    'Dumbarton':           'Others',
}

# ── Full team name mappings ──────────────────────────────────────────────────
# Maps abbreviated team names (as stored in SM97.DAT) to their full display names.

TEAM_NAMES = {
    # English clubs
    'Sheffield W':  'Sheffield Wednesday',
    'Sheffield U':  'Sheffield United',
    'Leeds':         'Leeds United',
    'Manchester U': 'Manchester United',
    'Newcastle':    'Newcastle United',
    'Blackburn':    'Blackburn Rovers',
    'Nottingham F': 'Nottingham Forest',
    'Derby':        'Derby County',
    'Nottingham C': 'Notts County',
    'Bor. Dortmund': 'Borussia Dortmund',
    'Barcelona':     'FC Barcelona',
    'Birmingham':    'Birmingham City',
    'Bradford':      'Bradford City',
    'Bristol C':     'Bristol City',
    'Bristol R':     'Bristol Rovers',
    'Bolton':        'Bolton Wanderers',
    'Brighton':      'Brighton & Hove Albion',
    'Cambridge':     'Cambridge United',
    'Cardiff':       'Cardiff City',
    'Carlisle':      'Carlisle United',
    'Charlton':      'Charlton Athletic',
    'Chester':       'Chester City',
    'Colchester':    'Colchester United',
    'Coventry':      'Coventry City',
    'Crewe':         'Crewe Alexandra',
    'Doncaster':     'Doncaster Rovers',
    'Exeter':        'Exeter City',
    'Grimsby':       'Grimsby Town',
    'Hartlepool':    'Hartlepool United',
    'Hereford':      'Hereford United',
    'Huddersfield':  'Huddersfield Town',
    'Hull':          'Hull City',
    'Ipswich':       'Ipswich Town',
    'Leicester':     'Leicester City',
    'Lincoln':       'Lincoln City',
    'Luton':         'Luton Town',
    'Manchester C':  'Manchester City',
    'Mansfield':     'Mansfield Town',
    'Northampton':   'Northampton Town',
    'Norwich':       'Norwich City',
    'Oldham':        'Oldham Athletic',
    'Orient':        'Leyton Orient',
    'Oxford':        'Oxford United',
    'Peterborough':  'Peterborough United',
    'Plymouth':      'Plymouth Argyle',
    'Preston':       'Preston North End',
    'QPR':           'Queens Park Rangers',
    'Rotherham':     'Rotherham United',
    'Rushden & D':   'Rushden & Diamonds',
    'Scunthorpe':    'Scunthorpe United',
    'Shrewsbury':    'Shrewsbury Town',
    'Southend':      'Southend United',
    'Stockport':     'Stockport County',
    'Stoke':         'Stoke City',
    'Swansea':       'Swansea City',
    'Swindon':       'Swindon Town',
    'Torquay':       'Torquay United',
    'Tottenham':     'Tottenham Hotspur',
    'Tranmere':      'Tranmere Rovers',
    'West Brom':     'West Bromwich Albion',
    'West Ham':      'West Ham United',
    'Wigan':         'Wigan Athletic',
    'Wolves':        'Wolverhampton Wanderers',
    'Wycombe':       'Wycombe Wanderers',
    'York':          'York City',
    # Scottish clubs
    'Dundee U':      'Dundee United',
    'Hearts':        'Heart of Midlothian',
    'Raith':         'Raith Rovers',
    'Dunfermline':   'Dunfermline Athletic',
    'Partick':       'Partick Thistle',
    'Airdrie':       'Airdrieonians',
    'Stirling':      'Stirling Albion',
    'Hamilton':      'Hamilton Academical',
    'Morton':        'Greenock Morton',
    # German clubs
    '1. FC K\'lautern': '1. FC Kaiserslautern',
    'Arm. Bielefeld':   'Arminia Bielefeld',
    'Bor. M\'gladbach': 'Borussia Mönchengladbach',
    'FC C. Z. Jena':    'FC Carl Zeiss Jena',
    'Fortuna D\'dorf':  'Fortuna Düsseldorf',
    'Frankfurt':        'Eintracht Frankfurt',
    'Leverkusen':       'Bayer Leverkusen',
    'Stuttgarter K.':   'Stuttgarter Kickers',
    'SV. W. Mannheim':  'SV Waldhof Mannheim',
    'Unterhaching':     'SpVgg Unterhaching',
    # French clubs
    'Chateauroux':   'Châteauroux',
    'Epinal':        'Épinal',
    'Louhans-C':     'Louhans-Cuiseaux',
    'Paris SG':      'Paris Saint-Germain',
    'St Etienne':    'Saint-Étienne',
    # Italian clubs
    'Castel Di Sangro': 'Castel di Sangro',
    'Inter':            'Internazionale',
    'Milan':            'AC Milan',
    'Verona':           'Hellas Verona',
    # Spanish clubs
    'Atl. Madrid':   'Atlético Madrid',
    'Deportivo':     'Deportivo La Coruña',
    # Eastern European clubs
    'Alania V\'kavkaz': 'Alania Vladikavkaz',
    'Din. Bucharest':   'Dinamo Bucharest',
    'Din. Minsk':       'Dinamo Minsk',
    'Din. Tibilisi':    'Dinamo Tbilisi',
    'O. Ljubljana':     'Olimpija Ljubljana',
    'Par. Belgrade':    'Partizan Belgrade',
}

# ── Stadium name corrections ─────────────────────────────────────────────────
# Fixes truncated or misspelled stadium names as stored in SM97.DAT.

STADIUM_NAMES = {
    'Westfalsenstadion':  'Westfalenstadion',
    'Bramall Lane Ground':'Bramall Lane',
    'Delle Alpi (TO)':    'Delle Alpi',
    # Shared stadiums stored with team-specific suffixes in the game data
    'Makarion (ON)':      'Makarion Stadium',
    'Makarion (APOEL)':   'Makarion Stadium',
    'Ta Qali (SW)':       'Ta Qali National Stadium',
    'Ta Qali (HIBS)':     'Ta Qali National Stadium',
    # English stadium corrections
    'Fratton Road':       'Fratton Park',
    'County Gorund':      'County Ground',
    'Saint Andrews':      "St Andrew's",
    'The Victoria Park':  'Victoria Park',
    'Oakwell Ground':     'Oakwell',
    'Dean Court Ground':  'Dean Court',
    'Layer Road Ground':  'Layer Road',
    'Belle Vue Ground':   'Belle Vue',
    'Field Mill Ground':  'Field Mill',
    'London Road Ground': 'London Road',
    'Millmoor Ground':    'Millmoor',
    'Plainmoor Ground':   'Plainmoor',
    'Molineux Ground':    'Molineux',
    'Vicarage Road Stadium': 'Vicarage Road',
    'The Cellnet Riverside Stadium': 'Riverside Stadium',
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def pos_rating(skill_row, position):
    """Return position-specific rating matching the game's Position Average display.

    Formula: floor(sum(weight[i] * skill[i]) / 100)
    Weights sourced from PositionRatings.cs (game mod), verified against known in-game values.
    """
    weights = POS_WEIGHTS.get(position, [0] * len(SKILL_COLS))
    skills = [int(skill_row.get(c, 0) or 0) for c in SKILL_COLS]
    return sum(w * s for w, s in zip(weights, skills)) // 100
