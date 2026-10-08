---
name: program
description: Run the learner's multi-course majors (Statistics, AWS ML cert, Indian History, Games). Use at the start of a learning session, or when asked "what's today", "what's next", "where am I", or to start, advance or finish a course. Decides the day's work from programs.json and each major's curriculum.json, then teaches with the /teach conventions.
argument-hint: "[status | <major-slug> | setup <major>]"
---

# /program: the layer above /teach

/teach runs one topic. /program decides **which** topic and course today, keeps each major's course map current, and moves
the learner through courses (placement → courses → checks). Lessons themselves still follow `.claude/skills/teach/SKILL.md`,
`CLAUDE.md`, `TEACHING-LOG.md` and `assets/README.md`.

## Where you are (computed before this skill loaded)

!`python3 ${CLAUDE_SKILL_DIR}/scripts/status.py`

If the block above is empty or shows an error, run `python3 .claude/skills/program/scripts/status.py` yourself.
Arguments: `$ARGUMENTS` (empty = run today's plan).

## Files
- `programs.json` (repo root): the week (which majors get today's two blocks), majors with weight, parked topics (a parked entry may carry a designed `curriculum`; tests and DAGs cover it).
- `topics/<major>/curriculum.json`: courses with `id`, `title`, `status` (`done` | `active` | `next` | `later`), `requires`,
  `topic` (lesson folder if not the major's own, e.g. Games → `chess`, `military-strategy`), `est_lessons`, `lessons` (file stems
  written), `completed` (stems the learner finished, recorded from pasted lp-results), `plan` (upcoming lessons, first = next),
  `pretest` (true = start the course with a pretest), `source`, `note`, `lane` (optional; with the curriculum's top-level `lanes` {day: lane}, the Today page shows only that day's lane), `books` ({primary, secondary[], tertiary[], skip[]}: a course
  is a block of its primary book; required for an active core course; `notes/major-design.md`). `topics/<major>/DAG.md` is generated
  by `scripts/major_dag.py`: rerun it after changing courses.
- `topics/<major>/SYLLABUS.md`: lesson-level plan for the active (and next) course: reading + 2–3 objectives per lesson, and a
  "Changes" log. `plan` in curriculum.json mirrors it. Write the next lesson *from* it; when a course starts, write its syllabus first.
- `topics/<major>/syllabi/<COURSE>.md` + `syllabi/PLAN.md`: the college-style course syllabus and program of study (every course,
  not only active ones; `notes/syllabus-standard.md`). The lesson-level SYLLABUS.md must agree with the course syllabus's schedule; when
  you change one, change the other and run `python3 scripts/render_syllabi.py`. New course or major → write its syllabus first.
- `topics/<major>/backlog.json` (optional, eng): project tickets mapped to courses; each lesson assigns one as a required rep
  (state assigned/shipped/skipped + dates); status shows open reps. Re-check the ticket on GitHub before assigning.
- `topics/<major>/catalog.json` (optional): a self-updating list of certs/skills/tracks with sources and a `verified` date;
  `scripts/catalog.py` lists what's due. Status shows CATALOG REFRESH DUE → re-check those entries on the web (official page first),
  update them, log changes in the topic's `CHANGES.md`; propose (don't make) plan changes they imply.
- `topics/<major>/PROGRAM.md`: the human-readable plan and its reasons. Change it when the plan changes, not for routine progress.

## What to do

**`/program status`**: show the block above in plain words (what's done, what's the learner's next step) and stop.

**`/program setup <major>`**, a new subject the learner asks for, or a major marked SETUP NEEDED: design it with
`notes/major-design.md`: a core sequence of books is the major (levels I and II); everything else is an optional extra.
Keep a "books needed" list for the learner. Don't build college bureaucracy. Ask its setup questions (the `setup` text in programs.json) with
AskUserQuestion where the answers are choices. Then write `topics/<slug>/MISSION.md`, `PROGRAM.md`, `curriculum.json` (placement first),
set `"curriculum"` in programs.json, and run the test (below). Until it's set up, give its blocks to the other full-weight major.

**`/program` (today) or `/program <major>`:**
1. **Grade first.** If the status shows ungraded free responses, `GET $BOOKS_URL/progress/ungraded`, grade against the lesson's
   rubric, `POST /progress/grades`, and add a short entry to the topic's `QUESTIONS.md` when feedback matters.
2. **For each of today's majors** (or just the named one), look at its active course line:
   - **Latest lesson NOT DONE YET** → don't write a new one. Give the learner its link
     (`<PAGES_URL>/topics/<topic>/lessons/<stem>.html`) and its reading, if any. Only prepare the next lesson if they ask or have extra time.
   - **Latest lesson DONE** → `GET /progress/summary?topic=<topic>`, write a learning record if it showed something new
     (the /teach format), then write the lesson named by the first `plan` entry, following /teach and CLAUDE.md
     (reading guide, optional homework, shared assets, lint + widget tests).
   - **Plan empty / estimate reached** → write the course check (chapter check, unit check, or a game-review lesson), then go to step 3.
3. **Starting a course:** open with its pretest unless the learner just tested out. Passing everything → set `"status": "done",
   "credit": "exam"` and move on. Never start a Level II course unless that level is in the major's `enrolled_levels`;
   when Level I is finished, ask whether they want to enroll in Level II.
3. **Finishing a course:** once its check is DONE, set it `done`. Pick the next **core** course whose `requires` are all `done`
   (prefer `next`, then the order in the file); offer optional extras only when they'd clearly help or the learner asks, set it `active`, choose its `books` (primary first), and fill its `plan` by slicing the primary book (rerun `scripts/major_dag.py`). If it has `pretest: true`,
   its first lesson is the pretest (see the major's PROGRAM.md for the format); after the pretest, rewrite `plan` to teach
   only what's missing and note the decision in NOTES.md.
4. **Grade by mastery (TEACHING-LOG rule 20):** each objective Got it / Not yet. Not yet → a 5-minute re-teach section in the
   next lesson of that course; a new lesson only for a prerequisite or a repeat Not yet, logged in SYLLABUS.md "Changes".
5. **Keep the map true after every lesson:** append the new stem to `lessons`, drop the `plan` entry it fulfilled, add stems to
   `completed` when the learner reports results without the progress server. Then run
   `python3 scripts/test_programs.py` and fix anything it reports.
6. **Commit and push** as CLAUDE.md says (`teach(<slug>): …` or `program: …`), update `notes/HANDOFF.md`, and end with the
   lesson links and the day's plan in one short list: review first, then block 1, then block 2.

## Tools (use these instead of reading files or hand-editing; they save most of the tokens)
| Job | Command |
|---|---|
| Grade free responses | `python3 scripts/grade.py` (answer + prompt + rubric per item), then `python3 scripts/grade.py post grades.json` |
| Record pasted results | `python3 scripts/lp_results.py "<lp-results lines>"` (marks lessons completed in curriculum.json) |
| Write a lesson | Markdown + `python3 scripts/render_lesson.py topics/<t>/lessons/NNNN-x.md --course <ID>` (updates index + curriculum) |
| Look something up in a book | `python3 scripts/books.py search "…" --book <id>`, `grep <id> "Definition 8.3.5"`, `read <id> <line> 60` |
| Quick review in chat (no new lesson) | the `/quiz-me` skill |
| Turn a Vim recording (`vim -W keys.log`) into drill notation | `python3 scripts/vimkeys.py keys.log` |
| Check a Vim drill (eng major) | `python3 scripts/vimcheck.py --drill topics/eng/vim-drills.json <id> "<keys>"` |
| Check before committing | `bash scripts/check_all.sh --quick` (add the browser test by dropping `--quick` when widgets changed) |

## Rules
- The learner's rule: **finish the whole day's plan before going deeper on one subject.** If they ask for more of one subject
  before the plan is done, say so once, then do what they ask.
- One active course per major is normal. Games may run two (G101 chess lab + one other).
- Don't invent courses or reorder a major without asking; propose the change and update PROGRAM.md once agreed.
- Keep this file and `status.py` small. If you need a new field, add it to `scripts/test_programs.py` and to "Files" above.
