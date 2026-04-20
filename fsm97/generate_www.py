#!/usr/bin/env python3
"""FIFA Soccer Manager 97 — Static Site Generator"""

import argparse
import os, re, unicodedata
from collections import defaultdict

from fsm97.constants import (
    SKILL_COLS, SKILL_LABELS, SKILL_GROUPS, POS_ORDER,
    LEAGUE_GROUPS, TEAM_NAMES, country_flag,
)
from fsm97.credits import CREDITS, NO_PLAYER_MATCH
from fsm97.data import Dataset

CSV_DIR  = None
OUT_DIR  = None
BASE_URL = None

ds                     = None
teams_raw              = None
players_raw            = None
skills_raw             = None
positions_raw          = None
countries_raw          = None
teams_by_slug          = None
league_names           = None
teams_by_league        = None
players_by_team        = None
skills_by_player       = None
players_by_nationality = None
players_by_position    = None
positions_info         = None
stadium_to_teams       = None
prating                = None
pos_ratings_by_player  = None
max_cap                = None
pos_order              = None
team_by_name           = None
nat_to_country         = None
nat_to_flag            = None
league_to_flag         = None
country_name_to_flag   = None

def pr(p):
    """Return position rating for a player dict."""
    return ds.get_rating(p)

# ── Country labels for "Others" teams ─────────────────────────────────────────
# Maps full team names (post-TEAM_NAMES correction) to their home country.
# Used to show a meaningful country label instead of "Others" on team pages.

OTHERS_COUNTRIES = {
    # Albania
    'Teuta Durres':        'Albania',
    # Armenia
    'Shirak Gyumri':       'Armenia',
    # Austria
    'Admira Wacker':       'Austria',
    'Austria Vienna':      'Austria',
    'Rapid Vienna':        'Austria',
    # Azerbaijan
    'Kapaz Ganja':         'Azerbaijan',
    # Belarus
    'Dinamo Minsk':        'Belarus',
    # Belgium
    'Anderlecht':          'Belgium',
    'Antwerp':             'Belgium',
    'Club Brugge':         'Belgium',
    'Lierse':              'Belgium',
    'Standard Liege':      'Belgium',
    # Bulgaria
    'CSKA Sofia':          'Bulgaria',
    'Leveski Sofia':       'Bulgaria',
    'Neftochimik':         'Bulgaria',
    'Slavia Sofia':        'Bulgaria',
    # Croatia
    'Hadjuk Split':        'Croatia',
    # Cyprus
    'APOEL Nicosia':       'Cyprus',
    'Omonia Nicosia':      'Cyprus',
    # Czech Republic
    'Banik Ostrava':       'Czech Republic',
    'Slavia Prague':       'Czech Republic',
    'Sparta Prague':       'Czech Republic',
    # Denmark
    'Aarhus':              'Denmark',
    'Brondby':             'Denmark',
    'Odense':              'Denmark',
    'Silkeborg':           'Denmark',
    # England
    'EA All Stars':        'England',
    'EA Select XI':        'England',
    'Kidderminster':       'England',
    'Rushden & Diamonds':  'England',
    # Estonia
    'Flora':               'Estonia',
    # Faroe Islands
    'Itrottarfelag':       'Faroe Islands',
    # Finland
    'MYPA':                'Finland',
    # France
    'Ales':                'France',
    'Angers':              'France',
    'Dunkerque':           'France',
    'Poitiers':            'France',
    # Georgia
    'Dinamo Tbilisi':      'Georgia',
    'Samtredia':           'Georgia',
    # Germany
    '1. FC Nürnberg':      'Germany',
    'Chemnitz':            'Germany',
    'Hannover 96':         'Germany',
    'Wattenscheid':        'Germany',
    # Greece
    'Athens':              'Greece',
    'Olympiakos':          'Greece',
    'Panathinaikos':       'Greece',
    # Hungary
    'Budapest':            'Hungary',
    'Ferencvaros':         'Hungary',
    # Iceland
    'Hafnarfjardar':       'Iceland',
    # Israel
    'Betar Jerusalem':     'Israel',
    # Italy
    'Ancona':              'Italy',
    'Avellino':            'Italy',
    'Fidelis Andria':      'Italy',
    'Pistoiese':           'Italy',
    # Latvia
    'Skonto Riga':         'Latvia',
    # Liechtenstein
    'Vaduz':               'Liechtenstein',
    # Lithuania
    'Inkaraz Grifas':      'Lithuania',
    # Luxembourg
    'Jeunesse':            'Luxembourg',
    'Spora':               'Luxembourg',
    # Malta
    'Hibernians':          'Malta',
    'Sliema':              'Malta',
    # Moldova
    'Tiligul Tiraspol':    'Moldova',
    # Netherlands
    'Ajax':                'Netherlands',
    'Feyenoord':           'Netherlands',
    'PSV Eindhoven':       'Netherlands',
    'Twente':              'Netherlands',
    'Vitesse':             'Netherlands',
    # Northern Ireland
    'Crusaders':           'Northern Ireland',
    'Derry':               'Northern Ireland',
    'Glenavon':            'Northern Ireland',
    'Linfield':            'Northern Ireland',
    # Norway
    'Lillestrom':          'Norway',
    'Rosenborg':           'Norway',
    'Stravanger':          'Norway',
    # Poland
    'Katowice':            'Poland',
    'Legia Warsaw':        'Poland',
    'Widzew Lodz':         'Poland',
    # Portugal
    'Belenenses':          'Portugal',
    'Benfica':             'Portugal',
    'Boavista':            'Portugal',
    'Porto':               'Portugal',
    'Sporting Lisbon':     'Portugal',
    # Republic of Ireland
    'Bohemians':           'Republic of Ireland',
    'Shamrock':            'Republic of Ireland',
    # Romania
    'Dinamo Bucharest':    'Romania',
    'Rapid Bucharest':     'Romania',
    'Steaua Bucharest':    'Romania',
    'Uni Craiova':         'Romania',
    # Russia
    'Alania Vladikavkaz':  'Russia',
    'CSKA Moscow':         'Russia',
    'Dinamo Moscow':       'Russia',
    'Rotor Volvograd':     'Russia',
    'Spartak Moscow':      'Russia',
    # San Marino
    'Tre Fiori':           'San Marino',
    # Serbia
    'Partizan':            'Serbia',
    'Partizan Belgrade':   'Serbia',
    'RS Belgrade':         'Serbia',
    # Slovakia
    'Slovan Bratislava':   'Slovakia',
    # Slovenia
    'Olimpija Ljubljana':  'Slovenia',
    # Spain
    'Atlético Madrid':     'Spain',
    'Deportivo La Coruña': 'Spain',
    'FC Barcelona':        'Spain',
    'Real Madrid':         'Spain',
    'Real Zaragoza':       'Spain',
    # Sweden
    'Gothenburg':          'Sweden',
    'Halmstads':           'Sweden',
    'Malmo':               'Sweden',
    # Switzerland
    'Grasshoppers':        'Switzerland',
    'Servette':            'Switzerland',
    'Sion':                'Switzerland',
    # Turkey
    'Besiktas':            'Turkey',
    'Fenerbache':          'Turkey',
    'Galatasaray':         'Turkey',
    # Ukraine
    'Dinamo Kiev':         'Ukraine',
    'Karpaty Lviv':        'Ukraine',
    # Wales
    'Aberystwyth':         'Wales',
}


def team_league_label(t):
    """Return a display label for a team's league (country name for Others teams)."""
    if t['league'] == 'Others':
        return OTHERS_COUNTRIES.get(t['team'], 'Others')
    return t['league']

_league_to_country = {lg: country for country, leagues in LEAGUE_GROUPS for lg in leagues}

def team_country(t):
    """Return the country a team is based in."""
    if t['league'] == 'Others':
        return OTHERS_COUNTRIES.get(t['team'], 'Others')
    return _league_to_country.get(t['league'], '')

# ── Utilities ──────────────────────────────────────────────────────────────────

def slug(s):
    s = unicodedata.normalize('NFD', str(s))
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-') or 'unknown'

def h(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def rating_class(v):
    v = float(v)
    if v >= 70: return 'rat-gold'
    if v >= 60: return 'rat-green'
    if v >= 50: return 'rat-mid'
    return 'rat-low'

def skill_bar(v):
    v = int(v)
    cls = 'bar-gold' if v>=80 else 'bar-green' if v>=60 else 'bar-mid' if v>=40 else 'bar-low'
    return f'<div class="bar-wrap"><div class="bar {cls}" style="width:{v}%"></div><span>{v}</span></div>'

# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg:      #0d1f14;
  --bg2:     #162b1e;
  --bg3:     #1e3a2a;
  --border:  #2d6a4f;
  --accent:  #4caf50;
  --gold:    #ffd700;
  --text:    #ddeedd;
  --muted:   #8aab8a;
  --red:     #e06060;
  --link:    #6fcf7f;
}
body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text);
       font-size: 15px; line-height: 1.5; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; color: var(--accent); }
nav { background: #0a1a10; border-bottom: 2px solid var(--border); padding: 0 1.5rem;
      display: flex; align-items: center; gap: 0; position: sticky; top: 0; z-index: 100; }
.nav-brand { font-weight: 700; font-size: 1rem; color: var(--gold); padding: 0.7rem 1rem 0.7rem 0;
             border-right: 1px solid var(--border); margin-right: 0.5rem; white-space: nowrap; }
nav a { color: var(--muted); padding: 0.7rem 0.75rem; display: inline-block; font-size: 0.88rem; }
nav a:hover, nav a.active { color: var(--text); text-decoration: none; background: var(--bg3); }
header { background: var(--bg2); border-bottom: 1px solid var(--border); padding: 1.5rem 2rem 1.2rem; }
header h1 { font-size: 1.8rem; color: var(--gold); }
header .sub { color: var(--muted); font-size: 0.9rem; margin-top: 0.3rem; }
.breadcrumb { font-size: 0.82rem; color: var(--muted); margin-top: 0.5rem; }
.breadcrumb a { color: var(--muted); }
.breadcrumb a:hover { color: var(--link); }
main { max-width: 1200px; margin: 0 auto; padding: 1.5rem 2rem 3rem; }
h2 { font-size: 1.3rem; color: var(--accent); margin: 1.5rem 0 0.7rem; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
h3 { font-size: 1.05rem; color: var(--gold); margin: 1.2rem 0 0.5rem; }
p  { margin: 0.5rem 0; color: var(--text); }
.muted { color: var(--muted); }
.section { margin-bottom: 2rem; }
/* Cards */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin: 1rem 0; }
.card { background: var(--bg2); border: 1px solid var(--border); border-radius: 6px;
        padding: 1rem; transition: border-color 0.2s; }
.card:hover { border-color: var(--accent); }
.card h3 { margin-top: 0; font-size: 0.95rem; }
.card .stat { font-size: 1.4rem; font-weight: 700; color: var(--gold); }
.card .label { font-size: 0.8rem; color: var(--muted); }
/* Tables */
table { width: 100%; border-collapse: collapse; margin: 0.5rem 0 1.5rem; font-size: 0.88rem; }
thead th { background: var(--bg3); color: var(--gold); text-align: left;
           padding: 0.5rem 0.7rem; font-weight: 600; border-bottom: 2px solid var(--border); }
