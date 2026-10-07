# C and C++: the major

*Designed 2026-10-07 with `/program setup` (`notes/major-design.md`). **Parked**: ready to start whenever you say; nothing is scheduled.*

## TL;DR
- **Shape:** placement pretest → **C, properly** → **C and the machine** (CS:APP) and **Core C++** in parallel →
  **Effective modern C++** and **the standard library / generics** → **concurrency**. That's Level I's core: 7 courses, about 65 lessons
  before the pretest cuts what you already know.
- **Branches after the core** (optional, by interest): Linux systems programming, CUDA, game-engine programming, and a running
  project (the engine for your 3D chess variant).
- **Level II (opt-in):** templates and metaprogramming, software design, performance engineering, then optional ML-systems reading and an
  open-source contribution.
- **Your library already has most of it:** 7 of the 9 Level I spine books are in your collection. **Buy two** before CP204 and the
  systems elective: *C++ Concurrency in Action* 2nd ed. and *The Linux Programming Interface*. (Full list below.)
- **Time:** at half weight (2 blocks a week) Level I core is roughly 7–8 months; at full weight (AWS's slot) roughly 4. Expect the
  placement test to take 20–30% off, since you already know syntax, architecture and OS.

## 1. Plan
**Starting point.** You know syntax basics, computer architecture and operating systems, but "aren't great with the language".
That usually means the gaps are in the parts the languages *specify* rather than the parts the hardware does: undefined behavior,
object lifetimes, the declaration and type system, the toolchain (preprocessor, linking), and, in C++, value semantics, RAII, move
semantics, templates and the memory model. The placement pretest checks exactly those.

**Why C first** (your choice at setup, and the usual advice): C++ inherits C's object model, pointers, arrays and undefined behavior.
Learning them in C, where nothing hides them, makes C++'s abstractions (smart pointers, containers, RAII) read as *solutions* to
problems you've already had. CS:APP then shows what that C becomes on the machine, which is where performance work starts.

**Why these books.** Each course is a block of one primary book (`notes/major-design.md`):
- *Modern C* (Gustedt) [1] teaches today's standard C rather than 1978 K&R C, written by a member of the ISO C committee. Your copy is the free
  2018 draft (C17, grade B). The 3rd edition (Manning, 2025) covers C23 [1].
- *Computer Systems: A Programmer's Perspective* (Bryant & O'Hallaron) is the standard "C on the machine" text (data representation, x86-64,
  optimization, caches, linking, virtual memory).
- *C++ Primer* 5th ed. (C++11, grade A in your library) is thorough and has exercises. Its gap is C++14–20, filled by *A Tour of C++* 3rd ed.
  (Stroustrup, 2022: concepts, ranges, modules) [2].
- *Effective Modern C++* (Meyers) is 42 items of "how to use C++11/14 well", the bridge from knowing the language to writing it idiomatically.
- *The C++ Standard Library* 2nd ed. (Josuttis) for the STL, with *C++ Primer* Ch. 16 for templates.
- *C++ Concurrency in Action* 2nd ed. (Williams, C++17) [3] is the standard book on threads, the memory model and atomics.

## 2. Courses

### Level I core (the major)
| Course | Primary book (library grade) | Requires | ≈ lessons |
|---|---|---|---|
| **CP000 Placement** | pretest across CP101–CP204 | — | 1 |
| **CP101 C, properly** | *Modern C*, Levels 1–2 + selected Level 3 (B) | CP000 | 10 |
| **CP120 C and the machine** | CS:APP 3rd ed. Ch. 2, 3, 5, 6, 7, 9 (B) | CP101 | 10 |
| **CP201 Core C++** | *C++ Primer* 5th ed., Parts I–III selected (A) + *Tour* 3rd ed. (wanted) | CP101 | 14 |
| **CP202 Effective modern C++** | *Effective Modern C++*, all 42 items (A); *Effective C++* 3rd ed. as backup (A) | CP201 | 12 |
| **CP203 Generic programming and the library** | Josuttis, *The C++ Standard Library* 2nd ed. (B) + *Primer* Ch. 16 | CP201 | 10 |
| **CP204 Concurrency** | *C++ Concurrency in Action* 2nd ed. (**to buy**); OSTEP concurrency (B) | CP202, CP120 | 10 |

CP120 and CP201 both need only CP101, so they can run side by side if you want variety.

### Optional extras (Level I)
| Course | Book | Requires | Ties to |
|---|---|---|---|
| CP310 Linux systems programming (elective) | *The Linux Programming Interface* (Kerrisk) [4] (**to buy**) | CP120 | systems |
| CP320 GPU programming with CUDA (elective) | *Programming Massively Parallel Processors* 4th ed. (A, in collection) | CP201, CP120 | ML / perf |
| CP330 Game engine programming (elective) | *Game Engine Architecture* 3rd ed. (Gregory) [5] (to buy); *Game Coding Complete* 4th ed. (B) | CP202 | Games major |
| CP390 Project: engine for the 3D chess variant (practice) | your own code; board representation → move generation + perft tests → search → threads | CP202 | Games major |

