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
    ('England',  ['English Premier League', 'English First Division',
                  'English Second Division', 'English Third Division']),
    ('Scotland', ['Scottish Premier League', 'Scottish First Division']),
    ('Germany',  ['German Bundesliga 1', 'German Bundesliga 2']),
    ('France',   ['French Division 1', 'French Division 2']),
    ('Italy',    ['Italian Serie A', 'Italian Serie B']),
]

# ── Per-team league overrides ────────────────────────────────────────────────
# Maps corrected team name → correct league (applied after TEAM_NAMES).
# Only needed for clubs the game placed in the wrong division.
TEAM_LEAGUES = {
    'Hamilton Academical': 'Others',
    'Dumbarton':           'Others',
}

# ── Club nation assignments ──────────────────────────────────────────────────
# Maps club name → nation for clubs not assigned a nation via their league.
# Clubs in LEAGUE_GROUPS-listed leagues derive their nation from that league.
# Easter egg clubs (EA All Stars, EA Select XI, Other, Spare) have no nation.
CLUB_NATIONS = {
    # Albania
    'Teuta Durres':        'Albania',
    # Armenia
    'Shirak Gyumri':       'Armenia',
    # Austria
    'Admira Wacker':       'Austria',
    'Austria Vienna':      'Austria',
    'Rapid Vienna':        'Austria',
    # Azerbaijan
    'Kapaz Ganja':         'Azerbaijan',
    # Belarus
    'Dinamo Minsk':        'Belarus',
    # Belgium
    'Anderlecht':          'Belgium',
    'Antwerp':             'Belgium',
    'Club Brugge':         'Belgium',
    'Lierse':              'Belgium',
    'Standard Liege':      'Belgium',
    # Bulgaria
    'CSKA Sofia':          'Bulgaria',
    'Leveski Sofia':       'Bulgaria',
    'Neftochimik':         'Bulgaria',
    'Slavia Sofia':        'Bulgaria',
    # Croatia
    'Hadjuk Split':        'Croatia',
    # Cyprus
    'APOEL Nicosia':       'Cyprus',
    'Omonia Nicosia':      'Cyprus',
    # Czech Republic
    'Banik Ostrava':       'Czech Republic',
    'Slavia Prague':       'Czech Republic',
    'Sparta Prague':       'Czech Republic',
    # Denmark
    'Aarhus':              'Denmark',
    'Brondby':             'Denmark',
    'Odense':              'Denmark',
    'Silkeborg':           'Denmark',
    # England (non-league clubs not in the Football League)
    'Kidderminster':       'England',
    'Rushden & Diamonds':  'England',
    # Estonia
    'Flora':               'Estonia',
    # Faroe Islands
    'Itrottarfelag':       'Faroe Islands',
    # Finland
    'MYPA':                'Finland',
    # France
    'Ales':                'France',
    'Angers':              'France',
    'Dunkerque':           'France',
    'Poitiers':            'France',
    # Georgia
    'Dinamo Tbilisi':      'Georgia',
    'Samtredia':           'Georgia',
    # Germany
    '1. FC Nürnberg':      'Germany',
    'Chemnitz':            'Germany',
    'Hannover 96':         'Germany',
    'Wattenscheid':        'Germany',
    # Greece
    'Athens':              'Greece',
    'Olympiakos':          'Greece',
    'Panathinaikos':       'Greece',
    # Hungary
    'Budapest':            'Hungary',
    'Ferencvaros':         'Hungary',
    # Iceland
    'Hafnarfjardar':       'Iceland',
    # Israel
    'Betar Jerusalem':     'Israel',
    # Italy
    'Ancona':              'Italy',
    'Avellino':            'Italy',
    'Fidelis Andria':      'Italy',
    'Pistoiese':           'Italy',
    # Latvia
    'Skonto Riga':         'Latvia',
    # Liechtenstein
    'Vaduz':               'Liechtenstein',
    # Lithuania
    'Inkaraz Grifas':      'Lithuania',
    # Luxembourg
    'Jeunesse':            'Luxembourg',
    'Spora':               'Luxembourg',
    # Malta
    'Hibernians':          'Malta',
    'Sliema':              'Malta',
    # Moldova
    'Tiligul Tiraspol':    'Moldova',
    # Netherlands
    'Ajax':                'Netherlands',
    'Feyenoord':           'Netherlands',
    'PSV Eindhoven':       'Netherlands',
    'Twente':              'Netherlands',
    'Vitesse':             'Netherlands',
    # Northern Ireland
    'Crusaders':           'Northern Ireland',
    'Derry':               'Northern Ireland',
    'Glenavon':            'Northern Ireland',
    'Linfield':            'Northern Ireland',
    # Norway
    'Lillestrom':          'Norway',
    'Rosenborg':           'Norway',
    'Stravanger':          'Norway',
    # Poland
    'Katowice':            'Poland',
    'Legia Warsaw':        'Poland',
    'Widzew Lodz':         'Poland',
    # Portugal
    'Belenenses':          'Portugal',
    'Benfica':             'Portugal',
    'Boavista':            'Portugal',
    'Porto':               'Portugal',
    'Sporting Lisbon':     'Portugal',
    # Republic of Ireland
    'Bohemians':           'Republic of Ireland',
    'Shamrock':            'Republic of Ireland',
    # Romania
    'Dinamo Bucharest':    'Romania',
    'Rapid Bucharest':     'Romania',
    'Steaua Bucharest':    'Romania',
    'Uni Craiova':         'Romania',
    # Russia
    'Alania Vladikavkaz':  'Russia',
    'CSKA Moscow':         'Russia',
    'Dinamo Moscow':       'Russia',
    'Rotor Volvograd':     'Russia',
    'Spartak Moscow':      'Russia',
    # San Marino
    'Tre Fiori':           'San Marino',
    # Scotland (clubs not in the main two divisions)
    'Dumbarton':           'Scotland',
    'Hamilton Academical': 'Scotland',
    # Serbia
    'Partizan':            'Serbia',
    'Partizan Belgrade':   'Serbia',
    'RS Belgrade':         'Serbia',
    # Slovakia
    'Slovan Bratislava':   'Slovakia',
    # Slovenia
    'Olimpija Ljubljana':  'Slovenia',
    # Spain
    'Atlético Madrid':     'Spain',
    'Deportivo La Coruña': 'Spain',
    'FC Barcelona':        'Spain',
    'Real Madrid':         'Spain',
    'Real Zaragoza':       'Spain',
    # Sweden
    'Gothenburg':          'Sweden',
    'Halmstads':           'Sweden',
    'Malmo':               'Sweden',
    # Switzerland
    'Grasshoppers':        'Switzerland',
    'Servette':            'Switzerland',
    'Sion':                'Switzerland',
    # Turkey
    'Besiktas':            'Turkey',
    'Fenerbache':          'Turkey',
    'Galatasaray':         'Turkey',
    # Ukraine
    'Dinamo Kiev':         'Ukraine',
    'Karpaty Lviv':        'Ukraine',
    # Wales
    'Aberystwyth Town':    'Wales',
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
    # Welsh clubs
    'Aberystwyth':   'Aberystwyth Town',
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
    # Welsh stadium corrections
    'Aberystwyth T': 'Park Avenue',
    # Israeli stadium corrections
    'Malcha':        'Teddy Stadium',
}

