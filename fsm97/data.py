"""
Dataset: loads all CSV files and provides indexed access.

Usage:
    from fsm97.data import Dataset
    ds = Dataset('/path/to/csv')

    ds.teams           — list of team dicts
    ds.players         — list of player dicts
    ds.skills          — list of player_skills dicts (same order as players)
    ds.positions       — list of position dicts
    ds.countries       — list of country dicts

    ds.teams_by_slug         — {slug: team_dict}
    ds.teams_by_league       — {league: [team_dict, ...]}
    ds.players_by_team       — {team_name: [player_dict, ...]}
    ds.skills_by_player      — {(first, last, team): skills_dict}
    ds.players_by_nationality— {nationality: [player_dict, ...]}
    ds.players_by_position   — {position: [player_dict, ...]}
    ds.positions_info        — {abbreviation: position_dict}
    ds.stadium_to_teams      — {stadium_name: [team_dict, ...]}
    ds.prating               — {(first, last, team): float}
    ds.league_names          — ordered list of unique league names
    ds.max_cap               — int, largest stadium capacity
"""

import csv
import re
import unicodedata
from collections import defaultdict

from .constants import POS_ORDER, TEAM_NAMES, STADIUM_NAMES, TEAM_LEAGUES


def _slug(s):
    s = unicodedata.normalize('NFD', str(s))
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-') or 'unknown'


def _load(csv_dir, name):
    with open(f"{csv_dir}/{name}", newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


class Dataset:
    """All game data loaded from CSV files with pre-built indexes."""

    def __init__(self, csv_dir):
        self.teams          = _load(csv_dir, 'teams.csv')
        self.players        = _load(csv_dir, 'players.csv')
        self.skills         = _load(csv_dir, 'player_skills.csv')
        self.pos_ratings    = _load(csv_dir, 'player_position_ratings.csv')
        self.positions      = _load(csv_dir, 'positions.csv')
        self.countries      = _load(csv_dir, 'countries.csv')

        for row in self.teams + self.players + self.skills + self.pos_ratings:
            if row['team'] in TEAM_NAMES:
                row['team'] = TEAM_NAMES[row['team']]

        for row in self.teams:
            if row['stadium'] in STADIUM_NAMES:
                row['stadium'] = STADIUM_NAMES[row['stadium']]
            if row['team'] in TEAM_LEAGUES:
                row['league'] = TEAM_LEAGUES[row['team']]

        for row in self.players + self.skills + self.pos_ratings:
            if row['team'] in TEAM_LEAGUES:
                row['league'] = TEAM_LEAGUES[row['team']]

        self._build_indexes()

    def _build_indexes(self):
        # Team indexes
        self.teams_by_slug   = {_slug(t['team']): t for t in self.teams}
        self.league_names    = list(dict.fromkeys(t['league'] for t in self.teams))
        self.teams_by_league = defaultdict(list)
        for t in self.teams:
            self.teams_by_league[t['league']].append(t)

        # Player indexes
        self.players_by_team         = defaultdict(list)
        self.skills_by_player        = {}
        self.players_by_nationality  = defaultdict(list)
        self.players_by_position     = defaultdict(list)

        for p, s in zip(self.players, self.skills):
            key = (p['first_name'], p['last_name'], p['team'])
            self.players_by_team[p['team']].append(p)
            self.skills_by_player[key] = s
            self.players_by_nationality[p['nationality']].append(p)
            self.players_by_position[p['position']].append(p)

        # Position info
        self.positions_info = {r['abbreviation']: r for r in self.positions}

        # Stadium index — exclude placeholder names
        self.stadium_to_teams = defaultdict(list)
        for t in self.teams:
            sname = t['stadium'].strip()
            if sname and not re.match(r'^XX\d+$', sname):
                self.stadium_to_teams[sname].append(t)

        # Position-specific ratings, pre-computed during extraction and stored in player_skills.csv
        self.prating = {}
        for p, s in zip(self.players, self.skills):
            key = (p['first_name'], p['last_name'], p['team'])
            self.prating[key] = int(s['pos_avg'])

        # Per-position ratings for every player, keyed by (first, last, team)
        self.pos_ratings_by_player = {
            (r['first_name'], r['last_name'], r['team']): r
            for r in self.pos_ratings
        }

        self.max_cap = max(
            (int(t['capacity']) for t in self.teams if t['capacity']),
            default=0,
        )

    def get_rating(self, player):
        """Return the position-specific rating for a player dict."""
        key = (player['first_name'], player['last_name'], player['team'])
        return self.prating.get(key, 0.0)

    def sorted_squad(self, team_name):
        """Return players for a team sorted by position display order."""
        players = self.players_by_team.get(team_name, [])
        order = {pos: i for i, pos in enumerate(POS_ORDER)}
        return sorted(players, key=lambda p: (order.get(p['position'], 99), -self.get_rating(p)))
