import shutil
from pathlib import Path

from chameleon import PageTemplateLoader


BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
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


class Scribe:
    def __init__(self, output_dir=OUT_DIR):
        self.output_dir = Path(output_dir)
        self.templates = PageTemplateLoader(
            search_path=[str(TEMPLATES_DIR)],
            default_extension=".pt",
        )

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
        content = self.render(
            "home",
            nav_links=NAV_LINKS,
            active="Home",
            page_title="FIFA Soccer Manager 97",
            header_title="FIFA Soccer Manager 97",
            header_sub="Interactive database — 1996/97 season",
            breadcrumb="",
        )
        self.write_file("index.html", content)
