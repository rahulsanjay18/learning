# How strong is the case for "spread it out" and "vary the questions"? (2026-10-07)

*Written after the learner asked for airtight arguments. This is the audit of my own pushback, holes included.*

## TL;DR
- **Strong:** spreading practice over sessions beats cramming **for remembering facts and concepts** (a large meta-analysis [1]).
- **Moderate, with conditions:** spacing also helps skill tasks on average (d ≈ 0.46), but the size depends on the task [3]; evidence
  for **complex procedural skills** (like system design) is thinner and mixed [4].
- **Moderate, with conditions:** interleaving (mixing problem types) helps on average (g = 0.42) but varies a lot between studies, and
  helps most when the things being mixed are **similar enough to confuse** [5][6].
- **My claim with no source:** "a long lesson is the one that gets abandoned". That's my judgment from your ADHD and the 1-hour floor.
- **Where my rule was sloppy:** "several varied questions on *one* concept" and "interleaving *different* problem types" are different
  things. The interleaving evidence is about the second; your request was mostly the first.
- **So the honest conclusion:** keep spacing (strong for concepts), interleave **confusable** problem types (moderate), and **test the rest
  on you**. The progress server already records first-try results and review outcomes, so we can compare retention of concepts taught
  "lesson-heavy" vs. "spread out" over a few weeks instead of arguing from the literature alone.

## The evidence
| Claim | Source | What it actually shows | Limits |
|---|---|---|---|
| Spacing beats massing for memory | Cepeda et al. 2006 [1] | 839 assessments, 317 experiments: spaced > massed; the best gap between sessions grows with how long you need to remember | **verbal recall tasks** only |
| Spacing and mixing in math practice | Rohrer & Taylor 2007 [2] | Exp. 1: spaced > massed one week later; Exp. 2: mixed problem types "vastly superior" one week later; mixing *felt* worse during practice | college students, one kind of math task, small samples |
| Spacing for skill tasks | Donovan & Radosevich 1999 [3] | 63 studies: d = 0.46 for spaced over massed on task performance; moderated by task type and interval | effect not uniform; complexity results not confirmed in the abstract |
| Spacing for procedural/complex skills | e.g. a 2020 study on math procedures, a piano study [4] | weaker or absent effects for some procedural skills; <10% of spacing research is on motor skills | single studies, mixed |
| Interleaving overall | Brunmair & Richter 2019 [5] | 59 studies: g = 0.42, substantial heterogeneity; best for visual categories (paintings, g = 0.67) | small effect for math; depends on similarity |
| Why similarity matters | reviews of [5] [6] | interleaving helps by forcing you to tell similar things apart | little benefit when items are very different |

## What changes in lessons (rule 29, revised)
1. Recap boxes for earlier concepts: kept (that's your preference, not an evidence claim).
2. 2–3 varied questions per concept in the lesson, more variants in later review: kept, now justified by spacing [1][3] rather than interleaving.
3. Interleave on purpose where problem types are **confusable** (Type I vs. Type II errors; consistency models; similar AWS services).
4. Measure it: tag lessons "lesson-heavy" or "spread out" and compare review retention after 2–4 weeks (an n = 1 experiment on your own data).

## Sources
1. Cepeda, Pashler, Vul, Wixted & Rohrer (2006), "Distributed practice in verbal recall tasks", *Psychological Bulletin* 132(3):354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/ (PDF: https://www.evullab.org/pdf/CepedaPashlerVulWixtedRohrer-PB-2006.pdf)
2. Rohrer & Taylor (2007), "The shuffling of mathematics problems improves learning", *Instructional Science* 35:481–498. https://digitalcommons.usf.edu/psy_facpub/1767/
3. Donovan & Radosevich (1999), "A meta-analytic review of the distribution of practice effect: Now you see it, now you don't", *Journal of Applied Psychology* 84(5). https://www.gwern.net/docs/spaced-repetition/1999-donovan.pdf
4. Frontiers in Psychology (2020) on distributed practice for procedural math knowledge. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.00811/pdf
5. Brunmair & Richter (2019), "Similarity matters: A meta-analysis of interleaved learning and its moderators", *Psychological Bulletin*, doi:10.1037/bul0000209. https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf
6. Review noting interleaving helps most for highly similar categories (Educational Psychology Review, 2022). https://link.springer.com/article/10.1007/s10648-022-09666-5
