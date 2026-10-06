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
- **No generated art or images.** Don't draw illustrations or decorative graphics yourself. If a lesson needs a picture, ask me
  (I'll supply it) or pull one from the web or my books, credited. Data-driven visuals (plots of formulas, game boards from
  positions, timelines from dates, maps from open map data) are fine unless I say otherwise.
- **The point is learning what I want to learn, not completing a college major.** Majors are just an organizing tool: keep what helps
  (book order, prerequisites, pretests, review) and deviate whenever there's real value in it (follow my interests, reorder, skip,
  add a tangent). Say so briefly when you deviate; don't ask permission for small changes.
- **Each subject is a major**, not a single course: plan it as a multi-course program (prerequisites, courses, placement),
  even for non-academic subjects like chess.
- Fun subject: **the Games major** (`topics/games/PROGRAM.md`), replacing chess as a standalone major; **chess is its first class**
  (lessons stay in `topics/chess/`). **Military Strategy is part of the Games major** (G150; lessons stay in `topics/military-strategy/`;
  framed as decision systems, not glorifying war). Mission: design a balanced 3D strategy game; the 3D chess variant is the running project. Non-technical subject: **Indian History** (chosen 2026-10-05 after the
  pretests; Economics parked, already solid at Principles level). Each major has a `PROGRAM.md` in its topic folder.
- Study plan (proposed 2026-10-05, see `notes/study-plan.md`): 4 subjects, 2 full (Statistics, AWS ML cert) + 2 half
  (one non-technical, one fun), daily review first. **Finish the whole day's plan before going deeper on any one subject**;
  extra time beyond the 1-hour floor is welcome after that.
- Chess.com username: rahulsanjay18 (I rarely play online). No Go account; I don't play Go online.

## Program layer (/program)
- This is a **general learning platform**: the majors in `programs.json` come first, but I'll ask for other subjects too. Every major
  (new or revised) follows `notes/major-design.md` (shape adapted from NYU Gallatin, but **this is assisted textbook reading, not a
  college**): a core sequence of books is the major; levels I (≈ undergraduate) and II (≈ graduate, opt-in); breadth, practice,
  capstones and an end-of-level conversation are optional extras, never requirements. Keep a "books needed" list; ask me for books.
- `/program` runs the majors: it prints today's plan and where each major stands (`programs.json` + `topics/<major>/curriculum.json`
  + the progress server), then teaches with /teach conventions. Start a learning session with it.
- After every lesson, update the major's `curriculum.json` (`lessons`, `plan`, `completed`) and run `python3 scripts/test_programs.py`.

## Handoff
- `notes/HANDOFF.md`: current state and to-do list across all topics and the platform. Read it at the start of a new thread; keep it current.

## Teaching log (read before writing any lesson)
- `TEACHING-LOG.md` at the repo root lists past teaching mistakes and the rules that prevent them, across all subjects. Read it
  before writing a lesson. When my questions or results reveal a flaw in an explanation or lesson, add an entry and a rule.
- Each topic keeps a `QUESTIONS.md`: my questions with the answers given.
- **Lesson design, all subjects:** assign a reading before the lesson whenever it makes sense (a short, specific primary-source slice
  with a reading guide). **Homework is fine but optional**: keep it small, and make every lesson work even if I skipped it
  (I'm not sure how much I'll do). Details: TEACHING-LOG.md rules 9 and 13.

## Progress server (`$BOOKS_URL/progress`, see `progress-server/README.md`)
- Session start: `/program` shows the digest (it calls `/progress/status`). Grade waiting free responses with
  `python3 scripts/grade.py` (answer + prompt + rubric), then `python3 scripts/grade.py post grades.json`.
- If I paste `lp-results …` lines: `python3 scripts/lp_results.py "<lines>"` records them in the curriculum; then decide on a learning record.
- If the server is unreachable, fall back to `lp-results` lines I paste.
- To pair a device: `POST /progress/devices {"name":"phone"}` and give me `<PAGES_URL>/assets/sync.html#endpoint=$BOOKS_URL/progress&token=<token>`.

## Tools: use these by default (they exist to save tokens; don't hand-roll what they do)
| Job | Use |
|---|---|
| Start a learning session / what's next | the `/program` skill |
| Write a lesson | Markdown + `python3 scripts/render_lesson.py topics/<t>/lessons/NNNN-x.md --course <ID>` (never hand-write lesson HTML) |
| Grade free responses | `python3 scripts/grade.py`, then `grade.py post grades.json` |
| Record pasted results | `python3 scripts/lp_results.py "<lp-results lines>"` |
| Look things up in my books | `python3 scripts/books.py find / search --book <id> / grep <id> "<phrase>" / read <id> <line> <n>` |
| Quick review in chat | the `/quiz-me` skill (`scripts/quiz.py`) |
| A game I played | the `/game-review` skill |
| I added books | the `/new-books` skill (`scripts/new_books.py`; server steps in `library/ADDING-BOOKS.md`) |
| Before committing | `bash scripts/check_all.sh --quick` (drop `--quick` after widget changes) |
| Widget markup | `assets/README.md` (don't read the JS source) |

## Shared lesson library (overrides the skill's per-topic `./assets/` guidance)
- All lessons and reference pages use the shared files in `assets/` at the repo root: `lp.css`, `lp.js`, and `assets/plugins/*` for
  subject-specific widgets (math, chess, Go, pixel art). Before writing a lesson, read `assets/README.md` (markup for every widget). Don't read the JS source.
- Never create a per-topic copy of a stylesheet or quiz script. Topic-only styles go in `topics/<slug>/assets/topic.css`.
  A widget another topic could reuse goes in `assets/` (generic) or `assets/plugins/` (subject-specific), and gets an example in `assets/gallery.html`.
- Keep CSS plain and quiet (one column, serif text, thin rules; no shadows, gradients or animation).
- **Write new lessons in Markdown** and render them: `python3 scripts/render_lesson.py topics/<t>/lessons/NNNN-x.md --course <ID>` (syntax: assets/README.md "Writing lessons in Markdown"). It also updates index.html and curriculum.json.
- Give every quiz a short `data-id`. Before committing run `bash scripts/check_all.sh` (all suites, one line each). Token-saving tools (grading packets, book lookups, results recording): the table in `.claude/skills/program/SKILL.md`.
- Daily review (`assets/review.html`) re-asks due questions from their lessons. Keep quiz `data-id`s stable; put a needed diagram right before its quiz (or use `data-context`).
- If I paste an `lp-results …` line, it's my results from a lesson: record it with `scripts/lp_results.py`, then use it for learning records and to choose what's next.

## My library (check before searching the web)
- Read `library/README.md` before using anything in `library/` or the book server, and follow it exactly. It says
  which books are safe to teach from (grades A/B/C/F in `library/MANIFEST.csv`).
- When creating or updating RESOURCES.md, search `library/MANIFEST.csv`, `library/LIBRARY.md`
  and `library/ACCESS.md` first. Mark entries "(in collection)", "(via <source>)", or "(check: <link>)", following library/ACCESS.md.
- If nothing in my collection or sources fits, say so in RESOURCES.md's Gaps section, then search the web.


