# Teaching log: what went wrong, and the rule that prevents it

Read this **before writing any lesson, in any subject**. When the learner's questions or results show that an explanation or a
lesson was flawed, add an entry: what happened (with the question that exposed it), why, and the rule. Rules apply to every topic.

## Rules (the short version)
1. **Define before use.** Before a lesson uses a term, check the topic's learning records. If the term was missed, skipped or never
   taught, define it in the lesson first. (Entry 1)
2. **Never test what wasn't taught.** Every practice item must be answerable from this lesson or an earlier one. (Entry 2)
3. **Small sorting questions.** categorize/order items: 3–4 rows. A long all-or-nothing item hides which part was missed. (Entry 3)
4. **Intuition → numbers → formula**, in that order. A formula alone doesn't land; a concrete story with real numbers does. (Entry 4)
5. **Give the sentence.** For anything people commonly mis-say (probability, causation), give a correct sentence to reuse and the
   common wrong one, side by side. (Entry 5)
6. **Precise wording in questions.** State every condition the answer depends on (e.g. "independent events *in the same
   experiment*"). Reread each prompt asking "could a careful reader object?" (Entry 6)
7. **Worked example before practice.** Walk through one, then give a similar one with new numbers. Not a cold question. (Entry 1)
8. **Multiple choice measures recognition.** Don't treat a right multiple-choice answer as known; check with recall (typed answers,
   timelines, free response). The learner guesses sometimes and says so. (Entry 7)
9. **Assign reading before the lesson whenever it makes sense** (all subjects, not only definition-heavy ones). Give a short,
   specific slice of the primary source with a reading guide (3 questions + "what surprised or confused you"), as its own block
   before the lesson. (Entries 8, 13)
