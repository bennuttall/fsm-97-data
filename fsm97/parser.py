"""
Binary parser for SM97.DAT — the FIFA Soccer Manager 97 game database.

Team block structure (offsets from block start):
    +2   team name       (null-terminated)
    +27  nickname        (null-terminated)
    +45  abbreviation    (3 chars, null-terminated)
    +52  stadium name    (null-terminated)
    +82  stadium address (null-terminated)
    +116 area            (null-terminated)
    +150 manager first   (null-terminated)
    +161 manager last    (null-terminated)
    +191 maps path       e.g. "maps\\engprem\\arsenal.map"
    +273 capacity        (4-byte little-endian int)
    +283 players start   (87-byte records follow)

Player record (87 bytes):
    [0:24]  first name  (null-padded)
    [24:42] last name   (null-padded)
    [42:87] stats block:
        stats[0]    unknown (always 0)
        stats[1]    nationality index   (0-based into COUNTRY.TXT list)
        stats[2]    position index      (0-based, 0=GK .. 15=SS)
        stats[3]    unknown
        stats[4]    shirt number
        stats[5:28] 23 skill values (Speed..Determination, 0-100 each)
        stats[28]   greed / personality (0-100)
        stats[29]   unknown
        stats[30]   form
        stats[31]   energy
        stats[32:35] unknown
        stats[35:37] date of birth (LE uint16, days since 1899-12-30)
        stats[37:45] unknown
"""

import struct
from datetime import date, timedelta

GAME_START = date(1996, 7, 29)
_DOB_BASE  = date(1899, 12, 30)

from .constants import LEAGUE_NAMES, POS_ABBR


def load_countries(country_file):
    """
    Parse COUNTRY.TXT into a list of dicts.

    The list is 0-indexed: index matches the nationality byte in player records.
    Each entry has keys: country, demonym, code.
    """
    countries = []
    with open(country_file, encoding='latin-1') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip().strip('"') for p in line.split(',')]
            if len(parts) >= 3:
                countries.append({
                    'country': parts[0],
                    'demonym': parts[1],
                    'code':    parts[2],
                })
    return countries


def load_divisions(division_file):
    """
    Parse DIVISION.TXT into a list of dicts.

    Each entry has keys: division_name, country_id, tier, param3, param4.
    """
    divisions = []
    with open(division_file, encoding='latin-1') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip().strip('"') for p in line.split(',')]
            if len(parts) >= 5:
                divisions.append({
                    'division_name': parts[0],
                    'country_id':    parts[1],
                    'tier':          parts[2],
                    'param3':        parts[3],
                    'param4':        parts[4],
                })
    return divisions


def _read_cstr(data, offset, max_len=None):
    """Read a null-terminated string from bytes at offset."""
    end = data.find(b'\x00', offset)
    if end == -1 or (max_len and end > offset + max_len):
        end = offset + (max_len or 64)
    s = data[offset:end].decode('latin-1', errors='replace').strip()
    return s.replace('`', "'")


def _find_block_positions(data):
    """
    Return sorted list of file positions where each team block's maps path begins.

    Each position is the offset of the 'm' in 'maps\\...'.
    The team block itself starts 191 bytes before this position.
    """
    needle = b'maps\x5c'  # literal: m a p s backslash
    positions = []
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return sorted(positions)


def parse_game_data(dat_file, countries):
    """
    Parse SM97.DAT and return (teams, players).

    teams   — list of dicts with team metadata
    players — list of dicts with player data including a 'skills' list of 23 ints
    """
    with open(dat_file, 'rb') as f:
        data = f.read()

    all_maps = _find_block_positions(data)

    teams = []
    all_players = []

    for i, mpos in enumerate(all_maps):
        bstart = mpos - 191
        next_bstart = (all_maps[i + 1] - 191) if i + 1 < len(all_maps) else len(data)

        # Team metadata
        name      = _read_cstr(data, bstart + 2,   max_len=25)
        nick      = _read_cstr(data, bstart + 27,  max_len=18)
        abbr      = _read_cstr(data, bstart + 45,  max_len=4)
        stadium   = _read_cstr(data, bstart + 52,  max_len=30)
        address   = _read_cstr(data, bstart + 82,  max_len=34) or ''
        address   = '' if address == '-' else address
        area      = _read_cstr(data, bstart + 116, max_len=17)
        area      = '' if area == '-' else area
        mgr_first = _read_cstr(data, bstart + 150, max_len=11)
        mgr_last  = _read_cstr(data, bstart + 161, max_len=15)

        # League name from the maps path (e.g. "maps\engprem\arsenal.map")
        maps_path  = _read_cstr(data, mpos, max_len=60)
        parts      = maps_path.replace('\\', '/').split('/')
        league_code = parts[1] if len(parts) >= 2 else 'others'
        league     = LEAGUE_NAMES.get(league_code, league_code)

        # Capacity: 4-byte little-endian at block offset +273
        capacity = struct.unpack_from('<I', data, bstart + 273)[0]

        # Players: 87-byte records starting at block offset +283
        players_start = bstart + 283
        max_players   = (next_bstart - players_start) // 87

        team_players = []
        for n in range(max_players):
            offset = players_start + n * 87
            record = data[offset:offset + 87]
            if len(record) < 87:
                break

            first = record[0:24].split(b'\x00')[0].decode('latin-1', errors='replace').strip().replace('`', "'")
            last  = record[24:42].split(b'\x00')[0].decode('latin-1', errors='replace').strip().replace('`', "'")
            if first == '-':
                first = ''
            if last == '-':
                last = ''
            if not first and not last:
                continue

            stats   = record[42:87]
            nat_idx = stats[1]
            pos_idx = stats[2]
            shirt   = stats[4]
            skills  = list(stats[5:28]) + [stats[28]]  # 23 skills + greed
            if any(s > 100 for s in skills):
                continue

            dob_offset = stats[35] + stats[36] * 256
            dob = _DOB_BASE + timedelta(days=dob_offset)
            age = (GAME_START.year - dob.year
                   - (1 if (GAME_START.month, GAME_START.day) < (dob.month, dob.day) else 0))

            nat = countries[nat_idx]['demonym'] if nat_idx < len(countries) else ''
            pos = POS_ABBR[pos_idx] if pos_idx < len(POS_ABBR) else ''

            team_players.append({
                'first_name':  first,
                'last_name':   last,
                'team':        name,
                'league':      league,
                'nationality': nat,
                'position':    pos,
                'shirt':       shirt,
                'dob':         dob.isoformat(),
                'age':         age,
                'skills':      skills,
            })

        # is_player_manager: manager's last name appears in the player roster
        player_surnames = {p['last_name'] for p in team_players}
        is_pm = mgr_last in player_surnames

        teams.append({
            'team':              name,
            'nickname':          nick,
            'abbreviation':      abbr,
            'league':            league,
            'stadium':           stadium,
            'stadium_address':   address,
            'area':              area,
            'capacity':          capacity,
            'manager':           f"{mgr_first} {mgr_last}".strip(),
            'is_player_manager': is_pm,
        })
        all_players.extend(team_players)

    return teams, all_players
