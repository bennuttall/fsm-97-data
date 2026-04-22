# Log Processing & Analytics

How Apache access logs are processed into traffic analytics for fsm.bennuttall.com.

This is based on the same approach used in [beemo](https://github.com/bennuttall/beemo),
a static site framework. The log processing and analytics modules here are adapted from beemo's
equivalent modules.

---

## Overview

The pipeline has three stages:

1. **Log processing** — parse gzipped Apache logs into CSV files (`fsm-logs`)
2. **Site build** — generate `manifest.json` alongside the HTML (`fsm-scribe`)
3. **Analytics generation** — combine CSVs + manifest into an analytics site (`fsm-analytics`)

---

## Log Processing

Apache access logs (Combined Log Format, gzipped) live in `logs/apache2/`. The `fsm-logs`
command processes them into CSVs in `logs/csv/`.

```
fsm-logs logs/apache2 --csv-dir logs/csv
```

Or via Make:

```
make logs
```

Each `.gz` file produces one `.csv` file. Already-processed files are skipped, so the command
is safe to run repeatedly as new logs arrive.

### Filtering

Only requests that pass all of the following are kept:

- HTTP status 200 or 304
- URL path ends in `/`, `.html`, or `.htm` (HTML pages only — assets and API requests excluded)

### Output columns

| Column | Description |
|---|---|
| `time` | Request timestamp (ISO format) |
| `remote_host` | Client IP address |
| `path` | Normalised URL path |
| `ua` | Simplified browser/bot name |
| `is_bot` | `True` if the user agent is identified as a bot |
| `referer` | Referring domain (empty if none) |

### Path normalisation

- Double slashes (`//`) are collapsed to `/`
- `/index.html` and `/index.htm` suffixes are stripped (e.g. `/clubs/index.html` → `/clubs/`)

### User agent parsing

User agents are parsed using the [`user-agents`](https://pypi.org/project/user-agents/) library.
A small override list (`fsm97/logs/ua.py`) handles cases the library misidentifies, including
ChatGPT, Feedly, Bytespider, and Go-http-client.

---

## Manifest

The `fsm-scribe` build command writes `www/manifest.json` alongside the HTML output. The manifest
maps every URL on the site to its page title:

```json
[
    {"url": "/", "title": "FIFA Soccer Manager 97", "type": "page"},
    {"url": "/clubs/arsenal/", "title": "Arsenal", "type": "page"},
    ...
]
```

This is used by the analytics step to show human-readable page titles rather than raw URL paths.
The manifest covers all ~850 pages: static section indexes plus every per-league, per-nation,
per-club, per-stadium, per-position, and per-nationality page.

---

## Analytics Generation

The `fsm-analytics` command reads the log CSVs and manifest, computes stats, and writes a small
static analytics site to `www-analytics/`.

```
fsm-analytics --csv-dir logs/csv --manifest www/manifest.json --base-url https://fsm.bennuttall.com
```

Or via Make:

```
make analytics
```

### Output pages

| Path | Contents |
|---|---|
| `index.html` | Last 30 days (always regenerated) |
| `all/index.html` | All-time aggregate |
| `YYYY/index.html` | Per-year |
| `YYYY/MM/index.html` | Per-month |

Pages other than the summary are skipped if their output file is newer than all source CSVs and
the template, so re-running is fast.

### Metrics computed

- Total hits, bot percentage, unique IPs, date range
- Hits by day and by month (for Chart.js bar charts)
- Top pages by hit count (human traffic only, matched against manifest for titles)
- Top 15 user agents (bots shown in grey in the chart)
- Top 20 referring domains (own domain excluded)

### Serving locally

```
make serve-analytics
```

Serves `www-analytics/` on port 8001.
