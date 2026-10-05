# Games: the major (draft program)

**Mission (see MISSION.md): learn how decisions in strategy games work, then design a balanced, complex strategy game in 3D space.**
Every class serves that: you study existing games *as a future designer*.

*Drafted 2026-10-05 from the learner's outline: intuition for perfect-information games → probabilistic / hidden-information games →
general theory. **Confirmed: Games is the "fun" major and replaces chess; chess is the first class** (`topics/chess/` holds it). Half weight: 2 blocks a week.*

## TL;DR
- **One big new game at a time**, with chess as the ongoing lab. Games are grouped by *family*, ordered by distance from what you
  already know: chess → its cousins (xiangqi, shogi) → Go (a different family) → chance (backgammon) → hidden information (poker).
- **Two threads run through every class and do the generalizing:**
  1. **Same ideas, different rules:** each class ends by asking what transferred from earlier games and what broke (tempo,
     material vs. territory, king safety, initiative, endgame counting). A late seminar puts these side by side.
  2. **How a computer plays it:** each class ends with a short "AI lens" lesson (alpha-beta for chess; why Go broke alpha-beta and
     needed Monte Carlo tree search; expectimax for backgammon; CFR for poker). It culminates in AlphaZero, one algorithm that mastered
     chess, shogi and Go from the rules alone. This is the career link.
  3. **The designer's lens:** for each game, ask *why does this rule exist?* Many rules are balancing devices: Go's komi (6.5–7.5
     points to White, since moving first is worth about 5–7 points), Hex's pie rule (the second player may swap sides, so the
     first move has to be fair), shogi's drops (they keep endgames from drying up into draws), xiangqi's palace and river. You keep a
     **design notebook** of these: it becomes your toolkit.
- **Then the general theory:** combinatorial game theory, classical game theory, game-playing AI, and a capstone.
- Half weight (2 blocks a week): this is a multi-year major, played and enjoyed as you go, not a race.

## Why this order
- Small steps from the familiar: xiangqi and shogi descend from the same ancestor as chess (chaturanga, from India), so you learn
  them *by transfer*, and each one changes more than the last (shogi's drops, where captured pieces come back, are the biggest
  change). Go comes after them because it's the most different (territory and influence, no king to checkmate).
- Chance comes after the deterministic games, one ingredient at a time: backgammon adds dice while everything stays visible; poker
  then adds hidden information.
- Theory comes last but is never new: by then every concept has been felt in at least two games.

## Courses

