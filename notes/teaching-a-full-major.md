# Can /teach take me through a whole college major?

*Written 2026-10-05. Answers: can it be done, how to keep the context window from becoming a problem, and what tools or skills would help.*

## TL;DR

- **Yes, it can be done.** But a major is about 15–25 required courses, which works out to roughly 1,000+ short lessons and years of work. That's too big for one chat. It works only because the teaching state lives in **files in this repo** and not in my context.
- **Core context rule:** each session loads only the *map* (a small summary of where you are) and the *current lesson's* materials. Heavy reading goes to subagents that send back summaries.
- **What's missing today:** a **program layer** above /teach. That means a course prerequisite graph, a "what's next" script, a cross-course review queue, rolled-up mastery summaries, and a few custom subagents.

---

## 1. Why the current skill doesn't scale to a major as-is

The /teach skill is built around **one topic = one mission = one workspace** [1, lines 12–20]. Its format rules say so directly: "One mission per workspace. If the user wants to learn two unrelated things, that is two workspaces." [2]

A major breaks that in three ways:

| Problem | Where it shows up in the skill |
|---|---|
| Many missions with prerequisite links between them (Calc → Diff Eq → Signals) | No concept of order *between* workspaces [1] |
| Learning records grow without limit, but the zone of proximal development is supposed to be calculated from them | `learning-records/` is read to compute the ZPD [1, line 17; lines 85–89] |
| Spacing and interleaving *across* courses | The skill asks for both [1, lines 41–45] but only inside one topic |

Your repo already shows the pattern: `topics/chess`, `topics/nasm-cpt` and so on are independent folders [3].

## 2. Proposed design: a program layer on top of /teach

Each **course** becomes an ordinary /teach topic folder, so the existing skill works unchanged. A thin **program** layer sits above the courses and decides which one is active.

```
programs/<major>/
  PROGRAM.md          # mission for the whole degree + which reference curriculum we follow
  curriculum.yaml     # course DAG: id, title, prereqs, status (todo|active|tested-out|done), primary text
  MASTERY.md          # 1 screen max: rolled-up "what you can do" per finished course
  review-queue.csv    # concept, course, last_seen, interval, due  (spaced repetition across courses)
topics/<major>-<course>/   # a normal /teach workspace (MISSION, RESOURCES, lessons, learning-records…)
  SUMMARY.md          # NEW: rolled-up learning records for this course, rewritten at each unit end
```

**Where the course list comes from.** It comes from a public, high-trust source and not from my memory. The skill says "Never trust your parametric knowledge" [1, line 30]. Candidates are a specific university's published degree requirements, MIT OpenCourseWare course materials [6], or a professional-body curriculum such as ACM/IEEE CS2023 for computer science [7]. Strip out gen-eds as you suggested and keep the required major courses plus their math/science prerequisites.

**Placement ("credit by exam").** Given your math, CompE and CS degrees, many courses should be *tested out of*, not taught. Each course would start with a short diagnostic. A pass is recorded as a prior-knowledge learning record, which the format already supports (rule 2: "The user disclosed prior knowledge… also record the *depth*") [2]. The course is then marked `tested-out` in the DAG.

## 3. Keeping the context window under control

The principle: **load the map, not the territory.** Concretely:

1. **One lesson per session.** Cloud sessions start from a fresh clone and only see what's committed [3], so git *is* the memory. Starting fresh each lesson is fine, and the short format suits ADHD well. Auto-summarizing a long chat is a safety net, not the plan.
2. **A fixed, small boot read.** At session start, read only `PROGRAM.md` → `curriculum.yaml` status → the current course's `MISSION.md` + `SUMMARY.md` + the last ~3 learning records + `NOTES.md`. That should stay under a few thousand tokens however far into the degree you are.
3. **Roll-ups (compaction on disk).** At the end of each unit, fold that unit's learning records into the course's `SUMMARY.md`. At the end of each course, fold `SUMMARY.md` into a few lines of `MASTERY.md`. The old records stay in git as history, the way the format's "supersession" rule keeps history [2].
4. **Subagents do the heavy reading.** Each subagent runs in its own context window and returns only a summary. The docs describe this case: "Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again" [4]. Searching books, building lessons and grading all fit.
5. **Never read whole books.** Your library contract already requires `grep -n -i` plus nearby lines only, and it restricts what each A/B/C/F grade allows [5]. That rule matters more at degree scale.
6. **Scripts calculate, the model judges.** "What's next?" (prerequisites met + review items due) should come from a script printing about 10 lines. I shouldn't work it out by reading 40 folders.

