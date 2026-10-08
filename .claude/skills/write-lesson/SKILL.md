---
name: write-lesson
description: Write one lesson end to end in any major (reading slice and guide, lesson body, questions, extra practice, render, review, curriculum update, commit and push), the same way every time. Use when a lesson has to be written, usually after /program has picked the major and course for today, or when asked for "the next lesson" or a lesson on a specific topic.
argument-hint: "<major> <course-id> [lesson topic]"
---

# /write-lesson: one lesson, start to finish

/program decides WHAT to teach today; /teach and PRINCIPLES.md say how to explain. This skill is the HOW of producing one
lesson file. It is a checklist: the rules live in the files named below, so read them there (copies drift). If this file and
a source file disagree, the source file wins; CLAUDE.md wins over everything.

Arguments: `$ARGUMENTS` (major slug, course id, optional topic; with no topic, write the first `plan` entry of the course).

## Source of truth (read before writing; skip what you already read this session)
| What | Where |
|---|---|
| Repo rules, cloud/push rules, tools table | `CLAUDE.md` |
| Teaching rules (every lesson) | `TEACHING-LOG.md`, rules section and "Why these rules exist" |
| How to explain, option building, visuals | `.claude/skills/teach/PRINCIPLES.md` |
| Lesson Markdown syntax, widgets, page skeleton | `assets/README.md` (never the JS source) |
| Book grades and lookups | `library/README.md`, `library/MANIFEST.csv`, `scripts/books.py` |
| Major's lesson anatomy and pace | `topics/<major>/PROGRAM.md` |
| Question families | `notes/practice-variants.md` (the questions themselves: the `write-questions` skill) |

