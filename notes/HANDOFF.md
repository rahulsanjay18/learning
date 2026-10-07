# Handoff: state of everything (2026-10-05, end of the first long thread)

New threads: read `CLAUDE.md`, then `TEACHING-LOG.md`, then the topic's folder. This file is the to-do list across topics.

## Learner's next actions
- **2026-10-06: syllabi + mastery grading.** Each major has `topics/<major>/SYLLABUS.md` (readings + objectives per lesson for the
  active courses); `plan` in curriculum.json mirrors it. Grade objectives Got it / Not yet (TEACHING-LOG rule 20; explainer
  `notes/mastery-grading.md`). Write lessons from the syllabus; don't redesign per session.
- (2026-10-06) Statistics **lesson 4** (power; reading C&B §8.3.1 pp. 382–385) still not done. Indian History **lesson 0003** (Indus
  cities; reading K&R Ch. 1 Indus sections) built today. Both have reading-guide boxes: reply to those answers when results come in.
- 2026-10-06: all 5 pending free responses graded and posted (stats ice-cream causal 0.75; IH 0002 answers).
- Daily review deck: `assets/review.html`.
- Progress server is **live** (deployed 2026-10-05; `/progress/health` → ok). Desktop + laptop share one device token (id 1, "desktop+laptop").

## Platform ideas (not urgent; learner deploys on their server)
- Small local model to offload easy work: `notes/slm-offload-plan.md` (semantic book search first, then first-pass grading with
  escalation after a ≥90% agreement test). Hardware known (32 GB RAM, 1× 5070 Ti 16 GB): enough; no second GPU yet. Waiting on: which other services use the GPU.
- AWS: target MLA-C02 (GA 2027-01-14). Learner's course = a 2024 Solutions Architect (Associate) course: use its core-AWS modules
  (IAM, S3, VPC, EC2, Lambda, CloudWatch) as the foundations course, then MLA-C02 prep from AWS's exam guide. Waiting on: the course
  files (learner will send) and a target date.

## Open teaching work
| Topic | Next | Notes |
|---|---|---|
| Statistics | **Program: all of Casella & Berger with proofs; chapter pretest (concept/calc/proof per section) before each chapter** (`topics/statistics/PROGRAM.md`). Lesson 3 done (record 0007); **lesson 4 (power, §8.3.1) built**, learner does it next. Then lesson 5: P(data given H1), likelihood ratios, power (~55% in the A/B example) | Numbers in `topics/statistics/QUESTIONS.md` |
| Indian History | Lesson 0002 done (record 0002). **0003 "The Indus cities" built 2026-10-06** (Wheeler's "Indra stands accused" vs Dales 1964 + Rakhigarhi 2019 genome; claim box on the headline "DNA study debunks Aryan invasion theory"). Rest of the Introduction became an optional skim on 0003. Next: 0004 Indo-Aryans and the Vedic age (Rigveda hymn as first text source) | `topics/indian-history/PROGRAM.md` |
| Games (fun major) | **Mission: design a balanced 3D strategy game** (MISSION.md). Chess is class G101 (continue `topics/chess/`, lessons 0001–0002 done: 9/10, 8/9; game 2 won as Black (LR 0005); next 0003 "what did their move do?"); program decided: chess → tiny games → xiangqi → shogi → Go → chance (Pig + backgammon unit) → poker → theory/AI | Chess.com: rahulsanjay18 |
| AWS ML cert | Ask: which exam, target date, AWS experience, prep materials | Check AWS's current exam list (don't guess names) |
| Military strategy | **Merged into Games** as G150 (lessons in `topics/military-strategy/`), feeding G350 Wargames and G360 Diplomacy | framed as "war as a game" (see its NOTES) |
| C and C++ | **Designed 2026-10-07, parked** (`topics/cpp/PROGRAM.md`, `DAG.md`). C first (Modern C → CS:APP) then C++ (Primer → Effective Modern C++ → STL → concurrency); electives systems / CUDA / game engine / 3D-chess engine project. Learner may start it after AWS ML or instead of it. Start = CP000 placement pretest | Buy *C++ Concurrency in Action* 2e before CP204 |
| Economics | Parked; Principles solid (13/13) | Resume at intermediate level |
| NASM-CPT | Started earlier (`topics/nasm-cpt/`); exam date unknown | Deadline-driven: ask for the date |

