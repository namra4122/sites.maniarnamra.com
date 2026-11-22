#!/usr/bin/env python3
"""Make every HTML file given as an argument load GA through /assets/ga.js.

- A page that already includes /assets/ga.js is left alone.
- A legacy inline gtag snippet (any measurement ID, including one left over
  from the upstream fork) is replaced by the ga.js include.
- Otherwise the include is inserted right after <head>.

The measurement ID and consent handling live only in assets/ga.js.
"""
import re
import sys

INCLUDE = '<script async src="/assets/ga.js"></script>\n'
INCLUDE_RE = re.compile(r"""<script[^>]+src=["']/assets/ga\.js["']""", re.IGNORECASE)
# Optional "<!-- Google tag (gtag.js) -->" comment, the gtag.js loader and the
# inline bootstrap script that calls gtag('config', ...).
LEGACY_RE = re.compile(
    r"""[ \t]*(?:<!--\s*Google tag \(gtag\.js\)\s*-->\s*)?"""
    r"""<script[^>]*src=["']https://www\.googletagmanager\.com/gtag/js\?id=[^"']+["'][^>]*>\s*</script>\s*"""
    r"""<script>(?:(?!</script>).)*?gtag\(\s*["']config["'](?:(?!</script>).)*?</script>[ \t]*\r?\n?""",
    re.IGNORECASE | re.DOTALL,
)
HEAD_RE = re.compile(r"<head(\s[^>]*)?>[ \t]*\r?\n?", re.IGNORECASE)

changed = 0
for path in sys.argv[1:]:
    with open(path, encoding="utf-8", newline="") as f:
        html = f.read()
    if INCLUDE_RE.search(html):
        print(f"ok (already loads ga.js): {path}")
        continue
    if LEGACY_RE.search(html):
        html = LEGACY_RE.sub(INCLUDE, html, count=1)
        action = "migrated"
    else:
        m = HEAD_RE.search(html)
        if not m:
            print(f"skip (no <head>, likely a fragment): {path}")
            continue
        html = html[: m.end()] + INCLUDE + html[m.end():]
        action = "injected"
    if "googletagmanager.com/gtag/js" in html:
        print(f"warning: {path} still loads gtag.js directly; fix by hand", file=sys.stderr)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"{action}: {path}")
    changed += 1
print(f"{changed} file(s) modified")
