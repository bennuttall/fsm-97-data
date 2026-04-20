# Game Files

FIFA Soccer Manager 97 is installed to a single directory. The files used by this
project are described below. For the extraction process that reads them, see
[data-extraction.md](data-extraction.md).

---

## Directory layout

```
FIFA Soccer Manager/
├── SM97.DAT          ← binary game database (teams, players, stadiums)
├── COUNTRY.TXT       ← country and nationality list
├── DIVISION.TXT      ← league/division definitions
├── POSITION.TXT      ← player position definitions
├── fmv/              ← full-motion video clips (.TGQ format)
├── graphics/         ← UI graphics (.TQI, .GRP formats)
├── maps/             ← per-league stadium layout data
│   ├── EngPrem/
│   ├── EngFirst/
│   └── …
└── …
```

---

## SM97.DAT

**Type:** Flat binary  
**Size:** ~740 KB

The master game database. Contains every club and player in the game in a single
unindexed binary file. There is no header or table of contents — data is located
by scanning for a known byte signature.

The file is organised as a sequence of **team blocks**. Each block contains club
metadata (name, nickname, stadium, manager, capacity) followed by a run of
fixed-size player records. The league a club belongs to is encoded in the path to
its stadium map file, stored within the block.

Player records are 87 bytes each and contain: first name, last name, nationality,
position, shirt number, 23 skill attributes, date of birth, and several other
fields. Skills are stored as integers in the range 0–100.

See [data-extraction.md](data-extraction.md) for the full binary layout.

---

## COUNTRY.TXT

**Type:** CSV (comma-separated, values double-quoted)  
**Encoding:** Latin-1

A list of all countries/nationalities recognised by the game. Each row has three
fields:

| Field | Example | Notes |
|-------|---------|-------|
| Country name | `"Albania"` | Full English country name |
| Demonym | `"Albanian"` | Used as the player nationality label in-game |
| Code | `"ALB"` | 3-letter code used internally for flags and lookups |

The **row index** (0-based) is what is stored in each player record as their
nationality — not the code or name. There are 118 entries.

Notable quirks in the file:
- `"Australia"` and `"Austria"` have their codes swapped (`AUT`/`AUS`)
- `"Azerbijan"` and `"Lietchenstein"` are misspelled
- `"Holland"` is used instead of `"Netherlands"`
- `"Eire"` is used instead of `"Republic of Ireland"`
- The file includes several non-standard entries: `"Alaska"`, `"West Indies"`,
  `"Yugoslavia"`, `"Zaire"`, and `"Other"`

---

## DIVISION.TXT

**Type:** CSV (comma-separated, values double-quoted)  
**Encoding:** Latin-1

A list of all divisions (leagues) defined in the game. Each row has five fields:

| Field | Example | Notes |
|-------|---------|-------|
| Division name | `"Super League"` | Display name |
| Country ID | `27` | 1-based index into COUNTRY.TXT |
| Tier | `0` | 0 = top flight, 1 = second tier, etc. |
| param3 | `40` | Possibly related to transfer activity or prestige; meaning not fully established |
| param4 | `90` | As above |

The file lists 69 divisions covering all European footballing nations, plus
placeholder entries (`"Other"`, `"Spare"`, `"HiddenEA"`) used for clubs not
assigned to a named league, and the easter egg EA teams.

The fully playable leagues (England, Scotland, Germany, France, Italy) have
non-zero `param3`/`param4` values. All other national leagues have these set to
zero, which in practice means they are reference-only — the game includes their
clubs in the database but does not simulate their seasons.

---

## POSITION.TXT

**Type:** CSV (comma-separated, values double-quoted)  
**Encoding:** Latin-1

A list of the 16 player positions used by the game. Each row has four fields:

| Field | Example | Notes |
|-------|---------|-------|
| Full name | `"Goalkeeper"` | Display name |
| Abbreviation | `"GK"` | 2–3 letter code used in squad views |
| Sort order | `0` | Display order within the position zone |
| Zone | `3` | 0 = Defender, 1 = Midfielder, 2 = Attacker, 3 = Goalkeeper |

The 16 positions in file order (which matches the index byte in player records):

| Index | Abbreviation | Full name |
|-------|--------------|-----------|
| 0 | GK | Goalkeeper |
| 1 | RB | Right Back |
| 2 | LB | Left Back |
| 3 | CD | Central Defence |
| 4 | RWB | Right Wing Back |
| 5 | LWB | Left Wing Back |
| 6 | SW | Sweeper |
| 7 | DM | Defensive Midfield |
| 8 | RM | Right Midfield |
| 9 | LM | Left Midfield |
| 10 | AM | Attacking Midfield |
| 11 | RW | Right Winger |
| 12 | LW | Left Winger |
| 13 | FR | Free Role |
| 14 | FOR | Forward |
| 15 | SS | Support Striker |

This project does not parse POSITION.TXT directly — position definitions are
hardcoded in `fsm97/constants.py` (sourced from the
[fsm97trainer](https://github.com/jiangsheng/fsm97trainer) project, which also
documents the position rating weight vectors used to compute the in-game Position
Average score).
