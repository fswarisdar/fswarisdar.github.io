#!/usr/bin/env python3
"""Fetch publications from Semantic Scholar and rebuild publications.html."""
from __future__ import annotations

import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

AUTHOR_ID = "152567681"
BASE = "https://api.semanticscholar.org/graph/v1"
FIELDS = "title,year,citationCount,venue,authors,externalIds,url"
OUT = Path(__file__).with_name("publications.html")
INDEX = Path(__file__).with_name("index.html")
META_JSON = Path(__file__).with_name("ss_meta.json")


def api_get(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "fahadsabah-portfolio-sync/1.0 (github pages)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_author() -> dict:
    q = urllib.parse.urlencode({"fields": "name,paperCount,citationCount,hIndex"})
    return api_get(f"{BASE}/author/{AUTHOR_ID}?{q}")


def fetch_papers() -> list[dict]:
    papers: list[dict] = []
    offset = 0
    limit = 100
    while True:
        q = urllib.parse.urlencode(
            {"fields": FIELDS, "limit": limit, "offset": offset}
        )
        data = api_get(f"{BASE}/author/{AUTHOR_ID}/papers?{q}")
        batch = data.get("data") or []
        papers.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
        if offset > 500:
            break
    return papers


def author_line(paper: dict) -> str:
    authors = paper.get("authors") or []
    compact = []
    for a in authors[:12]:
        name = (a.get("name") or "").strip()
        parts = [p for p in re.split(r"\s+", name) if p]
        if len(parts) >= 2:
            initials = "".join(p[0] for p in parts[:-1])
            compact.append(f"{initials} {parts[-1]}")
        elif parts:
            compact.append(parts[0])
    line = ", ".join(compact)
    if len(authors) > 12:
        line += ", et al."
    return line


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def render_html(author: dict, papers: list[dict], synced_at: str) -> str:
    by_year: dict[str | int, list[dict]] = defaultdict(list)
    for p in papers:
        title = (p.get("title") or "").strip()
        if not title:
            continue
        year = p.get("year")
        key: str | int = year if isinstance(year, int) else "Other / undated"
        by_year[key].append(p)

    def sort_key(k: str | int):
        return (0, -k) if isinstance(k, int) else (1, str(k))

    blocks = []
    for year in sorted(by_year.keys(), key=sort_key):
        items = sorted(
            by_year[year],
            key=lambda p: (-(p.get("citationCount") or 0), (p.get("title") or "").lower()),
        )
        blocks.append(f'      <h2>{esc(str(year))}</h2>\n      <div class="year-block">')
        for p in items:
            cites = p.get("citationCount")
            cite_s = "—" if cites is None else str(cites)
            venue = (p.get("venue") or "").strip()
            venue_html = (
                f'\n            <span class="pub-venue">{esc(venue)}</span>' if venue else ""
            )
            blocks.append(
                f'''        <article class="pub-item">
          <div>
            <span class="pub-title">{esc(p.get("title") or "")}</span>
            <span class="pub-authors">{esc(author_line(p))}</span>{venue_html}
          </div>
          <span class="cite" title="Cited by (Semantic Scholar)">{esc(cite_s)}</span>
        </article>'''
            )
        blocks.append("      </div>")

    body = "\n".join(blocks)
    name = author.get("name") or "Fahad Sabah"
    citations = author.get("citationCount")
    h_index = author.get("hIndex")
    paper_count = author.get("paperCount") or len(papers)
    metrics = (
        f"{citations} citations · h-index {h_index} · {paper_count} papers"
        if citations is not None
        else f"{paper_count} papers"
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Publications — Fahad Sabah</title>
  <meta name="description" content="Publication list for Fahad Sabah, synced from Semantic Scholar." />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="site-header">
    <div class="wrap">
      <p class="brand"><a href="index.html">Fahad Sabah</a></p>
      <nav aria-label="Primary">
        <a href="index.html#research">Research</a>
        <a href="publications.html" aria-current="page">Publications</a>
        <a href="index.html#appointments">Appointments</a>
        <a href="index.html#teaching">Teaching</a>
        <a href="index.html#contact">Contact</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="wrap page-hero page-hero-with-photo">
      <img class="portrait" src="photo.jpg" width="180" height="180" alt="Portrait of Fahad Sabah" />
      <div>
        <p class="eyebrow">Auto-synced from Semantic Scholar</p>
        <h1>Publications</h1>
        <p class="lede">
          Arranged by year (newest first). Citation counts from
          <a href="https://www.semanticscholar.org/author/{AUTHOR_ID}">Semantic Scholar</a>
          (often lower than Google Scholar). List refreshes weekly via GitHub Actions.
        </p>
        <p class="meta">{esc(metrics)} <span class="meta-note">(synced {esc(synced_at)})</span></p>
        <div class="cta">
          <a class="btn primary" href="https://scholar.google.com/citations?user=o41wvoGBicEC">Google Scholar</a>
          <a class="btn" href="https://orcid.org/0000-0003-1558-2616">ORCID</a>
          <a class="btn" href="https://www.semanticscholar.org/author/{AUTHOR_ID}">Semantic Scholar</a>
          <a class="btn" href="index.html">Home</a>
        </div>
      </div>
    </section>

    <section class="wrap section">
{body}
      <p class="more">
        Author profile on Semantic Scholar may miss some works.
        For application metrics, prefer
        <a href="https://scholar.google.com/citations?user=o41wvoGBicEC">Google Scholar</a>.
      </p>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p>© {esc(name)} · <a href="index.html">Home</a> · publications auto-updated from Semantic Scholar</p>
    </div>
  </footer>
</body>
</html>
'''


def patch_index(author: dict, synced_at: str) -> None:
    if not INDEX.exists():
        return
    text = INDEX.read_text(encoding="utf-8")
    citations = author.get("citationCount")
    h_index = author.get("hIndex")
    if citations is None or h_index is None:
        return
    # Keep Scholar snapshot wording on home for applications; add SS note only if a marker exists.
    note = (
        f'Semantic Scholar (auto): {citations} citations · h-index {h_index} '
        f'<span class="meta-note">(synced {html.escape(synced_at)})</span>'
    )
    if 'id="ss-metrics"' in text:
        text = re.sub(
            r'<p class="meta" id="ss-metrics">.*?</p>',
            f'<p class="meta" id="ss-metrics">{note}</p>',
            text,
            count=1,
            flags=re.S,
        )
    else:
        # Insert after the main Scholar metrics paragraph in the hero.
        text = text.replace(
            '<div class="cta">\n          <a class="btn primary" href="publications.html">All publications</a>',
            f'<p class="meta" id="ss-metrics">{note}</p>\n        <div class="cta">\n          <a class="btn primary" href="publications.html">All publications</a>',
            1,
        )
    INDEX.write_text(text, encoding="utf-8")


def main() -> None:
    print(f"Fetching Semantic Scholar author {AUTHOR_ID}…")
    author = fetch_author()
    papers = fetch_papers()
    synced_at = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    print(
        f"Author={author.get('name')} papers={len(papers)} "
        f"citations={author.get('citationCount')} h={author.get('hIndex')}"
    )
    html_out = render_html(author, papers, synced_at)
    OUT.write_text(html_out, encoding="utf-8")
    patch_index(author, synced_at)
    META_JSON.write_text(
        json.dumps(
            {
                "authorId": AUTHOR_ID,
                "syncedAt": synced_at,
                "name": author.get("name"),
                "paperCount": author.get("paperCount"),
                "citationCount": author.get("citationCount"),
                "hIndex": author.get("hIndex"),
                "papersRendered": len(papers),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT.name}, updated {INDEX.name}, {META_JSON.name}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Semantic Scholar HTTP error: {e.code} {e.reason}") from e
    except Exception as e:
        raise SystemExit(f"Sync failed: {e}") from e
