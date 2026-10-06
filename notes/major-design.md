# How a major is designed here (adapted from NYU Gallatin's individualized major)

*Written 2026-10-06 at the learner's suggestion. This is a general learning platform: the majors in `programs.json` come first,
and any new subject the learner asks for gets designed the same way. `/program setup <major>` follows this file.*

## TL;DR
NYU's Gallatin School lets students design their own major [1][2]. Its structure has seven parts, and each maps onto this platform:

| Gallatin [1] | What it is there | Here |
|---|---|---|
| **IAPC** (Intellectual Autobiography and Plan for Concentration) | 2–3 page essay: where you're coming from and the plan; adviser-approved, due at the midpoint | `MISSION.md` (why) + the **Plan** section of `PROGRAM.md` (what and in what order). Revisited at each level's midpoint |
| **Concentration** | a program organized "around a theme, problem, activity, period of history, area of the world or some central idea" [2] | the major's **core sequence** in `curriculum.json` |
| **Liberal arts + historical/cultural requirements** | humanities 8 cr., social science 8, math/science 4; premodern, early modern, global cultures 4 each | **breadth requirements** inside each major: courses that look at the subject from outside (its history, philosophy, other cultures, a neighbouring discipline) |
| **Electives** | 44–60 credits | **electives** group: chosen by interest once the core is done |
| **Internship / experiential learning** | up to 24 credits | **practice**: real data analyses, real games played and reviewed, museum or site visits, a project that leaves the platform |
| **Independent study / tutorial / senior project** | ≤ 8 credits; senior project ≈ 40-page paper | **independent study** (a reading contract: list + questions + one write-up) and a **capstone** (a substantial project or paper) |
| **Colloquium** | final oral exam: a conversation with two faculty about a **List of Works (20–25 works)** spanning "several academic disciplines and historical periods", prepared with a **Rationale** (5–8 pages) [1][3] | **Colloquium** at the end of each level: the learner builds a 20–25 work list, writes a rationale (here 1,500–2,500 words), then a 60-minute conversation with Claude, graded on a rubric |

## Levels
Majors can have levels, like a BS and then graduate coursework (the learner's request, 2026-10-06):
- **Level I** ≈ an undergraduate major. Ends with the level I capstone and colloquium.
- **Level II** ≈ master's and PhD coursework, **as far toward the PhD as self-study can go**: qualifying-exam-level courses, a
  written "quals" check, a research practicum (reproduce and extend a published result). The dissertation itself is out of scope.
- No hard line between undergraduate and graduate courses: as many courses as the subject needs.

## What every major's PROGRAM.md contains
1. **Plan** (IAPC): 1 page. Starting point (placement results), aims (from MISSION.md), the shape of the program, level by level.
2. **Courses** by group: `core`, `breadth`, `elective`, `practice`, `independent`, `capstone`, `colloquium`. Each with prerequisites,
   a spine text (library first; see `library/README.md`) and an estimated lesson count.
3. **List of Works** in progress: works get added as courses use them; the learner prunes it to 20–25 before the colloquium.
4. **Books needed**: what the library lacks, marked free (author's site) or to buy, so the learner can supply them.

## In curriculum.json
Each course may carry `"level": "I" | "II"` and `"group": "core" | "breadth" | "elective" | "practice" | "independent" |
"capstone" | "colloquium"`. `scripts/test_programs.py` checks the values.

## Colloquium rubric (for Claude, at the end of a level)
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
