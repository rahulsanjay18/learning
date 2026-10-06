# How to use this learning platform

*Written 2026-10-06. Short version: start every learning session with `/program`.*

## Commands (type them in a Claude Code session on this repo)
| You type | What happens | When |
|---|---|---|
| `/program` | Shows today's plan (review first, then the day's two blocks), grades any answers waiting on the progress server, then either gives you the link to the lesson you haven't done yet or writes the next one | **Start of every learning session** |
| `/program statistics` | Same, for one major only (`indian-history`, `games`, …) | Extra time on one subject, *after* the day's plan |
| `/program status` | Just "where am I", no teaching | Checking in |
| `/program setup aws-ml` | Designs a major: plan, levels, courses, books needed (see `notes/major-design.md`) | A major that isn't set up, or a new subject you want as a major |
| `/teach <topic>` | Teaches one topic outside the majors (same lesson style) | One-offs, or trying a subject before deciding it's a major |

You don't need `/teach` for your majors: `/program` uses the same teaching rules.

## During and after a lesson
- Lessons open in your browser (links are given at the end of each session; all lessons are listed on the
  [index](https://rahulsanjay18.github.io/learning/)). The [Today page](https://rahulsanjay18.github.io/learning/assets/today.html)
  shows the day's plan; the [review deck](https://rahulsanjay18.github.io/learning/assets/review.html) is the daily 10 minutes.
- Results reach Claude automatically on a paired browser (desktop and laptop are paired). Otherwise press **Copy my results**
  in the lesson footer and paste the `lp-results …` line into the next session.
- Questions mid-lesson: just ask in chat. They're saved to that topic's `QUESTIONS.md`.

## Levels
Every major has Level I (≈ undergraduate) and Level II (≈ graduate). You're enrolled in Level I only; Level II is a separate
choice later. Courses start with a pretest, so anything you already know (e.g. from the math degree) is credited without lessons.

## /program vs /teach, in one line
`/program` decides *what* to learn today across your majors and then teaches it using `/teach`'s rules; `/teach` teaches one
topic and knows nothing about schedules or majors. For majors, only ever type `/program`. A `/teach` topic that grows can become a
major with `/program setup <topic>`.

## Skills that could be added (proposed 2026-10-06; not built yet)
| Skill | What it would do | Why |
|---|---|---|
| `/game-review` | Paste a game (chess now; xiangqi/shogi/Go later) → engine analysis (`topics/chess/scripts/analyze_game.py`), written review, course plan updated | Done by hand twice already |
| `/new-books` | After adding books: update `library/MANIFEST.csv`, grade them, say what to rerun on the server, tick off "books needed" lists | Packages `scripts/build_library.py` + `grade_library.py` |
| `/quiz-me` | 5 minutes of due review questions in chat, results posted to the progress server | Phone-friendly, far cheaper than a lesson |
| `/week` | Weekly digest from the progress server, what slipped, a small schedule adjustment | Keeps the 1-hour floor realistic |
| SessionStart hook (not a skill) | Installs test dependencies at session start | Saves setup each session |

A skill is just `.claude/skills/<name>/SKILL.md` (instructions, optionally scripts). Easiest way to make your own: describe it,
Claude drafts it, you edit the wording.
