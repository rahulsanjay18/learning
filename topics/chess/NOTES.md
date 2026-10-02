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
- Open question for the learner: is 428 (PGN WhiteElo) their real chess.com rating?
