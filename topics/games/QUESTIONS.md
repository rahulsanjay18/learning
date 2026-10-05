# Games: questions asked, with answers

## 2026-10-05 · "Can we model the diplomacy part of war as a game too, internal and external politics? Is that more probabilistic?"
**Yes**: it's one of the best-developed uses of game theory. But the uncertainty is mostly about **other minds**, not dice.

**Four kinds of uncertainty a designer can use:**
| Kind | Example | In diplomacy? |
|---|---|---|
| Chance | dice, card draws | rarely central |
| Hidden information | what the other side knows: its strength, its resolve | **central** (Fearon: private information) |
| Strategic uncertainty | what they'll *do*, especially with simultaneous moves | **central** |
| Commitment | will they keep a promise? | **central** (non-binding deals) |
So it's probabilistic *in the players' heads* (beliefs about the other side, updated as they act: Bayesian games), not in the dice.

**Key models:**
- **Bargaining model of war** (Fearon, "Rationalist Explanations for War", 1995): war is costly, so a deal both sides prefer
  should exist. Bargaining fails through **private information** (incentives to bluff about strength and resolve), **commitment
  problems** (can't credibly promise, e.g. during power shifts) and, rarely, **indivisible** stakes.
- **Two-level games** (Putnam, "Diplomacy and Domestic Politics: The Logic of Two-Level Games", *International Organization*,
  1988): a negotiator plays two games at once, abroad and at home. A deal needs the two sides' **win-sets** (deals each
  side's domestic politics will accept) to overlap. This is your "internal and external politics".
- **The board game Diplomacy** (Allan B. Calhamer, designed 1954, released 1959): **no dice at all**, simultaneous secret orders,
  non-binding alliances. All its uncertainty is human. In 2022 Meta's AI (CICERO) played it online at a level "ranking in the top
  10% of players", which makes it a good G504/AI case study.

**For your 3D game, design levers:** a negotiation phase; non-binding vs. binding agreements; simultaneous orders; hidden
objectives or hidden strength (private information); a domestic-support track that limits which deals a player can accept
(two-level games); fighting costly enough that a bargain usually exists, so breakdowns are interesting rather than routine.

Sources: Wikipedia, "Bargaining model of war" (Fearon 1995), "Two-level game theory" (Putnam 1988), "Diplomacy (game)" (Calhamer;
CICERO, 2022). Binmore, *Game Theory* VSI (in collection) for Bayesian games and commitment.
