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

**How it compares to ours** (corrected 2026-10-07; the first version said our rules "already point this way", which overstated it):

| learn's idea | Our rule before today | Same? |
|---|---|---|
| Principle ii, motivated discovery of **every** step | Rule 21: reason through a **new definition** in revealed steps before naming it | Same idea, **narrower**: definitions only, not derivations, proofs or formula manipulations |
| Principle i, unconditional truths first | none | **Missing**. Rule 4 (concrete story → numbers → formula) is a different rule: it orders abstraction, not which facts anchor the lesson. It fits learn's loop as the *motivate* step |
| Probe until each strand is bracketed (one right, one miss) | Rule 8 (multiple choice ≠ known), confidence check, "I don't know" | **Missing**: we measure guessing, not where the edge is |
| Build options by mutating the right claim | Lint for equal word counts; rule 23 (labels mustn't name the answer) | **Partial**: we check the result, not the construction |
| Instant grading, "I don't know", note field | `lp.js` quizzes, `data-skip`, confidence step | **Same** |
| (none) | Rule 7: worked example before practice | **Ours only** |

In practice rule 21 has been applied in one lesson so far (Statistics 0006 is the only lesson Markdown with a `::: worked` block).
Note: learn has **no license file**, so legally it's
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

## What the point is (second pass, after "use this to understand what the point of this all is")

My first pass bolted learn's ideas on as an extra file and an extra rule. Read for its *purpose*, learn says something about our
rules themselves: **the goal is understanding, meaning each fact is connected to things you already accept, so it can be re-derived
instead of remembered.** It argues that a pile of lone facts doesn't stick while a few generating ideas do.

Our TEACHING-LOG was exactly such a pile: 25 rules, each a patch for one incident. Read through learn's lens, almost all of them
follow from four ideas, and your own complaints are all missing foundations or missing links:

| Idea | Our rules it explains | Your words that exposed it |
|---|---|---|
| A. Solid ground first (accepted as stated) | 1, 2, 9, 12, 15, 16, 17, 19, 24 | "you never describe what alpha is" (entry 1) |
| B. Every step motivated (discovered, not decreed) | 4, 7, 16, 21 | "I need to sit and reason through stuff" (entry 21) |
| C. Check each piece landed; measure knowing, not guessing | 3, 6, 8, 20, 23, 25 | "some of these answers were guesses" (entry 7) |
| D. One wrong fact poisons what's built on it | 5, 10, 14, 22 | the Ghaggar paraphrase (entry 14) |

**What changed because of it:**
- TEACHING-LOG now opens with "Why these rules exist": the purpose plus these four ideas. When no numbered rule covers a situation,
  the four ideas decide it.
- **Rule 21 widened.** It had turned your "reason through stuff" into "reason through *definitions*". Now it covers every new
  definition, formula, theorem and proof move, and each lesson opens with the problem that makes it necessary.
- Rule 4 (story → numbers → formula) isn't in conflict with "unconditional truths first": the story is the *motivate* step, and the
  truth comes right after it.
- **Left alone on purpose:** spaced review of plain facts (dates, names). Learn would say understood facts don't need drilling, but
  some facts in history are just facts. Linking them to a timeline or a cause is the learn-style improvement, case by case.

## Diagram templates (after "you can code diagram templates… then plug in the information")

`assets/plugins/diagram.js`: three templates drawn by code from facts you supply, with no hand-drawn or generated pictures:
a **graph** (dependency maps, flows, trees; layered layout with crossing reduction), a **sequence** diagram (who sends what to whom),
and a **Venn** diagram (2–3 sets, any shaded set expression such as `(A ∪ B)ᶜ ∩ C`). In Markdown lessons: `::: diagram` with
list lines. Learn's most important visual habit is adopted too: **look at the render before shipping.** `scripts/snap.mjs`
screenshots each diagram (light/dark, phone width) for checking, and every edge is verified like any other claim (the gallery's
axiom map follows the derivations as taught in Statistics lesson 0006). Tests: `scripts/test_diagram.js` (layout, De Morgan, distributive
law, every diagram in the repo).

## Does this work with other LLMs?

Mostly yes, by design (`notes/platform-portability.md`: essentials in scripts/APIs, `SKILL.md` as plain English, Claude-only
conveniences optional). Today's additions:
- **Model-free:** the diagram plugin, `snap.mjs`, the lint warning, the tests, everything in TEACHING-LOG, PRINCIPLES.md and
  the learning-record rules (plain text any model can follow).
- **Claude Code-specific, with a fallback:** `/quiz-me`'s picker (`AskUserQuestion`); the skill now says to use plain lettered options
  where a harness has no picker. The two agents in `.claude/agents/` use Claude Code's agent format; their bodies are plain prompts
  another harness can run as a sub-task, but the `tools:` line and the folder are Claude Code's.
- **Needs a vision-capable model:** the "look at the render" step (reading the PNGs).

## Sources
1. pi coding agent: https://github.com/badlogic/pi-mono (linked from [3]'s README).
2. Amos Blomqvist, *learn*: https://github.com/amosblomqvist/learn (README; `skills/teach/SKILL.md`; `extensions/quiz.ts`;
   `extensions/md-log.ts`; `agents/researcher.md`). Video: https://www.youtube.com/watch?v=kzcI5F4tGiU
3. HazAT, *pi-interactive-subagents* (MIT): https://github.com/hazat/pi-interactive-subagents (README; `agents/reviewer.md`, `agents/scout.md`).
4. Claude Code subagents docs: https://code.claude.com/docs/en/sub-agents
5. elpapi42, *pi-observational-memory* (MIT): https://github.com/elpapi42/pi-observational-memory (README;
   `src/agents/observer/prompts.ts`; `src/agents/reflector/prompts.ts`).
