# Four STEM majors, plus answers to the side questions (2026-10-08)

*A saved copy of what was built and answered in the 2026-10-08 session. The majors are designed and parked; nothing is scheduled.*

## TL;DR
- **Four majors designed, not started:** Mathematics, Physics, Mechanical Engineering, Unified Engineering. Each one is written
  as if you're starting from high school, and each `DAG.md` marks **where you actually enter**: courses your degrees cover are
  greyed out as credited, "maybe" courses are dotted, and the courses you'd start with have a thick border.
- **Shared courses are one course.** Calculus I has the same number (MA140) in all four majors, and Statics (ES211) is the same
  course in both engineering majors. Finishing a course anywhere counts everywhere. One script builds all four course maps from a
  single list: `scripts/build_stem_majors.py`.
- **Size from your entry points** (Level I core, computed by `build_stem_majors.py --stats`):

| Major | From high school | From your entry | Half subject (1 lesson/wk) | Full (2/wk) | You start with |
|---|---|---|---|---|---|
| Mathematics | 306 lessons | 106 | ≈ 2.0 yr | ≈ 1.0 yr | MA437 rings/fields/Galois, MA429 topology |
| Physics | 404 | 214 | ≈ 4.1 yr | ≈ 2.1 yr | PH237 modern physics, PH341 classical mechanics |
| Mechanical Eng. | 528 | 306 | ≈ 5.9 yr | ≈ 2.9 yr | statics, thermodynamics, materials, CAD |
| Unified Eng. | 616 | 360 | ≈ 6.9 yr | ≈ 3.5 yr | Unified I minus circuits (same courses as ME's start) |

  All four together, counting shared courses once: 1102 lessons from high school, 792 from your entry points. Lesson counts are
  estimates until each course's syllabus is written.
- **New rule for every course:** each lesson ends with an optional **Extra practice** section: book problems (numbers changed
  for math-heavy courses), one extra reading, and **one extra article**. For reading-heavy majors it's mostly the article.
- **Practice will use question families** instead of re-asking the same question (proposal below; review-deck code is a to-do).
- **Two new skills:** `/write-lesson` (the full procedure for writing one lesson) and `/write-questions` (question families,
  including textbook problems with new numbers).

## 1. Where you enter, and why
Based on Penn State's current bulletins [1][2]. Your catalog year may differ a little.
- **Math:** every math option requires MATH 140, 141, 220, 230, 250, 311W, 312, 414 and 415, so those are credited, plus 421
  (you took complex analysis). Which other courses you took depends on the option, so 403, 435, 436, 412 and 455 are "maybe".
  **Tell me your option** and I'll update them.
- **Physics:** computer engineering required PHYS 211, 212 and 214. PHYS 213 (fluids and thermal physics) was not required, so
  it's "maybe", along with math methods (Boas), which becomes a book you look things up in rather than a course.
- **Mechanical / Unified:** computer engineering had no engineering-mechanics course, so Statics is where new material starts.
  Circuits (EE 210), signals and systems (EE 353) and the digital courses are credited.

## 2. Would books on pedagogy help? Yes, two of yours in particular
Your library has a Pedagogy shelf, and two books on it fit this platform directly:
- **Felder & Brent, *Teaching and Learning STEM: A Practical Guide*** (grade A, `40d76146c5`). Written for people teaching STEM
  courses: learning objectives, problem-based teaching, assignments and tests. Its core advice is to "formulate learning
  objectives" as the first step in teaching problem-solving, and to share them with students as study guides [3]. The
  platform's syllabi and "you can…" objectives already work this way, so the book is the best check of how well they do it,
  especially for the three new STEM majors.
- **Brown, Roediger & McDaniel, *Make It Stick*** (grade A, `cb24c0244c`). The research on retrieval, spacing, interleaving and
  varied practice, in plain language. Chapter 3, "Mix Up Your Practice", is the basis for the practice fix below [4].
- **Lower value for this purpose (my judgment):** *Ultralearning*, *Unlimited Memory* and *Mindshift* are about self-study habits,
  not course design. *Peak* (Ericsson) is relevant to deliberate practice in games. Eggen & Kauchak, *Using Educational Psychology
  in Teaching*, is a full textbook: useful to look things up in, but too broad to read through.
- **Where it pays off:** reading Felder & Brent's chapters on objectives and on designing assignments, then revising
  `notes/syllabus-standard.md` and the two new skills to match. I'd do it as a short reading project, not a whole major.
  The platform's spacing and interleaving rules already rest on the primary research (`notes/evidence-spacing-and-variety.md`).

## 3. Making practice better than "re-ask the same question"
Full proposal: `notes/practice-variants.md`. Short version:
- **The problem:** a missed question returns word for word, so by the third time you can answer it from memory of that question.
- **Evidence:** testing helps transfer to new questions on the same material, not only to the question practiced (Butler 2010,
  replicated) [5]. *Make It Stick* summarizes the field: "Practice that's spaced out, interleaved with other learning, and varied
  produces better mastery, longer retention, and more versatility" [4]. **Limit:** neither source compares same-question practice
  directly against different-question practice, and one Pan & Rickard study found little transfer between closely related items.
  So we try it and measure it on your own results.
- **The fix:** each objective gets a family of 3–5 questions: the same problem with new numbers, a different format (choice →
  typed answer), the problem in reverse, an application to a new situation, and a near-miss that differs only in the detail
  people confuse. A miss brings back a sibling question, not the same one. For math-heavy courses, textbook exercises with the
  numbers changed are the default source (your suggestion). Answers are recomputed in code, and the library's grade rules still
  apply: on grade-B books, a problem's wording can be reused, but any formula is derived and checked in code (never copied
  from the converted text), or the lesson just cites the exercise number for you to read in your own copy.
