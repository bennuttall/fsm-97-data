import re
import shutil
import unicodedata
from pathlib import Path

from chameleon import PageTemplateLoader

from fsm97.constants import LEAGUE_GROUPS, country_flag
from fsm97.data import Dataset


BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CSV_DIR = BASE_DIR / "csv"
OUT_DIR = BASE_DIR / "www"

NAV_LINKS = [
    ("Home",          "/"),
    ("Leagues",       "/leagues/"),
    ("Nations",       "/nations/"),
    ("Clubs",         "/clubs/"),
    ("Players",       "/players/"),
    ("Stadiums",      "/stadiums/"),
    ("Positions",     "/positions/"),
    ("Nationalities", "/nationalities/"),
    ("Stats",         "/stats/"),
    ("Events",        "/events/"),
    ("Trivia",        "/trivia/"),
    ("Videos",        "/videos/"),
    ("Credits",       "/credits/"),
]


def slug(s):
    s = unicodedata.normalize("NFD", str(s))
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-") or "unknown"


class Scribe:
    def __init__(self, csv_dir=CSV_DIR, output_dir=OUT_DIR):
        self.output_dir = Path(output_dir)
        self.ds = Dataset(str(csv_dir))
        self.templates = PageTemplateLoader(
            search_path=[str(TEMPLATES_DIR)],
            default_extension=".pt",
        )
        country_name_to_flag = {c["country"]: country_flag(c["code"]) for c in self.ds.countries}
        self.league_to_flag = {
            lg: country_name_to_flag.get(cn, "")
            for cn, lgs in LEAGUE_GROUPS for lg in lgs
        }

    def setup_output_path(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for src in STATIC_DIR.rglob("*"):
            if src.is_file():
                rel = src.relative_to(STATIC_DIR)
                dst = self.output_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    def render(self, template_name, **kwargs):
        template = self.templates[template_name]
        layout = self.templates["layout"].macros["layout"]
        return template(layout=layout, **kwargs)

    def write_file(self, path, content):
        full_path = self.output_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def write_homepage(self):
        ds = self.ds
        total_leagues  = len(ds.league_names)
        total_teams    = len(ds.teams)
        total_players  = len(ds.players)
        total_stadiums = len(ds.stadium_to_teams)
        nats           = len(ds.players_by_nationality)
        num_nations    = len(ds.nation_names)

        best_player = max(ds.players, key=ds.get_rating)
        best_player_url = (
            f"/clubs/{slug(best_player['team'])}/"
            f"#{slug(best_player['first_name'])}-{slug(best_player['last_name'])}"
        )

        biggest = max(ds.teams, key=lambda t: int(t["capacity"] or 0))

        highlights = [
            {"value": f"{total_leagues}",   "label": "Leagues",       "url": "/leagues/"},
            {"value": f"{total_teams:,}",   "label": "Clubs",         "url": "/clubs/"},
            {"value": f"{total_players:,}", "label": "Players",       "url": "/players/"},
            {"value": f"{total_stadiums:,}","label": "Stadiums",      "url": "/stadiums/"},
            {"value": f"{nats:,}",          "label": "Nationalities", "url": "/nationalities/"},
        ]

        ordered_leagues = [
            lg for _, lgs in LEAGUE_GROUPS
            for lg in lgs
            if lg in ds.teams_by_league and len(lgs) > 1
        ]
        league_cards = [
            {
                "flag":    self.league_to_flag.get(lg, ""),
                "name":    lg,
                "url":     f"/leagues/{slug(lg)}/",
                "count":   len(ds.teams_by_league[lg]),
                "players": sum(len(ds.players_by_team[t["team"]]) for t in ds.teams_by_league[lg]),
            }
            for lg in ordered_leagues
        ]

        content = self.render(
            "home",
            nav_links=NAV_LINKS,
            active="Home",
            page_title="FIFA Soccer Manager 97",
            header_title="FIFA Soccer Manager 97",
            header_sub="Interactive database — 1996/97 season",
            breadcrumb="",
            total_leagues=total_leagues,
            total_players=total_players,
            highlights=highlights,
            best_player=best_player,
            best_player_rating=ds.get_rating(best_player),
            best_player_url=best_player_url,
            biggest=biggest,
            biggest_url=f"/stadiums/{slug(biggest['stadium'])}/",
            league_cards=league_cards,
            nats=nats,
            num_nations=num_nations,
        )
        self.write_file("index.html", content)