13. **(Exception 2026-10-07: in the Engineering career major `topics/eng/`, the rep is required at the learner's request; see its PROGRAM.md §3.)** **Homework is allowed but optional.** Keep it small and specific (one exercise, one game to play, one short write-up), mark it
    clearly as optional, and **design every lesson so it still works if the homework was skipped** (the learner isn't sure how
    much they'll do). Never make a later lesson depend on homework; if it builds on homework, include a 2-minute recap. Track what
    gets done in the topic's NOTES.md and adjust the amount to what actually happens. (Entry 13)
10. **Verify every fact and number** against a source or with code before publishing (already standard; keep doing it).
12. **Reading guides as note-taking:** for assigned readings, put 3 guide questions + "what surprised or confused you" as `free`
    boxes at the top of the lesson. They're the learner's notes, they reach the teacher with the results, and every answer gets a reply.
14. **Check paraphrases against the source sentence**, not memory of it: reread the passage before compressing it. (Entry 14)
15. **Reading guides flag notation traps:** where the source writes a familiar formula in an unfamiliar form (√(σ²/n) for σ/√n)
    or sets up an example earlier than the slice starts, say so in the reading box. (Entry 15)
11. **Remind the learner that formula boxes take expressions** (`8/28`, `160*0.05/(...)`), so arithmetic slips don't cost a question,
    **and say how to type them**: `*` for ×, `/`, `^`, `sqrt( )`, on every page with a formula box. (Entries 9, 18)
16. **Every problem is self-contained.** Restate every number and condition it needs (the setup, the threshold, the sample size);
    never "lesson 2's test" or "our test". The learner does one lesson a day and the review deck shows questions out of context.
    And **show where every number comes from** (e.g. derive an SE, don't just state it). (Entry 16)
17. **Say how each section relates to the reading:** "from the reading" vs. "beyond the reading". (Entry 17)
18. **Units in answer boxes are unambiguous** ("as a decimal, 0.10 means 10%"); prefer the form a mathematician would type. (Entry 18)
19. **Use the learner's own vocabulary next to the textbook's** (Type I = false positive, Type II = false negative). (Entry 19)
20. **Mastery rule: grade objectives Got it / Not yet, and extend only for "Not yet".** Every lesson has 2–3 "you can…" objectives
    (from the major's `SYLLABUS.md`). Keep 0–1 scores for the server, but the *decision* is binary:
    - **Got it:** the answer shows the idea correctly with no false statement, even if a detail is missing. Say what was missing in
      the feedback; **no re-teaching**.
    - **Not yet:** a false statement or misconception; the same objective missed twice (first try or in review); a skip, "I don't
      know" or self-reported guess; or the learner says they're confused.
    - **Can't tell** (a thin answer): one warm-up question on it next lesson; a miss there means Not yet.
    - **Not yet → a 5-minute re-teach section at the start of the next lesson in that course**, syllabus otherwise unchanged. Add a
      whole lesson only when the objective is a prerequisite for the next syllabus lessons, or it's still Not yet after one re-teach;
      log that in the syllabus's "Changes". **Facts (dates, names) go to spaced review and warm-ups, not extra lessons** (entry 10).
    - Plan the whole course up front in `SYLLABUS.md` (readings + objectives); sessions write the next lesson, they don't redesign. (Entry 20)
21. **Reason first, name second.** Introduce each new definition by a question the learner works through in revealed steps
    (`::: worked`), then name it and give the formal statement. At most ~2 new definitions per lesson; more → split. (Entry 21)
22. **Use the book's exercises; never leak answers.** Draw practice, pretest, proof and check items from the textbook's own
    exercises where they fit (cite them: "C&B Exercise 1.33"), adapting numbers only when needed. And never state an answer to a
    question the learner hasn't done yet, in chat or anywhere visible: verify answers with assertions that don't print them. (Entry 22)
23. **Choices must not give the answer away.** A candidate button labelled with the answer's own name (a map choice named
    "Lothal" when the question asks where Lothal is) tests reading, not knowing. Unlabelled map clicks, or labels that don't name
    the target. (Entry 23)
24. **Grade only against what was assigned.** If a rubric point needs a fact from a source the learner wasn't given (the
    paper behind a news article), it isn't a fault when they miss it; mention it as extra. Check what the assigned source
    actually says before calling an answer wrong. (Entry 24)

## Entries
1. **2026-10-05 · Statistics lesson 2 used α and power without defining them.** Learner: "you never describe what alpha is… I don't
   know what the first problem even means." Both were pretest misses (learning records). Fix: vocabulary section with the
   Type I/II table and a power plot, then a worked example before the practice question.
2. **2026-10-05 · Statistics lesson 2 tested "p vs effect size" without teaching it.** Learner: "I don't understand these two" and
   "the other question was hard." Only an ASA bullet mentioned it. Fix: a taught section with a study table and coin intuition.
3. **2026-10-05 · A six-statement sorting question was all or nothing.** One wrong row failed the item and hid what was understood.
   Fix: split into two 3-row items.
4. **2026-10-05 · "With huge samples, tiny effects get tiny p-values" explained only via z = effect/SE.** Learner asked again. The coin
   story (50.5% heads; 100 vs. 1,000,000 flips) worked. Fix: rule 4.
5. **2026-10-05 · The learner understood p but couldn't phrase it** ("is it 96% chance the website caused it?", "what is 1 − p?").
   The ideas were there; the wording wasn't. Fix: rule 5, plus a Q&A log per topic (`topics/<slug>/QUESTIONS.md`).
6. **2026-10-05 · Pretest Q2 said "independent" without saying the events are in the same experiment.** Learner flagged it.
7. **2026-10-05 · Indian History pretest: "some of these answers were guesses."** 9/13 overstated the level. Fix: rule 8; a
   "How sure were you?" step is planned for quiz widgets.
8. **2026-10-05 · The learner offered to read beforehand.** Lessons had been self-contained; for definition-heavy lessons, assign a
   short primary-source slice first (rule 9).
9. **2026-10-05 · An arithmetic slip cost a conceptual question** (fraction of duds). The math widget accepts expressions, but the
   learner wasn't told. Fix: rule 11.
10. **2026-10-05 · Pretest misses were mostly forgotten facts** (learner's words), not confusion. Fix: formula/reference sheets plus
    spaced review for recall gaps; save full lessons for ideas.
11. **2026-10-05 · "Effect size" was used but never defined, even in the section added to fix entry 2.** Learner: "the effect size
    thing is pretty much missing entirely." A fix for one gap can itself break rule 1. Fix: a plain definition where the term first
    appears (absolute and relative lift); lesson 3 teaches effect size properly (practical vs. statistical significance) before CIs.
    **Check every fix against rule 1 too.**
13. **2026-10-05 · Learner's standing preference:** readings before lessons are welcome in every subject when they make sense;
    homework is fine, but the learner is unsure how much they'll do. Rules 9 and 13.
14. **2026-10-05 · Indian History lesson 0002 paraphrased the Ghaggar passage wrongly** ("a tectonic shift sent its water into the
    Yamuna"); the book says the Yamuna once flowed *through* the Ghaggar valley and changed course. The learner's reading answer
    had it right, so the page contradicted the reading. Fix: corrected the page; rule 14.
15. **2026-10-05 · Lesson 3's reading (C&B Example 9.1.3) wrote SD(X̄) as √(1/4).** Learner: "why the 1/4 in the denominator? I
    thought the SD formula has the sqrt of the number of samples." It is σ/√n with σ = 1, n = 4, written as √(σ²/n), and the setup
    is in the previous example. Fix: a heads-up line in the reading box; rule 15.
16. **2026-10-05 · Lesson 3 problems lacked context.** Learner: "You really don't give enough context for these problems. I'm doing
    it like once a day, I don't remember every detail", and "how do you know the standard error? … was that given?" (it wasn't
    derived). Fix: a restated running example, a derived SE, self-contained prompts; rule 16.
17. **2026-10-05 · "I don't know how much of this has anything to do with the reading."** Lesson 3 mixed §9.1 with applied material
    without saying so. Fix: section labels; rule 17.
18. **2026-10-05 · Two right answers marked wrong by the format:** `rel-lift` wanted a percent, learner typed the decimal 0.5/4;
    `ci-lower`, learner couldn't find how to type × and estimated 2 instead of 1.96. Fix: decimal answer, typing help; rules 11, 18.
19. **2026-10-05 · "I usually remember type 1 and 2 errors as false positive and false negative."** Options used "missing a real
    effect" etc. Fix: FP/FN in lesson 2's table and lesson 3's options; rule 19.
20. **2026-10-06 · "The threshold of 'good enough' to 'needs work' is blurry and I am relying on you to set the line."** Lessons were
    being extended or planned one at a time, case by case. Learner: extend only for real gaps (not knowing vs. a lazy, thin answer),
    plan a syllabus ahead (it also saves tokens), and grade like the mastery scheme from school ("did you learn the thing").
    Mastery learning has research support with college students too (Kulik et al. 1990, 108 studies, ≈0.5 SD; self-paced versions
    lowered completion, so keep a fixed pace) and a college form in Nilson's specifications grading (pass/fail at B level). Fix: rule
    20, a `SYLLABUS.md` per major, objectives per lesson.
21. **2026-10-06 · "A lot of these definitions can just be confusing and i think i need to sit and reason though stuff."**
    Statistics lesson 4 stacked the power function, Type I/II error probabilities, size/level and the 2.8-SE rule in one lesson.
    Results were good (all objectives Got it), but the learner felt rushed through definitions. Fix: rule 21.
22. **2026-10-06 · Two catches from the Chapter 1 pretest.** (1) After writing it I printed three of its answers in chat while
    "checking the numbers". Learner: "did you just list the answers to me". Those three items were replaced with book exercises.
    (2) Learner: "are you borrowing questions from the exercises the book has? i think that may also be a good idea." I wasn't.
    Fix: rule 22.
23. **2026-10-07 · "The map question was useless, i just clicked lothal and then clicked the x."** Indian History 0003's
    `map-locate` had `data-choices` with place names on the buttons, so the answer was a label to click, not a place to know.
    Fix: dropped the choices (click the map); rule 23.
24. **2026-10-07 · "Did you expect me to actually read the paper? I just read the article you linked."** I marked down the
    learner's "pooling DNA is bad science" using details from the *Cell* paper. The linked article (The Week) quotes Reich on
    "pooling" data sets without saying they came from one skeleton, so the learner's reading was fair. Fix: regraded 0.6 → 0.75;
    rule 24.