- **Status:** the naming convention for question families is in place now. Making the review deck pick a sibling is a code
  change (lp.js, review.html, quiz.py, server), listed in HANDOFF.

## 4. Separate skills for lessons and for questions? Yes
The rules for writing a lesson, and especially for writing questions, are spread across about six files and roughly 20 numbered
teaching rules. A skill turns them into one checklist that every session follows the same way. **The condition:** each skill
points to those files instead of copying them, so there's only one copy of each rule. Both skills were built by subagents:
- `/write-lesson`: 14 steps from `git pull` to the Pages URL. It calls `/write-questions` for every objective and the
  `lesson-reviewer` agent before committing. It runs in the main conversation, not a separate subagent, because it needs your
  recent answers and complaints.
- `/write-questions`: question families in the lesson Markdown syntax, every numeric answer computed in code, checked against the
  question rules.

## Sources
1. Penn State Bulletin, *Mathematics, B.S.*: https://bulletins.psu.edu/undergraduate/colleges/eberly-science/mathematics-bs/
2. Penn State Bulletin, *Computer Engineering, B.S.*: https://bulletins.psu.edu/undergraduate/colleges/engineering/computer-engineering-bs/
3. Felder & Brent, *Teaching and Learning STEM: A Practical Guide* (Jossey-Bass, 2016), "Ideas to Take Away" in the chapter on
   problem-solving skills, and the section on formulating learning objectives (in your library, `40d76146c5`).
4. Brown, Roediger & McDaniel, *Make It Stick: The Science of Successful Learning* (Harvard, 2014), ch. 3 "Mix Up Your Practice"
   (in your library, `cb24c0244c`). Popular synthesis; points to the primary studies.
5. Butler (2010), *JEP: Learning, Memory, and Cognition* 36(5):1118–1133:
   https://profiles.wustl.edu/en/publications/repeated-testing-produces-superior-transfer-of-learning-relative-/ ; replication record:
   https://forrt.org/flora-replication-atlas/doi/10.1037/a0019902/
6. Pan & Rickard (2018), *Psychological Bulletin* 144(7):710–756, doi:10.1037/bul0000151 (moderator tables not read).
7. MIT Unified Engineering: https://www.ocw.mit.edu/courses/16-001-unified-engineering-materials-and-structures-fall-2021/pages/syllabus ;
   https://firstyear.mit.edu/wp-content/uploads/2025/02/Course-16-2025.pdf
