# Statistics: the major (program)

*Decided 2026-10-05 with the learner: cover **all of Casella & Berger**, cover to cover, **doing proofs yourself**. Full-weight
subject: 4 blocks of 25 minutes a week (`notes/study-plan.md`).*

## TL;DR
- **Spine:** Casella & Berger, *Statistical Inference*, 2nd ed. (grade A, in collection), all 12 chapters, in order [1].
- **First,** finish the A/B-testing arc already under way (S150: 2 more lessons, likelihood ratios and multiple testing). **Then** Chapter 1, page 1.
- **One lesson = 2 blocks:** block 1 reads ~7 pages with a reading guide; block 2 is the lesson page: idea → worked example →
  practice → **one proof you write**. About 2 lessons a week.
- **Size:** ~450 pages of text → at most ~66 lessons + 12 pretests + 12 chapter checks ≈ **40 weeks** (132 + 14 + 12 = 158 blocks) at 4 blocks a week if you
  knew nothing. Pretest skips will cut that, probably by a lot in Ch. 1–4. Extra time (after the day's plan is done) also shortens it.
- **Proofs:** every lesson has one proof task, graded by me with a rubric. Exercises from the book are optional homework (rule 13).
- **A pretest before every chapter.** It scores each section on three separate skills (**concept, calculation, proof**), and each
  section's lesson teaches only what's missing, or is skipped entirely if you know all three (section 2 below).


## 0. Two levels (revised 2026-10-06; structure: `notes/major-design.md`, adapted from NYU Gallatin)
The learner asked for **Stat I** (≈ an undergraduate major) and **Stat II** (≈ graduate coursework, as close to a PhD as
self-study gets). The full course map, with prerequisites, is `curriculum.json`; sections 1–7 below describe the Casella &
Berger core of Level I, unchanged.

**Plan (the "IAPC").** Starting point: probability mechanics solid, inference interpretation was the gap (records 0001–0002);
math degree, AI career. Aim (MISSION.md): read, run and defend real analyses (A/B tests first), then the theory behind them, then
graduate theory. Level I finishes Casella & Berger with proofs and adds the applied courses a BS needs; Level II is
qualifying-exam theory plus the modern topics an ML career leans on (causal, Bayesian, high-dimensional, bandits).

**Only the core row is the major**; the other rows are optional extras, suggested when they'd help or you want them.

| Group | Level I (≈ BS) | Level II (≈ MS + PhD coursework) |
|---|---|---|
| Core | S150 practitioners · S110 probability review · S201–S205, S301–S304, S401–S403 (all of C&B) · S310 applied regression/GLMs · S320 experiments and A/B testing · S330 computing and simulation · S340 Bayesian I | S500 analysis refresher · S501–S502 measure-theoretic probability · S511 estimation · S512 testing · S513 asymptotics · S520 GLM theory · S530 Bayesian · S540 causal · S550 learning theory and high-dimensional |
| Breadth | S190 history and philosophy of statistics · S195 measurement and ethics | S590 foundations of inference seminar |
| Electives | S360 time series · S370 sampling · S380 statistical learning | S560 nonparametrics · S570 computational · S580 bandits |
| Practice | S390 three real analyses end to end | S595 quals-style self-check · S596 reproduce and extend a published result |
| Capstone | S399 ~20-page analysis report | S599 ~40-page paper |
| End-of-level talk | S398 | S598 |

Rough size of the core: Level I ≈ 110 lessons (pretests will cut a lot, given the math degree), Level II ≈ 120. At 4 blocks a week that is years, which is expected.

**Works read so far** (for the optional end-of-level talk). Level I so far: Casella & Berger;
Bruce, Bruce & Gedeck; Hand, *Statistics* VSI; Kohavi et al. (when acquired). Candidates spanning periods and disciplines:
Bayes (1763) and Laplace on inverse probability; Fisher, *Statistical Methods for Research Workers* (1925); Neyman & Pearson
(1933); Jaynes; Tukey, "The Future of Data Analysis" (1962); Breiman, "Statistical Modeling: The Two Cultures" (2001).

**Books needed** (not in the library, or only as an unusable copy). Free ones first: please download them into the library.
- Free from the authors: Blitzstein & Hwang, *Introduction to Probability*; Durrett, *Probability: Theory and Examples*;
  Gelman et al., *Bayesian Data Analysis* 3rd ed.; Hernán & Robins, *Causal Inference: What If*; Hastie, Tibshirani &
  Friedman, *Elements of Statistical Learning* (your copy is garbled); James et al., *ISL* (garbled copy); Efron & Hastie,
  *Computer Age Statistical Inference*; Hyndman & Athanasopoulos, *FPP3*; Lattimore & Szepesvári, *Bandit Algorithms*.
- To buy, by when they're needed: Kohavi, Tang & Xu, *Trustworthy Online Controlled Experiments* (S320, soonest);
  Agresti, *Foundations of Linear and Generalized Linear Models* (S310/S520); Salsburg, *The Lady Tasting Tea* (S190);
  Abbott, *Understanding Analysis* (S500); Lehmann & Casella, *Theory of Point Estimation*; Lehmann & Romano, *Testing
  Statistical Hypotheses*; van der Vaart, *Asymptotic Statistics*; Keener, *Theoretical Statistics*; Imbens & Rubin, *Causal
  Inference*; Wainwright, *High-Dimensional Statistics*; Lohr, *Sampling*; Wasserman, *All of Nonparametric Statistics*;
  Mayo, *Statistical Inference as Severe Testing*.

---

## 1. Courses

Page ranges are the chapters' text, without exercises and miscellanea, from the book's own contents page [1].

| Course | Casella & Berger | Pages | Lessons | Notes |
|---|---|---|---|---|
| S100 Placement | — | — | 1 (done) | Lesson 0001. Probability mechanics solid; inference interpretation was the gap (records 0001–0002) |
| **S150 Inference for practitioners** (now) | slices of §8.3, §9.1 | — | 6 (4 done) | 0002 p-values · 0003 effect size and CIs · 0004 power (§8.3.1) · **0005 likelihood ratios: P(data given H1)** · **0006 multiple testing**. Ties straight to the A/B-test goal in the mission |
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

Total after S150: **up to** ~66 lessons. Each chapter starts with a **pretest** and ends with a **chapter check** (one block each).
Skipped and shortened sections bring the real number down; expect the biggest savings in Ch. 1–4.

**After Casella & Berger** (electives, for the parts of the mission the book doesn't cover; sources still to choose, see RESOURCES.md Gaps):
causal inference (the confounder → remedy gap in record 0004), Bayesian data analysis, and statistical learning (ISL) as the bridge to ML.

## 2. Chapter pretest: test out of what you already know
Before each chapter (one block; two for the long chapters 4–5), a pretest asks **three questions per section**, one per skill:

| Skill | What it checks | Item type (recall, not recognition: rule 8) |
|---|---|---|
| **Concept** | What it means, when it applies, why it's true in one sentence | short typed answer, sorting, or a "which is true and why" free box |
| **Calculation** | Can you compute with it | a number or formula answer (accepts expressions) |
| **Proof** | Can you prove the section's key result | a proof sketch (3–6 lines, free box, I grade it), sometimes "put the proof steps in order" |

- Every item has an **I don't know** button. Pressing it counts as not known, which is the honest answer, not a failure. If you
  guessed and got it right, say so in the note box and I'll count it as not known.
- Item ids encode the section and skill (`c3-s2-calc`), so the results line maps straight onto this table.

**What each section gets, from its three results:**

| Concept | Calculation | Proof | That section's lesson |
|---|---|---|---|
| ✓ | ✓ | ✓ | **Skip it.** Its pretest items go into the daily review, and the chapter check confirms it later |
| ✓ | ✓ | ✗ | **Proof lesson:** read only the proofs, then write them (1 block) |
| ✓ | ✗ | ✗ | **Calculation + proofs:** worked examples, practice, then a proof |
| ✗ | any | any | **Full lesson** (block 1 reading, block 2 the page) |
| other mixes | | | Teach the missing skills only; e.g. calculation without the concept gets a short concept section, then proofs |

Neighbouring short lessons can share a block. The plan for each chapter (which sections are skipped, short or full) goes in NOTES.md
after its pretest, so you can see it.

## 3. One lesson (2 blocks, or 1 for a short one)
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

## 4. Every chapter
- **Chapter check (1 block):** recall-heavy questions plus one proof, across the whole chapter, **including skipped sections**
  (so a skip based on one lucky answer gets caught).
- **Reference sheet:** each chapter adds to `reference/formulas.html` (results) and a new **theorem sheet** (statement, conditions,
  proof idea in one line).
- **Glossary:** starts with S201. Once it exists, every lesson uses its terms (sufficient, complete, ancillary, size vs. level…).

## 5. Checking proofs
- I check every proof myself against the book's text (grade A) and with code where it helps (sympy for algebra, simulation for a
  distributional claim).
- The *Solutions* manual for Casella & Berger is in the collection (grade B, id `787c6e8c5c`): I can use its prose to cross-check
  an argument, but never copy its equations. For exercises it covers, compare with your own copy after you've written yours.

## 6. Notation warnings (things that will trip you up)
- In §8.3.1 Casella & Berger write the **power function** as \(\beta(\theta) = P_\theta(X \in R)\) [1, p. 383]. Many applied texts
  (and lesson 0002) use \(\beta\) for the **Type II error rate**, so power = \(1-\beta\). Same letter, opposite meaning: lessons will
  flag it each time.
- Casella & Berger use "size" and "level" for different things (Definitions 8.3.5–8.3.6) [1, p. 385].

## 7. Mission link
- *A/B test end to end* → S150, then Ch. 8–9 and 11.
- *Read p-values and CIs correctly* → S150, Ch. 8–9.
- *Fit, interpret and critique a regression* → Ch. 11–12, then the causal-inference elective.
- *Bayesian updating (conjugate priors)* → §7.2.3, §8.2.2, §9.2.4, then the Bayesian elective.

## Sources
1. George Casella & Roger L. Berger, *Statistical Inference*, 2nd ed. (Duxbury, 2002): contents pages (pp. xiii–xvii) for the chapter
   and page ranges; preface quote; §8.3.1 pp. 382–385 for the notation notes. In collection (grade A, id `f9dc4d1d4c`), read on the book server.
2. Learner's request, 2026-10-05: pretest each chapter, scored separately on concept, calculation and proof. `notes/study-plan.md` (4 blocks a week for a full-weight subject); `TEACHING-LOG.md` rules 4, 7, 8, 12, 13.
3. *Solutions-Casella-Berger*, in collection (grade B, id `787c6e8c5c`), per `library/MANIFEST.csv`.
