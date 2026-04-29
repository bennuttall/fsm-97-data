# Game Save Format

Structure of the binary save files written by FIFA Soccer Manager 97 during
gameplay.  Save files are stored in the `games\` subdirectory of the game
installation, one file per managed club (e.g. `games\SWFC`).

---

## Overview

A save file is roughly **1.3 MB** — about twice the size of `SM97.DAT` (740 KB).
It is structured as:

```
[0        – 244,415]  Preamble  (244 KB of game-state data)
[244,416  – EOF    ]  Team/player blocks (same count and order as SM97.DAT)
```

The team and player block section is located by the same `maps\` scan used for
`SM97.DAT`.  There are 348 team blocks in the same order as in the base file.
The block metadata (team name, nickname, stadium, manager, maps path) is
identical in layout to `SM97.DAT`.  Player records are extended: each record
grows from 87 bytes to **128 bytes**.

---

## Preamble (bytes 0 – 244,415)

The preamble stores all dynamic game state not derivable from the base data
files: finances, fixture schedule, results history, league tables, transfer
records, and the current in-game date.  Most of it is not yet decoded.
Confirmed fields:

| Offset | Type | Content |
|--------|------|---------|
| +0 | LE int32 | Save format version (always `1`) |
| +4 | LE int32 | Managed team index (0-based into the team block list) |
| +136 | null-term string | Save file path (e.g. `games\SWFC`) |
| +448 | — | Start of upcoming fixture data (see below) |
| +1168 | LE int32 | Current in-game date (days since 1899-12-30) |

### Managed team index

The value at +4 identifies the club being managed.  Teams are ordered in the
block list alphabetically by league and then by club name (Premier League
first).  Examples:

| Save | +4 | Team |
|------|----|------|
| `Arsenal` | 0 | Arsenal |
| `Liverpool` | 8 | Liverpool |
| `SWFC` | 15 | Sheffield Wednesday |
| `Wrexham` | 131 | Wrexham |

### Current game date

Stored at offset +1168 as a little-endian 32-bit integer: days elapsed since
**30 December 1899** (the same epoch used for player DOBs).

```python
from datetime import date, timedelta
DOB_BASE = date(1899, 12, 30)
current_date = DOB_BASE + timedelta(days=struct.unpack_from('<I', data, 1168)[0])
```

Example values:

| Save | Raw | Decoded date |
|------|-----|-------------|
| `SWFC` | 35275 | 1996-07-29 (game start, no matches played) |
| `Arsenal` | 35301 | 1996-08-24 |
| `Wrexham` | 40180 | 2010-01-02 |

### Fixture dates

Starting at offset +448, upcoming fixture records appear at 24-byte intervals.
Each record contains (among other fields) a 4-byte little-endian date value at
byte offset 4 within the record, using the same days-since-1899 encoding.

The region from +448 through approximately +600 holds the near-term fixture
schedule for the managed club.  Records with all-`0xFF` bytes in certain fields
indicate unscheduled or empty slots.

---

## Team block differences

Every team block retains its SM97.DAT header layout (see
[data-extraction.md](data-extraction.md) for the field table).  Two additions
appear in the save format:

### 29-byte team state block

Inserted immediately before the player records (i.e. at block offset +283,
pushing the first player record to +312):

| Offset within block | Size | Notes |
|--------------------|------|-------|
| +283 | 4 bytes | `0x46 0x00 0x00 0x00` — consistent across all teams; possibly squad slot limit (70) |
| +287 | 8 bytes | Unknown |
| +295 | 8 bytes | Unknown (contains a non-zero float-like value) |
| +303 | 9 bytes | Unknown; last 4 bytes vary per team (possibly team index or finance reference) |

### Stadium capacity

The capacity stored at block offset +273 reads as garbage in save files.  The
save format appears not to maintain this field at the same offset (or it is
updated via a different mechanism when the user expands the stadium).

---

## Player record structure (128 bytes)

Each player record is 128 bytes, compared to 87 bytes in SM97.DAT.  The layout
is:

```
[0:24]    First name  (null-padded ASCII, unchanged from SM97.DAT)
[24:42]   Last name   (null-padded ASCII, unchanged from SM97.DAT)
[42:87]   Stats block (45 bytes, mostly unchanged — see differences below)
[87:128]  Extended data (41 bytes, new in save format)
```

### Stats block differences

The 45-byte stats block at `[42:87]` is structurally identical to SM97.DAT
except for two changes:

**1. Form is live.**  `stats[30]` holds the current form value (0–100).  In
SM97.DAT this field is always 0; in a save file it reflects in-game form after
pre-season and matches.

**2. Date of birth is shifted by one byte.**  A new byte has been inserted at
`stats[35]`, displacing the DOB from `stats[35:37]` to `stats[36:38]`.  The
DAT-era `stats[41:45]` (four unknown bytes at the end of the stats block) are
zeroed out and appear to have been sacrificed to accommodate this shift without
changing the block size.

Updated layout for the affected region:

| Index | Save field | DAT field |
|-------|-----------|-----------|
| stats[35] | New byte (currently always `0x00`) | DOB low byte |
| stats[36] | DOB low byte | DOB high byte |
| stats[37] | DOB high byte | Unknown |
| stats[38:42] | Same unknown bytes as DAT[37:41] | Unknown |
| stats[42:45] | `0x00 0x00 0x00` (zeroed) | Unknown (present in DAT) |

Reading the DOB from a save file:

```python
dob_raw = stats[36] + stats[37] * 256
dob = date(1899, 12, 30) + timedelta(days=dob_raw)
```

### Extended data (bytes 87–127, 41 bytes)

Appended after the 87-byte core.  Most fields are not yet decoded.  One field
is consistently interpretable:

| Bytes within extended block | Type | Likely meaning |
|-----------------------------|------|----------------|
| [0] | byte | Always `0x00` |
| [1:5] | LE float32 | In-game market value (units: millions, e.g. `11.9` = £11.9M) |
| [5:8] | 3 bytes | Unknown (always `0x00 0x00 0x00` in tested saves at game start) |
| [8:41] | 33 bytes | Unknown (contains additional numeric fields — likely wage, contract length, injury status, transfer flags) |

The market-value float at bytes [1:5] scales with player quality: Premier
League players at game start range from approximately £10M to £14M in the
game's internal economy.

---

## Example: Des Walker (save file)

Des Walker is the third player record in the Sheffield Wednesday block of the
SWFC save.  His 128-byte record:

```
 0: 44 65 73 00 00 00 00 00 00 00 00 00 00 00 00 00  Des.............
