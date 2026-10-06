# Using `/program`: "what do I do today?"

Short answer: **yes, it already does this.** Type `/program` at the start of a session.

## The three ways to call it

| You type | What happens | Writes anything? |
|---|---|---|
| `/program status` | Prints where every major stands and today's plan, then **stops**. | No |
| `/program` | Today's plan, then acts on it: grades pending free responses, hands you the link to any lesson you haven't done, and writes the next lesson only for majors where you finished the last one. Ends with a short list: review → block 1 → block 2. | Yes (lessons, commits) |
| `/program <major>` | Same as `/program`, for one major only (e.g. `/program statistics`). | Yes |

Source: `.claude/skills/program/SKILL.md`, section "What to do" and the `argument-hint` line.

**If you just want the to-do list, use `/program status`.** Plain `/program` also prepares lessons, which takes longer.

## How it decides "today"

1. Before the skill even loads, it runs `.claude/skills/program/scripts/status.py`, which reads:
   - `programs.json`: which majors get today's blocks (the weekly timetable),
   - each `topics/<major>/curriculum.json`: active course, lessons written, lessons completed, next planned lesson,
   - the progress server (`$BOOKS_URL/progress/status`): your recent quiz results, reviews due, ungraded answers.
2. Per major, the rule is (SKILL.md step 2):
   - latest lesson **not done** → you get its link; no new lesson is written;
   - latest lesson **done** → the next lesson in `plan` is written;
   - plan empty → a course check, then the next course.
3. Order of the day is always **daily review first** (`assets/review.html`), then the two subject blocks.
   You finish the whole day's plan before going deeper on one subject (CLAUDE.md, "About me as a learner").

## Example: what it said on 2026-10-06 (Tue)

```
Today: review (assets/review.html) -> Statistics -> Indian History
Statistics  S150: latest 0004-power NOT DONE YET (your next step)
Indian History IH100: latest 0002 DONE -> next to write: 0003 Introduction + Indus
AWS ML cert: SETUP NEEDED (its blocks go to Statistics until set up)
5 ungraded free responses
```

## Sources
- `.claude/skills/program/SKILL.md` (the skill's instructions)
- `.claude/skills/program/scripts/status.py` (the status digest, output above)
- `CLAUDE.md`, sections "Program layer (/program)" and "About me as a learner"

## What about days I missed? (makeup)

Partly handled, partly not. Checked against `status.py` (it picks today's majors only from `programs.json` → `week[<weekday>]`;
there is no "missed" or "last studied" logic in it).

| Missed thing | Caught up automatically? | Why |
|---|---|---|
| A lesson you didn't finish | **Yes** | Progress is tracked per lesson, not per date. An unfinished lesson stays "NOT DONE YET" and is your next step the next time that major comes up. Nothing is skipped. |
| Daily review | **Yes** | `assets/review.html` re-asks questions when they're due; skipped days just mean more are due next time. |
| A whole day's subject block | **No** | The timetable is fixed by weekday. Miss Saturday (Indian History + Games) and Sunday won't add them back; they wait until their next weekday slot. |

Workaround today: ask for it by name, e.g. `/program indian-history`. Sunday is empty in the timetable, so it's a natural makeup day.
Possible fix (not built yet): have `status.py` compare each major's last activity date with its scheduled days and print
"behind: <major>, missed <day>", suggesting makeup on Sunday or after the day's plan.
