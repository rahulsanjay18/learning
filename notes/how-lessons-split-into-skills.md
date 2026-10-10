# How lessons get split into skills (2026-10-10)

**Short answer:** today it's mostly judgment, inside a structure that is research-backed in places. The book's section boundaries
set what a lesson covers. I write 2–3 "you can…" objectives per lesson. Each objective gets a question family, and each objective is
graded Got it / Not yet. The research supports *grading* by objective (mastery learning) and *how many* new ideas fit in one lesson
(cognitive load). It does **not** support the claim that my particular split is the right one. In the learning-science literature
that's an empirical question, settled with learner data, and we haven't done that yet.

## What the platform does now, layer by layer

| Layer | What decides it | Basis |
|---|---|---|
| **Course → lessons** | The primary book's sections (a major is a sequence of books) | Judgment: the author already ordered prerequisites. Ours, not research |
| **Lesson → 2–3 objectives** | Written ahead in each major's syllabus, as observable "you can…" statements | Felder & Brent: an objective must be *observable* ("watch the students do it or see the product") [1]; Bloom's taxonomy for the verb level [1] |
| **At most ~2 new definitions per lesson** | Teaching-log rule 21, after a lesson stacked five definitions | Cognitive load: working memory holds roughly four chunks (Cowan, as cited by Felder & Brent [1]); overload blocks learning [1][2] |
| **Objective → question family** | Several variants per objective (compute, explain, spot the error, transfer) | Spacing and variety evidence already audited in `notes/evidence-spacing-and-variety.md` |
| **Objective → Got it / Not yet** | Mastery rule, rule 20 | Mastery learning meta-analysis: about 0.5 SD gain across 108 studies (Kulik et al. 1990) [3]; Nilson's specifications grading [4] |

## What the research says the "skill" unit should be

- **Knowledge components (KCs).** The Knowledge-Learning-Instruction framework (Koedinger, Corbett & Perfetti 2012) [5] calls the
  unit a *knowledge component*: a mental structure or process a learner uses, alone or with others, to do a step of a task. Our
  question families are a rough stand-in for KCs.
- **The right grain size is decided with data, not by the teacher.** Plot error rate against practice opportunities for each
  hypothesised KC. A real single skill gives a smooth curve that falls. A flat or bumpy curve means the "skill" is really two
  (split it), or the items are too easy (drop practice). CMU's DataShop does this. Koedinger's geometry case study found a
  better KC model this way and tested it with AIC/BIC [6]. Learning Factors Analysis automates the search [6].
- **Why the teacher's own split is suspect.** Experts leave out much of what they know when they describe a skill. A 2011 AERA
  abstract (Yates, Feldon & Clark) puts it at about 70% of the decisions involved. Feldon & Stowe report that experts' unaided
  explanations contain significant omissions and errors [7]. The 70% comes from a workshop abstract, not a full paper, so treat
  it as a rough figure. The direction is consistent across the work.
  That's why your misses matter more than my plan. "Indus origin stages" and "p vs. effect size" both became their own items
  because you missed them, not because I'd foreseen it.

## The holes in what we do (my judgment)
1. **Objectives aren't validated.** No learning curve has checked that a family behaves like one skill.
2. **One learner means thin data.** KC model fitting normally pools many students. With one person, a family needs about five or
   more attempts before its curve says anything. Most families have one or two attempts so far.
3. **Old lessons have no families.** Only lessons written since 2026-10-08 use `<family>-vN` ids.

## What I'd do about it (proposal, not built)
- Once families have about five attempts each, the progress server prints a per-family error curve in the session digest.
  A family that doesn't improve gets one of two fixes:
  - **Split it**, if its misses cluster on one variant kind, e.g. you can compute it but can't explain it.
  - **Retire it to stale-only review**, if it stays flat and low because it's too easy.
- Log each split in the course syllabus's "Changes" section, as done today for Not-yet re-teaches.

## Sources
1. Richard M. Felder & Rebecca Brent, *Teaching and Learning STEM: A Practical Guide* (Jossey-Bass, 2016), Ch. 2 "Learning
   objectives" (§2.2 Bloom's taxonomy; objectives must be observable) and the section on cognitive load (pp. 92–94, citing
   Cowan 2010 and Sweller, Ayres & Kalyuga 2011). In your library (40d76146c5).
2. J. Sweller, P. Ayres & S. Kalyuga, *Cognitive Load Theory* (Springer, 2011), as cited in [1].
3. C.-L. C. Kulik, J. A. Kulik & R. L. Bangert-Drowns, "Effectiveness of mastery learning programs: A meta-analysis", *Review of
   Educational Research* 60(2), 1990, pp. 265–299 (cited in `notes/mastery-grading.md`).
4. Linda B. Nilson, *Specifications Grading* (Stylus, 2014) (cited in `notes/mastery-grading.md`).
5. K. R. Koedinger, A. T. Corbett & C. Perfetti, "The Knowledge-Learning-Instruction Framework: Bridging the Science-Practice Chasm
   to Enhance Robust Student Learning", *Cognitive Science* 36(5), 2012, pp. 757–798.
   [CMU repository](https://kilthub.cmu.edu/articles/journal_contribution/The_knowledge-learning-instruction_framework_bridging_the_science-practice_chasm_to_enhance_robust_student_learning_/6470522) ·
   [preprint PDF](https://home.cs.colorado.edu/~mozer/Teaching/syllabi/TopicsInCognitiveScienceFall2011/KLI-paper-v5.00.pdf)
6. LearnLab DataShop: [research goals and learning-curve guidance](https://learnlab.org/datashop/ResearchGoals) and the
   [Koedinger geometry case study](https://datashop.phzh.ch/about/case-studies/koedinger-geometry-script-for-web.htm).
7. D. F. Feldon & K. Stowe (2009) and the Yates, Feldon & Clark AERA 2011 abstract, via [USU Digital Commons](https://digitalcommons.usu.edu/itls_facpub/454)
   and [Feldon's works page](https://works.bepress.com/david_feldon/115). I haven't read the full text of either.
