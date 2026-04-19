#!/usr/bin/env python3
"""
FIFA Soccer Manager 97 — Data Extraction Script

Reads game data files from an SM97 install and writes CSV files.

Usage:
    fsm-extract <game_dir> [--csv-dir <csv_dir>]
"""

import argparse
import csv
import os

from fsm97.constants import POSITIONS, SKILL_COLS, POS_ORDER, pos_rating
from fsm97.parser import load_countries, load_divisions, parse_game_data


def write_csv(csv_dir, filename, fieldnames, rows):
    path = os.path.join(csv_dir, filename)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  Written: {filename} ({len(rows)} rows)")


def write_countries(csv_dir, countries):
    rows = [{'id': i + 1, **c} for i, c in enumerate(countries)]
    write_csv(csv_dir, 'countries.csv', ['id', 'country', 'demonym', 'code'], rows)


def write_divisions(csv_dir, divisions):
    rows = [{'id': i + 1, **d} for i, d in enumerate(divisions)]
    write_csv(csv_dir, 'divisions.csv',
              ['id', 'division_name', 'country_id', 'tier', 'param3', 'param4'],
              rows)


def write_positions(csv_dir):
    rows = []
    for i, (abbr, name, zone, sort_order) in enumerate(POSITIONS):
        rows.append({
            'id':           i + 1,
            'position':     name,
            'abbreviation': abbr,
            'sort_order':   sort_order,
            'zone':         zone,
        })
    write_csv(csv_dir, 'positions.csv', ['id', 'position', 'abbreviation', 'sort_order', 'zone'], rows)


def write_teams(csv_dir, teams):
    fieldnames = [
        'team', 'nickname', 'abbreviation', 'league',
        'stadium', 'stadium_address', 'area', 'capacity',
        'manager', 'is_player_manager',
    ]
    write_csv(csv_dir, 'teams.csv', fieldnames, teams)


def write_players(csv_dir, players):
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
    write_csv(csv_dir, 'players.csv',
              ['first_name', 'last_name', 'team', 'league',
               'nationality', 'position', 'shirt', 'dob', 'age', 'skill_avg'],
              rows)


def write_player_skills(csv_dir, players):
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
    write_csv(csv_dir, 'player_skills.csv', fieldnames, rows)


def write_player_position_ratings(csv_dir, players):
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
    write_csv(csv_dir, 'player_position_ratings.csv', fieldnames, rows)


def main():
    parser = argparse.ArgumentParser(description="Extract data from FIFA Soccer Manager 97")
    parser.add_argument('game_dir', help="Path to the SM97 game install directory")
    parser.add_argument('--csv-dir', default='csv', help="Output directory for CSV files (default: ./csv)")
    args = parser.parse_args()

    game_dir = args.game_dir
    csv_dir  = args.csv_dir

    dat_file      = os.path.join(game_dir, 'SM97.DAT')
    country_file  = os.path.join(game_dir, 'COUNTRY.TXT')
    division_file = os.path.join(game_dir, 'DIVISION.TXT')

    os.makedirs(csv_dir, exist_ok=True)

    print("Loading reference data...")
    countries = load_countries(country_file)
    print(f"  {len(countries)} countries")
    divisions = load_divisions(division_file)
    print(f"  {len(divisions)} divisions")

    print("Parsing SM97.DAT...")
    teams, players = parse_game_data(dat_file, countries)
    print(f"  {len(teams)} teams, {len(players)} players")

    print("Writing CSV files...")
    write_countries(csv_dir, countries)
    write_divisions(csv_dir, divisions)
    write_positions(csv_dir)
    write_teams(csv_dir, teams)
    write_players(csv_dir, players)
    write_player_skills(csv_dir, players)
    write_player_position_ratings(csv_dir, players)

    print("Done.")


if __name__ == '__main__':
    main()