| Stage | Course | Core ideas | Sources (library first) |
|---|---|---|---|
| 1 | **G101 Chess** (first class; continues as the lab throughout) | safety, tactics → strategy and endgames; your games reviewed with Stockfish | existing `topics/chess/` lessons 0001–0002 count; Seirawan's *Winning Chess* series (A); Capablanca; Silman (A) |
| 1 | **G102 Tiny games, big ideas** (3–4 lessons) | game trees; win/lose positions; minimax by hand; parity and tempo; strategy stealing (Hex); Nim's binary trick | *Winning Ways* vols. 1 (C) and 2 (B); Martin Gardner (B) |
| 2 | **G201 Xiangqi** | what transfers from chess; the palace, river, cannon; elephants that can't cross | David H. Li, *First Syllabus on Xiangqi* and *Syllabus on Cannon* (B); W. F. Wong (F: recommend only) |
| 2 | **G202 Shogi** | drops (captured pieces return), promotion zones; why games never simplify | Leggett, *Japanese Chess: The Game of Shogi* (B); Aono, *Better Moves for Better Shogi* (C) |
| 3 | **G301 Go** | liberties, life and death, territory vs. influence, sente/gote; 9×9 → 13×13 | *A Go Guide by a Beginner* (A); Janice Kim, *Learn to Play Go* IV–V (B) |
| 4 | **G401 Decisions under chance** | expected value (Pig dice game); **backgammon unit** (3–4 lessons): pip count, the doubling cube (take point ≈ 22–25%), expectimax, TD-Gammon | Haigh, *Probability* VSI (A); your Statistics course; backgammon: gap |
| 4 | **G402 Poker** | hand and pot odds; ranges; bluffing and balance; GTO vs. exploitative play | *Elements of Poker* (A); Acevedo, *Modern Poker Theory* (B) |
| 5 | **G501 Comparative strategy** (seminar) | the "same ideas, different rules" thread made explicit across all the games | your own notes and games |
| 5 | **G502 Combinatorial game theory** | Sprague–Grundy values; sums of games; games as numbers | *Winning Ways* vols. 1–3 |
| 5 | **G503 Game theory** | strategic and extensive form; Nash equilibrium; von Neumann's minimax theorem; mixed strategies; backward induction | Binmore, *Game Theory* VSI (A); *Game Theory 101: The Rationality of War* (B) |
| 5 | **G504 Game-playing AI** | minimax + alpha-beta → expectimax → MCTS → CFR → self-play RL (AlphaZero across chess, shogi, Go) | Russell & Norvig, *AIMA* (B); Sutton & Barto, 2nd ed. (free PDF from the authors: http://incompleteideas.net/book/the-book-2nd.html) |
| 6 | **G601 Anatomy of strategy games** | what makes a decision interesting; depth from simple rules (Go); branching factor, game length, draws; information and luck as design levers | Sellers, *Advanced Game Design: A Systems Approach* (A); your design notebook |
| 6 | **G602 Balance** | symmetric vs. asymmetric balance; first-move advantage and fixes (komi, pie rule); dominant strategies; **measuring balance with self-play agents** | Tomašev, Paquet, Hassabis & Kramnik, "Assessing Game Balance with AlphaZero" (2020); your G504 agents |
| 6 | **G603 Designing in 3D** | geometry (cubic vs. hexagonal cells), adjacency and movement, board size vs. complexity, how players *see* 3D space; why earlier 3D chess variants stayed niche | Wikipedia, "Three-dimensional chess" (Raumschach, 5×5×5, 1907); playtests |
| 6 | **Capstone: your game** | design, paper-prototype, playtest with friends, balance-test with your own agents, iterate | everything above |

## What a lesson looks like
Same pattern as the other majors (see `TEACHING-LOG.md`): a short reading with a guide when it's definition-heavy, then
**play first**: a playable position, a puzzle or a hand. Then the idea that explains it, then practice, then review.
Theory lessons always point back to a game you've played.

## Widgets this major needs (add to the widget queue)
- **Xiangqi and shogi boards** with rules engines (like the chess and Go plugins); look for permissively licensed open-source rules
  libraries before writing our own, and verify their licenses.
- **Tiny-game boards you can play against a solver:** tic-tac-toe, Nim, Hex on a small board. The solver uses exact minimax, so feedback is
  ground truth ("this move loses in 3"). Boards are drawn from game state, which fits the no-generated-art rule.
- Chess and Go: the existing plugins. Poker: a hand/range grid and pot-odds drills. Dice and backgammon: Python simulations.

## Gaps (to fill with your incoming books)
- Game design classics to consider (check availability): Salen & Zimmerman, *Rules of Play*; Elias, Garfield & Gutschera,
  *Characteristics of Games*; Koster, *A Theory of Fun for Game Design*; Schell, *The Art of Game Design*.
- A real **game theory textbook** beyond the Very Short Introduction (e.g. an undergraduate text such as Osborne's or Maschler, Solan &
  Zamir's; check availability before choosing).
- **Backgammon** (none in the collection) if we include it in Stage 2.

## Questions for you
1. ~~Games replaces chess?~~ **Yes; chess is the first class** (answered 2026-10-05).
2. ~~Go timing?~~ **Answered:** after the chess family (stage 3); can move earlier if you want a contrast sooner.
3. ~~Backgammon?~~ **Yes** (2026-10-05): a 3–4 lesson unit in G401. Original reasoning kept below.
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
- Wikipedia, [Chaturanga](https://en.wikipedia.org/wiki/Chaturanga): "the prevailing view among chess historians is that chaturanga is the
  common ancestor of the board games chess, xiangqi … shogi"; earliest reference to the name c. AD 625 (Banabhatta's *Harsha Charita*).
- Tomašev, Paquet, Hassabis & Kramnik (2020), "Assessing Game Balance with AlphaZero: Exploring Alternative Rule Sets in Chess",
  [arXiv:2009.04374](https://arxiv.org/abs/2009.04374): "AlphaZero provides an alternative in silico means of game balance assessment."
- Wikipedia, [Komi (Go)](https://en.wikipedia.org/wiki/Komi_(Go)): 6.5 (Japanese/Korean) to 7.5 (Chinese/AGA); Black's first move is
  "generally considered to be between 5 and 7 points"; the half point prevents ties.
- Wikipedia, [Pie rule](https://en.wikipedia.org/wiki/Pie_rule): used in Hex, TwixT and others; the cutter "will make as equal a division as possible".
- Wikipedia, [Three-dimensional chess](https://en.wikipedia.org/wiki/Three-dimensional_chess): Raumschach (Ferdinand Maack, patented 1907, 5×5×5);
  of one 3D variant (Stereo Chess): "too complex for most people to learn and enjoy".
- Michael Sellers, *Advanced Game Design: A Systems Approach* (in collection, grade A, id `381eee38ce`).
- Wikipedia, [AlphaZero](https://en.wikipedia.org/wiki/AlphaZero): one self-play RL + MCTS algorithm mastered chess, shogi and Go
  "given no domain knowledge except the rules"; published in *Science*, December 2018.
- Berlekamp, Conway & Guy, *Winning Ways for Your Mathematical Plays*, vols. 1–3 (in collection; grades C, B, C).
