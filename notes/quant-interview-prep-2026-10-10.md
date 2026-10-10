# Is quant interview prep worth adding? (2026-10-10)

**Short answer: not as its own track now. Yes as practice material inside Statistics.**

## What quant interviews test
Quant loops (Jane Street, Citadel Securities, Two Sigma, HRT and similar) lean on fast probability, expected value,
brainteasers and mental math. Prep guides and candidate reports describe a timed mental-math screen at Jane Street,
then phone rounds of probability and brainteasers solved out loud, and harder later rounds with Markov chains,
martingales, optional stopping and generating functions [1][2][3]. These are prep sites and anonymous reviews, so the
details are anecdotal; the overall shape is consistent across them.

## Why it's not a career track for you right now (from your own plan)
1. **Your catalog already rates the quant tracks "watch, on hold"**: quant researcher (CR320) and low-latency C++
   quant dev (CR310). The reason recorded on 2026-10-07: top firms are mostly on-site and you want remote only
   (`topics/eng/catalog.json`). Today's check found nothing that changes that: Two Sigma's 2026 postings describe a
   hybrid policy, its internships are in the NYC office [4], and a Blind thread says full remote is rare and depends
   on seniority [5]. No official remote policy for Jane Street turned up.
2. **New job starts 2026-10-26, no job search for about 18 months** (HANDOFF). Interview prep is deadline-driven; drilling
   quant puzzles now would mostly decay before you could use them.
3. **The interview lane targets the big-tech staff bar** (coding, system design, behavioral, ML system design;
   `topics/eng/PROGRAM.md` §1a). Quant puzzle drills don't move any of those rounds much.

## Where it does pay off: Statistics
S201 (Casella & Berger Ch. 1) is next on conditional probability and independence, then random variables. The classic
quant problems (Bayes puzzles, expected-value games, coin-flip sequences, the "Fifty Challenging Problems" set)
are exactly that material, done fast and out loud. Using a few as **extra practice in S201/S202 lessons** costs
nothing, gives your 48%-right Statistics review set some fun variety, and builds the skill in case remote quant
roles ever open up for you. That's an intersection, not a new commitment (the focus-keeper rule).

My judgment (not a sourced fact): the expected career value of a dedicated quant track today is low *because of the
remote constraint*, not because of the content. If you drop that constraint, re-ask: then CR320 becomes a real
option, and your math + 6 years of AI is a strong profile for it.

## What I did
- Logged it in `notes/ideas.md` (feeds Statistics S201–S205 extra practice; full track stays parked with CR310/CR320).
- **Books to get (optional):** Mosteller, *Fifty Challenging Problems in Probability* (Dover); Zhou, *A Practical Guide
  to Quantitative Finance Interviews*. Neither is in `library/MANIFEST.csv` (checked; only Chan's *Quantitative Trading* is).

## Sources
1. techinterview.org, *Jane Street Interview Guide 2026*. https://www.techinterview.org/companies/jane-street/
2. eFinancialCareers, on electronic trading interviews. https://www.efinancialcareers.com/news/electronic-trading-interviews
3. QuantVault, *Jane Street Interview Process & Prep*. https://quantvault.org/jane-street-interview-process.html
4. Simplify job listing, Two Sigma Summer 2027 internship. https://simplify.jobs/p/d7896522-5218-4362-8092-60cacc29a642
5. Team Blind, "quant remote". https://www.teamblind.com/post/quant-remote-cxt0jacm
6. Bloomberg via BNN (2021, dated), Two Sigma hybrid trial. https://www.bnnbloomberg.ca/two-sigma-plans-to-test-remote-work-twice-a-week-after-labor-day-1.1577218
