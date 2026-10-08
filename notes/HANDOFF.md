# Handoff: state of everything (2026-10-05, end of the first long thread)

New threads: read `CLAUDE.md`, then `TEACHING-LOG.md`, then the topic's folder. This file is the to-do list across topics.

## Learner's next actions
- **2026-10-08: eng 0001 graded** (record eng/0001: tech lead, target Solver; nothing shrinks). SE000 done, **SE101 active: write its
  syllabus before Monday's staff block** (prefer Reilly Part I once the staff books are indexed). Vim is now a shown tip (rule 30).
- **2026-10-07 (later): lessons built ahead** with current info: eng 0001 staff placement and 0002 AWS placement (pretest), IH 0004
  Vedic age (opens with the Indus-stages re-teach), chess 0003 "what did their move do?", military strategy 0002 annihilation vs.
  exhaustion. Stats 0007 waits on 0006 results. MLA-C02 GA is **"TBD"** on AWS's page (not 2027-01-14); 0002 asks the learner for a target date.
- **2026-10-06: syllabi + mastery grading.** Each major has `topics/<major>/SYLLABUS.md` (readings + objectives per lesson for the
  active courses); `plan` in curriculum.json mirrors it. Grade objectives Got it / Not yet (TEACHING-LOG rule 20; explainer
  `notes/mastery-grading.md`). Write lessons from the syllabus; don't redesign per session.
- Statistics: Ch. 1 pretest (0005) done 2026-10-06; **0006 the three axioms** (reading C&B pp. 7–11) next, learner plans it for 2026-10-07. Indian History **lesson 0003 done 2026-10-07** (record 0003; re-teach the Indus origin stages in 0004, due Saturday). Both have reading-guide boxes: reply to those answers when results come in.
- 2026-10-06: all 5 pending free responses graded and posted (stats ice-cream causal 0.75; IH 0002 answers).
- Daily review deck: `assets/review.html`.
- Progress server is **live** (deployed 2026-10-05; `/progress/health` → ok). Desktop + laptop share one device token (id 1, "desktop+laptop").

## Platform ideas (not urgent; learner deploys on their server)
- Small local model to offload easy work: `notes/slm-offload-plan.md` (semantic book search first, then first-pass grading with
  escalation after a ≥90% agreement test). Hardware known (32 GB RAM, 1× 5070 Ti 16 GB): enough; no second GPU yet. Waiting on: which other services use the GPU.
- AWS: target MLA-C02 (GA "TBD" per AWS, checked 2026-10-07; beta running). Learner's course = a 2024 Solutions Architect (Associate) course: use its core-AWS modules
  (IAM, S3, VPC, EC2, Lambda, CloudWatch) as the foundations course, then MLA-C02 prep from AWS's exam guide. Waiting on: the course
  files (learner will send) and a target date.

