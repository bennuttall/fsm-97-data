#!/usr/bin/env python3
"""
FIFA Soccer Manager 97 — Data Extraction Script

Reads game data files from the Wine-installed SM97 and writes CSV files.

Usage:
    python3 extract.py

Paths are configured at the top of this file.
"""

import csv
import os

from fsm97.constants import POSITIONS, SKILL_COLS, POS_ORDER, pos_rating
from fsm97.parser import load_countries, load_divisions, parse_game_data

GAME_DIR = "/home/ben/.wine/drive_c/FIFA Soccer Manager"
CSV_DIR  = "/home/ben/Projects/bennuttall/fsm-97-data/csv"

DAT_FILE      = f"{GAME_DIR}/SM97.DAT"
COUNTRY_FILE  = f"{GAME_DIR}/COUNTRY.TXT"
DIVISION_FILE = f"{GAME_DIR}/DIVISION.TXT"


def write_csv(filename, fieldnames, rows):
    path = os.path.join(CSV_DIR, filename)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Written: {filename} ({len(rows)} rows)")


def write_countries(countries):
    rows = [{'id': i + 1, **c} for i, c in enumerate(countries)]
    write_csv('countries.csv', ['id', 'country', 'demonym', 'code'], rows)


def write_divisions(divisions):
    rows = [{'id': i + 1, **d} for i, d in enumerate(divisions)]
    write_csv('divisions.csv',
              ['id', 'division_name', 'country_id', 'tier', 'param3', 'param4'],
              rows)


def write_positions():
    rows = []
    for i, (abbr, name, zone, sort_order) in enumerate(POSITIONS):
        rows.append({
            'id':           i + 1,
            'position':     name,
            'abbreviation': abbr,
            'sort_order':   sort_order,
            'zone':         zone,
        })
    write_csv('positions.csv', ['id', 'position', 'abbreviation', 'sort_order', 'zone'], rows)


def write_teams(teams):
    fieldnames = [
        'team', 'nickname', 'abbreviation', 'league',
        'stadium', 'stadium_address', 'area', 'capacity',
        'manager', 'is_player_manager',
    ]
    write_csv('teams.csv', fieldnames, teams)


def write_players(players):
    rows = []
    for p in players:
        skills = p['skills']
        avg = round(sum(skills) / len(skills), 2) if skills else 0.0
        rows.append({
            'first_name':  p['first_name'],
            'last_name':   p['last_name'],
            'team':        p['team'],
            'league':      p['league'],
            'nationality': p['nationality'],
            'position':    p['position'],
            'shirt':       p['shirt'],
            'dob':         p['dob'],
            'age':         p['age'],
            'skill_avg':   avg,
        })
    write_csv('players.csv',
              ['first_name', 'last_name', 'team', 'league',
               'nationality', 'position', 'shirt', 'dob', 'age', 'skill_avg'],
              rows)


def write_player_skills(players):
    fieldnames = (
        ['first_name', 'last_name', 'team', 'league', 'nationality', 'position', 'shirt',
         'dob', 'age', 'pos_avg']
        + SKILL_COLS
    )
    rows = []
    for p in players:
        skill_row = dict(zip(SKILL_COLS, p['skills']))
        row = {
            'first_name':  p['first_name'],
            'last_name':   p['last_name'],
            'team':        p['team'],
            'league':      p['league'],
            'nationality': p['nationality'],
            'position':    p['position'],
            'shirt':       p['shirt'],
            'dob':         p['dob'],
            'age':         p['age'],
            'pos_avg':     pos_rating(skill_row, p['position']),
        }
        row.update(skill_row)
        rows.append(row)
    write_csv('player_skills.csv', fieldnames, rows)


def write_player_position_ratings(players):
    fieldnames = ['first_name', 'last_name', 'team', 'dob', 'age'] + POS_ORDER
    rows = []
    for p in players:
        skill_row = dict(zip(SKILL_COLS, p['skills']))
        row = {
            'first_name': p['first_name'],
            'last_name':  p['last_name'],
            'team':       p['team'],
            'dob':        p['dob'],
            'age':        p['age'],
        }
        for pos in POS_ORDER:
            row[pos] = pos_rating(skill_row, pos)
        rows.append(row)
    write_csv('player_position_ratings.csv', fieldnames, rows)


def main():
    os.makedirs(CSV_DIR, exist_ok=True)

    print("Loading reference data...")
    countries = load_countries(COUNTRY_FILE)
    print(f"  {len(countries)} countries")
    divisions = load_divisions(DIVISION_FILE)
    print(f"  {len(divisions)} divisions")

    print("Parsing SM97.DAT...")
    teams, players = parse_game_data(DAT_FILE, countries)
    print(f"  {len(teams)} teams, {len(players)} players")

    print("Writing CSV files...")
    write_countries(countries)
    write_divisions(divisions)
    write_positions()
    write_teams(teams)
    write_players(players)
    write_player_skills(players)
    write_player_position_ratings(players)

    print("Done.")


if __name__ == '__main__':
    main()
