# How grading and pacing work here (mastery + syllabus), 2026-10-06

## The idea
Like the mastery grading from 6th grade: the question is "did you learn the thing", not "was every detail there". Each lesson in a
major's `SYLLABUS.md` lists 2–3 objectives ("you can…"). Each one is judged **Got it** or **Not yet**.

| Verdict | When | What happens |
|---|---|---|
| Got it | The idea is right and nothing false was said, even if a detail is missing | Feedback says what was missing. No extra teaching |
| Not yet | Something false or confused; missed twice; skipped or guessed; you say you're confused | A 5-minute re-teach at the start of the next lesson in that course |
| Can't tell | A thin answer | One warm-up question next time; a miss there → Not yet |

- A whole extra lesson only if the gap blocks the next lessons, or it's still Not yet after one re-teach. Every such change is logged
  in the syllabus's "Changes" list, so you can see when and why the plan moved.
- **Facts (dates, names) never trigger extra lessons:** they go to warm-ups and the spaced review deck (1526 is the current example).
- Example from today: "Which periodisation would you use?" had a good reason but no example. That's **Got it** (you know the examples
  from the reading). The ice-cream answer proposed an observational fix for confounding. That's **Not yet**, so a 5-minute
  "why randomization removes confounding" section goes into Statistics 0007.

## Does mastery grading work for adults?
- A meta-analysis of 108 controlled studies found mastery-learning programs raised exam scores by about **0.5 standard deviations**,
  in colleges as well as schools, with bigger gains for weaker students [1].
- **Caveat that matters here:** *self-paced* mastery programs lowered completion rates in college classes [1]. So the syllabus keeps
  a fixed pace and caps re-teaching at short sections rather than "redo until perfect".
- Linda Nilson's *Specifications Grading* (2014) is the college version: each outcome graded pass/fail, where pass means solid
  (B-level) work, tied to learning outcomes rather than points [2].

## Why plan ahead
A syllabus written once (readings and objectives per lesson) means each session only writes the next lesson instead of designing
it. That's cheaper in tokens and gives you a visible road map: `topics/indian-history/SYLLABUS.md`, `topics/statistics/SYLLABUS.md`,
`topics/games/SYLLABUS.md`. The rule itself: `TEACHING-LOG.md` rule 20.

## Sources
1. Kulik, Kulik, Bangert-Drowns & Slavin, "Effectiveness of mastery learning programs: A meta-analysis", *Review of Educational
   Research* 60(2), 1990, pp. 265–299. Summary: https://www.academia.edu/81783373/Effectiveness_of_Mastery_Learning_Programs_A_Meta_Analysis
2. Linda B. Nilson, *Specifications Grading: Restoring Rigor, Motivating Students, and Saving Faculty Time* (Stylus, 2014). Review:
   https://wabashcenter.wabash.edu/resources/book-reviews/specifications-grading-restoring-rigor-motivating-students-and-saving-faculty-time
