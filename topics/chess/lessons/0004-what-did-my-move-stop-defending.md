---
title: What did my move stop defending?
subtitle: One block (~20 minutes). One win: before you move a piece, you list what it is guarding right now, and check each of those after the move.
crumb: Chess · Lesson 4
index: What did my move stop defending? (positions from your games)
---
## Why this lesson
In your 2 October game you had a good position after twelve moves: Stockfish rated it about **+1.4** for you. Then you played
**13. e4**, a natural central move, and the position was suddenly about even. Nothing of yours was hanging when you played it. The
problem was what the e-pawn had been doing *before* it moved.

Last lesson asked "what did **their** move do?" This one turns it around: **what did *my* move stop doing?**

## Warm-up: their move, two steps (3 minutes)

<details><summary>Recap: the two steps from last lesson</summary>

A move creates a new threat in only two ways: (1) the **moved piece** attacks something from its new square, or (2) the **square it
left** opens a line for a piece behind it (a discovered attack). Then count attackers and defenders on anything attacked.
</details>

::: board fen="rn1q4/4pk2/1pp3p1/p4bBp/3bp3/8/PPPQ1PPP/4RRK1 w - - 0 18" hl="d4" caption="Your 2 October game, after 17…Bxd4. White (you) to move."
:::

::: number wu-bxd4 answer=2
Black's bishop just came from g7 and took on d4. Run step 1: how many of your pieces and pawns does the bishop on d4 attack now?
--- hint
Follow both diagonals from d4 toward your side of the board, until each one hits something.
--- explain
Two: the pawns on **b2** and **f2**. Step 2 finds nothing new: nothing of Black's stood behind g7 on a line toward your pieces. (You
then found 18. c3!, which attacked the bishop and won it. Counted with python-chess.)
:::

## The idea
Start from something that's always true:

> **A piece guards squares only from where it stands. When it moves, it stops guarding every square it guarded before, except the
> ones it still reaches from its new square.**

That's just what "moving" means, so there's no exception to it. And it gives a routine you can always finish, for the piece you're
about to move:
1. **What is it guarding now?** List your own pieces and pawns it defends from its current square.
2. **After the move, count each one again** (lesson 1): attackers against defenders. Anything that drops to more attackers than
   defenders, or that only *looks* fine because a line is still closed, is the price of your move.

A pawn is the easiest piece to forget, because pawns don't feel like defenders. They're the best defenders there are: cheap, and
nobody wants to take one with a queen.

## The move that cost the advantage: 13. e4

::: board fen="rn1q1rk1/4ppb1/1pp2np1/p2p1bNp/3P1B2/1BN1P3/PPPQ1PPP/4RRK1 w - - 0 13" hl="e3" caption="Your 2 October game, move 13, before 13. e4. White (you) to move."
:::

::: number guard-list-v1 answer=2
Step 1 for the pawn on e3: how many of your own pieces and pawns is it guarding right now?
--- hint
A white pawn guards the two squares diagonally in front of it.
--- explain
Two: the pawn on **d4** and the bishop on **f4**. A pawn guards diagonally forward, so from e3 it covers d4 and f4.
:::

::: worked
**Step 1, what it guards.** From e3 the pawn guards **d4** and **f4**. So d4 has two defenders right now (queen d2, pawn e3), and
it isn't attacked at all: the black bishop on g7 is blocked by its own knight on f6, and the queen on d8 by its own pawn on d5.
--- step
**After 13. e4: f4.** The pawn left e3, so the diagonal from your queen on d2 through e3 is open: the queen now guards f4. The bishop
lost one defender and gained another. Fine.
--- step
**After 13. e4: d4.** Only the queen guards it now. That still looks fine, because nothing attacks d4 yet. But look at what the black
lines are waiting on: the bishop on g7 needs the knight on f6 to move, and the queen on d8 needs the pawn on d5 to move.
--- step
**What happened in the game.** 13…Nxe4 moved the knight (the g7 bishop's line opens) and 14…dxe4 moved the d5 pawn (the queen's line
opens). In two moves, d4 went from **0 attackers** to **2**, with your **1** defender. It was hanging, and it stayed hanging for three moves.
--- step
**The lesson.** 13. e4 didn't hang anything at the moment it was played. It removed a defender from a square that two closed black
lines were pointed at. Stockfish's choice was **13. f3**, preparing e4 so that a pawn would guard it and the knight couldn't take there.
:::

::: board fen="rn1q1rk1/4ppb1/1pp3p1/p4bNp/3PpB2/1B6/PPPQ1PPP/4RRK1 w - - 0 15" hl="d4" caption="The same game after 13. e4 Nxe4 14. Ncxe4 dxe4. White (you) to move."
:::

::: number hang-after-v1 answer=2
Count it (lesson 1). How many black pieces attack your pawn on d4 now?
--- explain
Two: the **bishop on g7** (its diagonal opened when the f6 knight took on e4) and the **queen on d8** (its file opened when the d5
pawn recaptured). You have one defender, the queen on d2. Two against one: the pawn is hanging.
:::