## Open teaching work
| Topic | Next | Notes |
|---|---|---|
| Statistics | **Program: all of Casella & Berger with proofs; chapter pretest (concept/calc/proof per section) before each chapter** (`topics/statistics/PROGRAM.md`). Lesson 3 done (record 0007); **lesson 4 (power, §8.3.1) built**, learner does it next. Then lesson 5: P(data given H1), likelihood ratios, power (~55% in the A/B example) | Numbers in `topics/statistics/QUESTIONS.md` |
| Indian History | Lesson 0002 done (record 0002). **0003 "The Indus cities" built 2026-10-06** (Wheeler's "Indra stands accused" vs Dales 1964 + Rakhigarhi 2019 genome; claim box on the headline "DNA study debunks Aryan invasion theory"). Rest of the Introduction became an optional skim on 0003. Next: 0004 Indo-Aryans and the Vedic age (Rigveda hymn as first text source) | `topics/indian-history/PROGRAM.md` |
| Games (fun major) | **Mission: design a balanced 3D strategy game** (MISSION.md). Chess is class G101 (continue `topics/chess/`, lessons 0001–0002 done: 9/10, 8/9; game 2 won as Black (LR 0005); next 0003 "what did their move do?"); program decided: chess → tiny games → xiangqi → shogi → Go → chance (Pig + backgammon unit) → poker → theory/AI | Chess.com: rahulsanjay18 |
| Military strategy | **Merged into Games** as G150 (lessons in `topics/military-strategy/`), feeding G350 Wargames and G360 Diplomacy | framed as "war as a game" (see its NOTES) |
| Engineering career (`topics/eng/`) | **New job starts 2026-10-26; no search for ~18 months.** Interview lane: alternate design (growth) / coding (maintenance) until 2027-10-26, then weekly mocks, then 2 blocks/week from 2028-02-26. Staff-at-new-job decision at day 90 (2027-01-24); don't presume. |
| Engineering career (`topics/eng/`, setup) | **Started 2026-10-07** as one continuous major (replaces cpp/staff/career/aws-ml; takes aws-ml's 4 blocks). Next: lesson 0001 SE000 staff placement (design exercise on Server #13) and 0002 AW000 AWS placement + MLA-C02 date. Rep 0 = Vim setup + vimtutor. Reps from `backlog.json`; required. Code reps need push access to the 3D chess repos (attached read-only) | Staff books owned, not on the book server; ask before filing the 2 proposed tickets; monthly catalog refresh? |
| Economics | Parked; Principles solid (13/13) | Resume at intermediate level |
| NASM-CPT | Started earlier (`topics/nasm-cpt/`); exam date unknown | Deadline-driven: ask for the date |

## Open platform work
- **2026-10-07 near-outage:** a 250 MB EPUB made pandoc use up the home server's RAM (logins hung, servers 502; no crash).
  Fixed in `scripts/reconvert.py`: memory cap per book (`--mem-gb`, default 4), 30-min timeout, no image extraction, per-book log,
  no partial files. Also fixed: add_books crash (two `run` functions) and a compose build-path check. Servers now on current code;
  47 old pretest review rows dropped. **Next:** learner reruns `add_books.py`, then `/new-books` (staff books).
- **2026-10-07: pretests no longer feed review** (TEACHING-LOG rule 28). **Learner: redeploy progress-server**; then I call
  `POST /progress/review/drop {"pages":["statistics/0001-placement-pretest","statistics/0005-ch1-pretest","indian-history/0001-placement-pretest","economics/0001-placement-pretest"]}`
  to clear the old server rows (the review deck already hides them). **Staff books aren't on the book server** (title and full-text search, 2026-10-07): redeploy book-server, then `/new-books`; add Reilly Ch. 1 to eng 0001 once it's there.
- **2026-10-07: ideas from three pi repos adopted** (`notes/inspiration-pi-repos-2026-10-07.md`): `.claude/skills/teach/PRINCIPLES.md` (TEACHING-LOG rule 26), agents `researcher` + `lesson-reviewer` in `.claude/agents/`, `/quiz-me` uses the AskUserQuestion picker with "I don't know", learning-record writing rules, lint warns when only the answer gives a reason. **Second pass:** TEACHING-LOG opens with "Why these rules exist" (understanding = connected facts; rules grouped under 4 ideas), rule 21 widened to every step; **diagram templates** `assets/plugins/diagram.js` (graph / sequence / venn) + `scripts/snap.mjs` to look at renders. Possible later: a session-transcript file (learn's md-log).
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
  `scripts/test_programs.py`. AWS ML is now the AW lane of the Engineering career major (`topics/eng/`).
- **Tiny-games widget built** (`assets/plugins/games.js`: tic-tac-toe, Nim, Hex ≤ 4×4 vs an exact solver; play + `game-move` quiz; `scripts/test_games.js`). G102 is unblocked.
- **Xiangqi + shogi boards built** (`assets/plugins/xiangqi.js`, `shogi.js`; perft-verified, `scripts/test_xiangqi_shogi.js`). Games widget queue is empty; next ideas: backgammon/dice sims (G401), poker range grid (G402).
- **Flashcards + "How sure were you?" built** (`card` quiz, `.lp-deck`, confidence step; server resets guessed items). **Learner: redeploy progress-server** (`git pull`, then `docker compose up -d --build progress-server`) so guesses reset server-side too.
- **Today page built** (`assets/today.html` + `today.js`, test `scripts/test_today.mjs`): plan from programs.json, ticks in localStorage.
- **Book server: `/search?book=<id>&compact=true` and `/grep/{id}?q=` written** (book-server/app.py, tests in book-server/test_app.py; client `scripts/books.py`). **Learner: redeploy book-server** (`git pull`, `docker compose up -d --build book-server`). Still to do: page numbers per chunk, per-book section maps, then hybrid (embedding) search. See
  `notes/program-layer-build-plan.md` (RAG update). Also a page-image endpoint for equations (`notes/math-books-strategy.md`).
- Library: Casella & Berger's /toc is junk (logged in `library/QUALITY-NOTES.md`); its real contents page is in the text near line 600.
