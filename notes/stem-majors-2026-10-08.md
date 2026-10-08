# Four STEM majors, plus answers to the side questions (2026-10-08)

*A saved copy of what was built and answered in the 2026-10-08 session. The majors are designed and parked; nothing is scheduled.*

## TL;DR
- **Four majors designed, not started:** Mathematics, Physics, Mechanical Engineering, Unified Engineering. Each one is written
  as if you're starting from high school, and each `DAG.md` marks **where you actually enter**: courses your degrees cover are
  greyed out as credited, "maybe" courses are dotted, and the courses you'd start with have a thick border.
- **Shared courses are one course.** Calculus I has the same number (MA140) in all four majors, and Statics (ES211) is the same
  course in both engineering majors. Finishing a course anywhere counts everywhere. One script builds all four course maps from a
  single list: `scripts/build_majors.py`.
- **Size from your entry points** (Level I core, computed by `build_majors.py --stats`):

| Major | From high school | From your entry | Half subject (1 lesson/wk) | Full (2/wk) | You start with |
|---|---|---|---|---|---|
| Mathematics | 306 lessons | 62 (+18 for the MA412 retake) | ≈ 1.2 yr | ≈ 0.6 yr | MA435 groups, MA429 topology, MA412 PDEs (then MA437) |
| Physics | 404 | 80 (50 without the "maybe" course) | ≈ 1.5 yr | ≈ 0.8 yr | PH361 quantum mechanics I |
| Mechanical Eng. | 528 | 306 | ≈ 5.9 yr | ≈ 2.9 yr | statics, thermodynamics, materials, CAD |
| Unified Eng. | 616 | 360 | ≈ 6.9 yr | ≈ 3.5 yr | Unified I minus circuits (same courses as ME's start) |

  All four together, counting shared courses once: 1102 lessons from high school, 596 from your entry points. Lesson counts are
  estimates until each course's syllabus is written.
- **New rule for every course:** each lesson ends with an optional **Extra practice** section: book problems (numbers changed
  for math-heavy courses), one extra reading, and **one extra article**. For reading-heavy majors it's mostly the article.
- **Practice will use question families** instead of re-asking the same question (proposal below; review-deck code is a to-do).
- **Two new skills:** `/write-lesson` (the full procedure for writing one lesson) and `/write-questions` (question families,
  including textbook problems with new numbers).

## 1. Where you enter, and why
Based on Penn State's current bulletins [1][2]. Your catalog year may differ a little.
- **Math:** every option requires MATH 140, 141, 220, 230, 250, 311W, 312, 414 and 415. You did the Applied option (adds
  403, 412, 436, 455) and took complex analysis (421) and 456, so those are credited except 412 (PDEs), which you're
  retaking (one course, counts in every major). Left in the core: abstract algebra I and
  II (groups, then rings/fields/Galois) and topology.
- **Physics:** computer engineering required PHYS 211, 212 and 214, and you also took modern physics, classical mechanics,
  electrodynamics and thermal physics, so all of those are credited, both E&M courses included (section 5). Quantum mechanics
  is the start. "Maybe": math methods (Boas, now a book you look things up in).
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

## 5. What "E&M II" covers, and why it's credited for you
Griffiths, *Introduction to Electrodynamics* (4th ed.), has twelve chapters [8]: 1 Vector Analysis, 2 Electrostatics,
3 Potentials, 4 Electric Fields in Matter, 5 Magnetostatics, 6 Magnetic Fields in Matter, 7 Electrodynamics, 8 Conservation
Laws, 9 Electromagnetic Waves, 10 Potentials and Fields, 11 Radiation, 12 Electrodynamics and Relativity.
- **E&M I (PH351) = ch. 1–6:** static fields. Charges and currents that don't change in time, in vacuum and in matter.
- **E&M II (PH352) = ch. 7–12:** what happens when fields change in time. Faraday's law and Maxwell's correction give the full
  Maxwell equations (ch. 7). Fields carry energy and momentum: the Poynting vector, the stress tensor (ch. 8). Light as an
  electromagnetic wave: reflection, refraction, waveguides (ch. 9). Retarded potentials and the fields of a moving charge
  (Liénard–Wiechert, ch. 10). How accelerating charges and dipoles radiate (ch. 11). Electromagnetism rewritten in special
  relativity's language: four-vectors and the field tensor (ch. 12).
- **Your course:** intro physics II (PHYS 212) was the calculus-based survey. A 400-level E&M course on Griffiths is a
  different, deeper course. Penn State's current one, PHYS 400, covers statics in vacuum and matter, time-varying fields up to
  Maxwell's equations, conservation laws, waves in vacuum, matter and at boundaries, potentials and fields, and "an
  introduction to radiation" [9]. That's roughly ch. 1–10 plus part of 11, i.e. both courses here, so PH352 is now credited.
- **What might be new:** radiation in depth (ch. 11) and the relativity chapter (ch. 12). Neither blocks anything: the
  general relativity elective (Schutz) starts by re-teaching special relativity, and Jackson (Level II) covers radiation fully.
  If you want to fill the gap, Griffiths ch. 11–12 makes a short optional reading project.
- **Limit:** this uses today's bulletin entry; your year's syllabus may have stopped earlier. You said you don't remember how
  far it went; if ch. 9–10 feel unfamiliar when they come up, we treat them as a look-up, not a course.

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
8. Griffiths, *Introduction to Electrodynamics* 4th ed., contents (Cambridge reprint): https://assets.cambridge.org/97810093/97759/toc/9781009397759_toc.pdf
9. Penn State course descriptions, PHYS 400 Intermediate Electricity and Magnetism: https://bulletins.psu.edu/university-course-descriptions/undergraduate/phys/
