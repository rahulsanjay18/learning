# What we took from three pi repos (2026-10-07)

You asked me to look at three repos for platform ideas ("or copy wholesale"). All three are built for **pi**, a different
coding-agent harness [1], so their TypeScript extensions don't run here. I adopted the ideas and prompts, not the code.
Clones were read at: learn `7cfd894` (2026-08-26), pi-interactive-subagents `c100577` (2026-05-13), pi-observational-memory `022da5e` (2026-10-05).

## 1. amosblomqvist/learn: the teaching philosophy and the quiz UI [2]

**What it is.** A pi config from the video "How I Use AI to Learn Things" [2]: a `teach` skill, a `visualize` skill, three
subagents (researcher, svg-maker, mermaid-maker) and TUI extensions (`quiz`, `ask-user-question`, `md-log`).

**The core idea** (its `skills/teach/SKILL.md`): understanding = a dependency graph of facts, not a pile of them.
- *Principle i, unconditional truths first*: start from facts accepted with no caveats (universal statements, real
  definitions), because the brain hedges on facts that something deeper might overturn.
- *Principle ii, "how could I have discovered this?"*: motivate every step (the 3Blue1Brown model).
- *Probe → plan → teach*: probe until each strand's edge is **bracketed** (a floor they get right and a ceiling they miss;
  all-correct means "too easy", not "done"); plan as a small DAG with the goal as sink; teach node by node:
  motivate → establish → connect → quiz-check.
- *Quiz-option construction*: write the right claim first, mutate it into distractors, no justification inside any option,
  no asymmetric bolding.

**The UI** (you mentioned it): `quiz.ts` is a terminal popup that grades instantly (✓/✗ + right answer + explanation), always offers a
separate **"I don't know"** (so a gap isn't recorded as an unlucky guess) and a free-text note field. `md-log.ts` mirrors the session
(prose + Q&A, never answer keys before answering) into a Markdown file rendered live in Obsidian.

**How it compares to ours.** Our TEACHING-LOG rules 4, 7 and 21 already point this way, and our HTML lessons already do instant
grading, "I don't know" (`data-skip`) and confidence checks. What we lacked: the *bracketing* rule for probes, the *mutation*
procedure for options, and an explicit "unconditional truth" vocabulary. Note: learn has **no license file**, so legally it's
"all rights reserved"; I paraphrased and credited it instead of copying text verbatim.

**Adopted:**
- `.claude/skills/teach/PRINCIPLES.md`: the principles, probe, DAG plan, and option procedure, rewritten for our widgets.
- TEACHING-LOG rule 26 points to it.
- `scripts/lint_lessons.py` now warns when only the right answer carries a reason ("because…").
- `/quiz-me` now asks choice questions through the **AskUserQuestion picker**, Claude Code's closest equivalent of that popup,
  with shuffled options, an "I don't know" option, and "Other" as the note box; it replies ✓/✗ + answer + key idea.
- `.claude/agents/researcher.md`: fact-check agent (library first, then web; verdict per claim).

**Not adopted:** md-log (lessons are already rendered HTML on Pages; a session transcript file is possible later if you want one);
svg/mermaid makers (CLAUDE.md: no generated art; data-driven plots already exist as widgets).

## 2. HazAT/pi-interactive-subagents: async subagents in terminal panes [3]

**What it is.** A pi extension where `subagent()` returns immediately, the child runs in a tmux/cmux/zellij/WezTerm pane, a
widget shows each one's state (`starting / active / waiting / stalled`), and the result is "steered back" into the main session
when it finishes. Children can `caller_ping` the parent for help and be resumed. Bundled roles: planner, scout, worker, reviewer,
visual-tester; a `/plan` command runs investigate → plan → execute → review [3].

**How it compares.** Claude Code already has background subagents (the Agent tool with `run_in_background`, custom agents in
`.claude/agents/`) [4], so the mechanics come free. The useful idea is the **roles**, especially an independent reviewer with fresh
context.

**Adopted:** `.claude/agents/lesson-reviewer.md`: read-only review of a lesson draft against TEACHING-LOG rules, PRINCIPLES.md and the syllabus,
returning ranked fixes and "Ship / Fix first". Plus the researcher above. (MIT-licensed.)

## 3. elpapi42/pi-observational-memory: memory that survives compaction [5]

**What it is.** Instead of summarizing a long session at compaction time (summaries of summaries lose rationale), background
agents continuously write **observations** (timestamped, rated, one fact per line, each citing source entry ids) and distill
**reflections** (durable facts that pass a "would a future agent need this to avoid a wrong decision?" test). A `recall` tool
fetches the source behind an id [5].

**How it compares.** Our memory is already the same two layers in files: learning records and QUESTIONS.md (≈ observations),
CLAUDE.md "About me", NOTES.md and HANDOFF (≈ reflections), and the progress server for scores. The observer/reflector *writing
rules* were the useful part.

**Adopted** (into `.claude/skills/teach/LEARNING-RECORD-FORMAT.md`, MIT-licensed source): assertions vs questions (what you *state*
about yourself is authoritative), quote your own terms, frame changes as supersession, mark completions, one fact per line, cite
evidence by `data-id`, and the durable-value test before writing a record.

**Not adopted:** the background observer/reflector agents themselves. Cloud sessions here are short and file-backed, so there's
little compaction to protect against; revisit if sessions start running long.

## Sources
1. pi coding agent: https://github.com/badlogic/pi-mono (linked from [3]'s README).
2. Amos Blomqvist, *learn*: https://github.com/amosblomqvist/learn (README; `skills/teach/SKILL.md`; `extensions/quiz.ts`;
   `extensions/md-log.ts`; `agents/researcher.md`). Video: https://www.youtube.com/watch?v=kzcI5F4tGiU
3. HazAT, *pi-interactive-subagents* (MIT): https://github.com/hazat/pi-interactive-subagents (README; `agents/reviewer.md`, `agents/scout.md`).
4. Claude Code subagents docs: https://code.claude.com/docs/en/sub-agents
5. elpapi42, *pi-observational-memory* (MIT): https://github.com/elpapi42/pi-observational-memory (README;
   `src/agents/observer/prompts.ts`; `src/agents/reflector/prompts.ts`).