### Level II (opt-in, `enrolled_levels`)
| Course | Primary book | Requires |
|---|---|---|
| CP401 Templates and metaprogramming | *C++ Templates: The Complete Guide* 2nd ed. (2017) [6] (wanted; your copy is the 2002 1st ed.) | CP203 |
| CP402 Software design in C++ | Iglberger, *C++ Software Design* (2022) [7] (wanted); *Design Patterns* (A); Feathers, *Legacy Code* (B) | CP202 |
| CP403 Performance engineering | Drepper, *What Every Programmer Should Know About Memory* (free) [8]; Agner Fog's optimization manuals (free) [9] | CP120, CP204 |
| CP490 Reading real C++ ML systems (practice) | a PyTorch C++/CUDA extension; ggml / llama.cpp source | CP403 |
| CP499 Capstone (optional) | one merged pull request to a C/C++ project you use | CP402 |

The generated picture is `DAG.md`.

## 3. One lesson (a ~25-minute block)
1. **Warm-up (2 min):** retrieval questions from earlier lessons (they also go into the daily review).
2. **Reading (~10 min):** a short slice of the primary book with a reading guide (three things to look for).
3. **Lesson page (~8 min):** the idea, one small program that shows it, and *why* the language works that way.
4. **Practice:** three kinds, every lesson:
   - **Predict:** "what does this print?" or "is this undefined behavior?" (auto-checked quizzes).
   - **Fix:** a short buggy program; name the bug (often caught by a sanitizer).
   - **Write:** one small function as a free response, graded against a rubric (`scripts/grade.py`).
5. **Optional homework:** one exercise from the primary book, cited by number.

**Toolchain from lesson 1, not as a separate course.** Every program is built with `-Wall -Wextra -g -fsanitize=address,undefined`, and
gdb, make/CMake and unit tests come in as they're needed. When you're away from a computer, a Compiler Explorer (godbolt.org) link does the job.

**Library rule that shapes these lessons.** Grade-B books (*Modern C*, CS:APP, Josuttis, K&R) are prose only (`library/README.md`): lessons
cite their sections and exercises but never copy their code. Every code sample is written fresh and compiled before it goes in a lesson.

## 4. Placement (CP000)
One pretest, ~30 minutes, three items per Level I core course (predict / fix / write). Result per course: pass everything → `done`
with `credit: exam`; partial → that course's `plan` keeps only the missing sections. Expect CP120 to shrink most (you know architecture).

## 5. Books needed
| Book | For | Status |
|---|---|---|
| Williams, *C++ Concurrency in Action* 2nd ed. (Manning, 2019) [3] | CP204 primary | **buy** (needed for Level I core) |
| Kerrisk, *The Linux Programming Interface* (No Starch, 2010) [4] | CP310 | buy if you take the systems elective |
| Stroustrup, *A Tour of C++* 3rd ed. (2022) [2] | CP201/CP203: C++20 | nice to have (cppreference.com fills in without it) |
| Seacord, *Effective C* 2nd ed. (No Starch, 2024, C23) [10] | CP101 | nice to have; would become CP101's primary |
| Gustedt, *Modern C* 3rd ed. (Manning, 2025, C23) [1] | CP101 | nice to have (your 2018 draft works) |
| Gregory, *Game Engine Architecture* 3rd ed. (2018) [5] | CP330 | only for that elective |
| *C++ Templates* 2nd ed. [6], Iglberger *C++ Software Design* [7] | Level II | only if you enroll in Level II |
| Drepper [8], Agner Fog [9] | CP403 | free downloads |

## Sources
1. Manning, *Modern C, Third Edition* (Gustedt, 2025; C23). https://manning.com/books/modern-c-third-edition. Your copy's own front matter
   (book id 030e99498b) says "the version of this book on Feb 13, 2018", CC BY-NC-ND.
2. Pearson, *A Tour of C++*, 3rd ed. (Stroustrup, 2022; C++20: modules, concepts, coroutines, ranges). https://www.pearson.com/store/en-us/p/tour-of-c-a/P200000002116/9780136816485
3. Manning, *C++ Concurrency in Action, Second Edition* (Williams, 2019; C++17). https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition
4. man7.org, *The Linux Programming Interface* (Kerrisk, No Starch 2010). https://www.man7.org/tlpi
5. *Game Engine Architecture*, 3rd ed. (Gregory, CRC Press 2018; ISBN 9781138035454). https://abebooks.fr/9781138035454/Game-Engine-Architecture-Gregory-Jason-1138035459/plp
6. Pearson, *C++ Templates: The Complete Guide*, 2nd ed. (Vandevoorde, Josuttis, Gregor, 2017; C++11/14/17). https://www.pearson.com/en-us/subject-catalog/p/c-templates-the-complete-guide/P200000000663/9780134778747
7. O'Reilly, *C++ Software Design* (Iglberger, 2022). https://www.oreilly.com/library/view/-/9781098113155/
8. LWN, Drepper, *What every programmer should know about memory* (full PDF). https://lwn.net/Articles/259710/
9. isocpp.org, *C++ Optimization Manuals: Agner Fog*. https://isocpp.org/blog/2012/12/agners-cpp-optimization-manuals
10. O'Reilly, *Effective C, 2nd Edition* (Seacord, No Starch 2024; C23). https://oreilly.com/library/view/effective-c-2nd/9781098182496
11. Pearson, *Programming: Principles and Practice Using C++*, 3rd ed. (2024; C++20/23), for reference: your copy is the 2nd ed. https://stroustrup.com/PPP3.html
12. Library grades and ids: `library/MANIFEST.csv`; edition checks from each book's first lines on the book server (2026-10-07).
