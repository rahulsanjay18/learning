# Learning wishlist: clusters, library coverage, widgets to build

*Written 2026-10-05 from your list. This file is the persistent record of what you want to learn; update it as things change.*

## TL;DR
- Your 23 subjects fall into **5 clusters**. Topics in the same cluster share widgets, reference material, and often prerequisites.
- **Library:** strong for history, economics, critical theory, literature, military strategy, woodworking and music theory. Weaker where it matters for **math-heavy topics**: most of those textbooks are grade B/C, so equations can't come from them [1]. Those topics will lean on A-grade/open sources and on derivations checked with sympy.
- **Widgets, ordered by how many topics each serves:** progress server → math (render + check answers) → interactive plots → in-browser Python → timeline/map → music notation + ear training → shogi / poker.
- **Woodworking:** yes, I can help a lot (details below), just not with your hands.
- **Suggestion (ADHD-friendly):** keep about **3 topics active** at once. Spaced review grows with every active topic.

---

## 1. Clusters

| Cluster | Subjects | Shared machinery |
|---|---|---|
| **A. Games** | Chess, Go, Shogi, Poker | problem quizzes, engine-checked answers, reviews of your own games |
| **B. Math & physics** | Logic, Statistics, ML/AI, PDEs, Quantum Mechanics, General Relativity | math rendering + answer checking, plots, Python exercises, proofs as ordered steps |
| **C. Engineering** | Motors, Mechanical Engineering, Nuclear Power Plant | same as B + unit-aware answers + small simulators (torque–speed curves, heat flow, reactor kinetics) |
| **D. Humanities & social science** | American History, Indian History, Military Strategy, Critical Theory, Sociology, Economics, Literature, Art history | timelines, maps, source analysis (free response + rubric), categorize/compare, economics graphs |
| **E. Hands-on crafts** | Woodworking, Drawing/Painting, Music Theory | real-world checklists, **photo upload + critique**, music notation + audio, ear training |

**Cross-links worth exploiting:**
- Poker is applied probability → Statistics.
- Statistics → ML.
- PDEs feed QM (Schrödinger), GR (field equations), Mech. Eng. (heat/wave equations) and Nuclear (neutron diffusion).
- Motors + Mech. Eng. → a power plant is turbines, pumps and generators around a reactor.
- Military strategy ↔ American/Indian history ↔ chess/Go strategy.
- Critical theory ↔ literature ↔ sociology ↔ art history.

## 2. What your library covers

Keyword search of `library/MANIFEST.csv` (titles only, so treat it as a first pass). Grade rules: A = teach and quote; B = prose only, **no equations/figures**; C = table of contents only; F = recommend only [1].

| Subject | Best in collection (grade) | Gap |
|---|---|---|
| Statistics | Casella & Berger *Statistical Inference* (A); *Practical Statistics for Data Scientists* (A); Hogg, Bertsekas & Tsitsiklis, Jaynes, *All of Statistics* (B); OpenStax *Introductory Statistics 2e* (B) | fine |
| ML/AI | Huyen *Designing ML Systems* (A); Murphy, Bishop, Russell & Norvig, Shalev-Shwartz (B); ISLR/ESL (C) | the core math texts are B/C, so equations need other sources |
| Logic | Priest VSI (A); several B intros | an A-grade formal logic text |
| PDEs | Zill, intro PDE texts (B) | **no A-grade PDE text** |
| Quantum Mechanics | *Problems and Solutions on QM* and others (B); VSI (A) | **no A-grade text** |
| General Relativity | Susskind *Special Relativity*, Choquet-Bruhat (B); VSI (A) | **no A-grade text** |
| Motors | Wildi *Electrical Machines, Drives and Power Systems* (B) | thin |
| Mech. Eng. | *Mark's Handbook*, FE Mechanical practice (B/C); Atkins thermo VSI (A) | an A-grade core text |
| Nuclear Power | *Nuclear Power* VSI (A) | **thin: no reactor-engineering text** |
| Economics | **OpenStax *Economics / Micro / Macro 3e* (A)**; ~24 VSIs (A) | none |
| American History | ~43 A-grade VSIs | a narrative survey |
| Indian History | ~30 A-grade VSIs (history, Hinduism, philosophy…) | a narrative survey |
| Military Strategy | ~33 A-grade (Clausewitz VSI, warfare VSIs…) | none (topic already active) |
| Critical Theory | Foucault, Habermas, Marx VSIs (A) | primary texts |
| Sociology | OpenStax *Introduction to Sociology 3e* (A); Aron *Main Currents* | none |
| Literature | ~23 A-grade VSIs | the works themselves |
| Art | Loomis *Eye of the Painter* (A); Edwards, Loomis, Kistler (B); Gardner's *Art Through the Ages* | none |
| Music Theory | Levy *Theory of Harmony* (A); Kostka/Payne, Aldwell & Schachter, Piston, Terefenko jazz (B) | equations aren't the issue; the B grade blocks taking **notation examples** from the books |
| Woodworking | Wearing *Essential Woodworker*, Schwarz *Anarchist's Tool Chest*, *Router Table Book* (A); Tage Frid, Flexner *Understanding Wood Finishing* (B) | none |
| Chess | Capablanca, Nimzowitsch, Silman (A/B); 16 books | none (topic already active) |
| Go | Janice Kim *Learn to Play Go* series (A/B) | thin |
| Shogi | 2 books (B/C) | thin |
| Poker | Acevedo *Modern Poker Theory* (B) | thin |

