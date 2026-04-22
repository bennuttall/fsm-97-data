import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from .enrich import Manifest


def load_csv(csv_path: Path) -> list[dict]:
    with open(csv_path) as f:
        return list(csv.DictReader(f))


def load_all_csvs(csv_dir: Path) -> list[dict]:
    rows = []
    for f in sorted(csv_dir.rglob("*.csv")):
        rows.extend(load_csv(f))
    return rows


def build_analytics(rows: list[dict], manifest: Manifest | None = None, base_url: str = "") -> dict:
    human_rows = [r for r in rows if r.get("is_bot", "False") not in ("True", True)]
    bot_rows = [r for r in rows if r.get("is_bot", "False") in ("True", True)]

    times = [datetime.fromisoformat(r["time"]) for r in human_rows]
    dates = sorted(set(t.date() for t in times))
    hits_by_day = [sum(1 for t in times if t.date() == d) for d in dates]

    month_counts = Counter(t.strftime("%Y-%m") for t in times)
    months_iso = sorted(month_counts)
    hits_by_month = [month_counts[m] for m in months_iso]

    path_counts = Counter(r["path"] for r in human_rows)
    ua_all = Counter(r["ua"] for r in rows)
    ua_bot = Counter(r["ua"] for r in bot_rows)
    ua_counts = [
        {"ua": ua, "hits": n, "is_bot": ua_bot[ua] > n / 2} for ua, n in ua_all.most_common(15)
    ]
    unique_ips = len(set(r["remote_host"] for r in human_rows))

    base_domain = (
        base_url.replace("https://", "").replace("http://", "").rstrip("/") if base_url else ""
    )
    referer_counts = Counter(
        r["referer"] for r in human_rows if r.get("referer") and r["referer"] != base_domain
    ).most_common(20)

    pages = []
    for path, n in path_counts.most_common():
        info = manifest.get(path) if manifest else None
        if not info:
            continue
        parts = path.strip("/").split("/")
        section = parts[0] if parts[0] else "home"
        pages.append({"path": path, "title": info["title"], "hits": n, "section": section})

    section_pages = {
        s: [p for p in pages if p["section"] == s and len(p["path"].strip("/").split("/")) > 1][:10]
        for s in ("clubs", "stadiums", "leagues")
    }

    total = len(rows)
    bot_pct = round(100 * len(bot_rows) / total, 1) if total else 0.0

    return {
        "date_from": dates[0].isoformat() if dates else "",
        "date_to": dates[-1].isoformat() if dates else "",
        "total_hits": total,
        "bot_hits": bot_pct,
        "unique_ips": unique_ips,
        "dates": [d.isoformat() for d in dates],
        "hits_by_day": hits_by_day,
        "months": months_iso,
        "hits_by_month": hits_by_month,
        "pages": pages,
        "section_pages": section_pages,
        "ua_counts": ua_counts,
        "referer_counts": referer_counts,
        "base_url": base_url,
    }