# Maps corrected stadium name → area, for stadiums where the game stored the
# area name as the stadium name (so the area field was left blank).
STADIUM_AREAS = {
    'Teddy Stadium': 'Malcha',
}

# ── 1996/97 final league positions ──────────────────────────────────────────
# Maps game team name → final finishing position in the real 1996/97 season.
# Sources: Wikipedia final tables for each league.

FINISH_POSITIONS = {
    # English Premier League
    'Manchester United':  1,
    'Newcastle United':   2,
    'Arsenal':            3,
    'Liverpool':          4,
    'Aston Villa':        5,
    'Chelsea':            6,
    'Sheffield Wednesday':7,
    'Wimbledon':          8,
    'Leicester City':     9,
    'Tottenham Hotspur': 10,
    'Leeds United':      11,
    'Derby County':      12,
    'Blackburn Rovers':  13,
    'West Ham United':   14,
    'Everton':           15,
    'Southampton':       16,
    'Coventry City':     17,
    'Sunderland':        18,
    'Middlesbrough':     19,
    'Nottingham Forest': 20,
    # English First Division
    'Bolton Wanderers':        1,
    'Barnsley':                2,
    'Wolverhampton Wanderers': 3,
    'Ipswich Town':            4,
    'Sheffield United':        5,
    'Crystal Palace':          6,
    'Portsmouth':              7,
    'Port Vale':               8,
    'Queens Park Rangers':     9,
    'Birmingham City':        10,
    'Tranmere Rovers':        11,
    'Stoke City':             12,
    'Norwich City':           13,
    'Manchester City':        14,
    'Charlton Athletic':      15,
    'West Bromwich Albion':   16,
    'Oxford United':          17,
    'Reading':                18,
    'Swindon Town':           19,
    'Huddersfield Town':      20,
    'Bradford City':          21,
    'Grimsby Town':           22,
    'Oldham Athletic':        23,
    'Southend United':        24,
    # English Second Division
    'Bury':               1,
    'Stockport County':   2,
    'Luton Town':         3,
    'Brentford':          4,
    'Bristol City':       5,
    'Crewe Alexandra':    6,
    'Blackpool':          7,
    'Wrexham':            8,
    'Burnley':            9,
    'Chesterfield':      10,
    'Gillingham':        11,
    'Walsall':           12,
    'Watford':           13,
    'Millwall':          14,
    'Preston North End': 15,
    'Bournemouth':       16,
    'Bristol Rovers':    17,
    'Wycombe Wanderers': 18,
    'Plymouth Argyle':   19,
    'York City':         20,
    'Peterborough United':21,
    'Shrewsbury Town':   22,
    'Rotherham United':  23,
    'Notts County':      24,
    # English Third Division
    'Wigan Athletic':       1,
    'Fulham':               2,
    'Carlisle United':      3,
    'Northampton Town':     4,
    'Swansea City':         5,
    'Chester City':         6,
    'Cardiff City':         7,
    'Colchester United':    8,
    'Lincoln City':         9,
    'Cambridge United':    10,
    'Mansfield Town':      11,
    'Scarborough':         12,
    'Scunthorpe United':   13,
    'Rochdale':            14,
    'Barnet':              15,
    'Leyton Orient':       16,
    'Hull City':           17,
    'Darlington':          18,
    'Doncaster Rovers':    19,
    'Hartlepool United':   20,
    'Torquay United':      21,
    'Exeter City':         22,
    'Brighton & Hove Albion':23,
    'Hereford United':     24,
    # German Bundesliga 1
    'Bayern München':          1,
    'Bayer Leverkusen':        2,
    'Borussia Dortmund':       3,
    'VfB Stuttgart':           4,
    'VfL Bochum':              5,
    'Karlsruher SC':           6,
    '1860 München':            7,
    'Werder Bremen':           8,
    'MSV Duisburg':            9,
    '1. FC Köln':             10,
    'Borussia Mönchengladbach':11,
    'FC Schalke 04':          12,
    'Hamburger SV':           13,
    'Arminia Bielefeld':      14,
    'Hansa Rostock':          15,
    'Fortuna Düsseldorf':     16,
    'SC Freiburg':            17,
    'FC St. Pauli':           18,
    # German Bundesliga 2
    '1. FC Kaiserslautern': 1,
    'VfL Wolfsburg':        2,
    'Hertha BSC':           3,
    '1. FSV Mainz 05':      4,
    'Stuttgarter Kickers':  5,
    'SpVgg Unterhaching':   6,
    'Eintracht Frankfurt':  7,
    'VfB Leipzig':          8,
    'KFC Uerdingen':        9,
    'SV Meppen':           10,
    'Fortuna Köln':        11,
    'FC Carl Zeiss Jena':  12,
    'FC Gütersloh':        13,
    'FSV Zwickau':         14,
    'SV Waldhof Mannheim': 15,
    'VfB Lübeck':          16,
    'Rot-Weiß Essen':      17,
    'VfB Oldenburg':       18,
    # Italian Serie A
    'Juventus':      1,
    'Parma':         2,
    'Internazionale':3,
    'Lazio':         4,
    'Udinese':       5,
    'Sampdoria':     6,
    'Bologna':       7,
    'Vicenza':       8,
    'Fiorentina':    9,
    'Atalanta':     10,
    'AC Milan':     11,
    'Roma':         12,
    'Napoli':       13,
    'Piacenza':     14,
    'Cagliari':     15,
    'Perugia':      16,
    'Hellas Verona':17,
    'Reggiana':     18,
    # Italian Serie B
    'Brescia':          1,
    'Empoli':           2,
    'Lecce':            3,
    'Bari':             4,
    'Genoa':            5,
    'Pescara':          6,
    'Chievo':           7,
    'Ravenna':          8,
    'Torino':           9,
    'Reggina':         10,
    'Foggia':          11,
    'Padova':          12,
    'Venezia':         13,
    'Lucchese':        14,
    'Salernitana':     15,
    'Castel di Sangro': 16,
    'Cosenza':         17,
    'Cesena':          18,
    'Palermo':         19,
    'Cremonese':       20,
    # French Division 1
    'Monaco':              1,
    'Paris Saint-Germain': 2,
    'Nantes':              3,
    'Bordeaux':            4,
    'FC Metz':             5,
    'Auxerre':             6,
    'Bastia':              7,
    'Lyon':                8,
    'Strasbourg':          9,
    'Montpellier':        10,
    'Marseille':          11,
    'Guingamp':           12,
    'RC Lens':            13,
    'Le Havre':           14,
    'Cannes':             15,
    'Rennes':             16,
    'Caen':               17,
    'Nancy':              18,
    'Lille':              19,
    'Nice':               20,
    # French Division 2
    'Châteauroux':     1,
    'Toulouse':        2,
    'Martigues':       3,
    'Gueugnon':        4,
    'Niort':           5,
    'Le Mans':         6,
    'Beauvais':        7,
    'Laval':           8,
    'Lorient':         9,
    'Valence':        10,
    'Sochaux':        11,
    'Mulhouse':       12,
    'Red Star':       13,
    'Toulon':         14,
    'Amiens':         15,
    'Perpignan':      16,
    'Saint-Étienne':  17,
    'Louhans-Cuiseaux':18,
    'Charleville':    19,
    'Troyes':         20,
    'Épinal':         21,
    'Saint-Brieuc':   22,
    # Scottish Premier League
    'Rangers':               1,
    'Celtic':                2,
    'Dundee United':         3,
    'Heart of Midlothian':   4,
    'Dunfermline Athletic':  5,
    'Aberdeen':              6,
    'Kilmarnock':            7,
    'Motherwell':            8,
    'Hibernian':             9,
    'Raith Rovers':         10,
    # Scottish First Division
    'St Johnstone':   1,
    'Airdrieonians':  2,
    'Dundee':         3,
    'St Mirren':      4,
    'Falkirk':        5,
    'Partick Thistle':6,
    'Stirling Albion':7,
    'Greenock Morton':8,
    'Clydebank':      9,
    'East Fife':     10,
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