::: chess-move hang-after-v2 fen="rn1q1rk1/4ppb1/1pp3p1/p4bNp/3PpB2/1B6/PPPQ1PPP/4RRK1 w - - 0 15" answer="c2c3|c3"
Find the move that gives d4 the second defender it needs, without giving anything else away.
--- hint
The cheapest defender is a pawn. Which pawn can reach a square that guards d4?
--- explain
**15. c3**: a pawn guards d4 and the count is two against two. Stockfish rates it best by over half a pawn. In the game you played
15. Bxf7+, which left d4 hanging for another two moves.
:::

## Moving a defender isn't always wrong
The routine says to **check**, not to never move a defender. Sometimes the thing you stop guarding isn't attacked, or you get more
than you give. Two positions from your games:

::: board fen="r4q2/3npk2/1p4p1/p2p1bBp/4p3/8/PP1Q1PPP/4RRK1 w - - 0 21" hl="d2 d5" caption="Your 2 October game, move 21. White (you) to move. You played 21. Qxd5+."
:::

::: exact guard-list-v2 answer="g5|Bg5|bishop g5|the bishop on g5|bishop on g5"
Step 1 for the queen on d2: which of your **bishops or knights** does it guard right now? Type the square.
--- explain
The bishop on **g5**, along the diagonal d2–e3–f4–g5. From d5 the queen won't guard it any more.
:::

::: number hang-after-v3 answer=0
After 21. Qxd5+, how many black pieces attack your bishop on g5?
--- explain
None, so leaving it unguarded costs nothing right now, and the move is a check that wins a pawn. Stockfish's top move. Step 2 of the
routine is the reason this is fine, not luck: you counted.
:::

::: board fen="8/pppk4/1b3K1p/8/3P4/P1P1n2P/R4pr1/1N5R b - - 0 36" flip=true hl="g2 f2" caption="Your 6 October game, move 36. Black (you) to move."
:::

::: exact guard-list-v3 answer="f2|the f2 pawn|pawn f2|f2 pawn"
Step 1 for your rook on g2: which of your pawns does it guard? Type the square.
--- explain
**f2**, along the 2nd rank. White's rook on a2 attacks it too, so right now it's one attacker against one defender.
:::

::: choice hang-after-v4
In the game you played **36…Rg1**, so the rook stopped guarding f2. What happens?
- [x] White can take on f2, and then Black takes White's h1 rook
- [ ] White can take on f2, and then White's rook attacks Black's knight
- [ ] White cannot take on f2, because the knight still guards the pawn
- [ ] White cannot take on f2, because the rook on a2 is pinned
--- hint
Step 1 tells you what the rook stops guarding. Now look at what it attacks from g1.
--- explain
37. Rxf2 wins the pawn, but 37…Rxh1 wins a whole rook: a pawn given for a rook. Stockfish's top move, and you played it. You
stopped defending f2 on purpose, because you'd counted what you got for it.
:::

## Take it to a real game
Play one game (any time control, the bot is fine). **Before each move, ask one question about the piece you're about to move: what
is it guarding right now?** Then check those things after the move. Send me the PGN, and the review will check exactly this, along
with last lesson's question about your opponent's move.

This is optional, and the next lesson works without it. Questions about anything here: ask me in chat.

## Extra practice (optional)
1. *Winning Chess Tactics*, Chapter 6 "Deflection", Tests 57–59 (p. 77), easiest first. Each one is the same idea from the other side:
   a piece is the only defender of something, so the attacker drags it away. Answers in the book's "Solutions to Tests from Part 1".
2. **Extra reading:** the opening pages of the same chapter (Diagrams 67–69, pp. 74–75): three games where "the defender's mistake was
   relying on his pieces to defend one another". It's the next step after this lesson: your defender doesn't move on its own; the
   opponent forces it to. (A full lesson on deflection comes later.)
3. **Extra article:** Dan Heisman, "Checking for safety requires more than using tactical vision" (Chess.com, about 800 words). A coach
   on why a quick glance misses tactics and why the safety check has to be a routine; his example move looked safe because the piece
   was guarded, and it wasn't. <https://www.chess.com/blog/danheisman/checking-for-safety-requires-more-than-using-tactical-vision>

## Sources
- Your games vs. Sven-BOT, 2 October and 6 October 2026; positions and counts checked with python-chess, evaluations with Stockfish
  (depth 20–22). The 13. e4 analysis is also in your 2 October game review.
- Yasser Seirawan & Jeremy Silman, *Winning Chess Tactics* (in your library, id 50634c974d), Chapter 6, "Deflection", pp. 73–77.
- Dan Heisman, *Is Your Move Safe?* (Mongoose Press, 2016): a move can look safe and not be. And his Chess.com article above.
