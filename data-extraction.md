# FSM97 Data Extraction

How player and team data is read from `SM97.DAT`, the binary game database shipped
with FIFA Soccer Manager 97.

---

## Overview

`SM97.DAT` is a flat binary file. It has no header or index — data is located by
searching for a known byte pattern. Each team occupies a variable-length block
containing metadata and a fixed run of 87-byte player records. A Python parser
(`fsm97/parser.py`) reads the file, extracts all fields, and writes them to CSV.
The website generator then reads those CSVs.

---

## Locating team blocks

Every team block contains a path to its map file of the form `maps\<league>\<team>.map`.
The parser scans the entire file for the byte sequence `6d 61 70 73 5c` (`maps\`) to
find every team block:

```python
needle = b'maps\x5c'
```

Each match gives the position of the maps path. The team block itself starts exactly
**191 bytes before** that position.

---

## Team block structure

Offsets are relative to the start of the team block:

| Offset | Content |
|--------|---------|
| +2 | Team name (null-terminated) |
| +27 | Nickname |
| +45 | Abbreviation (3 chars) |
| +52 | Stadium name |
| +82 | Stadium address |
| +116 | Area |
| +150 | Manager first name |
| +161 | Manager last name |
| +191 | Maps path (used to identify block start) |
| +273 | Stadium capacity (4-byte little-endian int) |
| +283 | **Player records begin** (87 bytes each) |

Player records run from offset +283 to the start of the next team block.
The number of players is inferred by dividing the available space by 87.

---

## Player record structure (87 bytes)

Each player record is exactly 87 bytes:

```
[0:24]   First name  (null-padded ASCII)
[24:42]  Last name   (null-padded ASCII)
[42:87]  Stats block (45 bytes)
```

### Stats block layout

| Index | Field | Notes |
|-------|-------|-------|
| stats[0] | Unknown | Always 0 |
| stats[1] | Nationality index | 0-based index into `COUNTRY.TXT` |
| stats[2] | Position index | 0–15, maps to GK/RB/LB/CD etc. |
| stats[3] | Unknown | Always 0 |
| stats[4] | Shirt number | |
| stats[5:28] | 23 skill values | Speed → Determination (see below) |
| stats[28] | Greed | Personality attribute, 0–100 |
| stats[29] | Unknown | |
| stats[30] | Form | 0 at game start |
| stats[31] | Energy | 80 at game start for all players |
| stats[32:35] | Unknown | |
| stats[35:37] | Date of birth | Little-endian uint16, days since 1899-12-30 |
| stats[37:45] | Unknown | |

### Skill order (stats[5:28])

The 23 values map to the game's attributes in this order:

| Index | Attribute | Index | Attribute |
|-------|-----------|-------|-----------|
| 5 | Speed | 17 | GK Throw |
| 6 | Agility | 18 | GK Handling |
| 7 | Acceleration | 19 | Throw-in |
| 8 | Stamina | 20 | Leadership |
| 9 | Strength | 21 | Consistency |
| 10 | Fitness | 22 | Determination |
| 11 | Shooting | — | — |
| 12 | Passing | **28** | **Greed** (separate byte) |
| 13 | Heading | | |
| 14 | Control | | |
| 15 | Dribbling | | |
| 16 | GK Kick | | |

### Birthdate encoding

The DOB is stored as a 16-bit little-endian unsigned integer: the number of days
elapsed since **30 December 1899** (the same base date used by Microsoft Excel and
the game's internal date system). The two bytes are combined as:

```
days = stats[35] + stats[36] * 256
dob  = date(1899, 12, 30) + timedelta(days=days)
```

This is a WORD (16-bit), so the maximum representable date is day 65,535 —
**5 October 2079**. After that point the game overflows and all player ages are
calculated incorrectly. This is known as the **2079 Bug**.

Age at game start (29 July 1996) is computed from the DOB using a standard
birthday-aware formula.

---

## Example: David Seaman

Seaman is the first player record in Arsenal's block. His raw 87 bytes:

```
 0:  44 61 76 69 64 00 00 00 00 00 00 00 00 00 00 00   David...........
16:  00 00 00 00 00 00 00 00 53 65 61 6d 61 6e 00 00   ........Seaman..
32:  00 00 00 00 00 00 00 00 00 00 00 1a 00 00 01 48   ...............H
48:  5e 46 47 4a 48 10 48 19 2f 1a 57 5d 2c 2a 18 57   ^FGJH.H./.W],*.W
64:  57 5f 1d 50 58 40 23 00 00 50 b6 52 01 e9 5a 04   W_.PX@#..P.R..Z.
80:  04 01 ff 8a 05 00 00                               .......
```

### Names

| Bytes | Hex | Value |
|-------|-----|-------|
| [0:6] | `44 61 76 69 64 00` | `David` |
| [24:30] | `53 65 61 6d 61 6e 00` | `Seaman` |

### Stats block (starting at byte 42)

```
Byte 42+1  = 0x1a = 26   → nationality index 26 (England)
Byte 42+2  = 0x00 =  0   → position GK
Byte 42+4  = 0x01 =  1   → shirt number 1
```

### Skills (stats[5:28] = bytes 47–69)

```
48 5e 46 47 4a 48 10 48 19 2f 1a 57 5d 2c 2a 18 57 57 5f 1d 50 58 40
```

| Attribute | Hex | Value |
|-----------|-----|-------|
| Speed | `48` | 72 |
| Agility | `5e` | 94 |
| Acceleration | `46` | 70 |
| Stamina | `47` | 71 |
| Strength | `4a` | 74 |
| Fitness | `48` | 72 |
| Shooting | `10` | 16 |
| Passing | `48` | 72 |
| Heading | `19` | 25 |
| Control | `2f` | 47 |
| Dribbling | `1a` | 26 |
| Coolness | `57` | 87 |
| Awareness | `5d` | 93 |
| Tackling Det. | `2c` | 44 |
| Tackling Skill | `2a` | 42 |
| Flair | `18` | 24 |
| GK Kick | `57` | 87 |
| GK Throw | `57` | 87 |
| GK Handling | `5f` | 95 |
| Throw-in | `1d` | 29 |
| Leadership | `50` | 80 |
| Consistency | `58` | 88 |
| Determination | `40` | 64 |

### Remaining stats

```
stats[28] = 0x23 = 35   → Greed
stats[30] = 0x00 =  0   → Form
stats[31] = 0x50 = 80   → Energy
stats[35] = 0xe9 = 233  ⎤
stats[36] = 0x5a =  90  ⎦ → 233 + 90×256 = 23273 days → 1963-09-19 (DOB)
```

Age on 29 July 1996: **32**.

---

## Data flow

```
SM97.DAT
  └─ parser.py (binary → Python dicts)
       └─ extract.py (dicts → CSV files)
            └─ data.py (CSV → indexed Dataset)
                 └─ generate_www.py (Dataset → static HTML)
```

CSV files written: `players.csv`, `player_skills.csv`, `player_position_ratings.csv`,
`teams.csv`, `countries.csv`, `divisions.csv`, `positions.csv`.
