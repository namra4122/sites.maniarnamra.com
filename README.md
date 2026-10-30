# sites.maniarnamra.com

Dumpyard for LLM-agent-generated static sites by Namra Maniar.
Served via Cloudflare at
<https://sites.maniarnamra.com>.

## Layout

- `/index.html` — apex page. Spartan. Keep it that way.
- `/research/<report-name>/index.html` — reports.
- `/learning/<guide-name>/index.html` — guides.
- `/llms.txt` — instructions for LLMs uploading to this repo. Read it before adding anything.

## Rules

- Every page is self-contained HTML with inline CSS/JS. No build step, no frameworks, no external dependencies unless unavoidable.
- Slugs are lowercase kebab-case.
- Adding a page? Follow `/llms.txt`.
