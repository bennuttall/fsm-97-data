import argparse
import re
import shutil
import unicodedata
from pathlib import Path

from chameleon import PageTemplateLoader

from fsm97.constants import LEAGUE_GROUPS, country_flag, CLUB_NATIONS, POS_ORDER, SKILL_COLS, SKILL_LABELS, SKILL_GROUPS
from fsm97.data import Dataset
from fsm97.generate_www import CLUB_TRIVIA


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
        self.country_name_to_flag = {c["country"]: country_flag(c["code"]) for c in self.ds.countries}
        self.nat_to_flag = {c["demonym"]: country_flag(c["code"]) for c in self.ds.countries}
        self.nat_to_country = {c["demonym"]: c["country"] for c in self.ds.countries}
        self.league_to_flag = {
            lg: self.country_name_to_flag.get(cn, "")
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

    def write_leagues_page(self):
        ds = self.ds
        league_groups = []

        for country, lgs in LEAGUE_GROUPS:
            rows = []
            for lg in lgs:
                if lg not in ds.teams_by_league:
                    continue
                teams = ds.teams_by_league[lg]
                players = sum(len(ds.players_by_team[t["team"]]) for t in teams)
                flag = self.league_to_flag.get(lg, "") if len(lgs) > 1 else ""
                rows.append({
                    "flag":    flag,
                    "name":    lg,
                    "url":     f"/leagues/{slug(lg)}/",
                    "clubs":   len(teams),
                    "players": players,
                })
            if rows:
                cflag = self.league_to_flag.get(lgs[0], "")
                league_groups.append({
                    "country":        country,
                    "flag":           cflag,
                    "rows":           rows,
                    "has_others_note": False,
                })

        if "Others" in ds.teams_by_league:
            others = ds.teams_by_league["Others"]
            players = sum(len(ds.players_by_team[t["team"]]) for t in others)
            league_groups.append({
                "country":        "Other Clubs",
                "flag":           "",
                "rows":           [{"flag": "", "name": "Others", "url": "/nations/", "clubs": len(others), "players": players}],
                "has_others_note": True,
            })

        content = self.render(
            "leagues",
            nav_links=NAV_LINKS,
            active="Leagues",
            page_title="Leagues",
            header_title="All Leagues",
            header_sub=f"{len(ds.league_names)} leagues",
            breadcrumb="",
            league_groups=league_groups,
        )
        self.write_file("leagues/index.html", content)

    def _rating_class(self, v):
        v = float(v)
        if v >= 70: return "rat-gold"
        if v >= 60: return "rat-green"
        if v >= 50: return "rat-mid"
        return "rat-low"

    def _club_row(self, t):
        ds = self.ds
        players = ds.players_by_team[t["team"]]
        pc = len(players)
        avg = (sum(ds.get_rating(p) for p in players) / pc) if pc else 0
        stadium = t["stadium"].strip()
        stadium_url = None if re.match(r"^XX\d+$", stadium) else f"/stadiums/{slug(stadium)}/"
        return {
            "slug":        slug(t["team"]),
            "name":        t["team"],
            "nickname":    t["nickname"],
            "stadium":     stadium,
            "stadium_url": stadium_url,
            "capacity":    int(t["capacity"] or 0),
            "manager":     t["manager"],
            "avg":         f"{avg:.1f}" if pc else "—",
            "avg_class":   self._rating_class(avg) if pc else "",
        }

    def write_nations_page(self):
        ds = self.ds
        rows = []
        for nation in ds.nation_names:
            clubs = ds.clubs_by_nation[nation]
            nplayers = sum(len(ds.players_by_team[t["team"]]) for t in clubs)
            flag = self.country_name_to_flag.get(nation, "")
            rows.append({
                "flag":    flag,
                "name":    nation,
                "url":     f"/nations/{slug(nation)}/",
                "clubs":   len(clubs),
                "players": nplayers,
            })

        content = self.render(
            "nations",
            nav_links=NAV_LINKS,
            active="Nations",
            page_title="Nations",
            header_title="Nations",
            header_sub=f"{len(ds.nation_names)} nations",
            breadcrumb="",
            rows=rows,
        )
        self.write_file("nations/index.html", content)

        for nation in ds.nation_names:
            self._write_nation_page(nation)

    def _write_nation_page(self, nation):
        ds = self.ds
        clubs = ds.clubs_by_nation[nation]
        flag = self.country_name_to_flag.get(nation, "")
        flag_str = f"{flag} " if flag else ""

        leagued_map = {}
        unaffiliated = []
        for t in sorted(clubs, key=lambda t: t["team"]):
            if t["league"] == "Others":
                unaffiliated.append(self._club_row(t))
            else:
                leagued_map.setdefault(t["league"], []).append(self._club_row(t))

        leagued = [
            {
                "name":     lg,
                "slug":     slug(lg),
                "flag_str": (self.league_to_flag.get(lg, "") + " ") if self.league_to_flag.get(lg) else "",
                "clubs":    lg_clubs,
            }
            for lg, lg_clubs in sorted(leagued_map.items())
        ]

        club_names = {t["team"] for t in clubs}
        top_players = sorted(
            [p for p in ds.players if p["team"] in club_names],
            key=ds.get_rating, reverse=True,
        )[:15]
        top_player_rows = [
            {
                "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
                "name":         f"{p['first_name']} {p['last_name']}",
                "team":         p["team"],
                "team_slug":    slug(p["team"]),
                "position":     p["position"],
                "pos_slug":     slug(p["position"]),
                "nationality":  p["nationality"],
                "nat_flag_str": (self.nat_to_flag.get(p["nationality"], "") + " ") if self.nat_to_flag.get(p["nationality"]) else "",
                "rating":       ds.get_rating(p),
                "rating_class": self._rating_class(ds.get_rating(p)),
            }
            for p in top_players
        ]

        breadcrumb = '<a href="/">Home</a> › <a href="/nations/">Nations</a> › ' + nation
        content = self.render(
            "nation",
            nav_links=NAV_LINKS,
            active="Nations",
            page_title=nation,
            header_title=f"{flag_str}{nation}",
            header_sub=f"{len(clubs)} {'club' if len(clubs) == 1 else 'clubs'}",
            breadcrumb=breadcrumb,
            leagued=leagued,
            unaffiliated=unaffiliated,
            unaffiliated_heading="Other clubs" if leagued_map else "Clubs",
            top_players=top_player_rows,
        )
        self.write_file(f"nations/{slug(nation)}/index.html", content)

    def _skill_bar(self, v):
        v = int(v)
        cls = "bar-gold" if v >= 80 else "bar-green" if v >= 60 else "bar-mid" if v >= 40 else "bar-low"
        return f'<div class="bar-wrap"><div class="bar {cls}" style="width:{v}%"></div><span>{v}</span></div>'

    def _skills_html(self, player):
        ds = self.ds
        key = (player["first_name"], player["last_name"], player["team"])
        s = ds.skills_by_player.get(key, {})
        pr_row = ds.pos_ratings_by_player.get(key, {})
        html = ""
        if s:
            html += '<details><summary>Skills</summary><div class="skill-grid">'
            for grp, cols in SKILL_GROUPS.items():
                html += f'<div><strong style="font-size:0.75rem;color:var(--gold)">{grp}</strong>'
                for c in cols:
                    html += f'<div class="skill-row"><span class="sk-label">{SKILL_LABELS[c]}</span>{self._skill_bar(s.get(c, 0))}</div>'
                html += "</div>"
            ungrouped = [c for c in SKILL_COLS if not any(c in v for v in SKILL_GROUPS.values())]
            if ungrouped:
                html += '<div><strong style="font-size:0.75rem;color:var(--gold)">Other</strong>'
                for c in ungrouped:
                    html += f'<div class="skill-row"><span class="sk-label">{SKILL_LABELS[c]}</span>{self._skill_bar(s.get(c, 0))}</div>'
                html += "</div>"
            html += "</div></details>"
        if pr_row:
            html += '<details><summary>Position ratings</summary><div class="skill-grid"><div>'
            for pos_code in POS_ORDER:
                v = int(pr_row.get(pos_code, 0) or 0)
                html += f'<div class="skill-row"><span class="sk-label"><a href="/positions/{slug(pos_code)}/" class="pos">{pos_code}</a></span>{self._skill_bar(v)}</div>'
            html += "</div></div></details>"
        return html

    def _build_best_xi(self, team_name):
        ds = self.ds
        players = ds.players_by_team[team_name]
        if len(players) < 7:
            return None

        GK_POS  = {"GK"}
        DEF_POS = {"RB", "CD", "LB", "RWB", "LWB", "SW"}
        MID_POS = {"DM", "RM", "LM", "AM", "RW", "LW", "FR"}
        ATT_POS = {"FOR", "SS"}

        by_skill = sorted(players, key=ds.get_rating, reverse=True)
        used = set()

        def pick(wanted, count, fallback=True):
            chosen = []
            for p in by_skill:
                if len(chosen) >= count: break
                if p["first_name"] + p["last_name"] not in used and p["position"] in wanted:
                    chosen.append(p)
                    used.add(p["first_name"] + p["last_name"])
            if fallback and len(chosen) < count:
                for p in by_skill:
                    if len(chosen) >= count: break
                    if p["first_name"] + p["last_name"] not in used:
                        chosen.append(p)
                        used.add(p["first_name"] + p["last_name"])
            return chosen

        def order_defs(ds): return sorted(ds, key=lambda p: {"LB":0,"LWB":0,"SW":1,"CD":1,"RWB":3,"RB":3}.get(p["position"], 2))
        def order_mids(ms): return sorted(ms, key=lambda p: {"LW":0,"LM":0,"DM":1,"RM":2,"AM":2,"RW":3,"FR":2}.get(p["position"], 1))

        gks  = pick(GK_POS, 1)
        defs = order_defs(pick(DEF_POS, 4))
        mids = order_mids(pick(MID_POS, 4))
        atts = pick(ATT_POS, 2)

        def bubble(p, gk=False):
            return {
                "position":    p["position"],
                "circle_class": "gk-circle" if gk else "",
                "last_name":   p["last_name"] or p["first_name"],
                "url":         f"/clubs/{slug(team_name)}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
                "rating":      ds.get_rating(p),
            }

        return [
            [bubble(p) for p in atts],
            [bubble(p) for p in mids],
            [bubble(p) for p in defs],
            [bubble(p, gk=True) for p in gks],
        ]

    def _linkify_trivia(self, text):
        for t in sorted(self.ds.teams, key=lambda t: -len(t["team"])):
            name = t["team"]
            url = f"/clubs/{slug(name)}/"
            text = re.sub(r"\b" + re.escape(name) + r"\b", f'<a href="{url}">{name}</a>', text)
        return text

    def write_clubs_page(self):
        ds = self.ds
        league_to_country = {lg: cn for cn, lgs in LEAGUE_GROUPS for lg in lgs}

        all_teams_sorted = sorted(ds.teams, key=lambda t: t["team"])
        letters = sorted(set(t["team"][0].upper() for t in all_teams_sorted))
        cur_letter = ""
        teams = []
        for t in all_teams_sorted:
            letter = t["team"][0].upper()
            players = ds.players_by_team[t["team"]]
            pc = len(players)
            avg = (sum(ds.get_rating(p) for p in players) / pc) if pc else 0
            stadium = t["stadium"].strip()
            stadium_url = None if re.match(r"^XX\d+$", stadium) else f"/stadiums/{slug(stadium)}/"

            # Nation column
            if t["league"] == "Others":
                nation = CLUB_NATIONS.get(t["team"], "")
            else:
                nation = league_to_country.get(t["league"], "")
            nation_flag = self.country_name_to_flag.get(nation, "")
            nation_html = (f'{nation_flag} ' if nation_flag else "") + (f'<a href="/nations/{slug(nation)}/">{nation}</a>' if nation else "")

            # League/Nation column
            if t["league"] != "Others":
                lg_flag = self.league_to_flag.get(t["league"], "")
                league_html = (f'{lg_flag} ' if lg_flag else "") + f'<a href="/leagues/{slug(t["league"])}/">{t["league"]}</a>'
            else:
                nat = CLUB_NATIONS.get(t["team"], "")
                nat_flag = self.country_name_to_flag.get(nat, "")
                league_html = (f'{nat_flag} ' if nat_flag else "") + (f'<a href="/nations/{slug(nat)}/">{nat}</a>' if nat else "Others")

            letter_anchor = letter if letter != cur_letter else None
            cur_letter = letter
            teams.append({
                "slug":          slug(t["team"]),
                "name":          t["team"],
                "letter_anchor": letter_anchor,
                "nation_html":   nation_html,
                "league_html":   league_html,
                "stadium":       stadium,
                "stadium_url":   stadium_url,
                "capacity":      int(t["capacity"] or 0),
                "player_count":  pc,
                "avg":           f"{avg:.1f}" if pc else "—",
                "avg_class":     self._rating_class(avg) if pc else "",
            })

        content = self.render(
            "clubs",
            nav_links=NAV_LINKS,
            active="Clubs",
            page_title="All Clubs",
            header_title="All Clubs",
            header_sub=f"{len(ds.teams):,} clubs",
            breadcrumb="",
            letters=letters,
            teams=teams,
        )
        self.write_file("clubs/index.html", content)

        for t in ds.teams:
            self._write_club_page(t)

    def _write_club_page(self, t):
        ds = self.ds
        team_name = t["team"]
        tslug = slug(team_name)
        players = ds.players_by_team[team_name]
        pc = len(players)
        avg = (sum(ds.get_rating(p) for p in players) / pc) if pc else 0

        # Stadium
        stadium = t["stadium"].strip()
        stadium_url = None if re.match(r"^XX\d+$", stadium) else f"/stadiums/{slug(stadium)}/"
        stadium_html = f'<a href="{stadium_url}">{stadium}</a>' if stadium_url else stadium

        # League/Nation card
        if t["league"] != "Others":
            league_card = f'<div class="stat">{t["league"]}</div><div class="label"><a href="/leagues/{slug(t["league"])}/">View league</a></div>'
        else:
            nation = CLUB_NATIONS.get(team_name)
            if nation:
                nation_flag = self.country_name_to_flag.get(nation, "")
                flag_str = f"{nation_flag} " if nation_flag else ""
                league_card = f'<div class="stat">{flag_str}{nation}</div><div class="label"><a href="/nations/{slug(nation)}/">View nation</a></div>'
            else:
                league_card = '<div class="stat">Others</div>'

        # Trivia
        trivia_text = CLUB_TRIVIA.get(tslug)
        trivia_html = self._linkify_trivia(trivia_text) if trivia_text else ""

        # Player-manager
        is_pm = t.get("is_player_manager") == "True"
        mgr_last = t.get("manager", "").split()[-1] if is_pm and t.get("manager") else ""

        # Squad rows
        squad_sorted = sorted(players, key=lambda p: int(p["shirt"]) if p["shirt"] else 99)
        squad = []
        for p in squad_sorted:
            nat = p["nationality"]
            nat_flag = self.nat_to_flag.get(nat, "")
            squad.append({
                "id":           f"{slug(p['first_name'])}-{slug(p['last_name'])}",
                "shirt":        p["shirt"],
                "pos_slug":     slug(p["position"]),
                "position":     p["position"],
                "first_name":   p["first_name"],
                "last_name":    p["last_name"],
                "is_pm":        is_pm and p["last_name"] == mgr_last,
                "skills_html":  self._skills_html(p),
                "nat_flag":     nat_flag,
                "nat_name":     nat,
                "nat_url":      f"/nationalities/{slug(nat)}/" if nat else None,
                "age":          p["age"],
                "dob":          p["dob"],
                "rating":       ds.get_rating(p),
                "rating_class": self._rating_class(ds.get_rating(p)),
            })

        # League/Nation sub-header
        if t["league"] == "Others":
            header_sub = CLUB_NATIONS.get(team_name, "Others")
        else:
            header_sub = t["league"]

        breadcrumb = f'<a href="/">Home</a> › <a href="/clubs/">Clubs</a> › {team_name}'
        content = self.render(
            "club",
            nav_links=NAV_LINKS,
            active="Clubs",
            page_title=team_name,
            header_title=team_name,
            header_sub=header_sub,
            breadcrumb=breadcrumb,
            team_slug=tslug,
            nickname=t.get("nickname", ""),
            league_card=league_card,
            stadium_html=stadium_html,
            capacity=int(t["capacity"] or 0),
            area=t.get("area", ""),
            manager=t.get("manager", ""),
            is_player_manager=is_pm,
            avg=f"{avg:.1f}" if pc else "—",
            avg_class=self._rating_class(avg) if pc else "",
            player_count=pc,
            trivia=trivia_html,
            best_xi=self._build_best_xi(team_name),
            squad=squad,
        )
        self.write_file(f"clubs/{tslug}/index.html", content)

    def write_players_page(self):
        ds = self.ds
        players_sorted = sorted(ds.players, key=lambda p: (p["last_name"].lstrip("-"), p["first_name"]))
        players = []
        for p in players_sorted:
            nat = p["nationality"]
            nat_flag = self.nat_to_flag.get(nat, "")

            if p["league"] != "Others":
                lg_flag = self.league_to_flag.get(p["league"], "")
                league_html = (f"{lg_flag} " if lg_flag else "") + f'<a href="/leagues/{slug(p["league"])}/">{p["league"]}</a>'
            else:
                nation = CLUB_NATIONS.get(p["team"], "")
                nat_f = self.country_name_to_flag.get(nation, "")
                league_html = (f"{nat_f} " if nat_f else "") + (f'<a href="/nations/{slug(nation)}/">{nation}</a>' if nation else "Others")

            players.append({
                "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
                "name":         f"{p['first_name']} {p['last_name']}",
                "team":         p["team"],
                "team_slug":    slug(p["team"]),
                "league_html":  league_html,
                "pos_slug":     slug(p["position"]),
                "position":     p["position"],
                "nat_flag":     nat_flag,
                "nat_name":     nat,
                "nat_slug":     slug(nat),
                "age":          p["age"],
                "dob":          p["dob"],
                "rating":       ds.get_rating(p),
                "rating_class": self._rating_class(ds.get_rating(p)),
            })

        content = self.render(
            "players",
            nav_links=NAV_LINKS,
            active="Players",
            page_title="Players",
            header_title="All Players",
            header_sub=f"{len(ds.players):,} players — search by name, club, position or nationality",
            breadcrumb="",
            total_players=len(ds.players),
            players=players,
        )
        self.write_file("players/index.html", content)


def main():
    parser = argparse.ArgumentParser(description="Generate FIFA Soccer Manager 97 website")
    parser.add_argument("--csv-dir", default=str(CSV_DIR), help="Input CSV directory")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output directory")
    args = parser.parse_args()

    scribe = Scribe(csv_dir=args.csv_dir, output_dir=args.out_dir)
    scribe.setup_output_path()
    scribe.write_homepage()
    scribe.write_leagues_page()
    scribe.write_nations_page()
    scribe.write_clubs_page()
    scribe.write_players_page()


if __name__ == "__main__":
    main()
