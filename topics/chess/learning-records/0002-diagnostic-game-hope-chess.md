# Diagnostic game: sound opening and good tactical eye; loses to the opponent's forcing replies

In the first untimed game vs. Sven-BOT (1100), the learner developed soundly (London-style setup, about equal through move 14),
spotted the engine's top move to win a piece (18. c3!), and held a +4 position for ten moves. The game was lost to one
move, 31. gxf3??, a recapture that opened the king to a forced mate in 5. Two earlier leaks: 13. e4 removed a defender of
d4 (it became 2 attackers vs. 1 defender), and 15. Bxf7+ was even on points but left d4 hanging and gave two minor pieces for rook + pawn.

**Evidence**: `games/2026-10-02-vs-sven.pgn`, Stockfish 16 review in `games/2026-10-02-vs-sven-review.md`.

**Implications**: the learner does not mainly hang pieces to one-move attacks. They play Heisman's "Hope Chess": not
listing the opponent's checks, captures and threats before moving, and not asking what a move stops defending.
Lesson 2 should be "checks first" (list every check the opponent would have after your move), with positions built
around king shelter after captures. Revisit "what did my move stop defending?" as an extension of lesson 1's counting.
The PGN header shows WhiteElo 428; confirm the learner's actual online rating (self-report was under ~1200).
