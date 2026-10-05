# Handoff: state of everything (2026-10-05, end of the first long thread)

New threads: read `CLAUDE.md`, then `TEACHING-LOG.md`, then the topic's folder. This file is the to-do list across topics.

## Learner's next actions
- Statistics **lesson 3** (reading Casella & Berger §9.1 pp. 417–419 first) and Indian History **IH 100.1** (reading Kulke & Rothermund
  Introduction, first half). Both have reading-guide boxes: reply to those answers when results come in.
- Daily review deck: `assets/review.html`.
- Deploy `progress-server/` (steps in its README); then pair devices (see CLAUDE.md).

## Open teaching work
| Topic | Next | Notes |
|---|---|---|
| Statistics | **Program: all of Casella & Berger with proofs** (`topics/statistics/PROGRAM.md`). Learner hasn't done lesson 3 yet. Then lesson 4: P(data given H1), likelihood ratios, power (~55% in the A/B example) | Numbers in `topics/statistics/QUESTIONS.md` |
| Indian History | Mission done (MISSION.md). Learner does lesson 0002 next; then lesson 0003: rest of Introduction + Indus with first primary source, and a first "judge a public claim" box (Aryan migration) | `topics/indian-history/PROGRAM.md` |
| Games (fun major) | **Mission: design a balanced 3D strategy game** (MISSION.md). Chess is class G101 (continue `topics/chess/`, lessons 0001–0002 done); program decided: chess → tiny games → xiangqi → shogi → Go → chance (Pig + backgammon unit) → poker → theory/AI | Chess.com: rahulsanjay18 |
| AWS ML cert | Ask: which exam, target date, AWS experience, prep materials | Check AWS's current exam list (don't guess names) |
| Military strategy | **Merged into Games** as G150 (lessons in `topics/military-strategy/`), feeding G350 Wargames and G360 Diplomacy | framed as "war as a game" (see its NOTES) |
| Economics | Parked; Principles solid (13/13) | Resume at intermediate level |
| NASM-CPT | Started earlier (`topics/nasm-cpt/`); exam date unknown | Deadline-driven: ask for the date |

## Open platform work
- Widgets: **tiny-game boards vs. a minimax solver** (tic-tac-toe, Nim, Hex) and **xiangqi / shogi boards** for the Games major.
- Widgets: **flashcards** + a **"How sure were you?"** step (guessed-right → treated as not known). Next in the widget queue.
- "Today" page that shows the day's plan from `notes/study-plan.md` and marks it done (enforces "finish the plan first").
- Book server: `/search?book=<id>`, page numbers per chunk, per-book section maps, then hybrid (embedding) search. See
  `notes/program-layer-build-plan.md` (RAG update). Also a page-image endpoint for equations (`notes/math-books-strategy.md`).
- Library: Casella & Berger's /toc is junk (logged in `library/QUALITY-NOTES.md`); its real contents page is in the text near line 600.
