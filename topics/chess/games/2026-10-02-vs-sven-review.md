# Game review: you (White) vs. Sven-BOT (1100), 2 Oct 2026, 0-1

PGN: [`2026-10-02-vs-sven.pgn`](./2026-10-02-vs-sven.pgn) · Engine: Stockfish 16, depth 18–22, run by
[`../scripts/analyze_game.py`](../scripts/analyze_game.py). Evaluations are in pawns, from White's point of view (+ means White is better).

## The short version

You beat a 1100 bot's position, then lost to one move.

- **Opening (moves 1–12): fine.** You developed every piece, castled, and kept the position about equal. That's a London-System-style setup
  (d4, Bf4, Nf3, e3) and it's a sensible choice.
- **Middlegame (moves 13–17): two safety leaks.** Both are exactly what lesson 1 counts. Details below.
- **Moves 18–29: you were winning.** 18. c3! was the engine's top move and won a piece. You stayed at about +4 for ten moves.
- **Move 31: 31. gxf3?? allowed a forced mate in 5.** Before that move the engine had you at +2.8; after it, mate. That is the whole game.

## Moment 1: 13. e4. Your move stopped defending something

Before 13. e4, your d4 pawn was defended twice (queen d2, pawn e3). 13. e4 moved the e3 pawn *away*, so d4 lost a defender.
After the trades 13…Nxe4 14. Ncxe4 dxe4, two black pieces were aiming at d4:

| Square d4 after 14…dxe4 | Pieces |
|---|---|
| Black attackers | bishop g7, queen d8 (2) |
| White defenders | queen d2 (1) |

That's 2 attackers against 1 defender: **d4 was hanging.** Trading off the f6 knight is also what opened the g7 bishop's
diagonal onto d4. The engine's choice was 15. c3, which defends d4 a second time.
[Position after 14…dxe4](https://lichess.org/analysis/standard/rn1q1rk1/4ppb1/1pp3p1/p4bNp/3PpB2/1B6/PPPQ1PPP/4RRK1_w_-_-_0_15)

**Lesson:** a safety check isn't only "is the piece I'm moving safe?" It's also "what did my move *stop* defending?"
(Heisman's point: a move can look safe and not be.)

## Moment 2: 15. Bxf7+. Even on points, still bad

Run the lesson 1 tally on f7: Bxf7+ (+1), Rxf7 (−3), Nxf7 (+5), Kxf7 (−3) = **0**. On points it's even, and that's
probably why it looked fine. The engine scores it −2.3 for two reasons:

1. **d4 was still hanging** (2 vs. 1), and nothing in the trade fixed that.
2. **Two minor pieces (bishop + knight) are usually worth more than a rook and a pawn in the middlegame.** Seirawan uses this exact trade
   in *Play Winning Chess*: rook + pawn vs. bishop + knight is "6 to 6", but two minor pieces "are usually more active than a Rook and a pawn,
   especially when many other pieces are on the board." So the count understates what you gave up.

Then 17. Bg5 left d4 hanging a third move in a row. The bot took it the wrong way (17…Bxd4?), and you found **18. c3!**,
winning the bishop. That's good tactical vision.

## Moment 3: 31. gxf3??. A capture that opened your king

[Position before 31. gxf3](https://lichess.org/analysis/standard/4q2k/1Q3R2/1p1r1p2/p4bpp/8/5p2/PP4PP/2R3K1_w_-_-_0_31) (White to move, engine +2.8)

Recapturing a pawn is natural, and the material count says it's fine. But gxf3 removes the pawn sheltering your king.
Black's queen then has checks: **31…Qe3+ 32. Kg2 Qd2+ 33. Kg3 h4#**. With any king move it's mate in 5.

- Best was **31. Re7!** (attacking the queen, engine +2.8). 31. Rc8 also held a draw.
- The miss is exactly what Heisman calls *Hope Chess*: playing a move without listing the opponent's **checks** first.

**Lesson:** before every capture near your own king, ask: *"after this, what checks does my opponent have?"*

## What this tells me about where to teach next

1. You don't mostly hang pieces outright. Your opening and your tactical eye are already decent (18. c3!, 21. Qxd5+ were both the engine's top move).
2. Your losses come from **not looking at the opponent's forcing replies**, checks above all. That is Heisman's checks → captures → threats routine.
3. The "what did I stop defending?" leak (Moment 1) is a direct extension of lesson 1's counting.

So: **lesson 2 = "Checks first"**: before you move, list every check your opponent would have.

## Sources
- Engine analysis: Stockfish 16, via [python-chess](https://python-chess.readthedocs.io/); script in `scripts/analyze_game.py`.
- Dan Heisman, ["Passive vs. Basic Hope Chess"](https://www.chess.com/article/view/passive-vs-basic-hope-chess), Chess.com, 2018 (Hope Chess; checks, captures, threats).
- Dan Heisman, *Is Your Move Safe?*, Mongoose Press, 2016 (moves that look safe but aren't).
- Yasser Seirawan, *Play Winning Chess*, Ch. 2 "The First Principle: Force", section "Assigning the Pieces Numerical Values". In your collection, grade B: prose only, so look at the diagram in your own copy.