tbody tr:nth-child(even) { background: var(--bg2); }
tbody tr:hover { background: #1f3d2a; }
td { padding: 0.4rem 0.7rem; border-bottom: 1px solid #1a3020; vertical-align: middle; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
th.num { text-align: right; }
/* Rating badges */
.rat-gold  { background: #5a4a00; color: var(--gold); border-radius: 4px; padding: 1px 6px; font-weight: 700; }
.rat-green { background: #1a4a1a; color: #7fff7f; border-radius: 4px; padding: 1px 6px; font-weight: 700; }
.rat-mid   { background: #2a3a1a; color: #afc; border-radius: 4px; padding: 1px 6px; }
.rat-low   { background: #1a1a1a; color: var(--muted); border-radius: 4px; padding: 1px 6px; }
/* Bars */
.bar-wrap { display: flex; align-items: center; gap: 6px; }
.bar-wrap span { font-size: 0.8rem; color: var(--muted); min-width: 2ch; }
.bar { height: 8px; border-radius: 4px; min-width: 2px; }
.bar-gold  { background: var(--gold); }
.bar-green { background: var(--accent); }
.bar-mid   { background: #7aaa7a; }
.bar-low   { background: #4a6a4a; }
/* Skill grid */
.skill-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
              gap: 0.4rem 1rem; margin: 0.5rem 0; }
.skill-row  { display: flex; align-items: center; gap: 8px; font-size: 0.82rem; }
.skill-row .sk-label { width: 80px; color: var(--muted); flex-shrink: 0; }
/* Position badge */
.pos { display: inline-block; background: var(--bg3); border: 1px solid var(--border);
       border-radius: 3px; padding: 0 5px; font-size: 0.78rem; color: var(--gold);
       font-weight: 600; min-width: 2.5rem; text-align: center; }
/* Details/summary */
details { margin: 0.3rem 0; }
details summary { cursor: pointer; color: var(--muted); font-size: 0.82rem; user-select: none; }
details summary:hover { color: var(--link); }
details[open] summary { color: var(--accent); margin-bottom: 0.5rem; }
/* Stat highlights */
.highlights { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin: 1rem 0; }
.hl { background: var(--bg2); border: 1px solid var(--border); border-radius: 6px; padding: 0.8rem 1rem; }
a:has(> .hl):hover .hl { border-color: var(--accent); }
.hl .hl-val { font-size: 1.6rem; font-weight: 700; color: var(--gold); }
.hl .hl-lbl { font-size: 0.78rem; color: var(--muted); }
.hl .hl-sub { font-size: 0.85rem; color: var(--link); }
/* Trivia box */
.trivia { background: #0f2820; border-left: 3px solid var(--gold); padding: 0.8rem 1rem;
          margin: 1rem 0; border-radius: 0 6px 6px 0; font-size: 0.9rem; color: var(--text); }
.trivia strong { color: var(--gold); }
/* Nationality flag-ish */
.nat { font-size: 0.82rem; color: var(--muted); }
footer { border-top: 1px solid var(--border); padding: 1rem 2rem; text-align: center;
         color: var(--muted); font-size: 0.8rem; margin-top: 2rem; }
/* Search (static filter) */
.filter-bar { display: flex; gap: 0.5rem; margin: 0.5rem 0 1rem; flex-wrap: wrap; }
.filter-bar input { background: var(--bg2); border: 1px solid var(--border); color: var(--text);
                    padding: 0.4rem 0.7rem; border-radius: 4px; font-size: 0.88rem; width: 240px; }
.filter-bar input::placeholder { color: var(--muted); }
/* Sortable headers */
thead th[data-sort] { cursor: pointer; user-select: none; white-space: nowrap; }
thead th[data-sort]:hover { color: var(--accent); }
thead th[data-sort]::after { content: ' ⇅'; opacity: 0.4; font-size: 0.75em; }
thead th[data-sort].sort-asc::after  { content: ' ▲'; opacity: 1; }
thead th[data-sort].sort-desc::after { content: ' ▼'; opacity: 1; }
/* Pitch / formation */
.pitch { background: linear-gradient(to bottom, #1a5c2a 0%, #236b33 40%, #1e6330 60%, #1a5c2a 100%);
         border: 2px solid #2d8a45; border-radius: 8px; padding: 1.2rem 0.5rem;
         margin: 0.5rem 0 1.5rem; position: relative; overflow: hidden;
         max-width: 50%; }
@media (max-width: 700px) { .pitch { max-width: 100%; } }
.pitch::before { content: ''; position: absolute; top: 50%; left: 0; right: 0;
                 height: 1px; background: rgba(255,255,255,0.15); }
.pitch::after  { content: ''; position: absolute; left: 50%; top: 50%;
                 transform: translate(-50%,-50%);
                 width: 80px; height: 80px; border-radius: 50%;
                 border: 1px solid rgba(255,255,255,0.15); }
.formation-row { display: flex; justify-content: space-around; align-items: flex-start;
                 margin: 0.6rem 0; position: relative; z-index: 1; }
.p-bubble { text-align: center; width: 90px; }
.p-circle { width: 52px; height: 52px; border-radius: 50%; margin: 0 auto 4px;
            border: 2px solid rgba(255,255,255,0.5); background: rgba(0,0,0,0.45);
            display: flex; align-items: center; justify-content: center;
            font-size: 0.72rem; font-weight: 700; color: #fff; }
.p-circle.gk-circle { border-color: var(--gold); color: var(--gold); }
.p-name { font-size: 0.72rem; color: #fff; line-height: 1.2; word-break: break-word; }
.p-name a { color: #cfc; text-decoration: none; }
.p-name a:hover { text-decoration: underline; }
.p-avg  { font-size: 0.68rem; color: rgba(255,255,255,0.65); }
/* Alphabet nav */
.alpha { display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0.5rem 0 1rem; }
.alpha a { background: var(--bg2); border: 1px solid var(--border); border-radius: 3px;
           padding: 0.15rem 0.4rem; font-size: 0.8rem; color: var(--muted); }
.alpha a:hover { color: var(--link); border-color: var(--accent); text-decoration: none; }
@media (max-width: 700px) {
  main { padding: 1rem; }
  header { padding: 1rem; }
  .highlights { grid-template-columns: repeat(2, 1fr); }
  nav { flex-wrap: wrap; }
}
"""

# ── HTML template ──────────────────────────────────────────────────────────────

def page(title, body, depth=1, active=None, breadcrumb='', header_title=None, header_sub=''):
    prefix = '../' * depth
    nav_links = [
        ('Home',          f'{prefix}'),
        ('Leagues',       f'{prefix}leagues/'),
        ('Teams',         f'{prefix}teams/'),
        ('Players',       f'{prefix}players/'),
        ('Stadiums',      f'{prefix}stadiums/'),
        ('Positions',     f'{prefix}positions/'),
        ('Nationalities', f'{prefix}nationalities/'),
        ('Stats',         f'{prefix}stats/'),
        ('Trivia',        f'{prefix}trivia/'),
        ('Credits',       f'{prefix}credits/'),
    ]
    nav_html = '\n'.join(
        f'<a href="{url}" class="{"active" if active==label else ""}">{label}</a>'
        for label, url in nav_links
    )
    ht = header_title or title
    hdr = f'<header><h1>{h(ht)}</h1>'
    if header_sub:
        hdr += f'<div class="sub">{header_sub}</div>'
    if breadcrumb:
        hdr += f'<div class="breadcrumb">{breadcrumb}</div>'
    hdr += '</header>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} — FIFA Soccer Manager 97</title>
<link rel="stylesheet" href="{prefix}style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'><text y='1em' font-size='16'>⚽</text></svg>">
</head>
<body>
<nav>
<span class="nav-brand">⚽ FSM97</span>
{nav_html}
</nav>
{hdr}
<main>{body}</main>
<footer>FIFA Soccer Manager 97 · Data extracted from <code>SM97.DAT</code> · A project by <a href="https://bennuttall.com/">Ben Nuttall</a> · See the project on <a href="https://github.com/bennuttall/fsm-97-data">GitHub</a></footer>
<script>
document.querySelectorAll('input[data-filter]').forEach(function(inp){{
  var tbl = document.getElementById(inp.dataset.filter);
  inp.addEventListener('input', function(){{
    var q = this.value.toLowerCase();
    tbl.querySelectorAll('tbody tr').forEach(function(tr){{
      tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
  }});
}});
document.querySelectorAll('thead th[data-sort]').forEach(function(th){{
  var asc = true;
  th.addEventListener('click', function(){{
    var tbl = th.closest('table');
    var idx = Array.from(th.parentElement.children).indexOf(th);
    var rows = Array.from(tbl.tBodies[0].querySelectorAll('tr'));
    rows.sort(function(a,b){{
      var ac = a.cells[idx], bc = b.cells[idx];
      var av = ac ? (ac.dataset.sortValue !== undefined ? ac.dataset.sortValue : ac.textContent.trim()) : '';
      var bv = bc ? (bc.dataset.sortValue !== undefined ? bc.dataset.sortValue : bc.textContent.trim()) : '';
      var an = parseFloat(av.replace(/[^0-9.-]/g,'')),
          bn = parseFloat(bv.replace(/[^0-9.-]/g,''));
      if(!isNaN(an)&&!isNaN(bn)) return asc ? an-bn : bn-an;
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});
    rows.forEach(function(r){{ tbl.tBodies[0].appendChild(r); }});
    tbl.querySelectorAll('thead th[data-sort]').forEach(function(t){{
      t.classList.remove('sort-asc','sort-desc');
    }});
    th.classList.add(asc ? 'sort-asc' : 'sort-desc');
    asc = !asc;
  }});
}});
(function(){{
  var h = window.location.hash;
  if (!h) return;
  var el = document.getElementById(h.slice(1));
  if (!el) return;
  el.querySelectorAll('details').forEach(function(d){{ d.open = true; }});
}})();
</script>
</body>
</html>"""

def bc(parts, prefix=''):
    # parts = list of (label, url) or (label, None) for current
    bits = ['<a href="{}">Home</a>'.format(prefix)]
    for label, url in parts:
        if url:
            bits.append(f'<a href="{url}">{h(label)}</a>')
        else:
            bits.append(h(label))
    return ' › '.join(bits)

# ── Trivia data ────────────────────────────────────────────────────────────────

PLAYER_TRIVIA = {
    ('Peter','Shilton'): "England's most capped player with 125 international appearances. At 47, Shilton was still playing professionally in 1996–97, making him likely the oldest outfield player in this database.",
    ('Eric','Cantona'): "The mercurial French captain inspired Manchester United to the 1995–96 Premier League and FA Cup double, returning from his infamous 8-month ban for the kung-fu kick at Selhurst Park. Retired suddenly in May 1997, aged 30.",
    ('Alan','Shearer'): "Signed by hometown club Newcastle United from Blackburn Rovers in summer 1996 for a then-world-record £15 million fee, rejecting Manchester United to do so. Newcastle United's record goalscorer.",
    ('Dennis','Bergkamp'): "Joined Arsenal from Internazionale for £7.5m in June 1995. His well-documented fear of flying meant he travelled to away fixtures by car and rail, missing European away legs entirely — but his performances at home made him worth it.",
    ('Patrick','Vieira'): "Arsène Wenger's first signing as Arsenal manager in summer 1996, purchased from AC Milan's reserves for £3.5m. The 20-year-old Frenchman would go on to captain Arsenal's Invincibles.",
    ('Ruud','Gullit'): "Appointed Chelsea player-manager in 1996, becoming the first continental European to manage a top-flight English club. Led Chelsea to FA Cup glory in 1997.",
    ('Zinedine','Zidane'): "In his second season at Juventus having moved from Bordeaux in 1996 for £3m. Two years later he scored twice in the World Cup final as France beat Brazil 3–0.",
    ('Ryan','Giggs'): "Despite representing England at schoolboy level, Giggs chose to play internationally for Wales — the country of his birth. A United stalwart since age 13.",
    ('Peter','Schmeichel'): "The commanding Danish goalkeeper was the cornerstone of United's success under Sir Alex Ferguson, winning five Premier League titles. His son Kasper would later follow him into professional football.",
    ('Lilian','Thuram'): "The composed Parma right back scored both goals in France's 1998 World Cup semi-final win over Croatia — the only international goals in his record-breaking 142-cap career.",
    ('David','Ginola'): "The charismatic French winger thrilled Premier League fans at Newcastle United and later Tottenham Hotspur. Widely blamed for France's failure to qualify for USA 94 after a misplaced pass in the final qualifier against Bulgaria.",
    ('Paolo','Maldini'): "AC Milan's legendary left back, widely considered one of the greatest defenders of all time. Spent his entire 25-year career at the club. Son of former Milan captain Cesare Maldini.",
    ('Da Silva','Roberto Carlos'): "Real Madrid's marauding left back, famous for the seemingly impossible free-kick against France in 1997 — struck with such swerve that the ball appeared to curve around the wall before bending back.",
    ('Luiz Nazario De Lima','Ronaldo'): "The Brazilian phenomenon joined FC Barcelona from PSV in 1996 and won FIFA World Player of the Year in his debut season. Moved to Internazionale at the end of 1996–97.",
    ('George','Weah'): "The Liberian striker at AC Milan was the reigning FIFA World Player of the Year (1995) and African, European and World Player of the Year simultaneously — the only African player to win the Ballon d'Or.",
    ('Roy','Keane'): "Manchester United's combative Irish captain. One of the most influential midfielders of his era; his famous Juventus performance in the 1999 Champions League semi-final — despite knowing he'd miss the final — is the stuff of legend.",
    ('Steve','Bruce'): "Joined Birmingham City as player-manager in 1996 after 11 trophy-laden years at Manchester United, where he never received an international cap despite being one of the best centre-backs in the country.",
    ('Gianluca','Pagliuca'): "Internazionale's veteran goalkeeper who famously became the first goalkeeper sent off in World Cup history, against Norway at USA 94.",
}

# Override display names for players whose stored name differs from their known name
PLAYER_DISPLAY_NAMES = {
    ('Da Silva', 'Roberto Carlos'):         'Roberto Carlos',
    ('Luiz Nazario De Lima', 'Ronaldo'):    'Ronaldo',
}

STADIUM_TRIVIA = {
    'highbury': "Opened in 1913, Highbury was Arsenal's home for 93 years. The Art Deco East and West Stands are Grade II listed buildings. Arsenal moved to the Emirates in 2006; the pitch now forms the centrepiece of 'Highbury Square' residential development.",
    'the-dell': "Southampton's intimate Victorian ground (opened 1898) held just 15,000 — one of the smallest capacities in top-flight history. Its steep banks and cramped atmosphere made it a genuine fortress. Southampton left for St Mary's in 2001.",
    'selhurst-park': "Crystal Palace's home since 1905. Wimbledon have groundshared here since 1991 after selling Plough Lane. The arrangement was meant to be temporary; Wimbledon eventually relocated to Milton Keynes as MK Dons.",
    'baseball-ground': "Derby County's ground from 1895, named after a baseball pitch that originally occupied the site. The 1996–97 season was Derby's last here before moving to the purpose-built Pride Park, which opened in 1997.",
    'ewood-park': "Blackburn Rovers' home since 1882, with a capacity of 31,800 in 1996–97. Substantially redeveloped in the early 1990s following the club's rise under Jack Walker's investment. Hosted Euro 96 group matches.",
    'stamford-bridge': "Chelsea's home since the club's founding in 1905. The ground had been substantially redeveloped through the 1990s. In 1996–97 it held 31,500 — further expansion followed in later years.",
    'highfield-road': "Coventry City's home from 1899 to 2005. Became the first all-seater top-flight ground in England when it was converted in 1981, ahead of the Taylor Report's requirements. Coventry left for the Ricoh Arena in 2005.",
    'elland-road': "Leeds United's home since 1919, with a capacity of 40,000 in 1996–97. One of the great English football grounds, with a passionate atmosphere — particularly the Kop end. The ground saw major redevelopment in the early 1990s following the title win.",
    'the-city-ground': "Nottingham Forest's home since 1898, situated on the banks of the River Trent directly opposite Notts County's Meadow Lane. Hosted some of Brian Clough's greatest European nights; capacity stood at around 30,000 in 1996–97.",
    'riverside-stadium': "Middlesbrough's gleaming new stadium opened in August 1995, replacing the ageing Ayresome Park. One of the first post-Taylor Report football-specific stadiums in England.",
    'hillsborough': "Sheffield Wednesday's imposing home, capacity 36,020 in 1996–97. Forever associated with the disaster of 15 April 1989, when 97 Liverpool supporters lost their lives during an FA Cup semi-final. The ground has since been significantly redeveloped.",
    'white-hart-lane': "Tottenham Hotspur's home from 1899 to 2017, with a capacity around 33,000 in 1996–97. Famous for its intimidating atmosphere and the iconic 'cockerel' atop the main stand. Spurs moved to their new 62,000-capacity stadium on the same site in 2019.",
    'upton-park': "West Ham United's home — officially the Boleyn Ground — from 1904 to 2016. The Bobby Moore Stand and intimate terracing gave the ground a distinctive character. West Ham United relocated to the London Stadium (former Olympic venue) in 2016.",
    'filbert-street': "Leicester City's home from 1891 to 2002. A compact ground with a capacity of around 22,500, it witnessed Leicester's remarkable run of near-misses and promotions. The club moved to the Walkers Stadium (now King Power Stadium) in 2002.",
    'roker-park': "Sunderland's home from 1898 to 1997 — the 1996–97 season was the last played here before the move to the Stadium of Light. Roker Park hosted three matches in the 1966 World Cup. At its peak it held over 75,000; by 1997 capacity was 22,657.",
    'racecourse-ground': "One of the oldest international football venues in the world — Wales played their first-ever home international here in 1877. Wrexham's home throughout their long Football League history, it remains a well-maintained non-league ground today.",
    'san-siro': "The Stadio Giuseppe Meazza — San Siro to everyone — has been shared by AC Milan and Internazionale since 1947. At 85,847 it is the largest stadium in this database. The iconic cylindrical staircase towers were added for the 1990 World Cup.",
    'olimpico': "Rome's Olympic Stadium, shared by Lazio and Roma since 1953. Designed for the 1960 Summer Olympics, it later hosted the 1990 World Cup Final.",
    'delle-alpi': "Opened for the 1990 World Cup and shared by Juventus and Torino, the Delle Alpi was almost immediately unpopular for its poor sightlines. It was demolished in 2008 and replaced by the current Juventus Stadium.",
    'nou-camp': "Camp Nou is the largest football stadium in Europe with a capacity of 115,000 — the biggest in this entire database. Built in 1957, it has hosted World Cup matches, European Cup finals, and an Olympic final.",
    'old-trafford': "Manchester United's 'Theatre of Dreams', opened in 1910. The 55,000 capacity in 1996–97 reflected recent expansion; it has since grown beyond 74,000.",
    'ibrox-stadium': "Rangers' imposing home in Govan was substantially rebuilt after the Ibrox disaster of 2 January 1971, when 66 supporters died in a stairway crush. The main stand is a B-listed building.",
    'celtic-park': "Known as 'Paradise', Celtic Park was comprehensively rebuilt in the mid-1990s as an all-seater stadium. The atmosphere on European nights is considered among the most intense in world football.",
    'anfield': "Liverpool's home since 1892. The famous Spion Kop terrace — once holding 28,000 standing fans — was converted to all-seater in 1994 following the Taylor Report.",
    'villa-park': "Aston Villa's home since 1897, one of England's great football grounds. Hosted three matches at the 1966 World Cup and three at Euro 96.",
    'st-james-park': "One of the most atmospheric stadiums in England. Newcastle United's vast home dominates the city skyline; the Gallowgate and Leazes ends create a cauldron of noise on matchday.",
    'goodison-park': "Everton's home since 1892, Goodison was the first purpose-built football ground in England. It hosted World Cup matches in 1966.",
    'bernabeu': "Real Madrid's iconic home, opened in 1947 and named after club president Santiago Bernabéu. The 95,000-capacity stadium is the jewel of the Santiago Bernabéu district of Madrid.",
    'das-antas': "Porto's compact, atmospheric home. The club would later move to the Estádio do Dragão, built for Euro 2004.",
    'parc-des-princes': "Paris Saint-Germain's modern home in the 16th arrondissement, shared with the French national team. Opened in 1972, its distinctive circular form replaced the original 1897 ground on the same site.",
    'westfalenstadion': "Borussia Dortmund's famous yellow wall — the Südtribüne — holds 25,000 standing fans, making it the largest single terrace in European football.",
}

CLUB_TRIVIA = {
    'aston-villa': "Under Brian Little, Villa were a solid top-half Premier League side in 1996–97. Won the League Cup in 1996 — their first major trophy since the 1982 European Cup. Dwight Yorke was emerging as one of the league's most exciting forwards.",
    'blackburn-rovers': "Reigning Premier League champions (1994–95), Blackburn Rovers had a difficult title defence and finished 7th. The departure of Alan Shearer to Newcastle United cast a long shadow over the 1996–97 campaign.",
    'coventry': "Under Ron Atkinson, Coventry City survived in the Premier League through a combination of resilience and late drama — a recurring pattern at Highfield Road. The Sky Blues had won the FA Cup in 1987, their only major honour.",
    'everton': "Joe Royle's Everton were FA Cup winners in 1995, beating Manchester United. In 1996–97 they finished mid-table with Duncan Ferguson as their talisman. The club had been one of the dominant forces of English football in the 1980s under Howard Kendall.",
    'leeds': "Howard Wilkinson's Leeds United were the last First Division champions before the Premier League era (1991–92). By 1996–97 they had declined from that peak; Tony Yeboah was the squad's standout attacker.",
    'leicester': "Newly promoted to the Premier League under Martin O'Neill, Leicester City were considered relegation candidates. Steve Claridge's controversial last-minute goal in the 1996 First Division play-off final had secured their place in the top flight.",
    'sheffield-wednesday': "One of the founding members of the Football League, Wednesday had won the league title four times, most recently in 1930. In 1996–97 they were a steady mid-table Premier League side with David Pleat as manager.",
    'southampton': "Matt Le Tissier's club. The Saints' mercurial playmaker was so loyal to Southampton that he repeatedly turned down bigger clubs. Graeme Souness was manager in 1996–97; the club were 16th in the league, narrowly avoiding relegation.",
    'sunderland': "Newly promoted under Peter Reid, Sunderland's 1996–97 campaign was their farewell to Roker Park before moving to the Stadium of Light. They were relegated at the end of the season, finishing bottom of the Premier League.",
    'tottenham': "Gerry Francis managed Spurs in 1996–97, with Teddy Sheringham leading the attack. The club had won the FA Cup twice in the early 1990s but were struggling to keep pace with the league's elite. Finished 10th.",
    'west-ham': "Harry Redknapp's West Ham United were known for producing young English talent — Rio Ferdinand and Frank Lampard Jr were both coming through the academy. Finished 8th in 1996–97, their best position for several years.",
    'wimbledon': "The 'Crazy Gang' — FA Cup winners in 1988 — spent the entire 1996–97 season as tenants at Selhurst Park, sharing with Crystal Palace. Despite finishing 8th in the Premier League, the club had no stadium of their own and regularly attracted fewer than 10,000 fans.",
    'derby-county': "Newly promoted to the Premier League in 1996 under Jim Smith, Derby County played their final season at the historic Baseball Ground before moving to the purpose-built Pride Park in 1997. Finished a respectable 12th in their first top-flight season for eight years.",
    'middlesbrough': "Had a tumultuous 1996–97 season — deducted three points for failing to fulfil a fixture at Blackburn Rovers due to illness (a decision widely regarded as harsh), ultimately contributing to their relegation despite reaching both the League Cup and FA Cup finals.",
    'newcastle-united': "Finished runner-up in 1995–96 having led the league by 12 points at one stage. In summer 1996 Kevin Keegan resigned, Les Ferdinand was sold, and Alan Shearer arrived for a world-record fee. Finished second again in 1996–97 under Kenny Dalglish.",
    'arsenal': "Arsenal appointed Arsène Wenger as manager in September 1996, after the season had started under Bruce Rioch. Wenger's arrival would transform the club, the league, and English football. The Frenchman introduced continental methods, diet, and a new philosophy.",
    'chelsea': "Under player-manager Ruud Gullit, Chelsea were becoming a cosmopolitan force with Italian, Dutch and French internationals. Won the FA Cup in 1997 — their first major trophy since 1971.",
    'manchester-united': "Reigning double-winners, Manchester United dominated the era under Sir Alex Ferguson. Eric Cantona retired unexpectedly in May 1997, but United still claimed the league title.",
    'wrexham': "The Welsh club in the English Football League. Best remembered for their 1992 FA Cup upset of Arsenal, Wrexham played in the lower leagues throughout this period.",
    'liverpool': "Under Roy Evans, Liverpool were stylish but inconsistent. The 'Spice Boys' tag — partly referring to their cream FA Cup final suits — haunted a squad that underachieved relative to its talent.",
    'nottingham-forest': "European Cup winners in 1979 and 1980 under Brian Clough. In 1996–97 they were relegated from the Premier League, though the club retained many talented players.",
    'boavista': "Porto's city rivals, playing at the compact Estádio do Bessa. Would go on to claim a remarkable Portuguese championship in 2000–01 under João Vale e Azevedo.",
    'ajax': "European Champions in 1995, Ajax's star-studded squad began to break up as players departed for Italy and Spain. Patrick Kluivert, Clarence Seedorf, Marc Overmars and Edgar Davids all left in this era.",
    'borussia-dortmund': "Bundesliga champions and on the brink of Champions League glory — they would beat Juventus in the 1997 Champions League Final, with Karl-Heinz Riedle scoring twice.",
    'juventus': "Italian champions with a formidable squad including Zidane, Del Piero, Vieri and the Frenchmen Deschamps, Thuram (at Parma), and Vieira (by now at Arsenal). Won the Champions League in 1996.",
    'fc-barcelona': "Johan Cruyff's long managerial reign had just ended (1996) and Bobby Robson was appointed. Despite the transition, FC Barcelona's squad included Ronaldo, Figo, and Giovanni van Bronckhorst.",
    'real-madrid': "Under Fabio Capello, Real Madrid won La Liga in 1996–97 but were still building towards the Galácticos era. The squad included Roberto Carlos, Seedorf, Raúl and Míchel.",
    'rosenborg': "Norway's dominant club force. Regularly reached the Champions League group stage, famously beating AC Milan 2–1 in the 1996–97 edition.",
    'ea-all-stars': "A hidden team of EA Sports developers who worked on FIFA Soccer Manager 97, inserted into the game as an easter egg. Their fictional home — the Electronic Arts Vellodrome in Berkshire — boasts a tongue-in-cheek capacity of 90,000. The players are real staff members, each assigned positions and ratings.",
    'ea-select-xi': "A second developer easter egg team alongside EA All Stars, representing a curated selection from the EA Sports team. Like their counterparts, they play out of the Electronic Arts Vellodrome. The Select XI carries no squad in the game data — presumably the devs couldn't agree on the starting eleven.",
    'dumbarton': "One of the oldest clubs in the world and a founder member of the Scottish Football League in 1890. Dumbarton were relegated from the Scottish First Division at the end of the 1995–96 season and appear in the game database without a squad as a result.",
    'hamilton-academical': "Hamilton Academical were relegated from the Scottish First Division at the end of the 1995–96 season. They appear in the game database without a squad as a result. The club are named after the local academy school, making them one of the few clubs in world football with an educational institution in their name.",
}

# ── Links helpers ──────────────────────────────────────────────────────────────

def team_url(team_name, prefix=''):
    return f"{prefix}teams/{slug(team_name)}/"

def league_url(league_name, prefix=''):
    return f"{prefix}leagues/{slug(league_name)}/"

def league_cell(league_name, prefix=''):
    if not league_name:
        return ''
    flag     = league_to_flag.get(league_name, '')
    flag_str = f'{flag} ' if flag else ''
    return f'{flag_str}{tlink(league_name, league_url(league_name, prefix))}'

def country_display(name):
    if not name:
        return ''
    flag     = country_name_to_flag.get(name, '')
    flag_str = f'{flag} ' if flag else ''
    return f'{flag_str}{h(name)}'

def linkify_trivia(text, prefix='../'):
    """HTML-escape trivia text and auto-link any team names mentioned."""
    escaped = h(text)
    for t in sorted(teams_raw, key=lambda t: -len(t['team'])):
        name = h(t['team'])
        url  = f'{prefix}teams/{slug(t["team"])}/'
        escaped = re.sub(
            r'\b' + re.escape(name) + r'\b',
            f'<a href="{url}">{name}</a>',
            escaped,
        )
    return escaped

def stadium_url(stadium_name, prefix=''):
    if re.match(r'^XX\d+$', stadium_name.strip()):
        return None
    return f"{prefix}stadiums/{slug(stadium_name)}/"

def nat_url(nationality, prefix=''):
    if not nationality:
        return None
    return f"{prefix}nationalities/{slug(nationality)}/"

def nat_cell(nationality, prefix=''):
    if not nationality:
        return ''
    country  = nat_to_country.get(nationality, nationality)
    flag     = nat_to_flag.get(nationality, '')
    flag_str = f'{flag} ' if flag else ''
    return f'<span title="{h(country)}">{flag_str}{tlink(nationality, nat_url(nationality, prefix))}</span>'

def pos_url(position, prefix=''):
    if not position:
        return None
    return f"{prefix}positions/{slug(position)}/"

def player_anchor(first, last, team):
    return f"{team_url(team)}#{slug(first)}-{slug(last)}"

def tlink(name, url, cls=''):
    return f'<a href="{url}" class="{cls}">{h(name)}</a>' if url else h(name)

# ── Shared helpers ─────────────────────────────────────────────────────────────

def squad_table(team_name, prefix, show_league=False):
    players = sorted(players_by_team[team_name],
                     key=lambda p: int(p['shirt']) if p['shirt'] else 99)
    if not players:
        return '<p class="muted">No player data.</p>'
    t = team_by_name.get(team_name, {})
    is_pm = t.get('is_player_manager') == 'True'
    mgr_last = t.get('manager', '').split()[-1] if is_pm and t.get('manager') else ''
    pm_star = ' <span title="Player-Manager" style="cursor:default">⭐</span>'
    rows = []
    for p in players:
        pid = f"{slug(p['first_name'])}-{slug(p['last_name'])}"
        key = (p['first_name'], p['last_name'], p['team'])
        s = skills_by_player.get(key, {})
        nat_link = nat_cell(p['nationality'], prefix)
        pos_link = f'<a href="{pos_url(p["position"], prefix)}" class="pos">{h(p["position"])}</a>' if p['position'] else ''
        avg = pr(p)
        avg_cell = f'<span class="{rating_class(avg)}">{avg}</span>'
        skill_cells = ''
        if s:
            skill_cells = '<details><summary>Skills</summary><div class="skill-grid">'
            for grp, cols in SKILL_GROUPS.items():
                skill_cells += f'<div><strong style="font-size:0.75rem;color:var(--gold)">{grp}</strong>'
                for c in cols:
                    v = s.get(c, '0')
                    skill_cells += f'<div class="skill-row"><span class="sk-label">{SKILL_LABELS[c]}</span>{skill_bar(v)}</div>'
                skill_cells += '</div>'
            # ungrouped
            ungrouped = [c for c in SKILL_COLS if not any(c in v for v in SKILL_GROUPS.values())]
            if ungrouped:
                skill_cells += '<div><strong style="font-size:0.75rem;color:var(--gold)">Other</strong>'
                for c in ungrouped:
                    v = s.get(c, '0')
                    skill_cells += f'<div class="skill-row"><span class="sk-label">{SKILL_LABELS[c]}</span>{skill_bar(v)}</div>'
                skill_cells += '</div>'
            skill_cells += '</div></details>'
        pr_row = pos_ratings_by_player.get(key, {})
        if pr_row:
            skill_cells += '<details><summary>Position ratings</summary><div class="skill-grid"><div>'
            for pos_code in pos_order:
                v = int(pr_row.get(pos_code, 0) or 0)
                skill_cells += f'<div class="skill-row"><span class="sk-label"><a href="{pos_url(pos_code, prefix)}" class="pos">{h(pos_code)}</a></span>{skill_bar(v)}</div>'
            skill_cells += '</div></div></details>'
        league_col = f'<td>{league_cell(p["league"], prefix)}</td>' if show_league else ''
        is_pm_player = is_pm and p['last_name'] == mgr_last
        name_star = pm_star if is_pm_player else ''
        rows.append(f'''<tr id="{pid}">
          <td class="num">{h(p["shirt"])}</td>
          <td>{pos_link}</td>
          <td data-sort-value="{p["last_name"]} {p["first_name"]}"><strong>{h(p["first_name"])} {h(p["last_name"])}</strong>{name_star}{skill_cells}</td>
          <td class="nat">{nat_link}</td>
          {league_col}
          <td class="num" title="{p["dob"]}">{p["age"]}</td>
          <td class="num">{avg_cell}</td>
        </tr>''')
    league_header = '<th data-sort>League</th>' if show_league else ''
    return f'''<table id="squad-{slug(team_name)}">
      <thead><tr><th class="num" data-sort>#</th><th data-sort>Position</th><th data-sort>Player</th><th data-sort>Nationality</th>{league_header}<th class="num" data-sort>Age</th><th class="num" data-sort>Rating</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>'''

# ── HOME PAGE ──────────────────────────────────────────────────────────────────

def make_home():
    total_teams   = len(teams_raw)
    total_players = len(players_raw)
    total_leagues = len(league_names)
    total_stadiums = len([s for s in stadium_to_teams if not re.match(r'^XX\d+$', s)])
    best_player   = max(players_raw, key=lambda p: pr(p))
    biggest       = max(teams_raw, key=lambda t: int(t['capacity'] or 0))
    nats          = len(players_by_nationality)

    highlights = f'''<div class="highlights">
      <a href="leagues/" style="text-decoration:none"><div class="hl"><div class="hl-val">{total_leagues}</div><div class="hl-lbl">Leagues</div></div></a>
      <a href="teams/" style="text-decoration:none"><div class="hl"><div class="hl-val">{total_teams:,}</div><div class="hl-lbl">Teams</div></div></a>
      <a href="players/" style="text-decoration:none"><div class="hl"><div class="hl-val">{total_players:,}</div><div class="hl-lbl">Players</div></div></a>
      <a href="stadiums/" style="text-decoration:none"><div class="hl"><div class="hl-val">{total_stadiums:,}</div><div class="hl-lbl">Stadiums</div></div></a>
      <a href="nationalities/" style="text-decoration:none"><div class="hl"><div class="hl-val">{nats:,}</div><div class="hl-lbl">Nationalities</div></div></a>
      <div class="hl">
        <div class="hl-val">{pr(best_player)}</div>
        <div class="hl-lbl">Highest rated player</div>
        <div class="hl-sub"><a href="{player_anchor(best_player['first_name'],best_player['last_name'],best_player['team'])}">{h(best_player["first_name"])} {h(best_player["last_name"])}</a></div>
      </div>
      <div class="hl">
        <div class="hl-val">{int(biggest["capacity"]):,}</div>
        <div class="hl-lbl">Largest stadium</div>
        <div class="hl-sub"><a href="stadiums/{slug(biggest["stadium"])}/">{h(biggest["stadium"])}</a></div>
      </div>
    </div>'''

    league_cards = ''
    ordered_leagues = [lg for _, lgs in LEAGUE_GROUPS for lg in lgs if lg in teams_by_league]
    for lg in ordered_leagues:
        teams = teams_by_league[lg]
        count = len(teams)
        players = sum(len(players_by_team[t['team']]) for t in teams)
        league_cards += f'''<a href="leagues/{slug(lg)}/" style="text-decoration:none">
          <div class="card">
            <h3>{league_to_flag.get(lg, '')+' ' if league_to_flag.get(lg) else ''}{h(lg)}</h3>
            <div class="stat">{count}</div>
            <div class="label">clubs · {players:,} players</div>
          </div></a>'''

    body = f'''
    <p style="color:var(--muted);margin-bottom:1.5rem">
      Data extracted from <strong>SM97.DAT</strong> — the master game database from FIFA Soccer Manager 97 (EA Sports, 1997).
      Covering {total_leagues} leagues across Europe with full player skill ratings, stadium data and club information.
    </p>
    {highlights}
    <h2>Leagues</h2>
    <div class="cards">{league_cards}</div>
    <h2>Browse</h2>
    <div class="cards">
      <a href="stats/" style="text-decoration:none"><div class="card"><h3>📊 Stats &amp; Records</h3><div class="label">Top players, skill leaders, squad rankings</div></div></a>
      <a href="stats/best-of/" style="text-decoration:none"><div class="card"><h3>🏆 Best Of All</h3><div class="label">Records by position, skill and league</div></div></a>
      <a href="trivia/" style="text-decoration:none"><div class="card"><h3>📖 Real World Trivia</h3><div class="label">The stories behind the players, clubs and stadiums</div></div></a>
      <a href="positions/" style="text-decoration:none"><div class="card"><h3>🎯 Positions</h3><div class="label">Browse by playing position</div></div></a>
      <a href="nationalities/" style="text-decoration:none"><div class="card"><h3>🌍 Nationalities</h3><div class="label">{nats} nationalities represented</div></div></a>
    </div>'''

    write(f"{OUT_DIR}/index.html",
          page("FIFA Soccer Manager 97", body, depth=0, active='Home',
               header_title="FIFA Soccer Manager 97",
               header_sub="Interactive database — 1996/97 season"))

# ── LEAGUE PAGES ──────────────────────────────────────────────────────────────

def make_leagues():
    # Index — grouped by country
    body = ''
    for country, lgs in LEAGUE_GROUPS:
        rows = ''
        cflag = league_to_flag.get(lgs[0], '')
        cflag_str = f'{cflag} ' if cflag else ''
        for lg in lgs:
            if lg not in teams_by_league:
                continue
            teams = teams_by_league[lg]
            pc = sum(len(players_by_team[t['team']]) for t in teams)
            lflag = league_to_flag.get(lg, '')
            lflag_str = f'{lflag} ' if lflag else ''
            rows += f'<tr><td><a href="{slug(lg)}/">{lflag_str}{h(lg)}</a></td><td class="num">{len(teams):,}</td><td class="num">{pc:,}</td></tr>'
        if rows:
            body += f'<h2>{cflag_str}{h(country)}</h2><table><thead><tr><th>League</th><th class="num">Teams</th><th class="num">Players</th></tr></thead><tbody>{rows}</tbody></table>'
    write(f"{OUT_DIR}/leagues/index.html",
          page("Leagues", body, depth=1, active='Leagues',
               header_title="All Leagues", header_sub=f"{len(league_names)} competitions"))

    # Per-league
    for lg in league_names:
        teams = sorted(teams_by_league[lg], key=lambda t: t['team'])
        prefix = '../../'

        top_players = sorted(
            [p for p in players_raw if p['league'] == lg],
            key=lambda p: pr(p), reverse=True
        )[:15]

        is_others = (lg == 'Others')
        team_rows = ''
        for t in teams:
            slink = stadium_url(t['stadium'])
            stad  = tlink(t['stadium'], stadium_url(t['stadium'], prefix)) if slink else h(t['stadium'])
            cap   = f'{int(t["capacity"]):,}' if t['capacity'] else '—'
            pc    = len(players_by_team[t['team']])
            avg   = (sum(pr(p) for p in players_by_team[t['team']]) / pc) if pc else 0
            avg_s = f'<span class="{rating_class(avg)}">{avg:.1f}</span>' if pc else '—'
            extra = f'<td>{country_display(OTHERS_COUNTRIES.get(t["team"], ""))}</td>' if is_others else f'<td>{h(t["manager"])}</td>'
            team_rows += f'''<tr>
              <td><a href="{prefix}teams/{slug(t["team"])}/">{h(t["team"])}</a></td>
              <td>{h(t["nickname"])}</td>
              <td>{stad}</td>
              <td class="num">{cap}</td>
              {extra}
              <td class="num">{avg_s}</td>
            </tr>'''

        player_rows = ''
        for p in top_players:
            player_rows += f'''<tr>
              <td><a href="{prefix}{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="{prefix}teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td><a href="{prefix}positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a></td>
              <td class="nat">{nat_cell(p["nationality"], prefix)}</td>
              <td class="num"><span class="{rating_class(pr(p))}">{pr(p)}</span></td>
            </tr>'''

        body = f'''
        <div class="filter-bar"><input data-filter="teams-{slug(lg)}" placeholder="Filter teams…"></div>
        <h2>Clubs</h2>
        <table id="teams-{slug(lg)}">
          <thead><tr><th data-sort>Club</th><th data-sort>Nickname</th><th data-sort>Stadium</th><th class="num" data-sort>Capacity</th><th data-sort>{"Country" if is_others else "Manager"}</th><th class="num" data-sort>Squad Rating</th></tr></thead>
          <tbody>{team_rows}</tbody>
        </table>
        <h2>Top 15 Players</h2>
        <table><thead><tr><th>Player</th><th>Club</th><th>Position</th><th>Nationality</th><th class="num">Rating</th></tr></thead>
        <tbody>{player_rows}</tbody></table>'''

        lflag = league_to_flag.get(lg, '')
        lflag_str = f'{lflag} ' if lflag else ''
        write(f"{OUT_DIR}/leagues/{slug(lg)}/index.html",
              page(lg, body, depth=2, active='Leagues',
                   header_title=f"{lflag_str}{lg}",
                   header_sub=f"{len(teams):,} clubs",
                   breadcrumb=bc([('Leagues','../'), (lg,None)], prefix='../../')))

# ── BEST XI ──────────────────────────────────────────────────────────────────

def best_xi(team_name, prefix):
    players = players_by_team[team_name]
    if len(players) < 7:
        return ''

    GK_POS  = {'GK'}
    DEF_POS = {'RB','CD','LB','RWB','LWB','SW'}
    MID_POS = {'DM','RM','LM','AM','RW','LW','FR'}
    ATT_POS = {'FOR','SS'}

    by_skill = sorted(players, key=lambda p: pr(p), reverse=True)
    used = set()

    def pick(wanted_pos, count, fallback=True):
        chosen = []
        for p in by_skill:
            if len(chosen) >= count: break
            if p['first_name']+p['last_name'] not in used and p['position'] in wanted_pos:
                chosen.append(p)
                used.add(p['first_name']+p['last_name'])
        if fallback and len(chosen) < count:
            for p in by_skill:
                if len(chosen) >= count: break
                if p['first_name']+p['last_name'] not in used:
                    chosen.append(p)
                    used.add(p['first_name']+p['last_name'])
        return chosen

    gks  = pick(GK_POS,  1)
    defs = pick(DEF_POS, 4)
    mids = pick(MID_POS, 4)
    atts = pick(ATT_POS, 2)

    # Order defenders L→R: LB/LWB, CD/SW, CD/SW, RB/RWB
    def order_defs(ds):
        order = {'LB':0,'LWB':0,'SW':1,'CD':1,'RWB':3,'RB':3}
        return sorted(ds, key=lambda p: order.get(p['position'], 2))

    def order_mids(ms):
        order = {'LW':0,'LM':0,'DM':1,'RM':2,'AM':2,'RW':3,'FR':2}
        return sorted(ms, key=lambda p: order.get(p['position'], 1))

    defs = order_defs(defs)
    mids = order_mids(mids)

    def bubble(p, gk=False):
        pid   = f"{slug(p['first_name'])}-{slug(p['last_name'])}"
        avg   = pr(p)
        circ  = 'gk-circle' if gk else ''
        lname = p['last_name'] or p['first_name']
        return f'''<div class="p-bubble">
          <div class="p-circle {circ}">{h(p["position"])}</div>
          <div class="p-name"><a href="../{player_anchor(p["first_name"],p["last_name"],team_name)}">{h(lname)}</a></div>
          <div class="p-avg">{avg}</div>
        </div>'''

    def row(players, gk=False):
        return '<div class="formation-row">' + ''.join(bubble(p, gk) for p in players) + '</div>'

    return f'''<h2>Best XI — 4-4-2</h2>
    <div class="pitch">
      {row(atts)}
      {row(mids)}
      {row(defs)}
      {row(gks, gk=True)}
    </div>'''

def best_xi_nat(players, prefix):
    """Return a Best XI — 4-4-2 HTML block for an arbitrary player list.

    Only rendered if there are enough players in each zone for a full 4-4-2
    (1 GK, 4 DEF, 4 MID, 2 ATT). No cross-zone fallback.
    """
    GK_POS  = {'GK'}
    DEF_POS = {'RB','CD','LB','RWB','LWB','SW'}
    MID_POS = {'DM','RM','LM','AM','RW','LW','FR'}
    ATT_POS = {'FOR','SS'}

    def in_zone(pos_set):
        return [p for p in players if p['position'] in pos_set]

    if not (len(in_zone(GK_POS)) >= 1 and len(in_zone(DEF_POS)) >= 4 and
            len(in_zone(MID_POS)) >= 4 and len(in_zone(ATT_POS)) >= 2):
        return ''

    by_skill = sorted(players, key=lambda p: pr(p), reverse=True)
    used = set()

    def pick(wanted_pos, count):
        chosen = []
        for p in by_skill:
            if len(chosen) >= count: break
            if p['first_name']+p['last_name'] not in used and p['position'] in wanted_pos:
                chosen.append(p)
                used.add(p['first_name']+p['last_name'])
        return chosen

    def order_defs(ds):
        order = {'LB':0,'LWB':0,'SW':1,'CD':1,'RWB':3,'RB':3}
        return sorted(ds, key=lambda p: order.get(p['position'], 2))

    def order_mids(ms):
        order = {'LW':0,'LM':0,'DM':1,'RM':2,'AM':2,'RW':3,'FR':2}
        return sorted(ms, key=lambda p: order.get(p['position'], 1))

    gks  = pick(GK_POS,  1)
    defs = order_defs(pick(DEF_POS, 4))
    mids = order_mids(pick(MID_POS, 4))
    atts = pick(ATT_POS, 2)

    def bubble(p, gk=False):
        avg   = pr(p)
        circ  = 'gk-circle' if gk else ''
        lname = p['last_name'] or p['first_name']
        return f'''<div class="p-bubble">
          <div class="p-circle {circ}">{h(p["position"])}</div>
          <div class="p-name"><a href="{prefix}{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(lname)}</a></div>
          <div class="p-avg">{avg}</div>
        </div>'''

    def row(ps, gk=False):
        return '<div class="formation-row">' + ''.join(bubble(p, gk) for p in ps) + '</div>'

    return f'''<h2>Best XI — 4-4-2</h2>
    <div class="pitch">
      {row(atts)}
      {row(mids)}
      {row(defs)}
      {row(gks, gk=True)}
    </div>'''

# ── TEAM PAGES ────────────────────────────────────────────────────────────────

def make_teams():
    # Index
    all_teams_sorted = sorted(teams_raw, key=lambda t: t['team'])
    letters = sorted(set(t['team'][0].upper() for t in all_teams_sorted))
    alpha = '<div class="alpha">' + ''.join(f'<a href="#{l}">{l}</a>' for l in letters) + '</div>'
    rows = ''
    cur_letter = ''
    for t in all_teams_sorted:
        l = t['team'][0].upper()
        anchor = f' id="{l}"' if l != cur_letter else ''
        cur_letter = l
        pc  = len(players_by_team[t['team']])
        avg = (sum(pr(p) for p in players_by_team[t['team']]) / pc) if pc else 0
        avg_cell = f'<span class="{rating_class(avg)}">{avg:.1f}</span>' if pc else '-'
        rows += f'''<tr{anchor}>
          <td><a href="{slug(t["team"])}/">{h(t["team"])}</a></td>
          <td>{country_display(team_country(t))}</td>
          <td>{league_cell(t["league"], '../')}</td>
          <td>{tlink(t["stadium"], f'../stadiums/{slug(t["stadium"])}/' ) if stadium_url(t["stadium"]) else h(t["stadium"])}</td>
          <td class="num">{int(t["capacity"]):,}</td>
          <td class="num">{pc}</td>
          <td class="num">{avg_cell}</td>
        </tr>'''
    body = f'''{alpha}
    <div class="filter-bar"><input data-filter="all-teams" placeholder="Filter teams…"></div>
    <table id="all-teams">
      <thead><tr><th data-sort>Team</th><th data-sort>Country</th><th data-sort>League</th><th data-sort>Stadium</th><th class="num" data-sort>Capacity</th><th class="num" data-sort>Players</th><th class="num" data-sort>Squad Rating</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>'''
    write(f"{OUT_DIR}/teams/index.html",
          page("All Teams", body, depth=1, active='Teams',
               header_title="All Teams", header_sub=f"{len(teams_raw)} clubs"))

    # Per-team
    for t in teams_raw:
        prefix   = '../../'
        tslug    = slug(t['team'])
        tplayers = players_by_team[t['team']]
        pc       = len(tplayers)
        avg      = (sum(pr(p) for p in tplayers) / pc) if pc else 0

        stad_link = stadium_url(t['stadium'])
        stad_html = tlink(t['stadium'], stadium_url(t['stadium'], prefix)) if stad_link else h(t['stadium'])

        trivia_html = ''
        ct = CLUB_TRIVIA.get(tslug) or CLUB_TRIVIA.get(slug(t['team']))
        if ct:
            trivia_html = f'<div class="trivia">{linkify_trivia(ct, prefix)}</div>'

        nick_card = f'<div class="card"><div class="stat">{h(t["nickname"])}</div><div class="label">Nickname</div></div>' if t['nickname'] else ''
        area_card = f'<div class="card"><div class="stat">{h(t["area"])}</div><div class="label">Area</div></div>' if t['area'] else ''
        pm_star = '&nbsp;<span title="Player-Manager" style="cursor:default">⭐</span>' if t['is_player_manager'] == 'True' else ''
        mgr_label = 'Player-Manager' if t['is_player_manager'] == 'True' else 'Manager'
        mgr_card = f'<div class="card"><div class="stat">{h(t["manager"])}{pm_star}</div><div class="label">{mgr_label}</div></div>' if t['manager'] else ''
        meta = f'''<div class="cards" style="margin-bottom:1rem">
          {nick_card}
          <div class="card"><div class="stat">{country_display(team_league_label(t))}</div><div class="label"><a href="{prefix}leagues/{slug(t["league"])}/">View league</a></div></div>
          <div class="card"><div class="stat">{stad_html}</div><div class="label">Stadium · {int(t["capacity"]):,} capacity</div></div>
          {area_card}
          {mgr_card}
          {f'<div class="card"><div class="stat"><span class="{rating_class(avg)}">{avg:.1f}</span></div><div class="label">Squad avg · {pc:,} players</div></div>' if pc else ''}
        </div>'''

        body = f'''{trivia_html}{meta}
        {best_xi(t["team"], prefix)}
        <h2>Full Squad</h2>
        {squad_table(t["team"], prefix)}'''

        write(f"{OUT_DIR}/teams/{tslug}/index.html",
              page(t['team'], body, depth=2, active='Teams',
                   header_title=t['team'],
                   header_sub=h(team_league_label(t)),
                   breadcrumb=bc([('Teams','../'), (t['team'],None)], prefix='../../')))

# ── STADIUM PAGES ─────────────────────────────────────────────────────────────

def make_stadiums():
    named = {s: ts for s, ts in stadium_to_teams.items() if not re.match(r'^XX\d+$', s.strip())}
    all_sorted = sorted(named.items(), key=lambda x: int(x[1][0]['capacity'] or 0), reverse=True)

    # Index
    rows = ''
    for i, (sname, ts) in enumerate(all_sorted, 1):
        cap = int(ts[0]['capacity'] or 0)
        country = team_country(ts[0])
        cities = ', '.join(set(t['area'] for t in ts if t['area']))
        addr = ts[0]['stadium_address'] or ''
        location = ', '.join(x for x in [addr, cities] if x)
        club_links = ', '.join(f'<a href="../teams/{slug(t["team"])}/">{h(t["team"])}</a>' for t in ts)
        rows += f'''<tr>
          <td class="num">{i}</td>
          <td><a href="{slug(sname)}/">{h(sname)}</a></td>
          <td>{h(location)}</td>
          <td>{country_display(country)}</td>
          <td>{club_links}</td>
          <td class="num">{cap:,}</td>
        </tr>'''
    body = f'''<div class="filter-bar"><input data-filter="stad-idx" placeholder="Filter stadiums…"></div>
    <table id="stad-idx">
      <thead><tr><th class="num" data-sort>#</th><th data-sort>Stadium</th><th data-sort>Location</th><th data-sort>Country</th><th data-sort>Club(s)</th><th class="num" data-sort>Capacity</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>'''
    write(f"{OUT_DIR}/stadiums/index.html",
          page("Stadiums", body, depth=1, active='Stadiums',
               header_title="All Stadiums", header_sub=f"{len(named)} named stadiums"))

    # Per-stadium
    for sname, ts in named.items():
        sslug  = slug(sname)
        prefix = '../../'
        cap    = int(ts[0]['capacity'] or 0)
        cities = ', '.join(set(t['area'] for t in ts if t['area']))
        addr   = ts[0]['stadium_address']

        trivia_html = ''
        tv = STADIUM_TRIVIA.get(sslug)
        if tv:
            trivia_html = f'<div class="trivia">{linkify_trivia(tv, prefix)}</div>'

        club_cards = ''
        for t in ts:
            pc  = len(players_by_team[t['team']])
            avg = (sum(pr(p) for p in players_by_team[t['team']]) / pc) if pc else 0
            club_cards += f'''<a href="{prefix}teams/{slug(t["team"])}/" style="text-decoration:none">
              <div class="card">
                <h3>{h(t["team"])}</h3>
                <div class="label">{league_cell(t["league"], prefix)}</div>
                <div class="label">Squad avg: <span class="{rating_class(avg)}">{avg:.1f}</span></div>
              </div></a>'''

        country = team_country(ts[0])
        meta = f'''<div class="highlights" style="margin-bottom:1rem">
          <div class="hl"><div class="hl-val">{cap:,}</div><div class="hl-lbl">Capacity</div></div>
          {"<div class='hl'><div class='hl-val' style='font-size:1rem'>"+h(addr)+"</div><div class='hl-lbl'>Address</div></div>" if addr else ""}
          {"<div class='hl'><div class='hl-val'>"+h(cities)+"</div><div class='hl-lbl'>Area</div></div>" if cities else ""}
          <div class="hl"><div class="hl-val">{country_display(country)}</div><div class="hl-lbl">Country</div></div>
        </div>'''

        shared = f'<p class="muted">Shared by {len(ts)} clubs.</p>' if len(ts) > 1 else ''
        body = f'''{trivia_html}{meta}{shared}
        <h2>{"Clubs" if len(ts)>1 else "Club"}</h2>
        <div class="cards">{club_cards}</div>'''

        write(f"{OUT_DIR}/stadiums/{sslug}/index.html",
              page(sname, body, depth=2, active='Stadiums',
                   header_title=sname,
                   header_sub=f"Capacity {cap:,} · {cities}",
                   breadcrumb=bc([('Stadiums','../'), (sname,None)], prefix='../../')))

# ── POSITION PAGES ────────────────────────────────────────────────────────────

def make_positions():
    zone_of = {p_info['abbreviation']: p_info['zone'] for p_info in positions_info.values()}

    def pos_rat(p, pos):
        key = (p['first_name'], p['last_name'], p['team'])
        r = pos_ratings_by_player.get(key)
        return int(r[pos]) if r else 0

    rows = ''
    for pos in pos_order:
        info = positions_info.get(pos, {})
        zone = info.get('zone', '')
        pp_zone = [p for p in players_raw if zone_of.get(p['position']) == zone]
        if not pp_zone: continue
        avg = sum(pos_rat(p, pos) for p in pp_zone) / len(pp_zone)
        rows += f'''<tr>
          <td><a href="{slug(pos)}/" class="pos">{h(pos)}</a></td>
          <td>{h(info.get("position",""))}</td>
          <td>{h(info.get("zone",""))}</td>
          <td class="num">{len(pp_zone):,}</td>
          <td class="num"><span class="{rating_class(avg)}">{avg:.1f}</span></td>
        </tr>'''
    body = f'''<table><thead><tr><th>Code</th><th>Position</th><th>Zone</th><th class="num">Players</th><th class="num">Avg Rating</th></tr></thead>
    <tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/positions/index.html",
          page("Positions", body, depth=1, active='Positions',
               header_title="Playing Positions"))

    prefix = '../../'
    for pos in pos_order:
        if not players_by_position.get(pos): continue
        info = positions_info.get(pos, {})
        zone = info.get('zone', '')

        # Main table — all players in the same zone, ranked by position-specific rating
        pp_zone = [p for p in players_raw if zone_of.get(p['position']) == zone]
        pp_zone_sorted = sorted(pp_zone, key=lambda p: pos_rat(p, pos), reverse=True)
        prows = ''
        for i, p in enumerate(pp_zone_sorted, 1):
            nat_pos = p['position']
            rating  = pos_rat(p, pos)
            pos_cell = '' if nat_pos == pos else f'<a href="{prefix}positions/{slug(nat_pos)}/" class="pos">{h(nat_pos)}</a>'
            prows += f'''<tr>
              <td class="num">{i}</td>
              <td><a href="{prefix}{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="{prefix}teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td>{league_cell(p["league"], prefix)}</td>
              <td class="nat">{nat_cell(p["nationality"], prefix)}</td>
              <td>{pos_cell}</td>
              <td class="num" title="{p["dob"]}">{p["age"]}</td>
              <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
            </tr>'''

        # Out-of-position section — top 10 players from outside this zone
        outside = [p for p in players_raw if zone_of.get(p['position']) != zone]
        top_outside = sorted(outside, key=lambda p: pos_rat(p, pos), reverse=True)[:10]
        oop_rows = ''
        for i, p in enumerate(top_outside, 1):
            nat_pos = p['position']
            rating = pos_rat(p, pos)
            oop_rows += f'''<tr>
              <td class="num">{i}</td>
              <td><a href="{prefix}{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="{prefix}teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td>{league_cell(p["league"], prefix)}</td>
              <td class="nat">{nat_cell(p["nationality"], prefix)}</td>
              <td><a href="{prefix}positions/{slug(nat_pos)}/" class="pos">{h(nat_pos)}</a></td>
              <td class="num" title="{p["dob"]}">{p["age"]}</td>
              <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
            </tr>'''

        body = f'''<p class="muted">Zone: <strong>{h(zone)}</strong> · {len(pp_zone_sorted):,} players</p>
        <div class="filter-bar"><input data-filter="pos-{slug(pos)}" placeholder="Filter players…"></div>
        <table id="pos-{slug(pos)}"><thead><tr><th class="num">#</th><th data-sort>Player</th><th data-sort>Club</th><th data-sort>League</th><th data-sort>Nationality</th><th data-sort>Natural Position</th><th class="num" data-sort>Age</th><th class="num" data-sort>Rating</th></tr></thead>
        <tbody>{prows}</tbody></table>
        <h2>Surprising performers</h2>
        <p class="muted">Top 10 players from outside the {h(zone)} zone, ranked by their {h(pos)} rating.</p>
        <table><thead><tr><th class="num">#</th><th>Player</th><th>Club</th><th>League</th><th>Nationality</th><th>Natural Position</th><th class="num">Age</th><th class="num">Rating</th></tr></thead>
        <tbody>{oop_rows}</tbody></table>'''
        write(f"{OUT_DIR}/positions/{slug(pos)}/index.html",
              page(f"{pos} — {info.get('position','')}", body, depth=2, active='Positions',
                   header_title=info.get('position', pos),
                   header_sub=f"{pos} · {zone} · {len(pp_zone_sorted):,} players",
                   breadcrumb=bc([('Positions','../'), (pos,None)], prefix='../../')))

# ── NATIONALITY PAGES ─────────────────────────────────────────────────────────

def make_nationalities():
    nats_sorted = sorted(players_by_nationality.items(),
                         key=lambda x: len(x[1]), reverse=True)
    rows = ''
    for nat, pp in nats_sorted:
        if not nat: continue
        avg = sum(pr(p) for p in pp) / len(pp)
        rows += f'''<tr>
          <td><span title="{h(nat_to_country.get(nat, nat))}">{f'{nat_to_flag[nat]} ' if nat_to_flag.get(nat) else ''}<a href="{slug(nat)}/">{h(nat)}</a></span></td>
          <td class="num">{len(pp):,}</td>
          <td class="num"><span class="{rating_class(avg)}">{avg:.1f}</span></td>
        </tr>'''
    body = f'''<div class="filter-bar"><input data-filter="nat-idx" placeholder="Filter nationalities…"></div>
    <table id="nat-idx"><thead><tr><th data-sort>Nationality</th><th class="num" data-sort>Players</th><th class="num" data-sort>Avg Rating</th></tr></thead>
    <tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/nationalities/index.html",
          page("Nationalities", body, depth=1, active='Nationalities',
               header_title="Nationalities", header_sub=f"{len(nats_sorted)} nationalities represented"))

    nat_prefix = '../../'
    for nat, pp in nats_sorted:
        if not nat: continue
        pp_sorted = sorted(pp, key=lambda p: pr(p), reverse=True)
        by_league = defaultdict(list)
        for p in pp_sorted:
            by_league[p['league']].append(p)
        prows = ''
        for p in pp_sorted:
            prows += f'''<tr>
              <td><a href="{nat_prefix}{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="{nat_prefix}teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td>{league_cell(p["league"], nat_prefix)}</td>
              <td><a href="{nat_prefix}positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a></td>
              <td class="num" title="{p["dob"]}">{p["age"]}</td>
              <td class="num"><span class="{rating_class(pr(p))}">{pr(p)}</span></td>
            </tr>'''
        xi_html = best_xi_nat(pp, prefix=nat_prefix)
        body = f'''{xi_html}
        <p class="muted">{len(pp):,} {h(nat)} players across {len(by_league):,} leagues</p>
        <div class="filter-bar"><input data-filter="nat-{slug(nat)}" placeholder="Filter…"></div>
        <table id="nat-{slug(nat)}"><thead><tr><th data-sort>Player</th><th data-sort>Club</th><th data-sort>League</th><th data-sort>Position</th><th class="num" data-sort>Age</th><th class="num" data-sort>Rating</th></tr></thead>
        <tbody>{prows}</tbody></table>'''
        flag = nat_to_flag.get(nat, '')
        flag_str = f'{flag} ' if flag else ''
        write(f"{OUT_DIR}/nationalities/{slug(nat)}/index.html",
              page(nat, body, depth=2, active='Nationalities',
                   header_title=f"{flag_str}{nat} Players",
                   header_sub=f"{len(pp):,} players",
                   breadcrumb=bc([('Nationalities','../'), (nat,None)], prefix='../../')))

# ── STATS PAGES ───────────────────────────────────────────────────────────────

def make_stats_age_groups():
    age_groups = [
        ('15-19', 15, 19),
        ('20-29', 20, 29),
        ('30-39', 30, 39),
        ('40+',   40, 999),
    ]
    sections = ''
    for label, lo, hi in age_groups:
        group = [p for p in players_raw if lo <= int(p['age']) <= hi]
        top10 = sorted(group, key=lambda p: pr(p), reverse=True)[:10]
        if not top10:
            continue
        rows = ''
        for i, p in enumerate(top10, 1):
            rows += f'''<tr>
              <td class="num">{i}</td>
              <td><a href="../../{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="../../teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td>{league_cell(p["league"], '../../')}</td>
              <td><a href="../../positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a></td>
              <td class="nat">{nat_cell(p["nationality"], '../../')}</td>
              <td class="num" title="{p["dob"]}">{p["age"]}</td>
              <td class="num"><span class="{rating_class(pr(p))}">{pr(p)}</span></td>
            </tr>'''
        sections += f'''<h2>Age {label}</h2>
        <p>{len(group):,} players in this age group</p>
        <table><thead><tr>
          <th class="num">#</th><th>Player</th><th>Club</th><th>League</th>
          <th>Position</th><th>Nat</th><th class="num">Age</th><th class="num">Rating</th>
        </tr></thead><tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/stats/age-groups/index.html",
          page("Age Groups", sections, depth=2, active='Stats',
               header_title="Top Players by Age Group",
               breadcrumb=bc([('Stats','../'), ('Age Groups',None)], prefix='../../')))


def make_stats_player_managers():
    # Find all player-managers: teams with is_player_manager=True, matched to their player record
    pm_players = []
    for t in teams_raw:
        if t.get('is_player_manager') != 'True':
            continue
        mgr_last = t['manager'].split()[-1] if t['manager'] else ''
        if not mgr_last:
            continue
        squad = players_by_team.get(t['team'], [])
        match = next((p for p in squad if p['last_name'] == mgr_last), None)
        if match:
            pm_players.append((t, match))

    pm_players.sort(key=lambda x: pr(x[1]), reverse=True)

    rows = ''
    for i, (t, p) in enumerate(pm_players, 1):
        rows += f'''<tr>
          <td class="num">{i}</td>
          <td><a href="../../{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a> <span title="Player-Manager" style="cursor:default">⭐</span></td>
          <td><a href="../../teams/{slug(t["team"])}/">{h(t["team"])}</a></td>
          <td>{league_cell(t["league"], '../../')}</td>
          <td><a href="../../positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a></td>
          <td class="nat">{nat_cell(p["nationality"], '../../')}</td>
          <td class="num" title="{p["dob"]}">{p["age"]}</td>
          <td class="num"><span class="{rating_class(pr(p))}">{pr(p)}</span></td>
        </tr>'''

    body = f'''<p>{len(pm_players)} player-managers in the game.</p>
    <table><thead><tr>
      <th class="num">#</th><th>Player</th><th>Club</th><th>League</th>
      <th>Position</th><th>Nat</th><th class="num">Age</th><th class="num">Rating</th>
    </tr></thead><tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/stats/player-managers/index.html",
          page("Player-Managers", body, depth=2, active='Stats',
               header_title="Player-Managers",
               breadcrumb=bc([('Stats','../'), ('Player-Managers',None)], prefix='../../')))


def make_stats_index():
    body = '''<div class="cards">
      <a href="top-players/" style="text-decoration:none"><div class="card"><h3>🥇 Top Players</h3><div class="label">Top 50 overall and top 10 by position</div></div></a>
      <a href="skill-leaders/" style="text-decoration:none"><div class="card"><h3>⚡ Skill Leaders</h3><div class="label">Best in each of the 23 individual skills</div></div></a>
      <a href="age-groups/" style="text-decoration:none"><div class="card"><h3>🎂 Age Groups</h3><div class="label">Top 10 best players in each age group</div></div></a>
      <a href="player-managers/" style="text-decoration:none"><div class="card"><h3>⭐ Player-Managers</h3><div class="label">All player-managers ranked by rating</div></div></a>
      <a href="stadiums/" style="text-decoration:none"><div class="card"><h3>🏟️ Stadium Rankings</h3><div class="label">Largest to smallest</div></div></a>
      <a href="squads/" style="text-decoration:none"><div class="card"><h3>👥 Squad Rankings</h3><div class="label">Best and worst rated squads</div></div></a>
      <a href="nationalities/" style="text-decoration:none"><div class="card"><h3>🌍 Nationality Stats</h3><div class="label">International representation by league</div></div></a>
      <a href="best-of/" style="text-decoration:none"><div class="card"><h3>🏆 Best Of All</h3><div class="label">Records, superlatives and extremes</div></div></a>
    </div>'''
    write(f"{OUT_DIR}/stats/index.html",
          page("Stats", body, depth=1, active='Stats',
               header_title="Stats & Records"))

def make_stats_top_players():
    top50 = sorted(players_raw, key=lambda p: pr(p), reverse=True)[:50]
    rows = ''
    for i, p in enumerate(top50, 1):
        rows += f'''<tr>
          <td class="num">{i}</td>
          <td><a href="../../{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
          <td><a href="../../teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
          <td>{league_cell(p["league"], '../../')}</td>
          <td><a href="../../positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a></td>
          <td class="nat">{nat_cell(p["nationality"], '../../')}</td>
          <td class="num"><span class="{rating_class(pr(p))}">{pr(p)}</span></td>
        </tr>'''

    by_pos_html = ''
    for pos in pos_order:
        def pos_rat(p, pos=pos):
            key = (p['first_name'], p['last_name'], p['team'])
            r = pos_ratings_by_player.get(key)
            return int(r[pos]) if r else 0

        pp = sorted(players_raw, key=pos_rat, reverse=True)[:10]
        if not pp: continue
        info = positions_info.get(pos, {})
        prows = ''
        for i, p in enumerate(pp, 1):
            rating = pos_rat(p)
            nat_pos = p['position']
            nat_pos_cell = f'<td><a href="../../positions/{slug(nat_pos)}/" class="pos">{h(nat_pos)}</a></td>'
            prows += f'''<tr>
              <td class="num">{i}</td>
              <td><a href="../../{player_anchor(p["first_name"],p["last_name"],p["team"])}">{h(p["first_name"])} {h(p["last_name"])}</a></td>
              <td><a href="../../teams/{slug(p["team"])}/">{h(p["team"])}</a></td>
              <td class="nat">{nat_cell(p["nationality"], '../../')}</td>
              {nat_pos_cell}
              <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
            </tr>'''
        by_pos_html += f'''<h3><a href="../../positions/{slug(pos)}/" class="pos">{pos}</a> {h(info.get("position",""))}</h3>
        <table><thead><tr><th class="num">#</th><th>Player</th><th>Club</th><th>Nationality</th><th>Natural Position</th><th class="num">Rating</th></tr></thead>
        <tbody>{prows}</tbody></table>'''

    body = f'''<h2>Top 50 Players Overall</h2>
    <table><thead><tr><th class="num" data-sort>#</th><th data-sort>Player</th><th data-sort>Club</th><th data-sort>League</th><th data-sort>Position</th><th data-sort>Nat</th><th class="num" data-sort>Rating</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <h2>Top 10 by Position</h2>
    {by_pos_html}'''
    write(f"{OUT_DIR}/stats/top-players/index.html",
          page("Top Players", body, depth=2, active='Stats',
               header_title="Top Players",
               breadcrumb=bc([('Stats','../'), ('Top Players',None)], prefix='../../')))

def make_stats_skill_leaders():
    # For each skill, find top 10 players
    sections = ''
    for col in SKILL_COLS:
        label = SKILL_LABELS[col]
        ranked = sorted(skills_raw, key=lambda s: int(s.get(col,0) or 0), reverse=True)[:10]
        rows = ''
        for i, s in enumerate(ranked, 1):
            v = int(s.get(col, 0))
            rows += f'''<tr>
              <td class="num">{i}</td>
              <td><a href="../../{player_anchor(s["first_name"],s["last_name"],s["team"])}">{h(s["first_name"])} {h(s["last_name"])}</a></td>
              <td><a href="../../teams/{slug(s["team"])}/">{h(s["team"])}</a></td>
              <td><a href="../../positions/{slug(s["position"])}/" class="pos">{h(s["position"])}</a></td>
              <td class="num"><span class="{rating_class(v)}">{v}</span></td>
            </tr>'''
        sections += f'''<h3>{h(label)}</h3>
        <table><thead><tr><th class="num">#</th><th>Player</th><th>Club</th><th>Position</th><th class="num">Value</th></tr></thead>
        <tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/stats/skill-leaders/index.html",
          page("Skill Leaders", sections, depth=2, active='Stats',
               header_title="Skill Leaders — Best in Every Category",
               breadcrumb=bc([('Stats','../'), ('Skill Leaders',None)], prefix='../../')))

def make_stats_stadiums():
    named = [(s, ts) for s, ts in stadium_to_teams.items()
             if not re.match(r'^XX\d+$', s.strip())]
    named.sort(key=lambda x: int(x[1][0]['capacity'] or 0), reverse=True)

    def stad_row(i, sname, ts, show_country=True):
        cap      = int(ts[0]['capacity'] or 0)
        clubs    = ', '.join(f'<a href="../../teams/{slug(t["team"])}/">{h(t["team"])}</a>' for t in ts)
        addr     = ts[0]['stadium_address'] or ''
        area     = ', '.join(set(t['area'] for t in ts if t['area']))
        location = ', '.join(x for x in [addr, area] if x)
        country  = team_country(ts[0])
        country_td = f'<td data-sort>{country_display(country)}</td>' if show_country else ''
        return f'''<tr>
          <td class="num" data-sort>{i}</td>
          <td data-sort><a href="../../stadiums/{slug(sname)}/">{h(sname)}</a></td>
          <td data-sort>{h(location)}</td>
          {country_td}
          <td data-sort>{clubs}</td>
          <td class="num" data-sort data-sort-value="{cap}">{cap:,}</td>
        </tr>'''

    def stad_table(entries, show_country=True):
        country_th = '<th data-sort>Country</th>' if show_country else ''
        rows = ''.join(stad_row(i, sname, ts, show_country) for i, (sname, ts) in enumerate(entries, 1))
        return f'''<table><thead><tr><th class="num" data-sort>#</th><th data-sort>Stadium</th><th data-sort>Location</th>{country_th}<th data-sort>Club(s)</th><th class="num" data-sort>Capacity</th></tr></thead>
        <tbody>{rows}</tbody></table>'''

    # Top 50 overall
    body = '<h2>Top 50 Overall</h2>' + stad_table(named[:50])

    # Top 10 per country (leagues only, not Others)
    league_countries = [c for c, lgs in LEAGUE_GROUPS if c != 'Others']
    by_country_html = ''
    for country in league_countries:
        country_stads = [(s, ts) for s, ts in named if team_country(ts[0]) == country]
        if not country_stads:
            continue
        by_country_html += f'<h3>{country_display(country)}</h3>' + stad_table(country_stads[:10], show_country=False)

    body += '<h2>Top 10 by Country</h2>' + by_country_html

    # Top 10 Others
    others_stads = [(s, ts) for s, ts in named if ts[0]['league'] == 'Others']
    if others_stads:
        body += '<h3>Others</h3>' + stad_table(others_stads[:10])

    write(f"{OUT_DIR}/stats/stadiums/index.html",
          page("Stadium Rankings", body, depth=2, active='Stats',
               header_title="Stadiums by Capacity",
               breadcrumb=bc([('Stats','../'), ('Stadium Rankings',None)], prefix='../../')))

def make_stats_squads():
    squad_stats = []
    for t in teams_raw:
        pp = players_by_team[t['team']]
        if not pp: continue
        avg  = sum(pr(p) for p in pp) / len(pp)
        nats = len(set(p['nationality'] for p in pp if p['nationality']))
        home_nat = t['league'].split()[0] if t['league'] else ''
        home_pct = sum(1 for p in pp if home_nat.lower() in p['nationality'].lower()) / len(pp) * 100
        squad_stats.append((t, pp, avg, nats, home_pct))
    squad_stats.sort(key=lambda x: x[2], reverse=True)

    rows = ''
    for i, (t, pp, avg, nats, home_pct) in enumerate(squad_stats, 1):
        rows += f'''<tr>
          <td class="num">{i}</td>
          <td><a href="../../teams/{slug(t["team"])}/">{h(t["team"])}</a></td>
          <td>{league_cell(t["league"], '../../')}</td>
          <td class="num">{len(pp):,}</td>
          <td class="num"><span class="{rating_class(avg)}">{avg:.1f}</span></td>
          <td class="num">{nats:,}</td>
        </tr>'''
    body = f'''<table><thead><tr>
      <th class="num">#</th><th>Club</th><th>League</th>
      <th class="num">Players</th><th class="num">Squad Rating</th><th class="num">Nationalities</th>
    </tr></thead><tbody>{rows}</tbody></table>'''
    write(f"{OUT_DIR}/stats/squads/index.html",
          page("Squad Rankings", body, depth=2, active='Stats',
               header_title="Squad Rankings",
               breadcrumb=bc([('Stats','../'), ('Squad Rankings',None)], prefix='../../')))

def make_stats_nationalities():
    # Players per nationality per league
    league_nat = defaultdict(lambda: defaultdict(int))
    for p in players_raw:
        league_nat[p['league']][p['nationality']] += 1

    rows = ''
    for lg in league_names:
        nat_counts = league_nat[lg]
        total = sum(nat_counts.values())
        top_nats = sorted(nat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_str  = ', '.join(f'{h(n)} ({c})' for n, c in top_nats)
        n_nats   = len(nat_counts)
        rows += f'''<tr>
          <td>{league_cell(lg, '../../')}</td>
          <td class="num">{total:,}</td>
          <td class="num">{n_nats:,}</td>
          <td>{top_str}</td>
        </tr>'''

    # Overall
    total_nats = sorted(players_by_nationality.items(), key=lambda x: len(x[1]), reverse=True)[:20]
    nat_rows = ''
    for nat, pp in total_nats:
        if not nat: continue
        avg = sum(pr(p) for p in pp) / len(pp)
        flag = nat_to_flag.get(nat, '')
        flag_str = f'{flag} ' if flag else ''
        country = nat_to_country.get(nat, nat)
        nat_rows += f'''<tr>
          <td><span title="{h(country)}">{flag_str}<a href="../../nationalities/{slug(nat)}/">{h(nat)}</a></span></td>
          <td class="num">{len(pp):,}</td>
          <td class="num"><span class="{rating_class(avg)}">{avg:.1f}</span></td>
        </tr>'''

    body = f'''<h2>By League</h2>
    <table><thead><tr><th>League</th><th class="num">Players</th><th class="num">Nationalities</th><th>Most represented</th></tr></thead>
    <tbody>{rows}</tbody></table>
    <h2>Top 20 Nationalities (All Leagues)</h2>
    <table><thead><tr><th>Nationality</th><th class="num">Players</th><th class="num">Avg Rating</th></tr></thead>
    <tbody>{nat_rows}</tbody></table>'''
    write(f"{OUT_DIR}/stats/nationalities/index.html",
          page("Nationality Stats", body, depth=2, active='Stats',
               header_title="Nationality Statistics",
               breadcrumb=bc([('Stats','../'), ('Nationalities',None)], prefix='../../')))

def make_stats_best_of():
    sections = ''

    def pos_rat(p, pos):
        key = (p['first_name'], p['last_name'], p['team'])
        r = pos_ratings_by_player.get(key)
        return int(r[pos]) if r else 0

    def nat_pos_rat(p):
        return pos_rat(p, p['position'])

    # Best per position — all players ranked by position-specific rating
    pos_rows = ''
    for pos in pos_order:
        best = max(players_raw, key=lambda p: pos_rat(p, pos))
        rating = pos_rat(best, pos)
        info = positions_info.get(pos, {})
        nat_pos = best['position']
        nat_pos_cell = f'<td><a href="../../positions/{slug(nat_pos)}/" class="pos">{h(nat_pos)}</a></td>' if nat_pos != pos else '<td></td>'
        pos_rows += f'''<tr>
          <td><a href="../../positions/{slug(pos)}/" class="pos">{pos}</a></td>
          <td>{h(info.get("position",""))}</td>
          <td><a href="../../{player_anchor(best["first_name"],best["last_name"],best["team"])}">{h(best["first_name"])} {h(best["last_name"])}</a></td>
          <td><a href="../../teams/{slug(best["team"])}/">{h(best["team"])}</a></td>
          <td class="nat">{nat_cell(best["nationality"], '../../')}</td>
          {nat_pos_cell}
          <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
        </tr>'''
    sections += f'''<h2>Best Player by Position</h2>
    <table><thead><tr><th>Position</th><th>Name</th><th>Best Player</th><th>Club</th><th>Nationality</th><th>Natural Position</th><th class="num">Rating</th></tr></thead>
    <tbody>{pos_rows}</tbody></table>'''

    # Best per skill
    sk_rows = ''
    for col in SKILL_COLS:
        best_s = max(skills_raw, key=lambda s: int(s.get(col, 0) or 0))
        v = int(best_s.get(col, 0))
        sk_rows += f'''<tr>
          <td>{h(SKILL_LABELS[col])}</td>
          <td><a href="../../{player_anchor(best_s["first_name"],best_s["last_name"],best_s["team"])}">{h(best_s["first_name"])} {h(best_s["last_name"])}</a></td>
          <td><a href="../../teams/{slug(best_s["team"])}/">{h(best_s["team"])}</a></td>
          <td><a href="../../positions/{slug(best_s["position"])}/" class="pos">{h(best_s["position"])}</a></td>
          <td class="num"><span class="{rating_class(v)}">{v}</span></td>
        </tr>'''
    sections += f'''<h2>Leader in Every Skill</h2>
    <table><thead><tr><th>Skill</th><th>Player</th><th>Club</th><th>Position</th><th class="num">Value</th></tr></thead>
    <tbody>{sk_rows}</tbody></table>'''

    # Best per league
    lg_rows = ''
    for lg in league_names:
        pp = [p for p in players_raw if p['league'] == lg]
        if not pp: continue
        best = max(pp, key=nat_pos_rat)
        rating = nat_pos_rat(best)
        lg_rows += f'''<tr>
          <td>{league_cell(lg, '../../')}</td>
          <td><a href="../../{player_anchor(best["first_name"],best["last_name"],best["team"])}">{h(best["first_name"])} {h(best["last_name"])}</a></td>
          <td><a href="../../teams/{slug(best["team"])}/">{h(best["team"])}</a></td>
          <td><a href="../../positions/{slug(best["position"])}/" class="pos">{h(best["position"])}</a></td>
          <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
        </tr>'''
    sections += f'''<h2>Best Player by League</h2>
    <table><thead><tr><th>League</th><th>Player</th><th>Club</th><th>Position</th><th class="num">Rating</th></tr></thead>
    <tbody>{lg_rows}</tbody></table>'''

    # Best per nationality
    nat_rows = ''
    for nat, pp in sorted(players_by_nationality.items(), key=lambda x: x[0]):
        if not nat or len(pp) < 3: continue
        best = max(pp, key=nat_pos_rat)
        rating = nat_pos_rat(best)
        nat_rows += f'''<tr>
          <td><a href="../../nationalities/{slug(nat)}/">{h(nat)}</a></td>
          <td class="num">{len(pp):,}</td>
          <td><a href="../../{player_anchor(best["first_name"],best["last_name"],best["team"])}">{h(best["first_name"])} {h(best["last_name"])}</a></td>
          <td><a href="../../teams/{slug(best["team"])}/">{h(best["team"])}</a></td>
          <td class="num"><span class="{rating_class(rating)}">{rating}</span></td>
        </tr>'''
    sections += f'''<h2>Best Player by Nationality</h2>
    <table><thead><tr><th>Nationality</th><th class="num">Players</th><th>Best Player</th><th>Club</th><th class="num">Rating</th></tr></thead>
    <tbody>{nat_rows}</tbody></table>'''

    write(f"{OUT_DIR}/stats/best-of/index.html",
          page("Best Of All", sections, depth=2, active='Stats',
               header_title="Best Of All",
               breadcrumb=bc([('Stats','../'), ('Best Of All',None)], prefix='../../')))

# ── TRIVIA PAGES ──────────────────────────────────────────────────────────────

def make_trivia():
    # Index
    body = '''<p style="color:var(--muted);margin-bottom:1rem">Real-world context for the players, stadiums and clubs in the database — 1996/97 season.</p>
    <div class="cards">
      <a href="players/" style="text-decoration:none"><div class="card"><h3>🧑 Players</h3><div class="label">Notable player stories</div></div></a>
      <a href="stadiums/" style="text-decoration:none"><div class="card"><h3>🏟️ Stadiums</h3><div class="label">The grounds and their histories</div></div></a>
      <a href="clubs/" style="text-decoration:none"><div class="card"><h3>⚽ Clubs</h3><div class="label">Club stories from the era</div></div></a>
    </div>'''
    write(f"{OUT_DIR}/trivia/index.html",
          page("Trivia", body, depth=1, active='Trivia',
               header_title="Real World Trivia",
               header_sub="1996/97 season context"))

    # Players trivia
    sections = '<p class="muted" style="margin-bottom:1rem">Notable players in the database and their real-world stories.</p>'
    for (first, last), text in PLAYER_TRIVIA.items():
        # Find the player
        matches = [p for p in players_raw
                   if p['first_name'] == first and (not last or p['last_name'] == last)]
        if matches:
            p = matches[0]
            display = PLAYER_DISPLAY_NAMES.get((first, last), f'{first} {last}')
            link = f'<a href="../../{player_anchor(first, last, p["team"])}">{h(display)}</a>'
            team_link = f'<a href="../../teams/{slug(p["team"])}/">{h(p["team"])}</a>'
            nat_link  = nat_cell(p["nationality"], '../../')
            avg = pr(p)
            badge = f'<span class="{rating_class(avg)}">{avg:.1f}</span>'
            header = f'{link} · {team_link} · {nat_link} · <a href="../../positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a> · {badge}'
        else:
            header = f'{h(first)} {h(last)}'
        sections += f'<div style="margin-bottom:1.5rem"><h3>{header}</h3><div class="trivia">{linkify_trivia(text, "../../")}</div></div>'

    write(f"{OUT_DIR}/trivia/players/index.html",
          page("Player Trivia", sections, depth=2, active='Trivia',
               header_title="Player Trivia",
               breadcrumb=bc([('Trivia','../'), ('Players',None)], prefix='../../')))

    # Stadiums trivia
    sections = '<p class="muted" style="margin-bottom:1rem">The grounds behind the game data.</p>'
    for sslug, text in STADIUM_TRIVIA.items():
        # Find matching stadium
        match_name = next((s for s in stadium_to_teams if slug(s) == sslug), None)
        if match_name:
            ts = stadium_to_teams[match_name]
            cap = int(ts[0]['capacity'] or 0)
            club_links = ', '.join(f'<a href="../../teams/{slug(t["team"])}/">{h(t["team"])}</a>' for t in ts)
            stad_link = f'<a href="../../stadiums/{sslug}/">{h(match_name)}</a>'
            header = f'{stad_link} · {club_links} · {cap:,} capacity'
        else:
            header = h(sslug.replace('-',' ').title())
        sections += f'<div style="margin-bottom:1.5rem"><h3>{header}</h3><div class="trivia">{linkify_trivia(text, "../../")}</div></div>'

    write(f"{OUT_DIR}/trivia/stadiums/index.html",
          page("Stadium Trivia", sections, depth=2, active='Trivia',
               header_title="Stadium Trivia",
               breadcrumb=bc([('Trivia','../'), ('Stadiums',None)], prefix='../../')))

    # Clubs trivia
    # Build alias map: old game-name slug → corrected slug (e.g. 'leeds' → 'leeds-united')
    slug_aliases = {slug(old): slug(new) for old, new in TEAM_NAMES.items()}

    sections = '<p class="muted" style="margin-bottom:1rem">Club stories from the 1996/97 season.</p>'
    for cslug, text in CLUB_TRIVIA.items():
        resolved = slug_aliases.get(cslug, cslug)
        match_team = next((t for t in teams_raw if slug(t['team']) == resolved), None)
        if match_team:
            tslug = slug(match_team['team'])
            team_link = f'<a href="../../teams/{tslug}/">{h(match_team["team"])}</a>'
            lg_link   = f'<a href="../../leagues/{slug(match_team["league"])}/">{h(match_team["league"])}</a>'
            header    = f'{team_link} · {lg_link}'
        else:
            header = h(cslug.replace('-',' ').title())
        sections += f'<div style="margin-bottom:1.5rem"><h3>{header}</h3><div class="trivia">{linkify_trivia(text, "../../")}</div></div>'

    write(f"{OUT_DIR}/trivia/clubs/index.html",
          page("Club Trivia", sections, depth=2, active='Trivia',
               header_title="Club Trivia",
               breadcrumb=bc([('Trivia','../'), ('Clubs',None)], prefix='../../')))

# ── PLAYERS PAGE ─────────────────────────────────────────────────────────────

def make_players():
    players_sorted = sorted(players_raw, key=lambda p: (p['last_name'].lstrip('-'), p['first_name']))
    rows = []
    for p in players_sorted:
        key  = (p['first_name'], p['last_name'], p['team'])
        avg  = pr(p)
        name = f'{h(p["first_name"])} {h(p["last_name"])}'
        name_link = f'<a href="../{player_anchor(p["first_name"], p["last_name"], p["team"])}">{name}</a>'
        team_link = f'<a href="../teams/{slug(p["team"])}/">{h(p["team"])}</a>'
        lg_link   = league_cell(p["league"], '../')
        pos_link  = f'<a href="../positions/{slug(p["position"])}/" class="pos">{h(p["position"])}</a>' if p['position'] else ''
        nat_link  = nat_cell(p['nationality'], '../')
        avg_cell  = f'<span class="{rating_class(avg)}">{avg}</span>'
        rows.append(
            f'<tr><td>{name_link}</td><td>{team_link}</td><td>{lg_link}</td>'
            f'<td>{pos_link}</td><td class="nat">{nat_link}</td>'
            f'<td class="num" title="{p["dob"]}">{p["age"]}</td>'
            f'<td class="num">{avg_cell}</td></tr>'
        )

    body = f'''
    <p class="muted" style="margin-bottom:1rem">{len(players_raw):,} players across all leagues.
    Search by name, team, league, position or nationality.</p>
    <div class="filter-bar">
      <input data-filter="all-players" placeholder="Search players…" autofocus>
    </div>
    <table id="all-players">
      <thead><tr>
        <th data-sort>Player</th>
        <th data-sort>Team</th>
        <th data-sort>League</th>
        <th data-sort>Position</th>
        <th data-sort>Nationality</th>
        <th class="num" data-sort>Age</th>
        <th class="num" data-sort>Rating</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>'''

    write(f"{OUT_DIR}/players/index.html",
          page("Players", body, depth=1, active='Players',
               header_title="All Players",
               header_sub=f"{len(players_raw):,} players — search by name, team, position or nationality"))


# ── CREDITS ───────────────────────────────────────────────────────────────────

def make_credits():
    prefix = '../'
    players_by_name = defaultdict(list)
    for p in players_raw:
        players_by_name[(p['first_name'], p['last_name'])].append(p)

    rows = []
    for first, last, role in CREDITS:
        matches = [] if (first, last) in NO_PLAYER_MATCH else players_by_name.get((first, last), [])
        if matches:
            p = matches[0]
            avg = pr(p)
            name_cell = f'<a href="../{player_anchor(first, last, p["team"])}">{h(first)} {h(last)}</a>'
            pos_cell  = f'<a href="{pos_url(p["position"], prefix)}" class="pos">{h(p["position"])}</a>' if p['position'] else ''
            nat_html  = nat_cell(p['nationality'], prefix)
            age_cell  = f'<span title="{p["dob"]}">{p["age"]}</span>'
            avg_cell  = f'<span class="{rating_class(avg)}">{avg}</span>'
            if len(matches) > 1:
                extra = ', '.join(
                    f'<a href="../{player_anchor(m["first_name"], m["last_name"], m["team"])}">{h(m["team"])}</a>'
                    for m in matches[1:]
                )
                name_cell += f' <span class="muted" style="font-size:0.8rem">(also: {extra})</span>'
        else:
            name_cell = f'{h(first)} {h(last)}'
            pos_cell = nat_html = age_cell = avg_cell = ''

        rows.append(
            f'<tr>'
            f'<td>{name_cell}</td>'
            f'<td>{h(role)}</td>'
            f'<td>{pos_cell}</td>'
            f'<td class="nat">{nat_html}</td>'
            f'<td class="num">{age_cell}</td>'
            f'<td class="num">{avg_cell}</td>'
            f'</tr>'
        )

    matches_count = sum(1 for f, l, _ in CREDITS if (f, l) in players_by_name)
    body = f'''
    <p class="muted" style="margin-bottom:1rem">
      The team who made FIFA Soccer Manager 97, as credited in the end-credits video.
      {matches_count} of {len(CREDITS)} people also appear as players in the game database.
    </p>
    <table id="credits-table">
      <thead><tr>
        <th data-sort>Name</th>
        <th data-sort>Role</th>
        <th data-sort>Position</th>
        <th data-sort>Nationality</th>
        <th class="num" data-sort>Age</th>
        <th class="num" data-sort>Rating</th>
      </tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    <h2 style="margin:2rem 0 1rem">End credits video</h2>
    <iframe width="560" height="315" src="https://www.youtube.com/embed/S8Ir0qe_7p8?si=iEr-KD7r7NSXhC5z" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'''

    write(f"{OUT_DIR}/credits/index.html",
          page("Game Credits", body, depth=1, active='Credits',
               header_title="Game Credits",
               header_sub="The team behind FIFA Soccer Manager 97"))


# ── SITEMAP ───────────────────────────────────────────────────────────────────

def make_sitemap():
    if not BASE_URL:
        return

    urls = [
        '/',
        '/leagues/',
        '/teams/',
        '/stadiums/',
        '/positions/',
        '/nationalities/',
        '/players/',
        '/stats/',
        '/stats/top-players/',
        '/stats/skill-leaders/',
        '/stats/age-groups/',
        '/stats/player-managers/',
        '/stats/stadiums/',
        '/stats/squads/',
        '/stats/nationalities/',
        '/stats/best-of/',
        '/trivia/',
        '/trivia/players/',
        '/trivia/stadiums/',
        '/trivia/clubs/',
        '/credits/',
    ]

    for lg in sorted(league_names):
        urls.append(f'/leagues/{slug(lg)}/')

    named_stadiums = sorted(s for s in stadium_to_teams if not re.match(r'^XX\d+$', s.strip()))
    for sname in named_stadiums:
        urls.append(f'/stadiums/{slug(sname)}/')

    for t in sorted(teams_raw, key=lambda t: t["team"]):
        urls.append(f'/teams/{slug(t["team"])}/')

    for pos in pos_order:
        if players_by_position.get(pos):
            urls.append(f'/positions/{slug(pos)}/')

    for nat in sorted(players_by_nationality):
        if nat:
            urls.append(f'/nationalities/{slug(nat)}/')

    loc_lines = '\n'.join(f'  <url><loc>{BASE_URL}{u}</loc></url>' for u in urls)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{loc_lines}
</urlset>'''

    write(f"{OUT_DIR}/sitemap.xml", xml)
    print(f"  Written: sitemap.xml ({len(urls)} URLs)")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    global CSV_DIR, OUT_DIR, BASE_URL
    global ds, teams_raw, players_raw, skills_raw, positions_raw, countries_raw
    global teams_by_slug, league_names, teams_by_league, players_by_team
    global skills_by_player, players_by_nationality, players_by_position
    global positions_info, stadium_to_teams, prating, pos_ratings_by_player
    global max_cap, pos_order, team_by_name
    global nat_to_country, nat_to_flag, league_to_flag, country_name_to_flag

    parser = argparse.ArgumentParser(description="Generate FIFA Soccer Manager 97 static site")
    parser.add_argument('--csv-dir',  default='csv',  help="Input CSV directory (default: ./csv)")
    parser.add_argument('--out-dir',  default='www',  help="Output directory (default: ./www)")
    parser.add_argument('--base-url', default=None,   help="Base URL for sitemap (e.g. https://example.com)")
    args = parser.parse_args()

    CSV_DIR  = args.csv_dir
    OUT_DIR  = args.out_dir
    BASE_URL = args.base_url.rstrip('/') if args.base_url else None

    ds = Dataset(CSV_DIR)
    teams_raw              = ds.teams
    players_raw            = ds.players
    skills_raw             = ds.skills
    positions_raw          = ds.positions
    countries_raw          = ds.countries
    teams_by_slug          = ds.teams_by_slug
    league_names           = ds.league_names
    teams_by_league        = ds.teams_by_league
    players_by_team        = ds.players_by_team
    skills_by_player       = ds.skills_by_player
    players_by_nationality = ds.players_by_nationality
    players_by_position    = ds.players_by_position
    positions_info         = ds.positions_info
    stadium_to_teams       = ds.stadium_to_teams
    prating                = ds.prating
    pos_ratings_by_player  = ds.pos_ratings_by_player
    max_cap                = ds.max_cap
    pos_order              = POS_ORDER
    team_by_name           = {t['team']: t for t in teams_raw}
    nat_to_country         = {c['demonym']: c['country'] for c in countries_raw}
    nat_to_flag            = {c['demonym']: country_flag(c['code']) for c in countries_raw}
    country_name_to_flag   = {c['country']: country_flag(c['code']) for c in countries_raw}
    league_to_flag         = {lg: country_name_to_flag.get(cn, '')
                               for cn, lgs in LEAGUE_GROUPS for lg in lgs}
    # Add Others-country names via OTHERS_COUNTRIES values
    for cname in OTHERS_COUNTRIES.values():
        country_name_to_flag.setdefault(cname, country_name_to_flag.get(cname, ''))

    write(f"{OUT_DIR}/style.css", CSS)
    print("Generating home…")
    make_home()
    print("Generating leagues…")
    make_leagues()
    print("Generating teams…")
    make_teams()
    print("Generating players…")
    make_players()
    print("Generating stadiums…")
    make_stadiums()
    print("Generating positions…")
    make_positions()
    print("Generating nationalities…")
    make_nationalities()
    print("Generating stats…")
    make_stats_index()
    make_stats_top_players()
    make_stats_skill_leaders()
    make_stats_age_groups()
    make_stats_player_managers()
    make_stats_stadiums()
    make_stats_squads()
    make_stats_nationalities()
    make_stats_best_of()
    print("Generating trivia…")
    make_trivia()
    print("Generating credits…")
    make_credits()
    print("Generating sitemap…")
    make_sitemap()

    # Count files
    total = sum(len(fs) for _, _, fs in os.walk(OUT_DIR))
    print(f"\nDone — {total} files written to {OUT_DIR}")


if __name__ == '__main__':
    main()
