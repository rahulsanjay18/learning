# Statistics: the major (program)

*Decided 2026-10-05 with the learner: cover **all of Casella & Berger**, cover to cover, **doing proofs yourself**. Full-weight
subject: 4 blocks of 25 minutes a week (`notes/study-plan.md`).*

## TL;DR
- **Spine:** Casella & Berger, *Statistical Inference*, 2nd ed. (grade A, in collection), all 12 chapters, in order [1].
- **First,** finish the A/B-testing arc already under way (S150: 2 more lessons, power and multiple testing). **Then** Chapter 1, page 1.
- **One lesson = 2 blocks:** block 1 reads ~7 pages with a reading guide; block 2 is the lesson page: idea → worked example →
  practice → **one proof you write**. About 2 lessons a week.
- **Size:** ~450 pages of text → ~66 lessons + 12 chapter checks ≈ **36 weeks (about 9 months)** at 4 blocks a week. Extra time
  (after the day's plan is done) shortens it.
- **Proofs:** every lesson has one proof task, graded by me with a rubric. Exercises from the book are optional homework (rule 13).

---

## 1. Courses

Page ranges are the chapters' text, without exercises and miscellanea, from the book's own contents page [1].

| Course | Casella & Berger | Pages | Lessons | Notes |
|---|---|---|---|---|
| S100 Placement | — | — | 1 (done) | Lesson 0001. Probability mechanics solid; inference interpretation was the gap (records 0001–0002) |
| **S150 Inference for practitioners** (now) | slices of §8.3, §9.1 | — | 5 (3 done) | 0002 p-values · 0003 effect size and CIs · **0004 power and likelihood ratios** · **0005 multiple testing**. Ties straight to the A/B-test goal in the mission |
| S201 Probability theory | Ch. 1 | 1–37 | 4 | Fast: your pretest was strong here. Proof focus: from the axioms (Kolmogorov) |
| S202 Transformations and expectations | Ch. 2 | 47–76 | 4 | Change of variables, mgfs, differentiating under the integral sign |
| S203 Common families of distributions | Ch. 3 | 85–127 | 6 | Fixes the rusty recall in record 0003 (geometric, Poisson, memorylessness). Exponential families matter for GLMs |
| S204 Multiple random variables | Ch. 4 | 139–192 | 7 | Conditional distributions, hierarchical models, covariance, inequalities (Jensen, Cauchy–Schwarz) |
| S205 Properties of a random sample | Ch. 5 | 207–255 | 7 | Sampling distributions, t and F, order statistics, convergence, delta method, generating random samples |
| S301 Principles of data reduction | Ch. 6 | 271–300 | 5 | Sufficiency, completeness, the likelihood principle: proof-heavy |
| S302 Point estimation | Ch. 7 | 311–355 | 7 | MoM, MLE, Bayes estimators, EM, MSE, Cramér–Rao, Rao–Blackwell |
| S303 Hypothesis testing | Ch. 8 | 373–402 | 5 | LRTs, Bayesian tests, Neyman–Pearson, p-values. Re-reads the S150 slices properly |
| S304 Interval estimation | Ch. 9 | 417–451 | 5 | Inverting tests, pivots, Bayesian intervals, optimality |
| S401 Asymptotic evaluations | Ch. 10 | 467–504 | 6 | Consistency, efficiency, bootstrap SEs, robustness, LRT asymptotics, Wald and score tests |
| S402 ANOVA and regression | Ch. 11 | 521–563 | 6 | One-way ANOVA, simple linear regression, prediction and confidence bands |
| S403 Regression models | Ch. 12 | 577–602 | 4 | Errors in variables, logistic regression, robust regression |

Total after S150: ~66 lessons. Each chapter ends with a **chapter check** (one block).

**After Casella & Berger** (electives, for the parts of the mission the book doesn't cover; sources still to choose, see RESOURCES.md Gaps):
causal inference (the confounder → remedy gap in record 0004), Bayesian data analysis, and statistical learning (ISL) as the bridge to ML.

## 2. One lesson (2 blocks)
**Block 1: reading (~25 min).** About 7 pages of Casella & Berger, with a reading guide: 3 questions + "what surprised or confused you"
as note boxes at the top of the lesson page (rule 12). The book says it plainly in its preface: "perhaps, the only way to master this
material is through practice" [1], so read with paper and pencil.

**Block 2: the lesson page (~25 min).**
1. Warm-up: 2–3 retrieval questions from earlier lessons (spaced and interleaved).
2. The idea: intuition → numbers → formula (rule 4), with a worked example (rule 7).
3. Practice: computed answers and recall, not just multiple choice (rule 8).
4. **Proof task:** usually a short theorem or lemma from the section, or one of its exercises. Two kinds:
   - *proof skeleton* (warm-up): put the steps of a proof in order, or fill the missing step;
   - *your proof* (main): write it in a free-response box (plain text or LaTeX). I grade it next session with a rubric
     (correct claim, every step justified, no hidden assumptions) and reply.
5. Optional homework: one book exercise, clearly marked optional. No later lesson depends on it.

## 3. Every chapter
- **Chapter check (1 block):** recall-heavy questions plus one proof, across the whole chapter.
- **Reference sheet:** each chapter adds to `reference/formulas.html` (results) and a new **theorem sheet** (statement, conditions,
  proof idea in one line).
- **Glossary:** starts with S201. Once it exists, every lesson uses its terms (sufficient, complete, ancillary, size vs. level…).

## 4. Checking proofs
- I check every proof myself against the book's text (grade A) and with code where it helps (sympy for algebra, simulation for a
  distributional claim).
- The *Solutions* manual for Casella & Berger is in the collection (grade B, id `787c6e8c5c`): I can use its prose to cross-check
  an argument, but never copy its equations. For exercises it covers, compare with your own copy after you've written yours.

## 5. Notation warnings (things that will trip you up)
- In §8.3.1 Casella & Berger write the **power function** as \(\beta(\theta) = P_\theta(X \in R)\) [1, p. 383]. Many applied texts
  (and lesson 0002) use \(\beta\) for the **Type II error rate**, so power = \(1-\beta\). Same letter, opposite meaning: lessons will
  flag it each time.
- Casella & Berger use "size" and "level" for different things (Definitions 8.3.5–8.3.6) [1, p. 385].

## 6. Mission link
- *A/B test end to end* → S150, then Ch. 8–9 and 11.
- *Read p-values and CIs correctly* → S150, Ch. 8–9.
- *Fit, interpret and critique a regression* → Ch. 11–12, then the causal-inference elective.
- *Bayesian updating (conjugate priors)* → §7.2.3, §8.2.2, §9.2.4, then the Bayesian elective.

## Sources
1. George Casella & Roger L. Berger, *Statistical Inference*, 2nd ed. (Duxbury, 2002): contents pages (pp. xiii–xvii) for the chapter
   and page ranges; preface quote; §8.3.1 pp. 382–385 for the notation notes. In collection (grade A, id `f9dc4d1d4c`), read on the book server.
2. `notes/study-plan.md` (4 blocks a week for a full-weight subject); `TEACHING-LOG.md` rules 4, 7, 8, 12, 13.
3. *Solutions-Casella-Berger*, in collection (grade B, id `787c6e8c5c`), per `library/MANIFEST.csv`.
