# Won vs. the 1100 bot as Black; the misses are "every move", not "don't know"

Second untimed game vs. Sven-BOT (1100), as Black: **won by checkmate** in 65 moves. Two own mistakes gave material away:
14…Rg8?? (rook to a square the queen attacked along a diagonal it had just used; 0 defenders; taken with check, so this is
exactly lesson 2's check list) and 41…Ra1? (ignored 41. Rd2, which attacked an undefended bishop that was pinned to the king; 41…c5 held).
Positives: found 35…Ne3+ and …Rg1 to win the bot's rook after its blunder, then promoted a passed pawn and mated with queen + rook.

**Evidence**: `games/2026-10-06-vs-sven.pgn`, review in `games/2026-10-06-vs-sven-review.md` (Stockfish 16; counts by python-chess).

**Implications**: the learner can count (L1 9/10) and list checks (L2 8/9) in lessons but skips the routine in games. That's a habit
gap, not a knowledge gap. A new failure type appeared: not asking "what does my opponent's last move attack?" (Heisman's thought
process starts there). Lesson 3 should be **"What did their move do?"**, built on 41. Rd2 from this game, with the 14…Rg8 position as a
review item. "What did my move stop defending?" moves to lesson 4. Interleave the old skills in each lesson, and keep games as the
transfer test. The pin appeared naturally (41. Rd2), so it's a good later tactic lesson.
