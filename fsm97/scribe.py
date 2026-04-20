import argparse
import re
import shutil
import unicodedata
from pathlib import Path

from chameleon import PageTemplateLoader

from fsm97.constants import LEAGUE_GROUPS, country_flag, CLUB_NATIONS, POS_ORDER, SKILL_COLS, SKILL_LABELS, SKILL_GROUPS
from fsm97.data import Dataset
from fsm97.generate_www import CLUB_TRIVIA, STADIUM_TRIVIA, PLAYER_TRIVIA, PLAYER_DISPLAY_NAMES, VIDEOS
from fsm97.credits import CREDITS, NO_PLAYER_MATCH


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

        for lg in ds.league_names:
            if lg == "Others":
                continue
            self._write_league_page(lg)

    def _write_league_page(self, lg):
        ds = self.ds
        teams = sorted(ds.teams_by_league[lg], key=lambda t: t["team"])
        flag = self.league_to_flag.get(lg, "")
        flag_str = f"{flag} " if flag else ""

        club_rows = []
        for t in teams:
            stadium = t["stadium"].strip()
            stadium_url = None if re.match(r"^XX\d+$", stadium) else f"/stadiums/{slug(stadium)}/"
            players = ds.players_by_team[t["team"]]
            pc = len(players)
            avg = (sum(ds.get_rating(p) for p in players) / pc) if pc else 0
            club_rows.append({
                "slug":        slug(t["team"]),
                "name":        t["team"],
                "nickname":    t["nickname"],
                "stadium":     stadium,
                "stadium_url": stadium_url,
                "capacity":    f"{int(t['capacity']):,}" if t["capacity"] else "—",
                "manager":     t["manager"],
                "avg":         f"{avg:.1f}" if pc else "—",
                "avg_class":   self._rating_class(avg) if pc else "",
            })

        top_players = sorted(
            [p for p in ds.players if p["league"] == lg],
            key=ds.get_rating, reverse=True,
        )[:15]
        player_rows = [self._pdict(p) for p in top_players]

        lg_slug = slug(lg)
        breadcrumb = f'<a href="/">Home</a> › <a href="/leagues/">Leagues</a> › {lg}'
        content = self.render(
            "league",
            nav_links=NAV_LINKS,
            active="Leagues",
            page_title=lg,
            header_title=f"{flag_str}{lg}",
            header_sub=f"{len(teams):,} clubs",
            breadcrumb=breadcrumb,
            lg_slug=lg_slug,
            club_rows=club_rows,
            player_rows=player_rows,
        )
        self.write_file(f"leagues/{lg_slug}/index.html", content)

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

    def _build_best_xi_from_players(self, players):
        ds = self.ds
        if len(players) < 7:
            return None

        GK_POS  = {"GK"}
        DEF_POS = {"RB", "CD", "LB", "RWB", "LWB", "SW"}
        MID_POS = {"DM", "RM", "LM", "AM", "RW", "LW", "FR"}
        ATT_POS = {"FOR", "SS"}

        by_skill = sorted(players, key=ds.get_rating, reverse=True)
        used = set()

        def pick(wanted, count):
            chosen = []
            for p in by_skill:
                if len(chosen) >= count: break
                if p["first_name"] + p["last_name"] not in used and p["position"] in wanted:
                    chosen.append(p)
                    used.add(p["first_name"] + p["last_name"])
            if len(chosen) < count:
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
                "position":     p["position"],
                "circle_class": "gk-circle" if gk else "",
                "last_name":    p["last_name"] or p["first_name"],
                "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
                "rating":       ds.get_rating(p),
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

            # League/Nation column
            if t["league"] != "Others":
                lg_flag = self.league_to_flag.get(t["league"], "")
                league_html = (f'{lg_flag} ' if lg_flag else "") + f'<a href="/leagues/{slug(t["league"])}/">{t["league"]}</a>'
            else:
                nat = CLUB_NATIONS.get(t["team"], "")
                nat_flag = self.country_name_to_flag.get(nat, "")
                league_html = (f'{nat_flag} ' if nat_flag else "") + (f'<a href="/nations/{slug(nat)}/">{nat}</a>' if nat else "")

            letter_anchor = letter if letter != cur_letter else None
            cur_letter = letter
            teams.append({
                "slug":          slug(t["team"]),
                "name":          t["team"],
                "letter_anchor": letter_anchor,
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
                league_html = (f"{nat_f} " if nat_f else "") + (f'<a href="/nations/{slug(nation)}/">{nation}</a>' if nation else "")

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


    def write_stats_page(self):
        self._write_stats_index()
        self._write_stats_top_players()
        self._write_stats_skill_leaders()
        self._write_stats_age_groups()
        self._write_stats_player_managers()
        self._write_stats_stadiums()
        self._write_stats_squads()
        self._write_stats_nationalities()
        self._write_stats_best_of()

    def _write_stats_index(self):
        content = self.render(
            "stats_index",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Stats & Records",
            header_title="Stats & Records",
            header_sub="",
            breadcrumb="",
        )
        self.write_file("stats/index.html", content)

    def _write_stats_top_players(self):
        ds = self.ds
        top50 = sorted(ds.players, key=ds.get_rating, reverse=True)[:50]
        top50_rows = [self._pdict(p) for p in top50]

        by_pos = []
        for pos in POS_ORDER:
            pp = sorted(ds.players, key=lambda p: self._pos_rating(p, pos), reverse=True)[:10]
            if not pp:
                continue
            info = ds.positions_info.get(pos, {})
            rows = []
            for p in pp:
                d = self._pdict(p)
                d["pos_rating"] = self._pos_rating(p, pos)
                d["pos_rating_class"] = self._rating_class(d["pos_rating"])
                rows.append(d)
            by_pos.append({
                "code":     pos,
                "slug":     slug(pos),
                "name":     info.get("position", ""),
                "players":  rows,
            })

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Top Players'
        content = self.render(
            "stats_top_players",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Top Players",
            header_title="Top Players",
            header_sub="",
            breadcrumb=breadcrumb,
            top50=top50_rows,
            by_pos=by_pos,
        )
        self.write_file("stats/top-players/index.html", content)

    def _write_stats_skill_leaders(self):
        ds = self.ds
        sections = []
        for col in SKILL_COLS:
            ranked = sorted(ds.skills, key=lambda s: int(s.get(col, 0) or 0), reverse=True)[:10]
            rows = []
            for s in ranked:
                key = (s["first_name"], s["last_name"], s["team"])
                p = next((p for p in ds.players if (p["first_name"], p["last_name"], p["team"]) == key), s)
                v = int(s.get(col, 0))
                nat = p.get("nationality", s.get("nationality", ""))
                rows.append({
                    "url":          f"/clubs/{slug(s['team'])}/#{slug(s['first_name'])}-{slug(s['last_name'])}",
                    "name":         f"{s['first_name']} {s['last_name']}",
                    "team":         s["team"],
                    "team_slug":    slug(s["team"]),
                    "nat_flag":     self.nat_to_flag.get(nat, ""),
                    "nat_name":     nat,
                    "nat_slug":     slug(nat),
                    "pos_slug":     slug(s.get("position", p.get("position", ""))),
                    "position":     s.get("position", p.get("position", "")),
                    "value":        v,
                    "value_class":  self._rating_class(v),
                })
            sections.append({"label": SKILL_LABELS[col], "rows": rows})

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Skill Leaders'
        content = self.render(
            "stats_skill_leaders",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Skill Leaders",
            header_title="Skill Leaders — Best in Every Category",
            header_sub="",
            breadcrumb=breadcrumb,
            sections=sections,
        )
        self.write_file("stats/skill-leaders/index.html", content)

    def _write_stats_age_groups(self):
        ds = self.ds
        age_groups = [
            ("15-19", 15, 19),
            ("20-29", 20, 29),
            ("30-39", 30, 39),
            ("40+",   40, 999),
        ]
        sections = []
        for label, lo, hi in age_groups:
            group = [p for p in ds.players if lo <= int(p["age"]) <= hi]
            top10 = sorted(group, key=ds.get_rating, reverse=True)[:10]
            if not top10:
                continue
            sections.append({
                "label":        label,
                "group_count":  len(group),
                "players":      [self._pdict(p) for p in top10],
            })

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Age Groups'
        content = self.render(
            "stats_age_groups",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Age Groups",
            header_title="Top Players by Age Group",
            header_sub="",
            breadcrumb=breadcrumb,
            sections=sections,
        )
        self.write_file("stats/age-groups/index.html", content)

    def _write_stats_player_managers(self):
        ds = self.ds
        pm_players = []
        for t in ds.teams:
            if t.get("is_player_manager") != "True":
                continue
            mgr_last = t["manager"].split()[-1] if t["manager"] else ""
            if not mgr_last:
                continue
            squad = ds.players_by_team.get(t["team"], [])
            match = next((p for p in squad if p["last_name"] == mgr_last), None)
            if match:
                pm_players.append(match)

        pm_players.sort(key=ds.get_rating, reverse=True)

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Player-Managers'
        content = self.render(
            "stats_player_managers",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Player-Managers",
            header_title="Player-Managers",
            header_sub="",
            breadcrumb=breadcrumb,
            total=len(pm_players),
            players=[self._pdict(p) for p in pm_players],
        )
        self.write_file("stats/player-managers/index.html", content)

    def _write_stats_stadiums(self):
        ds = self.ds
        league_to_country = {lg: cn for cn, lgs in LEAGUE_GROUPS for lg in lgs}
        named = sorted(
            ds.stadium_to_teams.items(),
            key=lambda x: int(x[1][0]["capacity"] or 0), reverse=True,
        )

        def stad_rows(entries):
            rows = []
            for i, (sname, ts) in enumerate(entries, 1):
                cap = int(ts[0]["capacity"] or 0)
                country = self._team_country(ts[0])
                country_flag = self.country_name_to_flag.get(country, "")
                cities = ", ".join(dict.fromkeys(t["area"] for t in ts if t["area"]))
                addr = ts[0]["stadium_address"] or ""
                location = ", ".join(x for x in [addr, cities] if x)
                clubs = [{"name": t["team"], "slug": slug(t["team"])} for t in ts]
                rows.append({
                    "rank":         i,
                    "slug":         slug(sname),
                    "name":         sname,
                    "location":     location,
                    "country":      country,
                    "country_flag": country_flag,
                    "country_slug": slug(country) if country else "",
                    "clubs":        clubs,
                    "capacity":     cap,
                })
            return rows

        top50 = stad_rows(named[:50])

        by_country = []
        for country, lgs in LEAGUE_GROUPS:
            if country == "Others":
                continue
            country_entries = [(s, ts) for s, ts in named if self._team_country(ts[0]) == country]
            if not country_entries:
                continue
            cflag = self.country_name_to_flag.get(country, "")
            by_country.append({
                "country":      country,
                "country_flag": cflag,
                "country_slug": slug(country),
                "rows":         stad_rows(country_entries[:10]),
            })

        others_entries = [(s, ts) for s, ts in named if ts[0]["league"] == "Others"]
        others_rows = stad_rows(others_entries[:10]) if others_entries else []

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Stadium Rankings'
        content = self.render(
            "stats_stadiums",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Stadium Rankings",
            header_title="Stadiums by Capacity",
            header_sub="",
            breadcrumb=breadcrumb,
            top50=top50,
            by_country=by_country,
            others_rows=others_rows,
        )
        self.write_file("stats/stadiums/index.html", content)

    def _write_stats_squads(self):
        ds = self.ds
        squads = []
        for t in ds.teams:
            pp = ds.players_by_team[t["team"]]
            if not pp:
                continue
            avg = sum(ds.get_rating(p) for p in pp) / len(pp)
            nats = len(set(p["nationality"] for p in pp if p["nationality"]))
            squads.append({
                "team_slug":    slug(t["team"]),
                "team":         t["team"],
                "league_html":  self._league_html(t["league"], t["team"]),
                "player_count": len(pp),
                "avg":          f"{avg:.1f}",
                "avg_class":    self._rating_class(avg),
                "nat_count":    nats,
            })
        squads.sort(key=lambda x: float(x["avg"]), reverse=True)
        for i, s in enumerate(squads, 1):
            s["rank"] = i

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Squad Rankings'
        content = self.render(
            "stats_squads",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Squad Rankings",
            header_title="Squad Rankings",
            header_sub="",
            breadcrumb=breadcrumb,
            squads=squads,
        )
        self.write_file("stats/squads/index.html", content)

    def _write_stats_nationalities(self):
        ds = self.ds
        from collections import defaultdict
        league_nat = defaultdict(lambda: defaultdict(int))
        for p in ds.players:
            league_nat[p["league"]][p["nationality"]] += 1

        by_league = []
        for lg in ds.league_names:
            nat_counts = league_nat[lg]
            total = sum(nat_counts.values())
            top_nats = sorted(nat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            by_league.append({
                "league_html": self._league_html(lg),
                "total":       total,
                "nat_count":   len(nat_counts),
                "top_nats":    [{"name": n, "count": c} for n, c in top_nats],
            })

        top20 = sorted(
            [(nat, pp) for nat, pp in ds.players_by_nationality.items() if nat],
            key=lambda x: len(x[1]), reverse=True,
        )[:20]
        top20_rows = []
        for nat, pp in top20:
            avg = sum(ds.get_rating(p) for p in pp) / len(pp)
            top20_rows.append({
                "nat":         nat,
                "slug":        slug(nat),
                "flag":        self.nat_to_flag.get(nat, ""),
                "country":     self.nat_to_country.get(nat, nat),
                "player_count": len(pp),
                "avg":         f"{avg:.1f}",
                "avg_class":   self._rating_class(avg),
            })

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Nationality Stats'
        content = self.render(
            "stats_nationalities",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Nationality Stats",
            header_title="Nationality Statistics",
            header_sub="",
            breadcrumb=breadcrumb,
            by_league=by_league,
            top20=top20_rows,
        )
        self.write_file("stats/nationalities/index.html", content)

    def _write_stats_best_of(self):
        ds = self.ds

        def nat_pos_rating(p):
            return self._pos_rating(p, p["position"])

        # Best per position
        best_by_pos = []
        for pos in POS_ORDER:
            best = max(ds.players, key=lambda p: self._pos_rating(p, pos))
            rating = self._pos_rating(best, pos)
            info = ds.positions_info.get(pos, {})
            d = self._pdict(best)
            d["pos_code"] = pos
            d["pos_full"] = info.get("position", "")
            d["pos_rating"] = rating
            d["pos_rating_class"] = self._rating_class(rating)
            best_by_pos.append(d)

        # Best per skill
        best_by_skill = []
        for col in SKILL_COLS:
            best_s = max(ds.skills, key=lambda s: int(s.get(col, 0) or 0))
            v = int(best_s.get(col, 0))
            nat = best_s.get("nationality", "")
            best_by_skill.append({
                "skill_label":  SKILL_LABELS[col],
                "url":          f"/clubs/{slug(best_s['team'])}/#{slug(best_s['first_name'])}-{slug(best_s['last_name'])}",
                "name":         f"{best_s['first_name']} {best_s['last_name']}",
                "team":         best_s["team"],
                "team_slug":    slug(best_s["team"]),
                "nat_flag":     self.nat_to_flag.get(nat, ""),
                "nat_name":     nat,
                "nat_slug":     slug(nat),
                "pos_slug":     slug(best_s.get("position", "")),
                "position":     best_s.get("position", ""),
                "value":        v,
                "value_class":  self._rating_class(v),
            })

        # Best per league
        best_by_league = []
        for lg in ds.league_names:
            pp = [p for p in ds.players if p["league"] == lg]
            if not pp:
                continue
            best = max(pp, key=nat_pos_rating)
            d = self._pdict(best)
            d["league_name"] = lg
            d["league_html"] = self._league_html(lg, best["team"])
            best_by_league.append(d)

        # Best per nationality
        best_by_nat = []
        for nat, pp in sorted(ds.players_by_nationality.items(), key=lambda x: x[0]):
            if not nat or len(pp) < 3:
                continue
            best = max(pp, key=nat_pos_rating)
            best_by_nat.append({
                "nat":         nat,
                "nat_slug":    slug(nat),
                "nat_flag":    self.nat_to_flag.get(nat, ""),
                "player_count": len(pp),
                "url":         f"/clubs/{slug(best['team'])}/#{slug(best['first_name'])}-{slug(best['last_name'])}",
                "name":        f"{best['first_name']} {best['last_name']}",
                "team":        best["team"],
                "team_slug":   slug(best["team"]),
                "rating":      nat_pos_rating(best),
                "rating_class": self._rating_class(nat_pos_rating(best)),
            })

        breadcrumb = '<a href="/">Home</a> › <a href="/stats/">Stats</a> › Best Of All'
        content = self.render(
            "stats_best_of",
            nav_links=NAV_LINKS,
            active="Stats",
            page_title="Best Of All",
            header_title="Best Of All",
            header_sub="",
            breadcrumb=breadcrumb,
            best_by_pos=best_by_pos,
            best_by_skill=best_by_skill,
            best_by_league=best_by_league,
            best_by_nat=best_by_nat,
        )
        self.write_file("stats/best-of/index.html", content)

    def write_nationalities_page(self):
        ds = self.ds
        nats_sorted = sorted(
            [(nat, pp) for nat, pp in ds.players_by_nationality.items() if nat],
            key=lambda x: len(x[1]), reverse=True,
        )
        rows = []
        for nat, pp in nats_sorted:
            avg = sum(ds.get_rating(p) for p in pp) / len(pp)
            country = self.nat_to_country.get(nat, nat)
            rows.append({
                "nat":         nat,
                "slug":        slug(nat),
                "flag":        self.nat_to_flag.get(nat, ""),
                "country":     country,
                "player_count": len(pp),
                "avg":         f"{avg:.1f}",
                "avg_class":   self._rating_class(avg),
            })

        content = self.render(
            "nationalities",
            nav_links=NAV_LINKS,
            active="Nationalities",
            page_title="Nationalities",
            header_title="Nationalities",
            header_sub=f"{len(nats_sorted)} nationalities represented",
            breadcrumb="",
            rows=rows,
        )
        self.write_file("nationalities/index.html", content)

        for nat, pp in nats_sorted:
            self._write_nationality_page(nat, pp)

    def _write_nationality_page(self, nat, pp):
        ds = self.ds
        flag = self.nat_to_flag.get(nat, "")
        flag_str = f"{flag} " if flag else ""

        pp_sorted = sorted(pp, key=ds.get_rating, reverse=True)
        by_league = {}
        for p in pp_sorted:
            by_league.setdefault(p["league"], True)

        best_xi = self._build_best_xi_from_players(pp_sorted)

        players = []
        for p in pp_sorted:
            lg = p["league"]
            if lg != "Others":
                lg_flag = self.league_to_flag.get(lg, "")
                league_html = (f"{lg_flag} " if lg_flag else "") + f'<a href="/leagues/{slug(lg)}/">{lg}</a>'
            else:
                nat_c = CLUB_NATIONS.get(p["team"], "")
                nat_c_flag = self.country_name_to_flag.get(nat_c, "")
                league_html = (f"{nat_c_flag} " if nat_c_flag else "") + (f'<a href="/nations/{slug(nat_c)}/">{nat_c}</a>' if nat_c else "")
            players.append({
                "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
                "name":         f"{p['first_name']} {p['last_name']}",
                "team":         p["team"],
                "team_slug":    slug(p["team"]),
                "league_html":  league_html,
                "pos_slug":     slug(p["position"]),
                "position":     p["position"],
                "age":          p["age"],
                "dob":          p["dob"],
                "rating":       ds.get_rating(p),
                "rating_class": self._rating_class(ds.get_rating(p)),
            })

        nat_slug = slug(nat)
        breadcrumb = f'<a href="/">Home</a> › <a href="/nationalities/">Nationalities</a> › {nat}'
        content = self.render(
            "nationality",
            nav_links=NAV_LINKS,
            active="Nationalities",
            page_title=nat,
            header_title=f"{flag_str}{nat} Players",
            header_sub=f"{len(pp):,} players",
            breadcrumb=breadcrumb,
            nat=nat,
            nat_slug=nat_slug,
            league_count=len(by_league),
            best_xi=best_xi,
            players=players,
        )
        self.write_file(f"nationalities/{nat_slug}/index.html", content)

    def _team_country(self, t):
        league_to_country = {lg: cn for cn, lgs in LEAGUE_GROUPS for lg in lgs}
        if t["league"] == "Others":
            return CLUB_NATIONS.get(t["team"], "")
        return league_to_country.get(t["league"], "")

    def _league_html(self, league, team=None):
        if league != "Others":
            flag = self.league_to_flag.get(league, "")
            return (f"{flag} " if flag else "") + f'<a href="/leagues/{slug(league)}/">{league}</a>'
        nat = CLUB_NATIONS.get(team, "") if team else ""
        flag = self.country_name_to_flag.get(nat, "")
        return (f"{flag} " if flag else "") + (f'<a href="/nations/{slug(nat)}/">{nat}</a>' if nat else "")

    def _pdict(self, p):
        """Common player row dict used across stats pages."""
        ds = self.ds
        nat = p["nationality"]
        return {
            "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
            "name":         f"{p['first_name']} {p['last_name']}",
            "team":         p["team"],
            "team_slug":    slug(p["team"]),
            "league_html":  self._league_html(p["league"], p["team"]),
            "pos_slug":     slug(p["position"]),
            "position":     p["position"],
            "nat_flag":     self.nat_to_flag.get(nat, ""),
            "nat_name":     nat,
            "nat_slug":     slug(nat),
            "age":          p["age"],
            "dob":          p["dob"],
            "rating":       ds.get_rating(p),
            "rating_class": self._rating_class(ds.get_rating(p)),
        }

    def _pos_rating(self, p, pos):
        key = (p["first_name"], p["last_name"], p["team"])
        r = self.ds.pos_ratings_by_player.get(key)
        return int(r[pos]) if r else 0

    def _player_row(self, p, pos, show_nat_pos=True, nat_pos_blank_if_same=False):
        ds = self.ds
        nat = p["nationality"]
        nat_flag = self.nat_to_flag.get(nat, "")
        lg = p["league"]
        if lg != "Others":
            lg_flag = self.league_to_flag.get(lg, "")
            league_html = (f"{lg_flag} " if lg_flag else "") + f'<a href="/leagues/{slug(lg)}/">{lg}</a>'
        else:
            nat_c = CLUB_NATIONS.get(p["team"], "")
            nat_c_flag = self.country_name_to_flag.get(nat_c, "")
            league_html = (f"{nat_c_flag} " if nat_c_flag else "") + (f'<a href="/nations/{slug(nat_c)}/">{nat_c}</a>' if nat_c else "")
        nat_pos = p["position"]
        rating = self._pos_rating(p, pos)
        return {
            "url":          f"/clubs/{slug(p['team'])}/#{slug(p['first_name'])}-{slug(p['last_name'])}",
            "name":         f"{p['first_name']} {p['last_name']}",
            "team":         p["team"],
            "team_slug":    slug(p["team"]),
            "league_html":  league_html,
            "nat_flag":     nat_flag,
            "nat_name":     nat,
            "nat_slug":     slug(nat),
            "nat_pos":      nat_pos,
            "nat_pos_slug": slug(nat_pos),
            "nat_pos_same": nat_pos == pos,
            "age":          p["age"],
            "dob":          p["dob"],
            "rating":       rating,
            "rating_class": self._rating_class(rating),
        }

    def write_positions_page(self):
        ds = self.ds
        zone_of = {info["abbreviation"]: info["zone"] for info in ds.positions_info.values()}
        rows = []
        for pos in POS_ORDER:
            info = ds.positions_info.get(pos, {})
            zone = info.get("zone", "")
            pp_zone = [p for p in ds.players if zone_of.get(p["position"]) == zone]
            if not pp_zone:
                continue
            avg = sum(self._pos_rating(p, pos) for p in pp_zone) / len(pp_zone)
            rows.append({
                "code":         pos,
                "slug":         slug(pos),
                "position":     info.get("position", ""),
                "zone":         zone,
                "player_count": len(pp_zone),
                "avg":          f"{avg:.1f}",
                "avg_class":    self._rating_class(avg),
            })

        content = self.render(
            "positions",
            nav_links=NAV_LINKS,
            active="Positions",
            page_title="Positions",
            header_title="Playing Positions",
            header_sub="",
            breadcrumb="",
            positions=rows,
        )
        self.write_file("positions/index.html", content)

        for pos in POS_ORDER:
            if not ds.players_by_position.get(pos):
                continue
            self._write_position_page(pos)

    def _write_position_page(self, pos):
        ds = self.ds
        zone_of = {info["abbreviation"]: info["zone"] for info in ds.positions_info.values()}
        info = ds.positions_info.get(pos, {})
        zone = info.get("zone", "")

        pp_zone = [p for p in ds.players if zone_of.get(p["position"]) == zone]
        pp_zone_sorted = sorted(pp_zone, key=lambda p: self._pos_rating(p, pos), reverse=True)
        players = [self._player_row(p, pos) for p in pp_zone_sorted]

        outside = [p for p in ds.players if zone_of.get(p["position"]) != zone]
        top_outside = sorted(outside, key=lambda p: self._pos_rating(p, pos), reverse=True)[:10]
        surprising = [self._player_row(p, pos) for p in top_outside]

        pos_slug = slug(pos)
        breadcrumb = f'<a href="/">Home</a> › <a href="/positions/">Positions</a> › {pos}'
        content = self.render(
            "position",
            nav_links=NAV_LINKS,
            active="Positions",
            page_title=f"{pos} — {info.get('position', '')}",
            header_title=info.get("position", pos),
            header_sub=f"{pos} · {zone} · {len(pp_zone_sorted):,} players",
            breadcrumb=breadcrumb,
            pos=pos,
            pos_slug=pos_slug,
            zone=zone,
            player_count=len(pp_zone_sorted),
            players=players,
            surprising=surprising,
        )
        self.write_file(f"positions/{pos_slug}/index.html", content)

    def write_stadiums_page(self):
        ds = self.ds
        named = {s: ts for s, ts in ds.stadium_to_teams.items()}
        all_sorted = sorted(named.items(), key=lambda x: int(x[1][0]["capacity"] or 0), reverse=True)

        rows = []
        for i, (sname, ts) in enumerate(all_sorted, 1):
            cap = int(ts[0]["capacity"] or 0)
            country = self._team_country(ts[0])
            country_flag = self.country_name_to_flag.get(country, "")
            cities = ", ".join(dict.fromkeys(t["area"] for t in ts if t["area"]))
            addr = ts[0]["stadium_address"] or ""
            location = ", ".join(x for x in [addr, cities] if x)
            clubs = [{"name": t["team"], "slug": slug(t["team"])} for t in ts]
            rows.append({
                "rank":         i,
                "slug":         slug(sname),
                "name":         sname,
                "location":     location,
                "country":      country,
                "country_flag": country_flag,
                "country_slug": slug(country) if country else "",
                "clubs":        clubs,
                "capacity":     cap,
            })

        content = self.render(
            "stadiums",
            nav_links=NAV_LINKS,
            active="Stadiums",
            page_title="Stadiums",
            header_title="All Stadiums",
            header_sub=f"{len(named)} named stadiums",
            breadcrumb="",
            stadiums=rows,
        )
        self.write_file("stadiums/index.html", content)

        for sname, ts in named.items():
            self._write_stadium_page(sname, ts)

    def _write_stadium_page(self, sname, ts):
        ds = self.ds
        sslug = slug(sname)
        cap = int(ts[0]["capacity"] or 0)
        cities = ", ".join(dict.fromkeys(t["area"] for t in ts if t["area"]))
        addr = ts[0]["stadium_address"] or ""
        country = self._team_country(ts[0])
        country_flag = self.country_name_to_flag.get(country, "")

        trivia_text = STADIUM_TRIVIA.get(sslug)
        trivia = self._linkify_trivia(trivia_text) if trivia_text else ""

        club_cards = []
        for t in ts:
            players = ds.players_by_team[t["team"]]
            pc = len(players)
            avg = (sum(ds.get_rating(p) for p in players) / pc) if pc else 0
            lg = t["league"]
            if lg != "Others":
                lg_flag = self.league_to_flag.get(lg, "")
                league_html = (f"{lg_flag} " if lg_flag else "") + f'<a href="/leagues/{slug(lg)}/">{lg}</a>'
            else:
                nat = CLUB_NATIONS.get(t["team"], "")
                nat_flag = self.country_name_to_flag.get(nat, "")
                league_html = (f"{nat_flag} " if nat_flag else "") + (f'<a href="/nations/{slug(nat)}/">{nat}</a>' if nat else "")
            club_cards.append({
                "name":        t["team"],
                "slug":        slug(t["team"]),
                "league_html": league_html,
                "avg":         f"{avg:.1f}" if pc else "—",
                "avg_class":   self._rating_class(avg) if pc else "",
            })

        breadcrumb = '<a href="/">Home</a> › <a href="/stadiums/">Stadiums</a> › ' + sname
        content = self.render(
            "stadium",
            nav_links=NAV_LINKS,
            active="Stadiums",
            page_title=sname,
            header_title=sname,
            header_sub=f"Capacity {cap:,}" + (f" · {cities}" if cities else ""),
            breadcrumb=breadcrumb,
            trivia=trivia,
            capacity=cap,
            address=addr,
            area=cities,
            country=country,
            country_flag=country_flag,
            country_slug=slug(country) if country else "",
            shared=len(ts) > 1,
            club_count=len(ts),
            club_cards=club_cards,
        )
        self.write_file(f"stadiums/{sslug}/index.html", content)

    def write_events_page(self):
        CATEGORY_ORDER = [
            ("windfall",          "Windfalls"),
            ("financial_event",   "Financial Events"),
            ("financial_warning", "Financial Warnings"),
            ("match_disruption",  "Match Disruptions"),
            ("pitch_event",       "Pitch Events"),
            ("pitch_warning",     "Pitch Warnings"),
            ("general_event",     "General Events"),
            ("player_event",      "Player Events"),
            ("player_message",    "Player Messages"),
            ("injury",            "Injuries"),
            ("retirement",        "Retirements"),
            ("dismissal",         "Dismissal"),
            ("discipline",        "Discipline"),
            ("season_result",     "Season Results"),
            ("competition",       "Cup Competition"),
            ("function_room",     "Function Room"),
            ("facility",          "Stadium Facilities"),
            ("misc",              "Miscellaneous"),
        ]
        from collections import defaultdict
        by_cat = defaultdict(list)
        for s in self.ds.strings:
            by_cat[s["category"]].append(s)

        total = sum(len(v) for v in by_cat.values())
        categories = []
        for cat_key, cat_label in CATEGORY_ORDER:
            events = by_cat.get(cat_key, [])
            if not events:
                continue
            categories.append({
                "key":    cat_key,
                "label":  cat_label,
                "events": [
                    {
                        "id":       re.sub(r"[^\w-]", "-", ev["title"].lower()).strip("-"),
                        "title":    ev["title"],
                        "text":     ev["text"],
                        "recovery": ev["recovery"],
                    }
                    for ev in events
                ],
            })

        content = self.render(
            "events",
            nav_links=NAV_LINKS,
            active="Events",
            page_title="In-Game Events",
            header_title="In-Game Events",
            header_sub="Random events and messages from FIFA Soccer Manager 97",
            breadcrumb="",
            total=total,
            categories=categories,
        )
        self.write_file("events/index.html", content)

    def write_trivia_page(self):
        ds = self.ds

        # Index
        content = self.render(
            "trivia",
            nav_links=NAV_LINKS,
            active="Trivia",
            page_title="Trivia",
            header_title="Real World Trivia",
            header_sub="1996/97 season context",
            breadcrumb="",
        )
        self.write_file("trivia/index.html", content)

        # Players sub-page
        players_by_name = {}
        for p in ds.players:
            players_by_name.setdefault((p["first_name"], p["last_name"]), []).append(p)

        player_entries = []
        for (first, last), text in PLAYER_TRIVIA.items():
            matches = players_by_name.get((first, last), [])
            display = PLAYER_DISPLAY_NAMES.get((first, last), f"{first} {last}")
            if matches:
                p = matches[0]
                nat = p["nationality"]
                player_entries.append({
                    "url":          f"/clubs/{slug(p['team'])}/#{slug(first)}-{slug(last)}",
                    "name":         display,
                    "team":         p["team"],
                    "team_slug":    slug(p["team"]),
                    "pos_slug":     slug(p["position"]),
                    "position":     p["position"],
                    "nat_flag":     self.nat_to_flag.get(nat, ""),
                    "nat_name":     nat,
                    "nat_slug":     slug(nat),
                    "rating":       ds.get_rating(p),
                    "rating_class": self._rating_class(ds.get_rating(p)),
                    "trivia":       self._linkify_trivia(text),
                    "found":        True,
                })
            else:
                player_entries.append({
                    "name":   display,
                    "trivia": self._linkify_trivia(text),
                    "found":  False,
                })

        content = self.render(
            "trivia_players",
            nav_links=NAV_LINKS,
            active="Trivia",
            page_title="Player Trivia",
            header_title="Player Trivia",
            header_sub="Notable player stories",
            breadcrumb='<a href="/">Home</a> › <a href="/trivia/">Trivia</a> › Players',
            entries=player_entries,
        )
        self.write_file("trivia/players/index.html", content)

        # Stadiums sub-page
        stadium_entries = []
        for sslug, text in STADIUM_TRIVIA.items():
            match_name = next((s for s in ds.stadium_to_teams if slug(s) == sslug), None)
            if match_name:
                ts = ds.stadium_to_teams[match_name]
                cap = int(ts[0]["capacity"] or 0)
                clubs = [{"name": t["team"], "slug": slug(t["team"])} for t in ts]
                stadium_entries.append({
                    "slug":     sslug,
                    "name":     match_name,
                    "clubs":    clubs,
                    "capacity": cap,
                    "trivia":   self._linkify_trivia(text),
                    "found":    True,
                })
            else:
                stadium_entries.append({
                    "name":   sslug.replace("-", " ").title(),
                    "trivia": self._linkify_trivia(text),
                    "found":  False,
                })

        content = self.render(
            "trivia_stadiums",
            nav_links=NAV_LINKS,
            active="Trivia",
            page_title="Stadium Trivia",
            header_title="Stadium Trivia",
            header_sub="The grounds and their histories",
            breadcrumb='<a href="/">Home</a> › <a href="/trivia/">Trivia</a> › Stadiums',
            entries=stadium_entries,
        )
        self.write_file("trivia/stadiums/index.html", content)

        # Clubs sub-page
        from fsm97.constants import TEAM_NAMES
        slug_aliases = {slug(old): slug(new) for old, new in TEAM_NAMES.items()}
        teams_by_slug = {slug(t["team"]): t for t in ds.teams}
        club_entries = []
        for cslug, text in CLUB_TRIVIA.items():
            resolved = slug_aliases.get(cslug, cslug)
            t = teams_by_slug.get(resolved)
            if t:
                club_entries.append({
                    "slug":        slug(t["team"]),
                    "name":        t["team"],
                    "league_html": self._league_html(t["league"], t["team"]),
                    "trivia":      self._linkify_trivia(text),
                    "found":       True,
                })
            else:
                club_entries.append({
                    "name":   cslug.replace("-", " ").title(),
                    "trivia": self._linkify_trivia(text),
                    "found":  False,
                })

        content = self.render(
            "trivia_clubs",
            nav_links=NAV_LINKS,
            active="Trivia",
            page_title="Club Trivia",
            header_title="Club Trivia",
            header_sub="Club stories from the era",
            breadcrumb='<a href="/">Home</a> › <a href="/trivia/">Trivia</a> › Clubs',
            entries=club_entries,
        )
        self.write_file("trivia/clubs/index.html", content)

    def write_videos_page(self):
        content = self.render(
            "videos",
            nav_links=NAV_LINKS,
            active="Videos",
            page_title="Videos",
            header_title="Game Videos",
            header_sub="FMV cutscenes from FIFA Soccer Manager 97",
            breadcrumb="",
            videos=VIDEOS,
        )
        self.write_file("videos/index.html", content)

    def write_credits_page(self):
        ds = self.ds
        players_by_name = {}
        for p in ds.players:
            players_by_name.setdefault((p["first_name"], p["last_name"]), []).append(p)

        seen = {}
        for first, last, role in CREDITS:
            key = (first, last)
            if key not in seen:
                seen[key] = []
            if role:
                seen[key].append(role)

        rows = []
        for (first, last), roles in seen.items():
            matches = [] if (first, last) in NO_PLAYER_MATCH else players_by_name.get((first, last), [])
            row = {
                "first":    first,
                "last":     last,
                "name":     f"{first} {last}",
                "role":     ", ".join(roles),
                "found":    bool(matches),
                "also":     [],
            }
            if matches:
                p = matches[0]
                nat = p["nationality"]
                row.update({
                    "url":          f"/clubs/{slug(p['team'])}/#{slug(first)}-{slug(last)}",
                    "team":         p["team"],
                    "team_slug":    slug(p["team"]),
                    "pos_slug":     slug(p["position"]),
                    "position":     p["position"],
                    "nat_flag":     self.nat_to_flag.get(nat, ""),
                    "nat_name":     nat,
                    "nat_slug":     slug(nat),
                    "age":          p["age"],
                    "dob":          p["dob"],
                    "rating":       ds.get_rating(p),
                    "rating_class": self._rating_class(ds.get_rating(p)),
                })
                if len(matches) > 1:
                    row["also"] = [
                        {"team": m["team"], "team_slug": slug(m["team"]),
                         "url": f"/clubs/{slug(m['team'])}/#{slug(first)}-{slug(last)}"}
                        for m in matches[1:]
                    ]
            rows.append(row)

        unique_people = list(seen.keys())
        matches_count = sum(
            1 for key in unique_people
            if key not in NO_PLAYER_MATCH and players_by_name.get(key)
        )

        content = self.render(
            "credits",
            nav_links=NAV_LINKS,
            active="Credits",
            page_title="Game Credits",
            header_title="Game Credits",
            header_sub="The team behind FIFA Soccer Manager 97",
            breadcrumb="",
            rows=rows,
            matches_count=matches_count,
            total_people=len(unique_people),
        )
        self.write_file("credits/index.html", content)

    def write_sitemap(self, base_url):
        ds = self.ds
        urls = [
            "/", "/leagues/", "/nations/", "/clubs/", "/stadiums/",
            "/positions/", "/nationalities/", "/players/",
            "/stats/", "/stats/top-players/", "/stats/skill-leaders/",
            "/stats/age-groups/", "/stats/player-managers/", "/stats/stadiums/",
            "/stats/squads/", "/stats/nationalities/", "/stats/best-of/",
            "/events/", "/trivia/", "/trivia/players/", "/trivia/stadiums/",
            "/trivia/clubs/", "/videos/", "/credits/",
        ]
        for lg in sorted(ds.league_names):
            if lg != "Others":
                urls.append(f"/leagues/{slug(lg)}/")
        for nation in ds.nation_names:
            urls.append(f"/nations/{slug(nation)}/")
        for sname in sorted(ds.stadium_to_teams):
            urls.append(f"/stadiums/{slug(sname)}/")
        for t in sorted(ds.teams, key=lambda t: t["team"]):
            urls.append(f"/clubs/{slug(t['team'])}/")
        for pos in POS_ORDER:
            if ds.players_by_position.get(pos):
                urls.append(f"/positions/{slug(pos)}/")
        for nat in sorted(ds.players_by_nationality):
            if nat:
                urls.append(f"/nationalities/{slug(nat)}/")

        template = self.templates["sitemap"]
        content = template(base_url=base_url.rstrip("/"), urls=urls)
        (self.output_dir / "sitemap.xml").write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate FIFA Soccer Manager 97 website")
    parser.add_argument("--csv-dir", default=str(CSV_DIR), help="Input CSV directory")
    parser.add_argument("--out-dir", default=str(OUT_DIR), help="Output directory")
    parser.add_argument("--base-url", default=None, help="Base URL for sitemap (e.g. https://example.com)")
    args = parser.parse_args()

    scribe = Scribe(csv_dir=args.csv_dir, output_dir=args.out_dir)
    scribe.setup_output_path()
    scribe.write_homepage()
    scribe.write_leagues_page()
    scribe.write_nations_page()
    scribe.write_clubs_page()
    scribe.write_players_page()
    scribe.write_positions_page()
    scribe.write_nationalities_page()
    scribe.write_stadiums_page()
    scribe.write_stats_page()
    scribe.write_events_page()
    scribe.write_trivia_page()
    scribe.write_videos_page()
    scribe.write_credits_page()
    if args.base_url:
        scribe.write_sitemap(args.base_url)


if __name__ == "__main__":
    main()
