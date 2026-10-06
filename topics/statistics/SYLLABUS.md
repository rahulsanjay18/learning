# Statistics syllabus

Planned ahead (2026-10-06). Course-level map: `PROGRAM.md` §1 (all of Casella & Berger). This file is the **lesson-level** plan for
the active course and the next one. Objectives are graded **Got it / Not yet** (mastery rule: `TEACHING-LOG.md` rule 20). A "Not yet"
adds a short re-teach section to the next lesson; bigger changes go in "Changes" below.

Books: Casella & Berger, *Statistical Inference*, 2nd ed. (C&B, id f9dc4d1d4c) · Bruce, Bruce & Gedeck, *Practical Statistics for
Data Scientists* (id a5650effae). Pace: Statistics is a full major (about 4–5 blocks a week).

## S150 Inference for practitioners (closed early 2026-10-06; leftovers move to S303)

| # | Lesson | Reading | Objectives: you can… |
|---|---|---|---|
| 0002 | What a p-value is | — | done |
| 0003 | Effect size and confidence intervals | C&B §9.1 | done |
| 0004 | Power | C&B §8.3.1 pp. 382–385 | (built; not done yet) compute power for a one-sided z-test · say how n, effect size and α move power · say "false negative rate = 1 − power" |
| 0005 | Likelihood ratios: P(data given H1) | C&B §8.2.1, Definition 8.2.1 and Example 8.2.2 | compute a likelihood ratio for two simple hypotheses · explain why a small p-value isn't P(H0 given data), with the A/B example (power ≈ 55%) · state the Neyman–Pearson idea in one sentence |
| 0006 | Multiple testing | Bruce, Bruce & Gedeck, Ch. 3 "Multiple Testing" | compute P(at least one false positive) for k tests · apply Bonferroni · spot multiplicity in a real analysis (many metrics, peeking) |
| 0007 | S150 check: an A/B test end to end | — | design (n from power), run, read p and CI, and write the conclusion sentence without the common wrong phrasings |

## S201 Probability theory, C&B Ch. 1 (active): 6 lessons at most

After the pretest there is **always one summary lesson** (learner's request, 2026-10-06); the pretest decides which of the other lessons run (numbered when written): anything you show you know is skipped (your placement said probability mechanics are solid).

| # | Lesson | Reading (C&B) | Objectives: you can… |
|---|---|---|---|
| 0005 | Ch. 1 pretest (concept, calculation and proof per section) | — | — |
| 0006 | **Chapter 1 summary (always)** | §1.1–1.6, skim | state the chapter's main results from memory and say what each is for |
| — | Sets and the axioms | §1.1, §1.2.1 | prove a probability fact from the Kolmogorov axioms alone (e.g. P(Aᶜ) = 1 − P(A), Bonferroni's inequality) |
| — | Calculus of probabilities and counting | §1.2.2–1.2.4 | count with/without replacement and order (the 4-way table) · prove inclusion–exclusion for two sets |
| — | Conditional probability and independence | §1.3 | derive Bayes' rule and use it on a base-rate problem · tell pairwise from mutual independence |
| — | Random variables, cdfs, densities | §1.4–1.6 | state the three properties of a cdf · move between pmf/pdf and cdf |
| last | Ch. 1 check | — | recall plus one proof, across the whole chapter including skipped sections |

## Known "Not yet" items (carried)
- **Confounding remedy** (pretest free response, 2026-10-06 grading): named the confounder but proposed an observational fix. Re-teach
  as a 5-minute section in S303 (Ch. 8) ("why randomization removes confounding"); full treatment in the causal-inference elective.

## Changes
- 2026-10-06: syllabus written; S150 = 0002–0007 (check added as 0007).
- 2026-10-06: **switched to Chapter 1 now** (learner: "thrust into the middle of something"; Ch. 1 "builds stuff from the ground up").
  S150 closed after 0004; its unwritten lessons (likelihood ratios, multiple testing, A/B check) move to S303. S110 merged into the
  S201 pretest. S201 lessons renumbered 0005–0010. Lessons follow TEACHING-LOG rule 21 (reason first, name second).
