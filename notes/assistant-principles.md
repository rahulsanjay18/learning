# Claude as a personal assistant: correctness first, tokens second (2026-10-07)

*From a brainstorm with the learner: "ways for you to be my personal assistant (for teaching but also kinda everything else) while
prioritizing correctness and saving tokens." Principles first, then what already exists, then the few next steps worth doing.
New ideas from future brainstorms go to `notes/ideas.md` (focus keeper), not here.*

## TL;DR: five principles
1. **Exact things go to tools, judgment goes to the model.** Anything with a checkable answer (arithmetic, schedules, legal moves,
   keystrokes, coverage, due dates) is computed by code. The model writes the code or the model once, and explains and decides.
2. **State lives in files and services, not in a conversation.** A new session reads a short digest instead of re-deriving the world.
3. **Everything the model produces that *can* be verified, is.** Tests, replays, solvers, engines, sympy, citations. A claim with no
   check gets labeled as judgment.
4. **Cheap work goes to cheap workers.** Small or local models do first passes, with escalation to a large model when unsure
   (`notes/slm-offload-plan.md`).
5. **Narrow interfaces, compact output.** Tools return a few lines of plain text (like `books.py`), not whole pages, so each call
   costs little context.

## What already follows these (built 2026-10-05 → 07)
| Principle | Already in place |
|---|---|
| 1 Exact → tools | `status.py` (the day's plan), `catalog.py` (what's stale), `vimcheck.py` (keystroke replay), `lp_results.py`, the chess/Go engines in widgets, sympy checks for equations, OR-Tools tested |
| 2 State in files | `programs.json`, curricula, `todo.json`, `backlog.json`, `catalog.json`, `HANDOFF.md`, the progress server |
| 3 Verify | `check_all.sh` (about 15 test suites), `test_programs.py`, perft tests in your engine, citations required in lessons, `notes/evidence-spacing-and-variety.md` as the bar for arguments |
| 4 Cheap workers | the lesson-reviewer and researcher agents; the SLM offload plan (not built) |
| 5 Narrow interfaces | `books.py`, the progress server's digest endpoints, `status.py`'s ~20-line block |

## Next steps worth doing (my judgment, ranked; nothing here is scheduled)
1. **A verified-facts cache.** Every fact that was checked against a source once (exam codes, pay figures, book editions, dates)
   gets stored with its source and check date, so no session re-searches it. `catalog.json` already does this for careers;
   generalizing it is cheap. *Saves tokens and keeps answers consistent.*
2. **The `/plan` solver** (OR-Tools, `notes/ideas.md`): once the week has real constraints.
3. **The SLM offload plan**, first for grading free responses: a small model does the first pass, and anything uncertain escalates
   (the plan's own ≥90%-agreement gate before trusting it).
4. **Beyond learning ("everything else")**, using what Claude already supports rather than building it:
   - **Connectors** (calendar, email, docs) for reading your real schedule; then the week planner can see your actual free time.
   - **Routines** (scheduled sessions) for things like a weekly review or a morning brief, no session needed from you.
   - Both need your setup in claude.ai and come with a privacy decision: what an assistant may read, and what it may do without asking.

## Where this stops helping
- Tools are only as right as their model of the problem: a solver optimizes the constraints it's given, so the constraints need review.
- Every service is something to run and secure. Build one only when a script in a session can't do the job (the browser case is
  the usual reason).