## Open platform work
- **Skills added 2026-10-06:** `/quiz-me` (`scripts/quiz.py`), `/game-review`, `/new-books` (`scripts/new_books.py`, `library/ADDING-BOOKS.md`); SessionStart hook installs test deps + stockfish + python-chess.
- **New books reviewed 2026-10-06** (`notes/new-books-2026-10-06.md`; partial, because the server went down during the scan).
  Use Schelling *Arms and Influence* (4bdcba34b3), Paret *Makers of Modern Strategy* (6979109f6e) and Perla *Art of Wargaming* (eb72110b76) in G150/G350; McMahon *ML Engineering with Python* (7d3ec3450a) for AWS ML; British Empire
  and Decolonization VSIs for IH204/205. WANTED.md reorganized by major. **Learner: restart/redeploy book-server** (502 since the scan);
  new `GET /catalog` + `python3 scripts/books.py new` lists unmanifested books in one call. Rerun it then, and add the new books to MANIFEST.csv.
- **Built 2026-10-06:** lesson renderer (Markdown → HTML), grading packets (`scripts/grade.py`), results recorder
  (`scripts/lp_results.py`), compact book client (`scripts/books.py`), `scripts/check_all.sh`; quiz types estimate / find-error /
  highlight; simulation plugin (CI coverage, CLT, multiple testing); majors redesigned on NYU Gallatin (`notes/major-design.md`),
  Statistics split into Level I and opt-in Level II. **5 free responses are waiting to be graded** (`python3 scripts/grade.py`).
- **Learner to do:** redeploy book-server and progress-server (`git pull`, `docker compose up -d --build book-server progress-server`);
  download the free books listed in `topics/statistics/PROGRAM.md` §0 into the library.
- **`/program` skill built** (2026-10-05): `.claude/skills/program/`, `programs.json`, `topics/{statistics,indian-history,games}/curriculum.json`,
  `scripts/test_programs.py`. AWS ML major still needs setup (`/program setup aws-ml`).
- **Tiny-games widget built** (`assets/plugins/games.js`: tic-tac-toe, Nim, Hex ≤ 4×4 vs an exact solver; play + `game-move` quiz; `scripts/test_games.js`). G102 is unblocked.
- **Xiangqi + shogi boards built** (`assets/plugins/xiangqi.js`, `shogi.js`; perft-verified, `scripts/test_xiangqi_shogi.js`). Games widget queue is empty; next ideas: backgammon/dice sims (G401), poker range grid (G402).
- **Flashcards + "How sure were you?" built** (`card` quiz, `.lp-deck`, confidence step; server resets guessed items). **Learner: redeploy progress-server** (`git pull`, then `docker compose up -d --build progress-server`) so guesses reset server-side too.
- **Today page built** (`assets/today.html` + `today.js`, test `scripts/test_today.mjs`): plan from programs.json, ticks in localStorage.
- **Book server: `/search?book=<id>&compact=true` and `/grep/{id}?q=` written** (book-server/app.py, tests in book-server/test_app.py; client `scripts/books.py`). **Learner: redeploy book-server** (`git pull`, `docker compose up -d --build book-server`). Still to do: page numbers per chunk, per-book section maps, then hybrid (embedding) search. See
  `notes/program-layer-build-plan.md` (RAG update). Also a page-image endpoint for equations (`notes/math-books-strategy.md`).
- Library: Casella & Berger's /toc is junk (logged in `library/QUALITY-NOTES.md`); its real contents page is in the text near line 600.
