# Syllabus standard (every course and every major, new ones included)

*Set 2026-10-08 at the learner's request: "a typical college style syllabus for all current courses … something you'd give to me if you
were actually my prof … make this standard for all new courses/majors going forward", plus "a master syllabus or course plan for each
major".*

## What exists, and where
| Document | File | Who writes it | What it is |
|---|---|---|---|
| **Program of study** (master plan) | `topics/<major>/syllabi/PLAN.md` → rendered into `syllabi/index.html` | Claude, when the major is designed | The whole major on one page: aims, structure, the default path term by term, requirements, books needed |
| **Course syllabus** | `topics/<major>/syllabi/<COURSE>.md` → `<COURSE>.html` | Claude, when the course is added to `curriculum.json` | The handout for one course: description, objectives, texts, weekly schedule, assessment |
| Lesson-level plan | `topics/<major>/SYLLABUS.md` | Claude, when a course starts | Reading + 2–3 objectives per lesson for the active course (unchanged; the course syllabus's schedule must agree with it) |
| Policies | `notes/course-policies.md` | shared | Meetings, late work, grading scale, honesty, accommodations. Linked from every syllabus, never copied |

**Rule:** every course in a `curriculum.json` has a syllabus, and every major has a `PLAN.md`. `python3 scripts/render_syllabi.py --check`
(run by `scripts/check_all.sh`) fails otherwise, and fails if a rendered page is stale. After editing a syllabus or `curriculum.json`,
run `python3 scripts/render_syllabi.py`.

## What the renderer fills in (never write these by hand)
Title, major, level and group, status and lessons done, instructor and office hours, meeting days (`programs.json` → `week`, or
the Engineering lane), length (`est_lessons`, or `lessons:` in the front matter), prerequisites (linked), projected dates (core
Level I path only, computed from lesson counts and weekly blocks), and the policies link.

## Course syllabus template
```
---
course: S202
updated: 2026-10-08
lessons: 6            (optional: overrides est_lessons)
---
## Course description
One catalog paragraph: what the course covers, why it is in this major, where it leads. Then one line "Placement:" saying how the
pretest works for this course (or that there is none).

## Learning objectives
By the end of the course you can:
1. Verb-first, checkable objectives (5–8). Each one is what a check question tests.

## Texts
- **Required:** the primary book, edition, and the exact chapters used (library id when in the collection).
- **Recommended:** secondary books, each with the gap it fills.
- **Optional:** tertiary background.
- **Not used:** considered and rejected, with the reason (so it isn't re-litigated).
Mark books not yet in the library "(to acquire)"; they also go on the major's books-needed list.

## Schedule
| Week | Topic | Reading | Due |
|---|---|---|---|
One row per week at this major's pace (Statistics 2 lessons/week, Indian History 1, Games 1 per course, Engineering 1 per lane).
"Due" names the graded item (proof task, rep, essay, check). Weeks are relative; the header carries projected dates.

## Assessment
| Component | Weight | What it is |
|---|---|---|
Weights add to 100%. They describe what the course grade is made of; nothing is a gate except mastery (notes/course-policies.md).

## Notes (optional)
Anything course-specific: notation traps, how the course connects to other majors, deliverables, exam logistics.
```

**Readings must be real:** chapter and section titles from the book's own contents page (book server `toc` / `read`, or the
publisher's page for books not yet in the library), not from memory. If a contents page couldn't be checked, the syllabus says so.

## Program of study (PLAN.md) template
```
---
major: statistics
updated: 2026-10-08
---
## The program in one paragraph
## Aims (what you can do when you finish Level I, and Level II)
## Structure (core vs. optional extras; levels; how pretests and credit by exam work here)
## Default path (term by term: Fall 2026, Spring 2027, …; core first, extras where they fit)
## Requirements to finish Level I / Level II
## Books needed (to acquire, by when)
```
The renderer appends the computed term table and the course catalog under it.

## For a new major or course
1. Design it per `notes/major-design.md` (DAG of books in `curriculum.json`).
2. Write `syllabi/PLAN.md` (new major) and one `syllabi/<COURSE>.md` per course, from the template above.
3. `python3 scripts/render_syllabi.py <major>`, then `bash scripts/check_all.sh --quick`.
4. Link the program page from `index.html` (one line under the topic).
