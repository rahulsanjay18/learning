---
name: quiz-me
description: A few minutes of review questions in chat, drawn from what's due on the learner's spaced-review schedule (or a topic's lessons), with answers recorded on the progress server. Use when the learner asks to be quizzed, for a quick review, or has a few spare minutes.
argument-hint: "[topic] [number of questions]"
---

# /quiz-me

Arguments: `$ARGUMENTS` (optional topic slug, optional count; default 5).

1. `python3 scripts/quiz.py due -n <count> [--topic <t>]`. If nothing is due, use `python3 scripts/quiz.py pick --topic <t> -n <count>`
   (ask which topic if none was given, or pick the one studied most recently) and say it's early practice.
   The output has a `KEY:` (and sometimes `WHY:`) line per question: **never show those before the learner answers.**
2. Ask **one question at a time**. Keep the wording of the `Q:` line. Math in plain text or LaTeX.
   - **Choice questions use a picker UI if the harness has one** (Claude Code: `AskUserQuestion`, one question per call, header = topic; elsewhere: plain text, options lettered). Shuffle the options so
     the key isn't always in the same place. With ≤ 3 options, add a last option **"I don't know"** (description: "No guess:
     shows the answer"); with 4, the picker's built-in "Other" box takes "idk" or a note. Never put the key or `WHY:` in a label
     or description. (Pattern from the `quiz` popup in github.com/amosblomqvist/learn: a separate "I don't know" so a gap isn't
     confused with an unlucky guess, plus a free-text note.)
   - Everything else in plain text: for `estimate`, ask for a 90% range; for `find-error`, list the steps; for `highlight`,
     show the passage and ask which sentences support the claim.
3. Judge each answer against the key, generously on wording, strictly on substance. Reply in 1–3 lines: ✓ or ✗, the right
   answer, the key idea (from `WHY:`), nothing more. "I don't know" counts as wrong (no shame: that's what review is for);
   record its answer as `idk` so it's distinguishable from a wrong guess. If they typed a note, answer it briefly.
4. Record it right away: `python3 scripts/quiz.py record "<item>" right|wrong "<their answer, short>"`.
5. At the end: one line with the score, and the one idea most worth remembering. If something was missed that a lesson taught
   badly, add an entry to `TEACHING-LOG.md` as usual.

Cheap by design: no HTML, no lesson writing, no file reading beyond the script's output.