16: 00 00 00 00 00 00 00 00 57 61 6c 6b 65 72 00 00  ........Walker..
32: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
   [first name: "Des", last name: "Walker"]

42: 00 1a 03 00 06 ...                               stats begin
   stats[1]=0x1a=26 (English), stats[2]=0x03 (CD), stats[4]=0x06 (shirt 6)

   stats[30]=0x3d=61  Form (initialised at pre-season)
   stats[31]=0x50=80  Energy
   stats[35]=0x00     New byte (purpose unknown)
   stats[36]=0x08 ⎤
   stats[37]=0x5e ⎦   DOB: 8 + 94×256 = 24072 days → 1965-11-26

87: 00 20 94 3e 41 00 00 00 ...
   extended[1:5] = 0x413E9420 → float32 ≈ 11.9 (market value ~£11.9M)
```

---

## Parsing save files

The existing `parse_game_data()` function in `fsm97/parser.py` cannot be used
directly on save files without modification.  The differences are:

1. **Preamble offset**: the first team block begins at byte 244,416, not byte 0.
   The `maps\` scan already handles this automatically.

2. **Player record size**: 128 bytes per record, not 87.  The gap-division logic
   must use `128` as the divisor and account for the 29-byte team state block
   before the first player record (i.e. players start at block offset +312, not
   +283).

3. **DOB offset**: read from `stats[36:38]`, not `stats[35:37]`.

4. **Form**: `stats[30]` is meaningful (non-zero after pre-season); in SM97.DAT
   it is always 0.
