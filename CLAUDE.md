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
- Committing and pushing directly to `main` is fine (and preferred) for this repo: GitHub Pages serves from `main`,
  so lessons only become viewable once they're there. You don't need a PR or my approval to push to `main`.
  If a session is assigned a feature branch, push it and also merge it into `main` and push `main`.
- Don't ask me to merge anything. (A GitHub Action also auto-merges `claude/**` branches into main.)

PAGES_URL=https://rahulsanjay18.github.io/learning
BOOKS_URL=https://books.tail59e10.ts.net

## About me as a learner (applies to every topic)
- **Time: at least 1 hour a day for learning, total across all topics.** That is a floor I set myself, not a cap; it may go up.
  Plan so a day's work fits in that hour (short lessons + review, not one long one), and offer more when I have more time.
- Active topics (keep ~3 + a game): **Economics, Statistics** (start with a placement pretest; I have a math degree that included stats),
  **Indian History**, plus chess or Go on the side. Full wishlist: `notes/learning-wishlist.md`.
- Two kinds of goals: **career** (Statistics, ML/AI, AWS ML-track certification, NASM-CPT exam) and **"good for the soul"**
  (Indian History, Economics, games, arts...). Keep both in each week; exam prep is deadline-driven, so ask me for exam dates.
  I can supply study materials (prep books, practice exams) for the certifications.
- Chess.com username: rahulsanjay18 (I rarely play online). No Go account; I don't play Go online.

## Progress server (once deployed: `$BOOKS_URL/progress`, see `progress-server/README.md`)
- At the start of a teaching session, `curl -s "$BOOKS_URL/progress/status"` (auth is injected) for a ~15-line digest; use
  `/progress/summary?topic=<slug>` for one topic and `/progress/ungraded` + `POST /progress/grades` to grade free responses.
- If it isn't reachable yet, fall back to `lp-results` lines I paste.
- To pair a device: `POST /progress/devices {"name":"phone"}` and give me `<PAGES_URL>/assets/sync.html#endpoint=$BOOKS_URL/progress&token=<token>`.

## Shared lesson library (overrides the skill's per-topic `./assets/` guidance)
- All lessons and reference pages use the shared files in `assets/` at the repo root: `lp.css`, `lp.js`, and `assets/plugins/*` for
  subject-specific widgets (math, chess, Go, pixel art). Before writing a lesson, read `assets/README.md` (markup for every widget). Don't read the JS source.
- Never create a per-topic copy of a stylesheet or quiz script. Topic-only styles go in `topics/<slug>/assets/topic.css`.
  A widget another topic could reuse goes in `assets/` (generic) or `assets/plugins/` (subject-specific), and gets an example in `assets/gallery.html`.
- Keep CSS plain and quiet (one column, serif text, thin rules; no shadows, gradients or animation).
- Give every quiz a short `data-id`. Before committing a lesson run `python3 scripts/lint_lessons.py` and `node scripts/test_widgets.mjs`.
- Daily review (`assets/review.html`) re-asks due questions from their lessons. Keep quiz `data-id`s stable; put a needed diagram right before its quiz (or use `data-context`).
- If I paste an `lp-results …` line, it's my results from a lesson: use it for learning records and to choose what's next.

## My library (check before searching the web)
- Read `library/README.md` before using anything in `library/` or the book server, and follow it exactly. It says
  which books are safe to teach from (grades A/B/C/F in `library/MANIFEST.csv`).
- When creating or updating RESOURCES.md, search `library/MANIFEST.csv`, `library/LIBRARY.md`
  and `library/ACCESS.md` first. Mark entries "(in collection)", "(via <source>)", or "(check: <link>)", following library/ACCESS.md.
- If nothing in my collection or sources fits, say so in RESOURCES.md's Gaps section, then search the web.


