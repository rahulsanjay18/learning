---
title: What did their move do?
subtitle: One block (~20 minutes). One win: before every move, you list what your opponent's last move attacks, including what it uncovered.
crumb: Chess · Lesson 3
index: What did their move do? (positions from your games)
---
## Why this lesson
In your 6 October game you lost material twice, and both times the reason was the same: **a move by the bot that you didn't look
at.** You can count attackers (lesson 1: 9/10) and list checks (lesson 2: 8/9), so this isn't missing knowledge. It's a missing
step: asking what their move did *before* you choose yours.

## Warm-up: checks, piece by piece (3 minutes)
Lesson 2's one miss was a position with six checks, where the bishop and pawn checks got skipped. The fix is a fixed order:
**queen, rooks, bishops, knights, pawns.** For each piece, look at every line toward the enemy king before moving on to the next piece.

::: board fen="4q2k/1Q3R2/1p1r1p2/p4bpp/8/5p2/PP4PP/2R3K1 w - - 0 31" caption="Your 2 October game, move 31, White to move (you)."
:::

::: number wu-checks answer=4
Suppose you play **31. h3** here. Using the order queen, rooks, bishops, knights, pawns, how many checks does Black then have?
--- hint
Queen first: which squares on the e-file and around your king can it check from? Then the rook on d6, the bishop, and the pawn on f3.
--- explain
Four: **Qe3+** and **Qe1+** (queen), **Rd1+** (rook), **f2+** (pawn). The pawn check is the easy one to skip; the fixed order
catches it. (Counted with python-chess.)
:::

## The idea
Start from something that's always true:

> **A move can create a new threat in only two ways: the moved piece attacks something from its new square, or the square it
> left opens a line for a piece behind it.**

There's no third way. So "what did their move do?" is never a vague question. It's two small checks you can finish every time:
1. **The moved piece:** look along every line (or every jump, for a knight) from its new square. What does it hit now?
2. **The square it left:** was it blocking a rook, bishop or queen? If so, what does that piece see now? A threat created this way is
   a **discovered attack**.

Then, for anything attacked, use lesson 1: count attackers and defenders. Is it hanging?

## The move you didn't look at: 41. Rd2

::: board fen="8/pppk4/7K/8/2Pb4/P6P/3R4/1r1n4 b - - 2 41" flip=true hl="d2" caption="Your 6 October game, after 41. Rd2. Black (you) to move."
:::

::: worked
**Step 1, the moved piece.** The rook now stands on d2. Look along its lines: down the d-file it hits the **knight on d1**; up the
d-file, d3 is empty, so it hits the **bishop on d4**. Along the 2nd rank there's nothing of yours.
--- step
**Step 2, the square it left.** Before this, the rook was on f2. Nothing of White's was standing behind it on that line, so nothing new was uncovered.
--- step
**Count (lesson 1).** Knight d1: attacked once, defended once (rook b1), so it's safe. Bishop d4: attacked once, defended **zero** times,
so it's **hanging**.
--- step
**One more thing about the bishop.** It stands on the d-file between the white rook and your king on d7. If it moves, the rook gives
check, which is illegal, so the bishop **can't** move. A piece that can't move (or shouldn't) because something more valuable stands
behind it on the line is **pinned**.
--- step
**So what saves it?** It can't run, so it needs a defender. In the game you played 41…Ra1 and lost it to 42. Rxd4+.
:::

::: chess-move rd2 fen="8/pppk4/7K/8/2Pb4/P6P/3R4/1r1n4 b - - 2 41" flip=true answer="c7c5|c5"
Find the move that keeps all your material.
--- hint
The bishop can't move and needs one defender. Which of your pawns can reach a square that guards d4?
--- explain
**41…c5**: the pawn guards d4, and the knight was already guarded. Stockfish rates it best by a wide margin. The check 41…Rb6+ looks
active, but after 42. Kh5 c5 43. Rxd1 the knight is lost instead.
:::

## Practice: run both steps

::: board fen="r2qk2r/ppp5/2np1p1p/b3p3/4P1b1/P1PP1N1P/Q4PP1/RN2K2R b KQ - 0 13" flip=true hl="h3" caption="6 October, after 13. h3. Black (you) to move."
:::

::: exact p-h3 answer="g4|Bg4|bishop g4|the bishop on g4"
What does White's last move, **13. h3**, attack? Type the square.
--- explain
The pawn on h3 attacks **g4**, where your bishop stands, and a pawn attacking a bishop wins it unless the bishop moves. (Nothing was
uncovered: the rook on h1 behind it still looks only at its own pawn.) In the game you saw it and played 13…Bxf3, trading
the bishop for White's knight before it could be taken; Stockfish agrees that's the best reply.
:::

::: board fen="rn1q1rk1/4ppb1/1pp3p1/p2p1bNp/3PnB2/1BN5/PPPQ1PPP/4RRK1 w - - 0 14" hl="e4" caption="Your 2 October game, after 13…Nxe4. White (you) to move."
:::

::: number p-nxe4 answer=5
Black's knight just took on e4. Run both steps. How many of your pieces and pawns are attacked now that weren't attacked before?
--- hint
Step 1: the knight on e4 jumps to eight squares; which of them hold your pieces? Step 2: the knight left f6. Which black piece was
behind f6, and what does it see now?
--- explain
**Five.** The knight on e4 hits four: the queen on d2, the knights on c3 and g5, and the pawn on f2. And by leaving f6 it opened the
long diagonal for the bishop on g7, which now hits **d4**: a discovered attack. (Counted with python-chess.)
:::

::: exact p-disc answer="d4|the d4 pawn|pawn d4|d4 pawn"
In that position, which of your pawns or pieces is attacked by the piece that was **uncovered**, rather than by the knight itself? Type the square.
--- explain
**d4**, by the bishop on g7. Step 2 is the step people skip, because the piece that attacks didn't move.
:::

## Take it to a real game
Play one game (any time control, the bot is fine). **Before each of your moves, say the two steps out loud, or write them down,
for your opponent's last move:** what does the moved piece hit, and what did it uncover? Then send me the PGN, and the review will
check exactly this.

This is optional homework, and the next lesson works without it. Lesson 4 turns the question around: what did *your* move stop
defending? Questions about anything here: ask me in chat.

## Sources
- Your games vs. Sven-BOT, 2 October and 6 October 2026 (`topics/chess/games/`); positions and counts checked with python-chess,
  move quality with Stockfish 16 (`topics/chess/scripts/analyze_game.py`).
- Dan Heisman, *The Improving Chess Thinker* (Mongoose Press): his thought process starts each move with what the opponent's move does.
- Yasser Seirawan & Jeremy Silman, *Winning Chess Tactics* (in your library, id 50634c974d): the pin and the discovered attack get full lessons later (G101 0006).
