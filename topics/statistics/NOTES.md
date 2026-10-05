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
