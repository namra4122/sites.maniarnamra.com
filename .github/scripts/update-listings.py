#!/usr/bin/env python3
"""Regenerate research/index.html and learning/index.html listings from slug dirs,
and write search-index.json (read by the Cmd+K palette in assets/cmdk.js).

Usage: update-listings.py [repo-root]  (defaults to cwd)
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
UL_RE = re.compile(r"<ul>.*?</ul>", re.DOTALL)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL | re.IGNORECASE)
DESC_RE = re.compile(
    r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", re.DOTALL | re.IGNORECASE
)
KINDS = {"research": "report", "learning": "guide"}
INDEX = "search-index.json"


def clean(text: str) -> str:
    return " ".join(html.unescape(text).split())


def title_of(page: Path, slug: str) -> str:
    m = TITLE_RE.search(page.read_text(encoding="utf-8"))
    return clean(m.group(1)) if m else slug


def entries(name: str) -> list:
    base = ROOT / name
    out = []
    for s in sorted(p.name for p in base.iterdir() if p.is_dir() and (p / "index.html").is_file()):
        text = (base / s / "index.html").read_text(encoding="utf-8")
        t = TITLE_RE.search(text)
        m = DESC_RE.search(text)
        out.append({
            "title": clean(t.group(1)) if t else s,
            "url": f"/{name}/{s}/",
            "section": name,
            "description": clean(m.group(1)) if m else "",
        })
    return out


def write_index() -> bool:
    pages = [e for section in KINDS if (ROOT / section).is_dir() for e in entries(section)]
    new = json.dumps({"pages": pages}, ensure_ascii=False, indent=2) + "\n"
    path = ROOT / INDEX
    if path.is_file() and path.read_text(encoding="utf-8") == new:
        print(f"unchanged {INDEX}")
        return False
    path.write_text(new, encoding="utf-8")
    print(f"updated   {INDEX} ({len(pages)} entries)")
    return True


def update(name: str) -> bool:
    base = ROOT / name
    kind = KINDS[name]
    slugs = sorted(
        p.name for p in base.iterdir() if p.is_dir() and (p / "index.html").is_file()
    )
    if slugs:
        items = "\n".join(
            f'  <li><a href="/{name}/{s}/">'
            f"{html.escape(title_of(base / s / 'index.html', s))}</a></li>"
            for s in slugs
        )
    else:
        items = "  <li><em>Nothing here yet.</em></li>"
    block = (
        "<ul>\n"
        f'  <!-- one <li> per {kind}: <li><a href="/{name}/slug/">Title</a></li> -->\n'
        f"{items}\n"
        "</ul>"
    )
    listing = base / "index.html"
    text = listing.read_text(encoding="utf-8")
    new, n = UL_RE.subn(block, text, count=1)
    if n == 0:
        print(f"error: no <ul> block in {listing}", file=sys.stderr)
        sys.exit(1)
    if new == text:
        print(f"unchanged {listing.relative_to(ROOT)}")
        return False
    listing.write_text(new, encoding="utf-8")
    print(f"updated   {listing.relative_to(ROOT)} ({len(slugs)} entries)")
    return True


if __name__ == "__main__":
    changed = False
    for section in KINDS:
        if (ROOT / section / "index.html").is_file():
            changed |= update(section)
    changed |= write_index()
    sys.exit(0)
