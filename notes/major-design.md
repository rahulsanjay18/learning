# How a major is designed here (adapted from NYU Gallatin's individualized major)

*Written 2026-10-06 at the learner's suggestion. This is a general learning platform: the majors in `programs.json` come first,
and any new subject the learner asks for gets designed the same way. `/program setup <major>` follows this file.*

## TL;DR
**This is assisted textbook reading, not a college.** The learner's words (2026-10-06): "I'm not trying to literally do a college major, I want to learn the things I want to learn." Deviate from any of this whenever it serves that. A major is a good sequence of books, read with Claude's help, with pretests
to skip what's known. That sequence (the **core**) is the only requirement. Everything else below is an **optional extra**:
offered when it would help or when the learner wants it, never a gate, never a credit count. Don't reproduce college
bureaucracy (credit totals, distribution requirements, mandatory exams).

NYU's Gallatin School lets students design their own major [1][2]. Its structure gave the shape; here is what survives, and how lightly:

| Gallatin [1] | What it is there | Here |
|---|---|---|
| **IAPC** (Intellectual Autobiography and Plan for Concentration) | 2–3 page essay: where you're coming from and the plan | `MISSION.md` (why) + a short **Plan** paragraph in `PROGRAM.md`. Claude writes it; the learner just corrects it |
| **Concentration** | a program organized "around a theme, problem, activity, period of history, area of the world or some central idea" [2] | the **core**: the textbook sequence in `curriculum.json`. **The only required part** |
| **Liberal arts + historical/cultural requirements** | humanities 8 cr., social science 8, math/science 4; premodern, early modern, global cultures 4 each | **not copied.** A few optional **breadth** courses (a subject's history or philosophy) sit on the map as electives, for interest only |
| **Electives** | 44–60 credits | **electives** group: chosen by interest once the core is done |
| **Internship / experiential learning** | up to 24 credits | optional **practice**: real data analyses, real games played and reviewed, site visits. Suggested when it fits, never required |
| **Independent study / tutorial / senior project** | ≤ 8 credits; senior project ≈ 40-page paper | optional **capstone** project, if the learner wants one |
| **Colloquium** | final oral exam: a conversation with two faculty about a **List of Works (20–25 works)** spanning "several academic disciplines and historical periods", prepared with a **Rationale** (5–8 pages) [1][3] | optional **end-of-level conversation**: a short list of the works read and a chat about how they fit together. A nice way to consolidate, not an exam |

## Levels
Majors can have levels, like a BS and then graduate coursework (the learner's request, 2026-10-06):
- **Level I** ≈ an undergraduate major's worth of core books.
- **Level II** ≈ graduate textbooks, **as far toward the PhD as self-study can go**. Optional extras there: a quals-style
  self-check, reproducing a published result.
- No hard line between undergraduate and graduate courses: as many courses as the subject needs.
- **Level II is opt-in**, per major (`enrolled_levels` in programs.json; default `["I"]`). Finishing Level I never commits the
  learner to Level II; the tools won't activate a Level II course until it's enrolled.
- **Testing out.** Every course opens with a short pretest (the Statistics chapter-pretest format: concept, calculation, proof or
  the subject's equivalent per section). Pass all of it → the course is `done` with `"credit": "exam"` and no lessons; partial →
  lessons only for what's missing. Expect a lot of this where a major overlaps a degree the learner already has (e.g. the
  probability and analysis in Statistics, from the math degree).

## What every major's PROGRAM.md contains
1. **Plan** (IAPC): 1 page. Starting point (placement results), aims (from MISSION.md), the shape of the program, level by level.
2. **Core courses**: the textbook sequence, each with prerequisites, a spine text (library first; see `library/README.md`) and
   an estimated lesson count. Then a short list of **optional extras** (electives, breadth, practice, capstone, end-of-level talk).
3. **Books needed**: what the library lacks, marked free (author's site) or to buy, so the learner can supply them.

Rule: **prerequisites only ever point at core courses.** No optional extra may block the core path or Level II.

## In curriculum.json
Each course may carry `"level": "I" | "II"` and `"group": "core" | "breadth" | "elective" | "practice" | "independent" |
"capstone" | "colloquium"`. `scripts/test_programs.py` checks the values.

## End-of-level conversation (optional; if the learner wants a rubric)
Score 1–4 on each: **command of the works** (accurate, specific), **connections** (across disciplines and periods), **argument**
(a clear claim about the field, defended), **response** (handles counter-questions), **reflection** (how the plan changed and why).
Pass = no score below 2 and a mean of at least 3. The conversation can be typed in a session; Claude records it as a learning record.

## Sources
1. NYU Bulletins, *Individualized Major (BA)*, Gallatin School of Individualized Study: program requirements (IAPC "two- to three-page
   essay"; liberal arts 20 credits; historical and cultural 12; internship ≤ 24 credits; independent study + tutorial ≤ 8 credits;
   senior project ≈ 40 pages; Colloquium with a "five- to eight-page" Rationale and a List of Works of "20-25 works" representing
   "several academic disciplines and historical periods"). https://bulletins.nyu.edu/undergraduate/individualized-study/programs/individualized-major-ba/
2. Wikipedia, *Gallatin School of Individualized Study*: the concentration is organized "around a theme, problem, activity, period of
   history, area of the world or some central idea". https://en.wikipedia.org/wiki/Gallatin_School_of_Individualized_Study
3. Search summary of gallatin.nyu.edu, *Colloquium*: "an intellectual conversation between the student, the student's primary faculty
   adviser, and one other member of the faculty". https://gallatin.nyu.edu/academics/undergraduate/colloquium.html (the page itself
   refused a direct fetch, HTTP 405).
