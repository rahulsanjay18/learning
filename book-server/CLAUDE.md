# Learning repo (used with the /teach skill in Claude Code cloud sessions)

This repo is my persistent storage for /teach. Cloud sessions start from a fresh clone and
only see what's committed, so anything not pushed is lost.

## Layout
- Each topic lives in `topics/<topic-slug>/`. Treat THAT folder as the /teach "current directory"
  (MISSION.md, RESOURCES.md, NOTES.md, learning-records/, lessons/, reference/, assets/ go inside it).
- If I say "continue <topic>", read `topics/<topic-slug>/` first. If the folder doesn't exist, start a new topic there.
- `index.html` at the repo root lists every topic and links each topic's lessons and reference docs. Keep it updated.

## Cloud-session rules (override anything in the skill that assumes a local machine)
- You can't open files in my browser. Instead, end each lesson by giving me the path, plus the
  GitHub Pages URL if `PAGES_URL` below is filled in: `<PAGES_URL>/topics/<slug>/lessons/<file>.html`.
- Lessons must be fully self-contained or use relative links only (they get served from GitHub Pages).
- Commit and push after every lesson and after every learning-record update, not just at the end.
  Use small commits with messages like `teach(<slug>): lesson 0003 <name>`.
- Don't ask me to merge anything; a GitHub Action merges your branch into main automatically.

PAGES_URL=
BOOKS_URL=

## My library (check before searching the web)
- Read `library/README.md` before using anything in `library/` or the book server, and follow it exactly. It says
  which books are safe to teach from (grades A/B/C/F in `library/MANIFEST.csv`).
- When creating or updating RESOURCES.md, search `library/MANIFEST.csv`, `library/LIBRARY.md`
  and `library/ACCESS.md` first. Mark entries "(in collection)", "(via <source>)", or "(check: <link>)", following library/ACCESS.md.
- If nothing in my collection or sources fits, say so in RESOURCES.md's Gaps section, then search the web.