## 4. Tools and skills that would help

### Already available here
| Tool | Use |
|---|---|
| **Subagents** (Agent tool; custom ones as `.claude/agents/*.md`) [4] | Research, lesson building, exam writing/grading in isolated context |
| **Book server + `library/`** [5] | Primary texts. The library has e.g. 204 Engineering, 128 Math/Logic and 74 OpenStax entries in `MANIFEST.csv` |
| **Python / sympy** | Check every equation before it reaches a lesson (library rule 4) [5] |
| **`session-start-hook` skill** | Print "you are here: course X, lesson N, 7 reviews due" automatically at session start |
| **Routines / `send_later`** | Scheduled spaced-review sessions (e.g. a daily 10-minute review) |
| **Artifacts with a database** | Possible fix for the biggest gap (below): quiz results I can actually read back |

### Worth building
1. **A `/program` (or `/major`) skill.** It builds `curriculum.yaml` from an official source, creates the course folders, runs placement diagnostics and picks the next course. It then hands off to `/teach` for the lesson itself.
2. **Custom subagents** in `.claude/agents/`:
   - `researcher`: library-first resource search following `library/README.md`, writes `RESOURCES.md`
   - `lesson-builder`: writes one lesson from a brief, reuses `assets/`
   - `examiner`: writes quizzes and unit/course exams, and grades free-response answers against a rubric
3. **Scripts:** `next.py` (DAG + due reviews → next action), `schedule.py` (spaced-repetition intervals for `review-queue.csv`), and a generated `index.html`. Hand-editing the index won't scale to 1,000 lessons; today `CLAUDE.md` asks for it to be kept updated by hand [3].

### The biggest real gap: feedback
Lessons on GitHub Pages are static, so **I never see your quiz results** unless you paste them. The skill wants a tight feedback loop [1, line 108], and mastery tracking across a degree depends on it. Options are: (a) you paste a score line at the start of each session, (b) quizzes write to a shared artifact database I can read, or (c) a tiny endpoint on your existing server. (a) works today; (b) is the cleanest.

## 5. Honest limits
- **Labs and hands-on work** (circuits, wet labs, studio) can't be fully replaced. They can be partly substituted with simulators or home kits.
- **Grading proofs and long-form work** by an LLM is useful but fallible. For high-stakes checkpoints, cross-check against textbook solutions or a community.
- **Wisdom / peers.** The skill hands this off to communities [1, lines 112–120]. At degree scale that means study groups, forums, office-hours-style communities.
- **No credential.** You'd get the knowledge, not the degree.
- **Time.** Even with placement, a full major is likely a year or more of steady short sessions.

---

## Sources
1. `.claude/skills/teach/SKILL.md` (this repo). Workspace layout (L12–20), "never trust parametric knowledge" (L30), spacing/interleaving (L41–45), ZPD (L85–89), feedback loop (L108), communities (L112–120).
2. `.claude/skills/teach/MISSION-FORMAT.md` and `LEARNING-RECORD-FORMAT.md` (this repo). "One mission per workspace", prior-knowledge records, supersession.
3. `CLAUDE.md` (this repo root). Topic layout, fresh-clone cloud sessions, index.html upkeep.
4. Claude Code docs, *Subagents*: https://code.claude.com/docs/en/sub-agents (separate context windows; `.claude/agents/` definitions).
5. `library/README.md` and `library/MANIFEST.csv` (this repo). Grade rules, grep-only reading, equation checking.
6. MIT OpenCourseWare: https://ocw.mit.edu (free course materials organized by department).
7. ACM/IEEE-CS/AAAI *Computer Science Curricula 2023*: https://csed.acm.org/
8. Learning-science background for the spacing/retrieval design: Roediger & Karpicke (2006), "Test-Enhanced Learning," *Psychological Science* 17(3); Cepeda et al. (2006), "Distributed practice in verbal recall tasks," *Psychological Bulletin* 132(3).
