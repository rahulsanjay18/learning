# Notes: Statistics

- Learner: B.S. Mathematics + B.S. Computer Engineering (Penn State), M.S. CS (Georgia Tech), 5 years working in AI. Speak at that level.
- ADHD (inattentive): keep lessons short, one win per lesson, clear structure.
- Wants sources cited in text and at the end; wants explanations also saved as Markdown.
- Time: at least 1 hour a day across all topics (see CLAUDE.md). Statistics is a "career" topic.
- 2026-10-05: placement pretest (lesson 0001) built. Results arrive as an `lp-results` line (progress server not deployed yet).
  Map item ids to areas: prob-*, rv-*, dist-*, clt-*, est-*, ht-*, reg-*, bayes-*, ml-*, design-*.
- Library: Casella & Berger (id f9dc4d1d4c) is grade A, but its front matter and /toc are garbage (logged in library/QUALITY-NOTES.md).
  Find sections with /search, not /toc. Don't cite chapter numbers from memory.
- 2026-10-05: pretest results: 10/21 right first try, 6 missed, 4 skipped; rated it **too hard**. See learning-records 0001–0004.
  Starting point: probability mechanics solid; inference interpretation is the gap. Lessons should be short and narrow.
- Graded reg-causal 0.6/1: named the confounder (summer), but the proposed study is still observational; said "prove".
- 2026-10-05: **Casella & Berger is the primary source** (grade A; learner's choice). All of Statistics is the companion (grade B: prose and section pointers only, no equations from it). Casella is dense: point to specific sections, never whole chapters.
- Learner says most pretest misses were forgotten facts, not confusion. Prefer the formula sheet + spaced retrieval for recall gaps; keep lessons for ideas.
- 2026-10-05: **teaching rule after feedback:** lesson 2 used α and power without defining them, and the learner couldn't follow.
  Before using a term, check the learning records: if it was missed or skipped on the pretest, **define it in the lesson first**.
  Prefer a worked example followed by a similar practice item over a cold question.
- 2026-10-05: learner found lesson 2's six-statement sort "hard": it tested effect size/sample size before teaching it, and was
  all-or-nothing. Fixed: taught first, split into two 3-item sorts. **Rule: keep categorize/order items to 3–4 rows, and never
  test an idea the lesson hasn't taught.**
- 2026-10-05: **lesson 3 = "Effect size and confidence intervals"** (learner: effect size is "missing entirely"). Order: what effect
  size is (absolute, relative, in SE units), practical vs. statistical significance, CIs as size + uncertainty. The learner's
  P(data | H1) / likelihood-ratio question comes after (lesson 4).
- 2026-10-05: lesson 3 (effect size and CIs) built, with reading Casella & Berger §9.1 pp. 417–419 (+ Practical Statistics "Confidence
  Intervals" from p. 65). Reading-guide answers arrive as free responses (read-gain, read-coverage, read-random, read-surprise): reply to them.
  Next: lesson 4 = the learner's P(data | H1) question (likelihood ratios, power ~55%), see QUESTIONS.md for the numbers.
- 2026-10-05: **learner wants all of Casella & Berger, cover to cover, doing proofs themselves.** Order: finish S150 (lesson 4 power +
  likelihood ratios, lesson 5 multiple testing), then Ch. 1 onward. Plan in `PROGRAM.md` (~66 lessons + 12 chapter checks, ~9 months).
  Every lesson gets one proof task (free response, graded with a rubric). Solutions manual in collection: grade B, id 787c6e8c5c.
- 2026-10-05: lesson 3 not done yet (learner asked for the link). Lesson 4 not built: wait for lesson 3 results. Its reading:
  C&B §8.3.1 pp. 382–385 (Def. 8.3.1 to Example 8.3.4); flag that C&B's β(θ) is power, not the Type II rate.
- 2026-10-05: **chapter pretests** (learner's request): before each chapter, one item per section per skill (concept, calculation,
  proof); each section's lesson teaches only the missing skills, or is skipped. Mapping table in PROGRAM.md §2. Record each
  chapter's resulting plan here after its pretest.
- 2026-10-05: lesson 3 results 1/12 (record 0007), mostly lesson-design problems; fixed the page (teaching log 16–19). Learner does
  **one lesson a day and doesn't remember details from the day before**: restate everything in each problem.
- 2026-10-05: **lesson 4 = power only** (all from the reading, §8.3.1), with the p-vs-effect revisit and a first proof task
  (`proof-powerfn`). The likelihood-ratio question moved to lesson 5; multiple testing is lesson 6. Reply to read-powerfn,
  read-binom, read-n, read-surprise4 and grade proof-powerfn when results come in.

## 2026-10-06 · Chapter 1 pretest → plan (PROGRAM.md §2 table)
Learner was tired ("Also i am tired"): read borderline results generously; the chapter check catches lucky skips.

| § | Concept | Calc | Proof | Decision |
|---|---|---|---|---|
| 1.1 Sets | ✓ | ✓ | ✓ | **skip** (items go to review) |
| 1.2 Axioms, rules, counting | ✗ (couldn't state the axioms) | ✓ | ✓ (Bonferroni) | **0006 short**: the three axioms and what follows from them |
| 1.3 Conditional prob., independence | ✗ (pairwise vs mutual) | ✓ (Bayes) | ½ (assumed independence; no positivity) | **0007** |
| 1.4 Random variables | ✗ | ✓ (3/8 rejected by a widget bug, now fixed) | ✗ | **0008** with 1.5 |
| 1.5 Distribution functions | ✗ (F = P(X ≤ x), properties) | ✓ | ✗ | **0008** |
| 1.6 Densities and mass functions | ✗ | ✗ | ½ (right intuition) | **0009 full** |

Then 0010 Chapter 1 summary (always), 0011 chapter check. Pattern: calculations are solid (math degree); **formal definitions and
proofs from definitions** are the gap, which is exactly what C&B Ch. 1 trains. Lessons: reason first, name second (rule 21), and
proofs from C&B's own exercises (rule 22).

2026-10-06 (later): §1.4–1.6 merged into one lesson 0008 at the learner's suggestion ("why not try to combine them?"); summary 0009, check 0010.
