# Game review: Sven-BOT (1100, White) vs. you (Black), 6 Oct 2026, 0-1, you won by checkmate

PGN: [`2026-10-06-vs-sven.pgn`](./2026-10-06-vs-sven.pgn) · Engine: Stockfish 16, depth 13 (move by move) via
[`../scripts/analyze_game.py`](../scripts/analyze_game.py). Evaluations are in pawns from **White's** side, so negative is good for you.

## The short version

**You won a 65-move game against an 1100 bot, playing Black, and finished with a checkmate.** Two of your own moves gave
material away, and both were the same kind of miss: an opponent's capture you didn't look at.

| Phase | What happened | Engine |
|---|---|---|
| Moves 1–10 | Solid Italian Game. You won a pawn (8…Bxb4) | about −1.5 (you better) |
| 11. Bxf7+? | The bot gave away a bishop | −5 (you winning) |
| **14…Rg8??** | Your rook went to a square the queen attacks, **with check** | +2.2 (White better) |
| Moves 15–34 | A long grind. The bot traded queens (20. Qxd8+) | White about +1 to +2 |
| 35. Kf5? | The bot blundered; 35…Ne3+ and …Rg1 won its rook | −5 |
| **41…Ra1?** | Gave back a bishop | −3.7 (still winning) |
| Moves 42–65 | You pushed the a-pawn, promoted (54…a1=Q) and mated with queen and rook | mate |

## Moment 1: 14…Rg8??, a capture that comes with check

[Position before 14…Rg8](https://lichess.org/analysis/standard/r2qk2r/ppp5/2np1p1p/b3p3/4P3/P1PP1P1P/Q4P2/RN2K2R_b_KQ_-_0_14) (Black to move, engine −5.3)

The idea was natural: put the rook on the open g-file. But run lesson 2's routine on it. After …Rg8, White has
**3 checks**: Qxg8+, Qf7+ and Qe6+. The first is also a capture. Now run lesson 1's count on g8:

| g8 after 14…Rg8 | |
|---|---|
| White attackers | queen a2, along the a2–g8 diagonal (1) |
| Black defenders | none (0) |

The rook was **hanging**, and it got taken with check, so you had no time to do anything about it. That diagonal wasn't hidden:
White's queen had used it two moves earlier (12. Qa2+). The engine wanted 14…Kd7, getting the king off that line first.

**Lesson-2 skill, missed under game conditions:** "picture the move, list the checks." Qxg8+ would have been the first item on the list.

## Moment 2: 41…Ra1?, not asking what the opponent's last move attacks

[Position after 41. Rd2](https://lichess.org/analysis/standard/8/pppk4/7K/8/2Pb4/P6P/3R4/1r1n4_b_-_-_2_41) (Black to move, engine −6.9)

The bot's 41. Rd2 attacked **two** of your pieces down the d-file: the bishop on d4 and the knight on d1.

| | White attackers | Black defenders |
|---|---|---|
| bishop d4 | rook d2 | **none** |
| knight d1 | rook d2 | rook b1 |

The bishop also couldn't move: it stood between the white rook and your king on d7, so it was **pinned**. The engine's 41…c5 defends
it with a pawn. 41…Ra1 didn't, and 42. Rxd4+ took it with check.

This miss happens *before* your own move: **what does my opponent's last move attack?** Heisman's thought-process
books start every move there, with what the opponent's move does, before choosing your own [3].

## What went well

- **The opening**, and grabbing the b4 pawn when the bot offered it.
- **Not panicking** after 14…Rg8. Down material, you kept playing and were ready when the bot erred (35…Ne3+, then …Rg1 winning the rook).
- **Finishing.** You pushed a passed pawn all the way, promoted, and mated with queen and rook. The finish took a while (the engine
  had faster routes, e.g. 57…Qf7+ instead of 57…Qe7+), but a win is a win, and converting quickly is a skill for later.

## The pattern across both games

| Game | Your costly miss | Which step of the routine |
|---|---|---|
| 2 Oct | 31. gxf3?? allowed mate in 5 | Checks after my move (lesson 2) |
| 2 Oct | 13. e4 left d4 2 attackers vs. 1 | What my move stopped defending |
| 6 Oct | 14…Rg8?? hung a rook with check | Checks after my move (lesson 2), and captures (lesson 1) |
| 6 Oct | 41…Ra1? left a pinned bishop attacked | **What their last move attacks** (new) |

You know the counting and the check-listing (9/10 and 8/9 in the lessons). The gap is **doing them every move, in a real game**.
The step that's never been taught is the very first one: before thinking about your move, ask what their move just did.

## Sources
1. Engine analysis: Stockfish 16 via [python-chess](https://python-chess.readthedocs.io/); attacker/defender counts computed with python-chess.
2. Dan Heisman, ["Passive vs. Basic Hope Chess"](https://www.chess.com/article/view/passive-vs-basic-hope-chess), Chess.com, 2018.
3. Dan Heisman, [*The Improving Chess Thinker*](https://mongoosepress.com/catalog/books/improving_thinker.html), Mongoose Press, and his
   ICC lecture ["Introduction to Thought Process"](https://shop.chessclub.com/products/heisman-2-introduction-to-thought-process-icc-c-heisman-intro-3),
   which covers "everything that happens after your opponent makes a move until you make yours."
