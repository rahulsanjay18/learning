# How to explain: two principles, a probe, and quiz-option construction

Adapted 2026-10-07 from Amos Blomqvist's `teach` skill (github.com/amosblomqvist/learn, `skills/teach/SKILL.md`), rewritten
for this repo (HTML lessons, `assets/` widgets, TEACHING-LOG rules). TEACHING-LOG's "Why these rules exist" section is
the short form of this file; rule 21 (widened 2026-10-07) is principle 2. This file is *how* to explain; SKILL.md and CLAUDE.md say *what* to produce.

## Goal: connected facts, not a pile of them

Two learners can give the same answers today. One holds disconnected facts; the other holds a few core truths the facts
follow from. Only the second keeps them, because each fact is held in place by its links. Every move below builds that graph:
**nodes** (principle 1) and **edges** (principle 2). A learner hedges on a fact that something deeper might later contradict,
so it never fully sticks; both principles remove that risk.

## Principle 1: unconditional truths first

Start each lesson from the few facts the learner can accept **as stated, with no caveats** ("usually", "in most cases"
disqualify it; dig one level deeper). These stick at once because nothing will overturn them.

- Strongest forms: **universal statements** ("every X is Y", "no X is Y"; e.g. "every probability is a number assigned to an
  event") and **real definitions** (not a list of typical properties).
- Say "unconditional truth" by default; keep "axiom" for things that really derive from nothing (C&B's three axioms are both).
- Check each root reads as obviously true *to this learner* (a one-question quiz) before building on it.

## Principle 2: "how could I have discovered this?"

A fact that looks arbitrary doesn't stick. Show the path by which the learner could have found it: start from the problem
that sends us down this road ("why are we doing this at all?"), and motivate every step ("why try this formula?", "why
rearrange it this way?"). 3Blue1Brown is the model. In this repo the tool is `::: worked` (revealed steps, rule 21).

- **Socratic** (the learner attempts the step before the reveal) by default when they can plausibly reason it out; if the step
  has a right answer it is a graded quiz, not an open question.
- **Expository** (you narrate the discovery) when it is out of cold-reasoning reach or the learner is tired.

## Probe: find the edge, bracketed on both sides

Pretests and warm-ups are for finding where knowledge runs out, per strand the lesson depends on.

- The edge is found only when it is **bracketed**: something at that level they get right (floor) *and* something they miss
  (ceiling). All-correct means the questions were too easy; escalate sharply. One miss is one data point; probe around it to tell
  a slip from a gap from a misconception (misconceptions need dislodging, not topping up).
- Only probe the strands the next lessons will lean on.

## Plan: show the dependency map

When a lesson or course introduces more than two or three linked ideas, draw its backbone as a small DAG: unconditional truths
as roots, the objective as the sink. Keep it to a few nodes. Before using it, check every root: is it really accepted at face
value, or is it a theorem in disguise? A wrong root corrupts everything built on it. Every node then gets the same loop:
**motivate → establish → connect (say which earlier node it hangs off) → quiz-check**.

## Writing choice options (applies to every `choice` quiz)

Auditing options after writing them isn't enough, because the answer has already stood out by then. Build them so they can't stand out:

1. **Every option is a bare claim, with no justification.** The classic giveaway is the right answer carrying its own "because …".
   All reasoning goes in the explanation (`.explain`).
2. **Write the right claim first, then mutate it into each distractor**: take a specific misconception and state what
   someone holding it would claim, in the same skeleton, length and register.
3. Each distractor is a mistake this learner could really make (so the pick is diagnostic), and unambiguously wrong.
4. **No asymmetric emphasis**: bold the parallel term in every option or in none.

If, reading the set cold, you can tell the answer without knowing the material, regenerate it; don't patch it.
`scripts/lint_lessons.py` warns on unequal word counts and on a justification word that appears only in the answer.

## Visuals: one idea, fewest elements, look before shipping

Draw a diagram only when it shows something words can't: a dependency map, a flow, who-sends-what-when, set regions, geometry.
Use the code templates in `assets/plugins/diagram.js` (graph, sequence, venn; markup in `assets/README.md`) or the plot,
timeline and map plugins; never draw or generate pictures by hand. Before briefing yourself, cut to the fewest elements that
carry the idea (about 7 nodes; ask of each "if I delete this, is the idea still clear?"). Every edge is a claim: verify it like any
other fact. Then **look at it**: `node scripts/snap.mjs <page> [selector] [--dark] [--width 380]` writes PNGs; open them, check
every arrow and label is true and readable in both themes and at phone width, and fix before committing.
(From amosblomqvist/learn's `visualize` skill and its maker agents' render-and-inspect loop.)

## Verify before you say it

Any fact, name, date or formula you are even slightly unsure of: check it before it goes in a lesson (TEACHING-LOG rule 10).
Library first (`scripts/books.py`), then the web; the `researcher` agent (`.claude/agents/researcher.md`) does this in a
separate context. If a check changes what you were going to teach, say so plainly.
