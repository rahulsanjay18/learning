# Notes (teacher's scratchpad)

## Learner preferences
- Background: BS Math + BS CompE (Penn State), MS CS (Georgia Tech), 5 yrs in AI. Speak at that level; analogies to
  search/minimax/evaluation functions are welcome.
- Inattentive ADHD: keep lessons short, one idea, tight feedback loops. 20–30 min per session.
- Wants citations in text and at the end of every explanation, and a saved Markdown/HTML copy of explanations.
- Mission order of priority: (2) deep understanding, then (1) winning online. (3) casual and (4) AI/engines also matter.
- Plays on Chess.com; happy to play untimed bot games so I can diagnose. Ask for the PGN.

## Working notes
- Library: Seirawan "Winning Chess" series (Tactics, Strategies, Endings, Combinations: grade A) is the core
  reading. Polgar 5334 and Henkin 1000 Checkmates are grade B (figures unreliable: recommend only, never take diagrams).
- python-chess won't pip-install in the cloud container (setuptools `install_layout` error). Workaround: `pip download chess`
  and use the unpacked source tarball via PYTHONPATH. Verify every lesson position with `scripts/verify_positions.py`.
- Stockfish: `apt-get install -y stockfish` works in the container (Stockfish 16 at /usr/games/stockfish).
  `scripts/analyze_game.py <pgn>` gives a move-by-move review. Store games in `games/` with a `-review.md` next to each.
- GLOSSARY.md started after lesson 1 (9/10): point count, exchange, tally, hanging. Candidates next: Hope Chess, back rank.
- Lesson 1 = counting one square (static exchange). Diagnostic game (LR 0002) => lesson 2 = "checks first".
  After that: what a move stops defending, then double attack (fork), then pin. Converting a winning position is a later theme.
- Spacing: each lesson opens with 2 retrieval questions on the previous lesson(s). Lesson 3 should review checks-counting + one tally.
- Lesson 2 positions: verify with `scripts/verify_checks.py` (python-chess + Stockfish).
- Open question for the learner: is 428 (PGN WhiteElo) their real chess.com rating? (CLAUDE.md: username rahulsanjay18, rarely plays online.)
- Lessons 0001–0002 have no quiz data-ids, so lp.js uses positional ids (q1, q2, ...). NEVER reorder or insert quizzes in them,
  or their review schedules break. Give every quiz in 0003+ a data-id.
- Results: L1 9/10, L2 8/9 (missed q6 = count 6 checks after Kf1). Game 2 (6 Oct, Black): WON by mate; see LR 0005. Plan: L3 = "what did their move do?", L4 = "what did my move stop defending?".

- 2026-10-11: learner asked for more position variety (TEACHING-LOG rule 35). From 0005 on: own game for the motivating example only;
  practice from the Lichess puzzle database (filter by theme, e.g. fork / hangingPiece / discoveredAttack, and rating ~1000–1400) and
  Seirawan's diagrams, each checked with Stockfish. Reviewing 0003/0004's practice items for variety is optional; not done.
