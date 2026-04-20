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
    'lead',       'cons',       'deter',       'greed',
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
    'greed':       'Greed',
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
    'Birmingham':    'Birmingham City',
    'Blackburn':     'Blackburn Rovers',
    'Bolton':        'Bolton Wanderers',
    'Bradford':      'Bradford City',
    'Brighton':      'Brighton & Hove Albion',
    'Bristol C':     'Bristol City',
    'Bristol R':     'Bristol Rovers',
    'Cambridge':     'Cambridge United',
    'Cardiff':       'Cardiff City',
    'Carlisle':      'Carlisle United',
    'Charlton':      'Charlton Athletic',
    'Chester':       'Chester City',
    'Colchester':    'Colchester United',
    'Coventry':      'Coventry City',
    'Crewe':         'Crewe Alexandra',
    'Derby':         'Derby County',
    'Doncaster':     'Doncaster Rovers',
    'Exeter':        'Exeter City',
    'Grimsby':       'Grimsby Town',
    'Hartlepool':    'Hartlepool United',
    'Hereford':      'Hereford United',
    'Huddersfield':  'Huddersfield Town',
    'Hull':          'Hull City',
    'Ipswich':       'Ipswich Town',
    'Leeds':         'Leeds United',
    'Leicester':     'Leicester City',
    'Lincoln':       'Lincoln City',
    'Luton':         'Luton Town',
    'Manchester C':  'Manchester City',
    'Manchester U':  'Manchester United',
    'Mansfield':     'Mansfield Town',
    'Newcastle':     'Newcastle United',
    'Northampton':   'Northampton Town',
    'Norwich':       'Norwich City',
    'Nottingham C':  'Notts County',
    'Nottingham F':  'Nottingham Forest',
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
    'Sheffield U':   'Sheffield United',
    'Sheffield W':   'Sheffield Wednesday',
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
    'Airdrie':       'Airdrieonians',
    'Dundee U':      'Dundee United',
    'Dunfermline':   'Dunfermline Athletic',
    'Hamilton':      'Hamilton Academical',
    'Hearts':        'Heart of Midlothian',
    'Morton':        'Greenock Morton',
    'Partick':       'Partick Thistle',
    'Raith':         'Raith Rovers',
    'Stirling':      'Stirling Albion',
    # German clubs
    '1. FC K\'lautern': '1. FC Kaiserslautern',
    'Arm. Bielefeld':   'Arminia Bielefeld',
    'Bor. Dortmund': 'Borussia Dortmund',
    'Bor. M\'gladbach': 'Borussia Mönchengladbach',
    'FC C. Z. Jena':    'FC Carl Zeiss Jena',
    'Fortuna D\'dorf':  'Fortuna Düsseldorf',
    'Frankfurt':        'Eintracht Frankfurt',
    'Leverkusen':       'Bayer Leverkusen',
    'SV. W. Mannheim':  'SV Waldhof Mannheim',
    'Stuttgarter K.':   'Stuttgarter Kickers',
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
    'Barcelona':     'FC Barcelona',
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

# ── Country name corrections ─────────────────────────────────────────────────
# Fixes misspelled or non-standard country names as stored in COUNTRY.TXT.

COUNTRY_NAMES = {
    'Azerbijan':     'Azerbaijan',
    'Eire':          'Republic of Ireland',
    'Holland':       'Netherlands',
    'Lietchenstein': 'Liechtenstein',
}

# ── Country ISO codes ────────────────────────────────────────────────────────
# Maps the game's internal 3-letter country codes to ISO 3166-1 alpha-2 codes
# for flag emoji generation.  Codes not present have no standard flag.
# Note: the game swapped AUT (Australia) and AUS (Austria).
# GB subdivision codes (ENG, SCO, WAL, NIR) are handled as special cases.