**Two concrete asks:**
1. **Re-convert your key math/physics PDFs** so they reach grade A (`library/RECONVERT.csv` already tracks failed conversions). This matters most for PDEs, QM, GR and ML.
2. For **Nuclear** and **Go/Shogi/Poker**, I'll mostly use web and open sources; RESOURCES.md will flag them as gaps [2].

**Open alternatives for math/physics** (to check against `library/ACCESS.md`): OpenStax *University Physics* [3] and MIT OCW (fine for personal study, but non-commercial [4]).

## 3. Widgets to build, by how many topics each serves

| # | Widget | Serves | Notes |
|---|---|---|---|
| 0 | **Progress server** | all | Cross-cutting; needed for photo uploads and spaced review |
| 1 | **Math**: render with KaTeX [5] + check symbolic answers in the browser (e.g. Compute Engine [6]; sympy on the server as backup) | Stats, ML, Logic, PDE, QM, GR, Motors, ME, Nuclear, Econ (10) | "Is `2x(x+1)` equal to `2x²+2x`?" checked automatically |
| 2 | **Interactive plot with sliders** | Stats, ML, PDE, QM, Econ, Motors, ME, Nuclear (8) | supply/demand, distributions, wave functions, torque–speed curves |
| 3 | **Python in the browser** (Pyodide [7]) | Stats, ML, PDE, QM, Nuclear sims (5) | exercises with hidden tests |
| 4 | **Timeline + map** | Am. & Indian history, military, art history, literature (5) | timeline can extend the existing `order` widget |
| 5 | **Photo upload + critique** | drawing/painting, woodworking (and screenshots of game positions) | needs #0 |
| 6 | **Music**: notation (abcjs [8] or VexFlow [9]) + playback + ear training (intervals/chords, auto-graded) | Music theory | ear training is ideal for spaced repetition |
| 7 | **Truth tables / proof steps** | Logic | proof steps already work with `order`; truth tables are new |
| 8 | **Shogi board** | Shogi | like chess; drops and promotion. Borrow rules from an open-source project |
| 9 | **Poker**: hand/range grid, pot-odds and equity drills | Poker (+ Stats) | |

**Engines for checking answers and reviewing your games** (they run on the server or in a session, not inside widgets):
- Stockfish: chess, already used in `topics/chess/scripts/analyze_game.py`
- KataGo: Go [10]
- YaneuraOu: shogi [11]
- an open-source solver such as TexasSolver: poker [12]

## 4. Woodworking: what I can and can't do
**Can:**
- **Knowledge:** wood movement, grain, joinery choice, sharpening angles, finishing chemistry, shop safety. Your library is strong here.
- **Planning:** cut lists, board-foot math, joinery sequence, jig design, and SketchUp guidance (you have the *Fine Woodworking* SketchUp guide).
- **Practice:** checklists for real sessions ("cut 5 practice dovetails, photograph the baseline").
- **Critique of photos:** gaps in joints, tear-out, finish defects.

**Can't:** feel the cut or spot unsafe body position live. For that: a local class or a community (woodworking forums) is the "wisdom" part of the skill [13].

## 5. Suggested next steps
1. **Pick ~3 active topics.** Chess, military strategy, NASM-CPT and pixel art are already open. Spaced review piles up across every active topic.
2. **Major-style pilot:** two good candidates.
   - **Statistics** (one course): good library coverage, your math background, and it unlocks Poker and ML.
   - **Economics** (a mini-major): A-grade OpenStax texts cover micro and macro end to end.
   - A **physics track** (PDEs → QM → GR) is the most exciting, but it should wait for the math widget and re-converted textbooks.
3. **Widgets:** build #0 (progress server) and #1 (math) next.

---

## Sources
1. `library/README.md` (grade rules) and `library/MANIFEST.csv` (titles, grades; keyword search of titles) in this repo.
2. `CLAUDE.md` (RESOURCES.md gap rules), `library/ACCESS.md`.
3. OpenStax *University Physics Vol. 1*: https://openstax.org/details/books/university-physics-volume-1 ; *Principles of Economics 3e*: https://openstax.org/details/books/principles-economics-3e
4. MIT OCW terms: https://ocw.mit.edu/pages/privacy-and-terms-of-use/ (CC BY-NC-SA 4.0).
5. KaTeX: https://katex.org
6. CortexJS Compute Engine: https://cortexjs.io/compute-engine/
7. Pyodide: https://pyodide.org
8. abcjs: https://www.abcjs.net
9. VexFlow: https://www.vexflow.com
10. KataGo (check: https://github.com/lightvector/KataGo)
11. YaneuraOu (check: https://github.com/yaneurao/YaneuraOu)
12. TexasSolver (check: https://github.com/bupticybee/TexasSolver)
13. `.claude/skills/teach/SKILL.md` L112–120 (wisdom comes from communities).

*(Sources 3, 5–9 were checked reachable on 2026-10-05; GitHub pages 10–12 were blocked from the cloud container, hence "check".)*