## Inputs to gather (the lesson's facts come from here, not memory)
1. `topics/<major>/curriculum.json` → the course: `topic` (lesson folder, if not the major's own), `books` (primary first),
   `plan`, `lessons`, `completed`.
2. `topics/<major>/SYLLABUS.md` → this lesson's reading and 2–3 "you can…" objectives; `syllabi/<COURSE>.md` → its week.
3. `topics/<topic>/learning-records/` (latest 2–3) and `GET $BOOKS_URL/progress/summary?topic=<topic>`: any objective graded
   **Not yet** gets a 5-minute re-teach at the top (rule 20); terms missed or never taught get defined (rule 1).
4. `topics/<topic>/QUESTIONS.md` (what confused the learner before), `NOTES.md` if present, and the conversation itself
   (recent answers, complaints, interests).
5. `notes/ideas.md` and `notes/learning-wishlist.md`: use a parked idea as an example, dataset or article when it fits the
   lesson. Material only; never add it to the plan.

## Procedure
1. **Sync and pick the number.** `git pull origin main`. Next number = highest `NNNN` in `topics/<topic>/lessons/` + 1; confirm
   neither that file nor the stem is in the course's `lessons` (another session may have just written it). File:
   `topics/<topic>/lessons/NNNN-<dash-case-name>.md`.
2. **Reading slice and guide** (rules 9, 12, 15, 17). From the course's primary book: find the real section titles and pages with
   `python3 scripts/books.py find|search|grep|read` (check the book's grade first: A/B teach prose, B no equations, C toc only).
   Write a `::: reading` box (exact span, what to skip, notation traps) and 3 guide questions + "what surprised or confused you" as
   `free` boxes. Skip the reading only when it truly doesn't make sense, and say why in the lesson.
3. **Plan the body before writing it.** List the objectives, the unconditional truths they rest on, and at most ~2 new definitions
   (more → split; rule 21). Note which earlier concepts the lesson leans on: each gets a short recap box (rule 29a).
4. **Write the body** (Markdown, `assets/README.md` syntax):
   - "Why this lesson": the problem that makes it necessary. Then the warm-up/re-teach from step 3 of Inputs.
   - Per idea: intuition → numbers → formula (rule 4); reason first, name second via `::: worked` (rule 21); a worked example
     before any practice (rule 7); label sections "from the reading" or "beyond the reading" (rule 17); learner's vocabulary next
     to the book's (rule 19); give the sentence for anything commonly mis-said (rule 5).
   - Visuals only from the data plugins or `diagram.js` templates; no drawn or generated art. Look at them with `scripts/snap.mjs`.
   - Plain teacher's prose: no file paths, rule numbers, platform jargon, or the learner's words quoted back (rule 31).
5. **Questions: invoke the `write-questions` skill** for every objective (and the warm-up), giving it the objective, what this
   and earlier lessons taught, the reading span, and the book's exercise numbers. Place what it returns at the right spot in the
   body; variants beyond v1–v2 go in the lesson's `.variants.md` bank. Then run
   `python3 .claude/skills/write-questions/check_questions.py <lesson.md>` and fix every error. Do not write question rules here
   or improvise questions without it.
6. **Check every fact and number.** Compute anything checkable with code (sympy, Python, dates) using assertions that don't print
   answers (rule 22). Anything you're unsure of, or any paraphrase of the book: send the `researcher` agent, or reread the
   source sentence yourself (rules 10, 14). If a check changes the teaching, say so.
7. **Extra practice (optional)** heading, last before Sources (rule 32): (a) 2–5 book exercises easiest first, with where the
   answers are; (b) one extra reading from a secondary book; (c) one extra article: find a real one, open it, confirm it says what
   your one-line blurb claims, and confirm the link works (`curl -sSL -o /dev/null -w '%{http_code}\n' <url>` → 200, or open it with
   WebFetch if the site blocks curl). No later lesson may depend on any of it (rule 13).
8. **`## Sources`**: the book (edition, sections, pages, library id), every web source cited in the text, the article.
9. **Render:** `python3 scripts/render_lesson.py topics/<topic>/lessons/NNNN-x.md --course <ID>` (writes the HTML, updates
   `index.html`, appends the stem to `lessons`, drops the fulfilled `plan` entry). Never hand-edit the HTML.
10. **Lint:** `python3 scripts/lint_lessons.py topics/<topic>/lessons/NNNN-x.html`. Fix every ERROR; fix WARNs unless you can
    say why they're fine.
11. **Review:** run the `lesson-reviewer` agent on the `.md` + `.html` (give it the major, course and lesson path). Fix everything
    it ranks above "fit"; re-render and re-lint. Don't commit on "Fix first".
12. **Keep the map true:** check `curriculum.json` (`lessons`, `plan`); if the lesson changed the course's plan, update
    `SYLLABUS.md` (and its "Changes" log) and `syllabi/<COURSE>.md`, then `python3 scripts/render_syllabi.py`. Run
    `python3 scripts/test_programs.py` and `bash scripts/check_all.sh --quick` (drop `--quick` if widgets changed).
13. **Commit and push** (CLAUDE.md "Cloud-session rules" and "Several sessions"): `git pull origin main`, rerun
    `check_all.sh --quick` after the merge, commit `teach(<slug>): lesson NNNN <name>`, push to `main` (on an assigned branch: push
    it, merge into `main`, push `main`). Update `notes/HANDOFF.md` only for decisions or plans no script knows.
14. **Hand it over:** give the path and `<PAGES_URL>/topics/<topic>/lessons/NNNN-x.html`, the reading in one line, and the
    time estimate. Never state an answer to any question on the page.

## Major-specific add-ons (details in each major's PROGRAM.md)
| Major | Add |
|---|---|
| Engineering (`eng`) | Open with a one-minute Vim tip (keys shown, trying it optional; rule 30; replay sent keys with `scripts/vimcheck.py`). End with the **required rep** from `topics/eng/backlog.json`: re-check the ticket on GitHub first, give a definition of done and who does what. Don't write the next lesson in that lane until the last rep shipped or was skipped with a reason. Claude writes the code and the learner does the staff-level work, except where the code is the skill (C, C++, CUDA, Spark). |
| Statistics | One proof task per lesson (skeleton warm-up or "your proof" free response with a rubric), from the book's theorems or exercises. Two blocks: reading (~25 min) + lesson page (~25 min). |
| Reading majors (Critical Theory, and any major whose PROGRAM.md has reading days) | Check PROGRAM.md for whether today is a **reading day** (slice + guide only, no lesson page) or a **seminar** (a lesson page: recap boxes, the week's hardest idea, 3–5 recall questions, one graded free response). The article is the main extra; book problems usually don't apply (same for Indian History). |
| Games | Positions and boards from real games or engine-checked lines (`assets/plugins/`); lessons may live in a sub-topic folder (`chess`, `military-strategy`): use the course's `topic`. |
| Pretest lessons | `main: data-skip=true data-pretest=true`; nothing on the page feeds review (rule 28). |

## Don'ts
- Don't start writing before step 1's pull and number check.
- Don't print quiz answers in chat or in a commit message.
- Don't ask permission to push to `main` or ask the learner to merge.
- Don't use C/F-grade text as a source, or equations from a B-grade book.