COUNTRY_ISO = {
    'ALB': 'AL',  # Albania
    'ALG': 'DZ',  # Algeria
    'USA': 'US',  # United States
    'SAU': 'SA',  # Saudi Arabia
    'ARG': 'AR',  # Argentina
    'AUT': 'AU',  # Australia (game code swapped)
    'AUS': 'AT',  # Austria (game code swapped)
    'AZE': 'AZ',  # Azerbaijan
    'BEG': 'BE',  # Belgium
    'BOL': 'BO',  # Bolivia
    'BRA': 'BR',  # Brazil
    'BUL': 'BG',  # Bulgaria
    'CAM': 'CM',  # Cameroon
    'CAN': 'CA',  # Canada
    'CHL': 'CL',  # Chile
    'CHI': 'CN',  # China
    'COL': 'CO',  # Colombia
    'COS': 'CR',  # Costa Rica
    'CRO': 'HR',  # Croatia
    'CUB': 'CU',  # Cuba
    'CYP': 'CY',  # Cyprus
    'CZE': 'CZ',  # Czech Republic
    'DEN': 'DK',  # Denmark
    'HOL': 'NL',  # Netherlands
    'EGY': 'EG',  # Egypt
    'ENG': 'ENG', # England (GB subdivision)
    'EST': 'EE',  # Estonia
    'ETH': 'ET',  # Ethiopia
    'FIJ': 'FJ',  # Fiji
    'FIN': 'FI',  # Finland
    'FRA': 'FR',  # France
    'GEO': 'GE',  # Georgia
    'GER': 'DE',  # Germany
    'GHA': 'GH',  # Ghana
    'GRC': 'GR',  # Greece
    'HUN': 'HU',  # Hungary
    'ICE': 'IS',  # Iceland
    'IND': 'IN',  # India
    'ISR': 'IL',  # Israel
    'ITA': 'IT',  # Italy
    'IVO': 'CI',  # Ivory Coast
    'JAM': 'JM',  # Jamaica
    'JAP': 'JP',  # Japan
    'JOR': 'JO',  # Jordan
    'LAT': 'LV',  # Latvia
    'LIB': 'LR',  # Liberia
    'LBY': 'LY',  # Libya
    'LTS': 'LI',  # Liechtenstein
    'LIT': 'LT',  # Lithuania
    'LUX': 'LU',  # Luxembourg
    'MAL': 'MT',  # Malta
    'MEX': 'MX',  # Mexico
    'MOL': 'MD',  # Moldova
    'NIR': 'NIR', # Northern Ireland (GB subdivision)
    'NWZ': 'NZ',  # New Zealand
    'NIG': 'NG',  # Nigeria
    'NKO': 'KP',  # North Korea
    'NOR': 'NO',  # Norway
    'PAK': 'PK',  # Pakistan
    'PER': 'PE',  # Peru
    'POL': 'PL',  # Poland
    'POR': 'PT',  # Portugal
    'ROM': 'RO',  # Romania
    'RUS': 'RU',  # Russia
    'EIR': 'IE',  # Ireland
    'SCO': 'SCO', # Scotland (GB subdivision)
    'SER': 'RS',  # Serbia
    'SLO': 'SK',  # Slovakia
    'SLV': 'SI',  # Slovenia
    'WSO': 'WS',  # Samoa
    'SAF': 'ZA',  # South Africa
    'SKO': 'KR',  # South Korea
    'SPA': 'ES',  # Spain
    'SRI': 'LK',  # Sri Lanka
    'SWE': 'SE',  # Sweden
    'SWI': 'CH',  # Switzerland
    'TRI': 'TT',  # Trinidad & Tobago
    'TUR': 'TR',  # Turkey
    'UGA': 'UG',  # Uganda
    'UKR': 'UA',  # Ukraine
    'URU': 'UY',  # Uruguay
    'VEN': 'VE',  # Venezuela
    'WAL': 'WAL', # Wales (GB subdivision)
    'ZIM': 'ZW',  # Zimbabwe
    'BOS': 'BA',  # Bosnia & Herzegovina
    'MAC': 'MK',  # North Macedonia
    'NEW': 'PG',  # Papua New Guinea
    'GAM': 'GM',  # Gambia
    'SEN': 'SN',  # Senegal
    'MON': 'MN',  # Mongolia
    'TON': 'TO',  # Tonga
    'CHA': 'TD',  # Chad
    'PAN': 'PA',  # Panama
    'ZAM': 'ZM',  # Zambia
    'BER': 'BM',  # Bermuda
    'BAR': 'BB',  # Barbados
    'SLE': 'SL',  # Sierra Leone
    'MOR': 'MA',  # Morocco
    'SUR': 'SR',  # Suriname
    'GUA': 'GP',  # Guadeloupe
    'TAH': 'PF',  # French Polynesia (Tahiti)
    'MAR': 'MQ',  # Martinique
    'BEN': 'BJ',  # Benin
    'SAN': 'SM',  # San Marino
    'CON': 'CG',  # Republic of Congo
    'ARM': 'AM',  # Armenia
    'HAI': 'HT',  # Haiti
    'TUN': 'TN',  # Tunisia
    'MAD': 'MG',  # Madagascar
    'BEL': 'BY',  # Belarus
    'FAR': 'FO',  # Faroe Islands
    'PAR': 'PY',  # Paraguay
    'ANG': 'AO',  # Angola
    'KAZ': 'KZ',  # Kazakhstan
    'MAU': 'MU',  # Mauritius
    # No standard flag:
    # ALA - Alaska (US state, not a country)
    # WIN - West Indies (regional grouping)
    # YUG - Yugoslavia (dissolved 1992)
    # ZAI - Zaire (now Democratic Republic of Congo, dissolved 1997)
    # OTH - Other
}

# GB subdivision flag emoji sequences
_GB_FLAGS = {
    'ENG': '\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F',
    'SCO': '\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F',
    'WAL': '\U0001F3F4\U000E0067\U000E0062\U000E0077\U000E006C\U000E0073\U000E007F',
    'NIR': '\U0001F1EC\U0001F1E7',  # 🇬🇧 — no standard NI flag
}


def country_flag(game_code):
    """Return flag emoji for a game country code, or empty string if unavailable."""
    if game_code in _GB_FLAGS:
        return _GB_FLAGS[game_code]
    iso2 = COUNTRY_ISO.get(game_code, '')
    if len(iso2) == 2:
        return chr(0x1F1E6 + ord(iso2[0]) - 65) + chr(0x1F1E6 + ord(iso2[1]) - 65)
    return ''


# ── Helpers ──────────────────────────────────────────────────────────────────

def pos_rating(skill_row, position):
    """Return position-specific rating matching the game's Position Average display.

    Formula: floor(sum(weight[i] * skill[i]) / 100)
    Weights sourced from PositionRatings.cs (game mod), verified against known in-game values.
    """
    weights = POS_WEIGHTS.get(position, [0] * len(SKILL_COLS))
    skills = [int(skill_row.get(c, 0) or 0) for c in SKILL_COLS]
    return sum(w * s for w, s in zip(weights, skills)) // 100
