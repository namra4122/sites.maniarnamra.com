#!/usr/bin/env python3
"""Fail if any page could send analytics to a property that isn't Namra's.

Rules (HTML and JS files, outside .github/):
1. Only assets/ga.js may load the Google tag (gtag.js / gtm.js). Pages
   include /assets/ga.js instead; inject-ga.py migrates legacy snippets.
2. No Google measurement/container IDs other than the allowed one, e.g. the
   upstream fork's G-J2YR2RVR6L coming back through `git merge upstream/main`.

Usage: check-analytics.py [repo-root]  (defaults to cwd)
"""
import pathlib
import re
import sys

ALLOWED_IDS = {"G-4H49QFHPQK"}
GA_LOADER = pathlib.PurePosixPath("assets/ga.js")
TAG_RE = re.compile(r"googletagmanager\.com/(?:gtag/js|gtm\.js)", re.IGNORECASE)
# G-/AW-/DC- IDs need at least one digit so ordinary words don't match.
ID_RE = re.compile(r"\b(?:(?:G|AW|DC)-(?=[A-Z0-9]*\d)[A-Z0-9]{8,12}|GTM-[A-Z0-9]{5,8}|UA-\d{4,10}-\d{1,4})\b")

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
problems = []
for path in sorted(root.rglob("*")):
    rel = pathlib.PurePosixPath(path.relative_to(root).as_posix())
    if not path.is_file() or path.suffix.lower() not in {".html", ".htm", ".js", ".mjs"}:
        continue
    if rel.parts[0] in {".git", ".github", "node_modules"}:
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if rel != GA_LOADER and TAG_RE.search(text):
        problems.append(f"{rel}: loads the Google tag directly; include /assets/ga.js instead "
                        f"(python3 .github/scripts/inject-ga.py {rel})")
    for m in sorted(set(ID_RE.findall(text)) - ALLOWED_IDS):
        problems.append(f"{rel}: unexpected analytics ID {m}")

if problems:
    print("Analytics check failed:\n  " + "\n  ".join(problems))
    sys.exit(1)
print("Analytics check passed: only assets/ga.js loads GA, with " + ", ".join(sorted(ALLOWED_IDS)))
