# Lists checks reliably in simple positions; misses some in a crowded one

Lesson 2: 8/9 right on the first try, rated "just right". Right: both review tallies, three of the four count-the-checks items
(2, 2 and 1 checks, including spotting the back-rank mate behind a "free" queen), and all three safe/lost judgments.
Missed: q6 (A4), after 31. Kf1 in the learner's own game, where Black has **6** checks: …Qb5+, …Qe2+, …Qe1+, …Rd1+, …Bd3+, …fxg2+.

**Evidence**: `lp-results chess/0002-checks-first | 8/9 right first try | missed: q6 | rating: just-right` (2026-10-05); the progress server shows the same.

**Implications**: the habit "picture the move, then list the checks" has landed. Completeness is the weak spot when many
pieces can reach the king. The likely misses are the less obvious checkers (the bishop's …Bd3+, the pawn capture …fxg2+). Next time, teach
a *systematic* scan, going piece by piece (queen, rooks, bishops, knights, pawns), instead of scanning by eye. That's Heisman's
point about "passive" Hope Chess. The three safe/lost items were two-option choices (TEACHING-LOG rule 8: recognition, 50% guessable),
so treat them as weaker evidence than the typed counts. Lesson 3: "what did my move stop defending?", opening with a piece-by-piece check-scan review.
