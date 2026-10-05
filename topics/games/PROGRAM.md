# Games: the major (draft program)

*Drafted 2026-10-05 from the learner's outline: intuition for perfect-information games → probabilistic / hidden-information games →
general theory. **Confirmed: Games is the "fun" major and replaces chess; chess is the first class** (`topics/chess/` holds it). Half weight: 2 blocks a week.*

## TL;DR
- **Stage 1, play and feel (deterministic, perfect information):** **chess first** (with friends; it continues as a lab through
  every stage), then a short class on *tiny* games you can solve by hand (tic-tac-toe, Nim, Hex) that names the core ideas: game
  trees, winning and losing positions, minimax, tempo and parity. Go follows.
- **Stage 2, chance and secrets:** dice games (expected value, using your Statistics), then **poker** (hidden information, ranges,
  bluffing as a mixed strategy).
- **Stage 3, the general theory:** combinatorial game theory, classical game theory (Nash equilibrium, the minimax theorem, backward
  induction), and **game-playing AI** (minimax and alpha-beta, Monte Carlo tree search, CFR for poker, self-play reinforcement learning). That last
  course meets your AI career.
- **Design rule:** every theorem arrives *after* you've felt it in a game. Solve tic-tac-toe by hand before meeting backward induction;
  bluff before meeting mixed strategies.

## Why this order works
- Small solvable games give **complete feedback**: you can check every line, so intuition gets trained on ground truth, not vibes.
  Big games (chess, Go) don't allow that, which is why they're a long-running lab rather than a prerequisite to finish.
- Chance comes second because **expected value** is the new idea, and Statistics is giving you that toolkit in parallel.
- Theory comes last but is **spiralled in early**: each Stage 1–2 course ends with one short "name the idea" lesson so Stage 3 feels
  like recognition, not new material.

## Courses

| Stage | Course | Core ideas | Sources (library first) |
|---|---|---|---|
| 1 | **G101 Chess** (first class; continues as a lab through every stage) | safety, tactics → strategy and endgames; your games reviewed with Stockfish | existing `topics/chess/` lessons 0001–0002 count; Seirawan's *Winning Chess* series (A); Capablanca; Silman (A) |
| 1 | **G102 Tiny games, big ideas** (short: 3–4 lessons) | game trees; win/lose positions; minimax by hand; parity and tempo; strategy stealing (Hex); Nim's binary trick | *Winning Ways* vol. 1 (grade C: point to chapters only) and vol. 2 (B); Martin Gardner, *Colossal Book of Mathematics* (B) |
| 1 | **G120 Go intuition** | capture and liberties, life and death on 9×9, territory vs. influence | *A Go Guide by a Beginner* (A); Janice Kim, *Learn to Play Go* IV–V (B) |
| 2 | **G201 Decisions under chance** | expected value; risk vs. reward; when to stop (Pig dice game); simulation in Python | Haigh, *Probability* VSI (A); your Statistics course |
| 2 | **G210 Poker** | hand odds and pot odds; ranges; bluffing and balance; game-theory-optimal (GTO) vs. exploitative play | *Elements of Poker* (A); Acevedo, *Modern Poker Theory* (B) |
| 3 | **G301 Combinatorial game theory** | Sprague–Grundy values; sums of games; games as numbers | *Winning Ways* vols. 1–3 |
| 3 | **G310 Game theory** | strategic and extensive form; Nash equilibrium; von Neumann's minimax theorem; mixed strategies; backward induction | Binmore, *Game Theory* VSI (A); *Game Theory 101: The Rationality of War* (B; links to military strategy) |
| 3 | **G320 Game-playing AI** | minimax + alpha-beta; Monte Carlo tree search (MCTS); counterfactual regret minimization (CFR) for poker; self-play reinforcement learning | Russell & Norvig, *AIMA* (B, adversarial search); Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed. (free PDF from the authors: http://incompleteideas.net/book/the-book-2nd.html) |
| — | **Capstone** | build and analyse an agent for a small game, or a deep analysis of your own games | — |

## What a lesson looks like
Same pattern as the other majors (see `TEACHING-LOG.md`): a short reading with a guide when it's definition-heavy, then
**play first**: a playable position, a puzzle or a hand. Then the idea that explains it, then practice, then review.
Theory lessons always point back to a game you've played.

## Widgets this major needs (add to the widget queue)
- **Tiny-game boards you can play against a solver:** tic-tac-toe, Nim, Hex on a small board. The solver uses exact minimax, so feedback is
  ground truth ("this move loses in 3"). Boards are drawn from game state, which fits the no-generated-art rule.
- Chess and Go: the existing plugins. Poker: a hand/range grid and pot-odds drills. Dice and backgammon: Python simulations.

## Gaps (to fill with your incoming books)
- A real **game theory textbook** beyond the Very Short Introduction (e.g. an undergraduate text such as Osborne's or Maschler, Solan &
  Zamir's; check availability before choosing).
- **Backgammon** (none in the collection) if we include it in Stage 2.

## Questions for you
1. ~~Games replaces chess?~~ **Yes; chess is the first class** (answered 2026-10-05).
2. Include **Go** in Stage 1 from the start, or wait until chess has some footing?
3. **Backgammon** in Stage 2 (a great bridge from perfect information to chance), or straight to poker?
   *Case for (2026-10-05):* adds one new ingredient (chance) while everything stays visible, before poker adds hidden information;
   the doubling cube is a clean expected-value decision (take if p ≥ 25% ignoring gammons and cube ownership; "the takepoint in money
   play is about 22%" per [Wikipedia: Doubling cube](https://en.wikipedia.org/wiki/Doubling_cube)); minimax → expectimax (chance
   nodes); TD-Gammon (Tesauro, IBM, 1990s: self-play temporal-difference learning, near-expert level,
   [Wikipedia](https://en.wikipedia.org/wiki/TD-Gammon)) is a precursor of AlphaZero, and it's covered in Sutton & Barto. *Against:* time
   at half weight, no library book, fewer friends play, and the Pig dice game already teaches expected value.
   **Suggested:** a 3–4 lesson backgammon unit inside G201 (cube, expectimax, TD-Gammon); grow it into a class only if it sticks.

## Sources
- `library/MANIFEST.csv` (titles and grades above).
- Ken Binmore, *Game Theory: A Very Short Introduction* (in collection, grade A): covers von Neumann's minimax theorem, mixed Nash
  equilibria, backward induction (checked via the book server).
- Berlekamp, Conway & Guy, *Winning Ways for Your Mathematical Plays*, vols. 1–3 (in collection; grades C, B, C).
