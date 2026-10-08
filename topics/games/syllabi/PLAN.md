---
major: games
updated: 2026-10-08
---
## Overview
This major studies strategy games as a designer would, with one goal at the end: designing a balanced strategy game played in
three dimensions. You start with chess, then move outward one family at a time: tiny solved games, xiangqi and shogi (chess's
cousins), Go (a different family), games of chance (backgammon), and games of hidden information (poker). Then come the theories
that explain all of them: combinatorial game theory, classical game theory, and game-playing AI. Military strategy is part of the
major, treated as decision-making under uncertainty. The last stage is design: what makes a game deep, how to balance it, and
how to build one in 3D.

Games meets twice a week, and lessons are usually one meeting each. Two courses run at once: a game course (chess now) and the
strategy course.

## Three questions in every course
1. **What carries over?** At the end of each game course: what transferred from earlier games (tempo, material, king safety,
   initiative, endgames) and what broke.
2. **How does a computer play it?** Each game course ends with a lesson on the algorithm that plays it well: alpha-beta for chess,
   Monte Carlo tree search for Go, expectimax for backgammon, counterfactual regret minimization for poker. This thread ends with
   AlphaZero, which learned chess, shogi and Go from the rules alone.
3. **Why does this rule exist?** Many rules are there to balance the game: Go's komi, Hex's swap rule, shogi's drops, xiangqi's
   palace. You keep a design notebook of them. It becomes your toolkit for the capstone.

## The running project
Your 3D chess variant grows through the major:

| After | Project step |
|---|---|
| G101 | Version 0 on paper: board, piece movement in 3D, win condition. Play a few games against yourself |
| G102 | Measure it: branching factor and game length, with a short script |
| Each game course | Take or reject one idea from that game, and write down why in the design notebook |
| G504 | A rules engine and a search agent; self-play to measure first-move advantage and draw rate |
| G700 | Playtest, balance from data, revise |

## What you'll be able to do
**After Level I:** play chess, xiangqi, shogi, Go, backgammon and poker competently; explain what transfers between them; solve
small games exactly; use expected value, Nash equilibrium and backward induction; analyse a military campaign by aims, methods
and means.

**After Level II (optional):** compute combinatorial game values; build a game-playing agent with search and self-play; measure a
game's balance from data; design and balance a game of your own.

## How the major is organized
**Required (Level I):** G101 Chess → G102 Tiny games → G201 Xiangqi → G202 Shogi; G301 Go; G401 Decisions under chance; G402
Poker; G150 Strategy foundations; G501 Comparative strategy seminar; G503 Game theory.

**Optional:** G190 history of board games; G195 play log; G350 wargames; G360 diplomacy and politics as games; G398 closing conversation.

**Level II** (only if you sign up): G502 combinatorial game theory, G504 game-playing AI, G601 anatomy of strategy games, G602
balance, G603 designing in 3D, G700 capstone (your game), G598 closing conversation.

## Order
The game courses go G101 → G102 → G201 → G202, then G301, G401 → G402. G150 runs alongside the game courses the whole time. G503
comes after G401 because it needs expected value. G501 comes after you have played four families of games. Go can move earlier if
you want a contrast with chess sooner.

## What it takes to finish
- **Level I:** G101, G102, G150, G201, G202, G301, G401, G402, G501, G503.
- **Level II:** G502, G504, G601, G602, G603.

## Books
**In your library:** Seirawan and Silman, *Winning Chess Tactics*; Seirawan, *Winning Chess Endings*; Capablanca, *Chess
Fundamentals*; Echevarria, *Military Strategy: A Very Short Introduction*; Clausewitz, *On War*; Sun Tzu, *The Art of War*;
Polybius, *The Rise of the Roman Empire*; Freedman, *Strategy: A History*; Schelling, *Arms and Influence*; Paret (ed.), *Makers
of Modern Strategy*; Perla, *The Art of Wargaming*; Berlekamp, Conway and Guy, *Winning Ways*; Li, *First Syllabus on Xiangqi*;
Leggett, *Japanese Chess*; *A Go Guide by a Beginner*; Angelo, *Elements of Poker*; Acevedo, *Modern Poker Theory*; Binmore, *Game
Theory: A Very Short Introduction*; Russell and Norvig, *Artificial Intelligence: A Modern Approach*; Sellers, *Advanced Game Design*.

**Free online:** Sutton and Barto, *Reinforcement Learning: An Introduction*, 2nd ed.; the AlphaZero, MuZero and CFR papers.

**To buy, in the order you'll need them:** Albert, Nowakowski and Wolfe, *Lessons in Play* (G102, G502); a backgammon book, such as
Magriel, *Backgammon* (G401); Osborne, *An Introduction to Game Theory* (G503); Parlett, *The Oxford History of Board Games*
(G190); Sabin, *Simulating War* (G350); Elias, Garfield and Gutschera, *Characteristics of Games* (G601); Schreiber and Romero,
*Game Balance* (G602); Salen and Zimmerman, *Rules of Play* (G601).
