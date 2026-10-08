---
name: write-questions
description: Write the practice and check questions for a lesson as question families (several variants per objective) in the lesson Markdown quiz syntax, with every numeric answer computed by code. Use for every lesson (the write-lesson skill calls it), or on its own to add variants to an existing lesson's .variants.md bank.
argument-hint: "<lesson .md path or 'objectives: ...'> [--bank to add variants only]"
---

# /write-questions

Arguments: `$ARGUMENTS`: a lesson `.md` (its objectives come from the major's `SYLLABUS.md` / the course syllabus), or a concept
plus its source passage. `--bank`: the lesson exists; only add variants to `topics/<t>/lessons/NNNN-name.variants.md`.

**Sources of truth** (this file only summarizes them; read them when unsure): `notes/practice-variants.md` (families, the five
variant kinds, the bank), TEACHING-LOG.md "Rules", `.claude/skills/teach/PRINCIPLES.md` "Writing choice options",
`assets/README.md` ("Writing lessons in Markdown", "Scored widgets", "Daily review deck", Math plugin), `library/README.md`
(what each book grade allows), `notes/evidence-spacing-and-variety.md` (why vary and interleave).

## Inputs to gather first
1. The objectives (2–3 "you can…" lines) and what this lesson and earlier ones actually taught (rule 2): the lesson draft, the
   topic's learning records, `QUESTIONS.md`. A question may only use what is on that list.
2. The course's books (`curriculum.json` → `books`) and their grades in `library/MANIFEST.csv`; find exercises with
   `python3 scripts/books.py grep <id> "<phrase>"` / `read <id> <line> <n>` (rule 22).
3. Ids already in use: `grep -o 'data-id="[^"]*"' topics/<t>/lessons/*.html topics/<t>/lessons/*.variants.md`. Ids are permanent.

## Book exercises are the default source (quantitative courses)
For math-heavy courses, make isomorphic variants and extra practice by **taking an exercise or example from the course's books
(assigned reading or not), citing it, changing the numbers, and recomputing the answer with code**. Write "Adapted from <Book>,
Exercise N.M, numbers changed" in the prompt or explain. What the book's grade allows (library/README.md):
- **A:** use it; re-derive or re-check every equation you carry over (the converted text garbles symbols).
- **B:** the problem's prose is usable, but no equation, figure or table may come from the converted text: derive any formula
  yourself (verify with code) or just give the exercise number for the learner to read in their copy.
- **C/F:** cite the exercise number only; the learner reads it in their own copy.

Choose new numbers so the answer is clean-ish but not guessable (not the book's answer, not 0.5, not a round input), and check
the changed problem still makes sense: probabilities in [0, 1], counts whole, lengths and variances positive, a test's
conditions still met. Non-quantitative courses: write variants from the reading (rule 14: check paraphrases against the page).

## Procedure, for each objective
1. **Name the family**: a short slug for the idea (`atleast`, `purusha-date`), new in this topic. Ids are `<family>-v<n>`.
2. **Write v1** for the lesson body, right after the section that teaches it (a worked example comes first, rule 7).
3. **Write 2–4 more variants** spanning the kinds in `notes/practice-variants.md`: isomorphic (new numbers, often a book
   exercise), format switch (choice ↔ typed, or find-error), reverse (give the answer, ask for the setup), transfer (a situation
   the lesson never showed), discriminate (the confusable near-miss; interleave confusable pairs on purpose, rule 29c).
4. **Pick quiz types** (rule 8): at least one variant per family is recall, not recognition: `number`, `math`, `exact`, `cloze`,
   `free`, `recall`/`card`, `estimate`, `timeline-place`, unlabelled `map-locate`. `choice`/`categorize`/`order`/`find-error`/
   `highlight` measure recognition. Sorting items have 3–4 rows (rule 3).
5. **Compute every numeric answer with code** (python/sympy/fractions) before writing it in; never in prose. Put the exact
   expression in `math` answers, a decimal plus a `tolerance` in `number`. Keep answers out of chat (rule 22): use asserts.
6. **Write the explain** (why the answer is right, shown once right) and a **hint** for choices (shown after a miss). For `free`, a `--- rubric` that grades
   only what the prompt asks for in words (rule 25) and only from what was assigned (rule 24).
7. **Place them:** v1 and usually v2 in the lesson (2–3 varied questions per concept, rule 29b); the rest in the bank, from which
   the next lesson's warm-up and the review deck draw (phase 2 of practice-variants.md).
8. **Self-check every item** against the checklist below, then run the checks.

## Checklist (each item, read cold)
- Taught here or earlier (2)? Every number and condition restated, no "our test" / "lesson 2's example", numbers derived (16)?
- Could a careful reader object to the wording (6)? Units and answer form stated: "as a decimal, 0.10 means 10%" (18)?
- Formula box: says how to type (`*`, `/`, `^`, `sqrt( )`) and that expressions are accepted (11)?
- Choice options: right claim first, distractors mutated from real misconceptions, same skeleton and word count, no "because"
  in any option, bold all parallel terms or none (PRINCIPLES.md, 26); can't be answered by reading the options alone (23)?
- Uses the learner's words next to the textbook's (19: false positive = Type I); comparisons say exactly how much overlaps (27)?
- Prose a teacher would say; no file paths, rule numbers or platform jargon in learner-facing text (31)?
- Gives the right sentence where people mis-say it (5); self-contained enough to come back alone in review (Daily review deck)?

## Output
Markdown quiz blocks (syntax in assets/README.md). Lesson items go in the lesson `.md`; the rest in the bank
`NNNN-name.variants.md`, which has no front matter, one `## <family>` heading per family, and the same blocks. Then:
- `python3 .claude/skills/write-questions/check_questions.py topics/<t>/lessons/NNNN-name.md` renders throwaway copies of the
  lesson and bank, runs `scripts/lint_lessons.py` on them (unequal option word counts, reasons only in the answer, bad keys),
  checks math answers parse, ids are unique across lesson + bank, families have 3+ members and a recall member. Fix every ERROR;
  fix WARNs unless you can say why not.
- After write-lesson renders the page, `python3 scripts/lint_lessons.py topics/<t>/lessons/NNNN-name.html` must also be clean.

## Never
- Reuse or rename a data-id (review schedules hang off them), or a family name another lesson in the topic uses.
- Test what wasn't taught, or grade a point the prompt didn't ask for.
- Let length, emphasis, a reason, or a label naming the target give the answer away.
- Write context-dependent prompts ("our test", "the example above") or put a needed diagram anywhere but right before the quiz.
- Make variants for a pretest page (`data-pretest`): pretests measure and never feed review (rule 28).
- Write a numeric answer you didn't compute, or copy an equation from a grade B/C/F conversion.

## Worked example (family `atleast`; answers computed with fractions; v1, v2 in the lesson, v3 in the bank)
```
::: number atleast-v1 answer=0.5705 tolerance=0.0005
*Adapted from Casella & Berger, Example 3.2.3, numbers changed.* A pair of fair dice is thrown 30 times, independently.
What is the probability of at least one double six? Answer as a decimal (0.10 means 10%); the box accepts expressions
such as `1-(35/36)^30` (`*` for ×, `/`, `^` for powers).
--- explain
"At least one" is the complement of "none": \(1 - (35/36)^{30} \approx 0.5705\), since each throw misses with probability 35/36.
:::

::: find-error atleast-v2
A student finds the probability of at least one six in 4 independent rolls of a fair die. Which step is wrong?
- Each roll shows a six with probability \(1/6\).
- [x] The four "six on roll \(i\)" events add, so the answer is \(4 \cdot 1/6 = 2/3\).
- "At least one six" is the complement of "no sixes".
- So the probability is \(1 - (5/6)^4 \approx 0.518\).
--- explain
Two rolls can both be sixes, so the events aren't disjoint and their probabilities don't add (Axiom 3 needs disjoint events).
With 7 rolls the same method would give \(7/6 > 1\).
:::

::: number atleast-v3 answer=0.0961 tolerance=0.0005
Five servers each fail on a given day with probability 0.02, independently of each other. What is the probability that at
least one fails that day? Answer as a decimal (0.10 means 10%).
--- explain
\(1 - 0.98^5 \approx 0.0961\): the complement of "none fail", and "none fail" is a product because the servers are independent.
:::
```
Kinds: v1 isomorphic (book example, new numbers, recall), v2 discriminate + format switch (add vs. complement), v3 transfer.
