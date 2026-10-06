# Handoff: state of everything (2026-10-05, end of the first long thread)

New threads: read `CLAUDE.md`, then `TEACHING-LOG.md`, then the topic's folder. This file is the to-do list across topics.

## Learner's next actions
- Statistics **lesson 4** (reading Casella & Berger §8.3.1 pp. 382–385 first) and Indian History **IH 100.1** (reading Kulke & Rothermund
  Introduction, first half). Both have reading-guide boxes: reply to those answers when results come in.
- Daily review deck: `assets/review.html`.
- Progress server is **live** (deployed 2026-10-05; `/progress/health` → ok). Desktop + laptop share one device token (id 1, "desktop+laptop").

## Open teaching work
| Topic | Next | Notes |
|---|---|---|
| Statistics | **Program: all of Casella & Berger with proofs; chapter pretest (concept/calc/proof per section) before each chapter** (`topics/statistics/PROGRAM.md`). Lesson 3 done (record 0007); **lesson 4 (power, §8.3.1) built**, learner does it next. Then lesson 5: P(data given H1), likelihood ratios, power (~55% in the A/B example) | Numbers in `topics/statistics/QUESTIONS.md` |
| Indian History | Mission done (MISSION.md). Learner does lesson 0002 next; then lesson 0003: rest of Introduction + Indus with first primary source, and a first "judge a public claim" box (Aryan migration) | `topics/indian-history/PROGRAM.md` |
| Games (fun major) | **Mission: design a balanced 3D strategy game** (MISSION.md). Chess is class G101 (continue `topics/chess/`, lessons 0001–0002 done: 9/10, 8/9; game 2 won as Black (LR 0005); next 0003 "what did their move do?"); program decided: chess → tiny games → xiangqi → shogi → Go → chance (Pig + backgammon unit) → poker → theory/AI | Chess.com: rahulsanjay18 |
| AWS ML cert | Ask: which exam, target date, AWS experience, prep materials | Check AWS's current exam list (don't guess names) |
| Military strategy | **Merged into Games** as G150 (lessons in `topics/military-strategy/`), feeding G350 Wargames and G360 Diplomacy | framed as "war as a game" (see its NOTES) |
| Economics | Parked; Principles solid (13/13) | Resume at intermediate level |
| NASM-CPT | Started earlier (`topics/nasm-cpt/`); exam date unknown | Deadline-driven: ask for the date |

## Open platform work
- **New books reviewed 2026-10-06** (`notes/new-books-2026-10-06.md`; partial, because the server went down during the scan).
  Use Schelling *Arms and Influence* (4bdcba34b3) in G150; McMahon *ML Engineering with Python* (7d3ec3450a) for AWS ML; British Empire
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
