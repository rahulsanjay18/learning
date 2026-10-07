# Staff engineer: senior → staff

*Designed 2026-10-07 with `/program setup` (`notes/major-design.md`). **Parked**: it takes over the AWS ML major's blocks after your
first AWS cert, or sooner if you choose it instead of AWS.*

## TL;DR
- **Why first:** senior → staff is the biggest pay lever on your current path (see `topics/career/PROGRAM.md`), and staff skills are the
  ones cited as least exposed to AI automation.
- **You're closer than most seniors:** you already lead cross-team projects, mentor and set technical direction. Those are three of the
  core staff behaviours. What's missing from your answers is **writing**: design docs, decision records, a written strategy. At staff
  level, writing is how scope becomes visible to the people who decide levels, so it gets the most weight.
- **Shape:** placement → what staff is → writing → system/ML design depth → software design → execution → strategy → evidence and leveling.
  About 45 lessons before placement cuts. The courses after placement can run in parallel.
- **Each lesson** is a short reading, the idea, **one "at work this week" action** (15 minutes or less), and one graded free response
  (a doc section, a design critique, a decision write-up). You also keep a **brag document** from lesson 1.
- **Both routes stay open** (your choice): the same evidence becomes a promotion packet (promotion) or an interview story bank (switching).
- **Books:** 3 of the main books are in your library (*Designing Data-Intensive Applications*, *Designing ML Systems*, *Clean
  Architecture*) and 2 are free online (*Software Engineering at Google*, Larson's staffeng.com guides). **Buy one:** Reilly, *The
  Staff Engineer's Path*. It's the backbone of four courses.

## 1. Plan
**Starting point.** Senior. You already do the work Larson calls the *Tech Lead* archetype (leading a cross-functional initiative) and
some of the *Architect* (owning direction for an area) [2]. Placement (SE000) checks this against a public staff rubric and a timed design
exercise, then shrinks the courses you don't need.

**What staff means here.** Reilly frames the job as three pillars: the big picture (strategy, seeing across teams), execution (making
cross-team projects succeed) and leveling up the people around you [1]. Larson adds four archetypes (Tech Lead, Architect, Solver,
Right Hand) and the practical mechanics: working on what matters, staying aligned with authority, and promotion packets [2]. The program
follows Reilly's order and uses Larson for the mechanics.

**Why writing first.** At Google, design docs are "informal documents of between 3 and 20 pages" that set out a design and its trade-offs
and collect feedback before the code starts [3]. They are the main artifact that lets people outside your team see staff-scope
judgment. Promotion committees and staff interview loops both evaluate that judgment, so you need a few strong examples on file.

**Why the brag document.** Julia Evans's argument: important work is often invisible at review time unless you write it down as it
happens [4]. Each course adds entries, and SE160 turns them into the packet or the story bank.

## 2. Courses (Level I)
| Course | Primary book | Requires | ≈ lessons | Deliverable |
|---|---|---|---|---|
| **SE000 Placement** | public staff rubric + design exercise + evidence inventory | — | 1 | a gap list |
| **SE101 What staff is** | Reilly, Part I (**buy**) + Larson / staffeng.com (free) | SE000 | 4 | your archetype; brag doc started |
| **SE110 Writing: design docs, RFCs, decision records** | *Software Engineering at Google* (free) [3] | SE000 | 6 | one real design doc through review |
| **SE120 System and ML system design at depth** | Kleppmann, *DDIA* (in collection) + Huyen, *Designing ML Systems* (in collection) | SE000 | 12 | three staff-depth written designs (one ML) |
| **SE130 Software design** | Ousterhout, *A Philosophy of Software Design* 2nd ed. [5] (wanted) + *Clean Architecture* (in collection) | SE000 | 5 | a code-review/design standard for your team |
| **SE140 Execution without authority** | Reilly, Part II | SE101 | 6 | kickoff doc + decision log on a real project |
| **SE150 Technical strategy** | Larson, *An Elegant Puzzle* (wanted) + Reilly | SE110, SE140 | 5 | a written technical strategy for your area |
| **SE160 Evidence and leveling** | Larson's promotion-packet guide + Reilly Part III; Voss, *Never Split the Difference* (in collection) for negotiation | SE120, SE150 | 6 | promo packet **and** interview story bank; mock staff loops passed |

**Optional extras:** SE170 Mentoring and raising the bar (you already mentor) · SE390 one staff-scope project run with the course
tools (ongoing practice) · SE399 capstone: the title itself · **Level II** (opt-in): SE401 Principal.

The generated map is `DAG.md`. The Career major's CR150 (interviewing) and CR160 (distributed systems) are covered here, by SE160 and SE120.

## 3. One lesson (~25 minutes)
1. **Warm-up (2 min):** retrieval questions from earlier lessons.
2. **Reading (~10 min):** a slice of the primary book, with a reading guide.
3. **The idea (~8 min):** what staff engineers do differently, with a worked example.
4. **Practice:** one graded free response, e.g. "rewrite this design doc's problem statement", "list the three riskiest assumptions in
   this plan", or "write the decision record for X".
5. **At work this week:** one small action, 15 minutes or less (e.g. "add a non-goals section to your current project's doc", "ask
   your manager what staff evidence they'd want to see"). Optional, like all homework here, and every lesson works without it.

## 4. Books needed
| Book | For | Status |
|---|---|---|
| Reilly, *The Staff Engineer's Path* (O'Reilly, 2022) [1] | SE101, SE140, SE150, SE160 | **buy**: the backbone |
| Ousterhout, *A Philosophy of Software Design* 2nd ed. (2021) [5] | SE130 | wanted (short; the 2nd edition's new material is a free download) |
| Larson, *An Elegant Puzzle* (2019) | SE150 | wanted |
| Xu, *System Design Interview* vol. 1–2; Aminian & Xu, *ML System Design Interview* | SE120, SE160 | wanted (interview route) |
| Rumelt, *Good Strategy/Bad Strategy*; Skelton & Pais, *Team Topologies* | SE150 | nice to have |
| Free: *Software Engineering at Google* [3], staffeng.com [2], Evans's brag-document post [4] | | |
| In collection: Kleppmann *DDIA* (A), Huyen *Designing ML Systems* (A), Martin *Clean Architecture* (A), Voss *Never Split the Difference* (A), Brooks *Mythical Man-Month* (B), Takada *Distributed Systems for Fun and Profit* (A) | | |

## Sources
1. O'Reilly, *The Staff Engineer's Path* (Reilly, 2022): Parts I The Big Picture, II Execution, III Leveling Up. https://www.oreilly.com/library/view/the-staff-engineers-path/9781098118723/
2. Larson, *Staff Engineer: Leadership beyond the management track* (archetypes Tech Lead, Architect, Solver, Right Hand; guides
   "Work on what matters", "Stay aligned with authority", "Promotion packets"). https://staffeng.com/book ; https://staffeng.com/guides/
3. Winters, Manshreck & Wright, *Software Engineering at Google* (free HTML). https://abseil.io/resources/swe-book ; design-doc
   description via Simon Willison, *Design docs at Google*. https://simonwillison.net/2020/Aug/7/design-docs-google
4. Julia Evans, *Get your work recognized: write a brag document*. https://jvns.ca/blog/brag-documents/
5. *A Philosophy of Software Design*, 2nd ed. (Ousterhout, Yaknyam Press 2021). https://www.i-programmer.info/book-watch-archive/14822-a-philosophy-of-software-design-2nd-ed-yaknyam-press-.html
6. Pay figures and "AI-resistant skills": `topics/career/PROGRAM.md` sources 17, 18 and 20.
7. Library grades and ids: `library/MANIFEST.csv`.
