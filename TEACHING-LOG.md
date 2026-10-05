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
13. **Homework is allowed but optional.** Keep it small and specific (one exercise, one game to play, one short write-up), mark it
    clearly as optional, and **design every lesson so it still works if the homework was skipped** (the learner isn't sure how
    much they'll do). Never make a later lesson depend on homework; if it builds on homework, include a 2-minute recap. Track what
    gets done in the topic's NOTES.md and adjust the amount to what actually happens. (Entry 13)
10. **Verify every fact and number** against a source or with code before publishing (already standard; keep doing it).
12. **Reading guides as note-taking:** for assigned readings, put 3 guide questions + "what surprised or confused you" as `free`
    boxes at the top of the lesson. They're the learner's notes, they reach the teacher with the results, and every answer gets a reply.
14. **Check paraphrases against the source sentence**, not memory of it: reread the passage before compressing it. (Entry 14)
11. **Remind the learner that formula boxes take expressions** (`8/28`, `160*0.05/(...)`), so arithmetic slips don't cost a question. (Entry 9)

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
