---
title: Random variables, cdfs and densities
subtitle: Two sittings on two days. Day 1 (~40 min): the reading, a re-teach and warm-ups. Day 2 (~40 min): the lesson. Three wins: say what a random variable is and what it induces; state the cdf's three properties and prove one; tell a pmf from a pdf and find a normalizing constant.
crumb: Statistics · Lesson 8 · C&B §1.4–1.6
index: Random variables, cdfs and densities (reading: C&B §1.4–1.6, pp. 27–37)
main: data-confidence=true
---
## Why this lesson
So far every probability has been about *events*: "the sum is 8", "the warden names B". But a statistician almost never asks
about one outcome of an experiment. They ask about a *number* computed from it: the count of heads, the sample mean, a test
statistic. Chapter 2 onward (expectations, transformations, every named distribution) is written entirely in that language. This
lesson builds it in three steps: what a random variable is, the one function that describes any random variable (the cdf), and
the two ways to describe it pointwise (the pmf and the pdf). Your Chapter 1 pretest got the calculations here right. The
formal side didn't land yet: "a random variable is a function", the cdf's three properties, and proofs that go past "more area"
to the definitions. So the formal side is the focus.

## Day 1, block 1: read first

::: reading
### Reading
**Casella & Berger, §1.4–1.6, pp. 27–37:** from the start of §1.4 ("Random Variables") through Theorem 1.6.5, stopping at §1.7 (Exercises).
About ten pages; they build on each other, so read them in one go.

- **Read closely:** Definition 1.4.1 and Example 1.4.3 (three coin tosses); Definition 1.5.1 (the cdf), Example 1.5.2 and the paragraph
  after it, just before Theorem 1.5.3 (why *right*-continuous); Theorem 1.5.3; Definitions 1.5.7 and 1.6.1, 1.6.3; Theorem 1.6.5.
- **Skim:** the end of §1.4 about uncountable sample spaces (the idea is in the formula, the measure-theory caveat is not for now);
  Example 1.5.6 (a cdf with jumps that also rises smoothly) and Definition 1.5.8 with Theorem 1.5.10 (identically distributed:
  same cdf, not the same variable). We'll come back to those two in the Chapter 1 summary.
- **Notation traps.** Capital \(X\) is the random variable (a function); lower-case \(x\) is a number it might take. So
  \(F_X(x) = P_X(X \le x)\) reads "the cdf of \(X\), evaluated at the number \(x\)". The subscript on \(P_X\) is the *induced*
  probability on the real line; the book drops it later and writes \(P(X \le x)\). In Definition 1.6.3 the integration variable
  is \(t\), a dummy, because \(x\) is already the upper limit.
- **Older notation you'll meet:** "\(X \sim F_X(x)\)" means "\(X\) has cdf \(F_X\)". Same for "\(X \sim f_X(x)\)".
:::

::: free read-rvfunc
In Example 1.4.3 (three coin tosses), what is the sample space, what does \(X\) do to each outcome, and how does the book get \(P_X(X = 1)\)?
--- rubric
S = the 8 strings HHH … TTT, equally likely; X maps each string to its number of heads (a function S → {0,1,2,3}); P_X(X = 1) =
P({HTT, THT, TTH}) = 3/8, the probability of the set of outcomes X sends to 1. Graded only on those points; this is the learner's own note.
:::

::: free read-rightcont
The paragraph just before Theorem 1.5.3 (after Example 1.5.2) says right-continuity is "a consequence of the definition". What would change if the cdf
were defined as \(P(X < x)\) instead?
--- rubric
The book's point: with ≤, F(x) includes the jump P(X = x) at x itself, so F is right-continuous; with <, F(x) would exclude the
jump and F would be left-continuous instead. Grade on the swap right ↔ left; any clear version is fine.
:::

::: free read-zero
§1.6 says that for a continuous random variable, \(P(X = x) = 0\) for every \(x\). In your own words: if every single value has
probability 0, how does \(X\) still take *some* value?
--- rubric
Probability is countably additive, not uncountably: the values form an uncountable set, so "sum of 0 over all x" isn't something the
axioms add up. Probabilities of intervals are positive, and come from the density integrated over the interval. Any answer that
points to intervals (or to uncountably many points not being summed) earns full marks.
:::

::: free read-surprise8
One thing that surprised or confused you.
:::

## Day 1, block 2: re-teach and warm-ups

### Re-teach: disjoint is not independent (5 minutes, from lesson 7)

Last lesson, one idea didn't land yet: whether disjoint events with positive probabilities can be independent. Here it is again, from a different angle.

::: worked
**Start with sets.** Roll two dice. \(A\) = the first die shows 6, \(B\) = the first die shows 1.
They can't both happen: \(A \cap B = \varnothing\). **Disjoint.**
--- step
**Now ask what \(B\) tells you about \(A\).** Before you learn anything, \(P(A) = 1/6\). Someone says "\(B\) happened". Now you know the
first die is 1, so \(A\) is impossible: \(P(A \mid B) = 0\). Learning \(B\) changed the chance of \(A\) from \(1/6\) to 0. That is the
opposite of "tells you nothing". **Dependent**, as strongly as two events can be.
--- step
**The product test says the same.** Independence is \(P(A \cap B) = P(A)P(B)\). Disjoint gives \(P(A \cap B) = 0\), but
\(P(A)P(B) = \frac16 \cdot \frac16 = \frac{1}{36} > 0\). The only way disjoint events can pass is if one of them has probability 0.
--- step
**The picture to keep.** *Disjoint* is about the sets (they don't overlap). *Independent* is about information (one says nothing about
the other). Independent events with positive probabilities **must** overlap, and by exactly the right amount: \(P(A)P(B)\).
:::

**Say it this way:** "Disjoint events with positive probability are dependent: if one happens, the other can't." **Not this:**
"Disjoint events are independent because they have nothing to do with each other."

::: categorize indep2-v4
Two fair dice are rolled. \(A\) = the first die shows 6. Sort each event by how it relates to \(A\).
- The first die shows 2 > Disjoint from A
- The second die shows 6 > Independent of A
- The sum is 7 > Independent of A
- The sum is 12 > Overlaps A, dependent
--- explain
First die 2: no overlap, so dependent, \(P = 0 \ne \frac1{36}\). Second die 6: \(\frac1{36} = \frac16\cdot\frac16\). Sum 7: only (6,1) is in both,
\(\frac1{36} = \frac16 \cdot \frac6{36}\), so independent, which surprises most people: whatever the first die shows, exactly one
second-die value makes 7. Sum 12: only (6,6), \(\frac1{36} \ne \frac16 \cdot \frac1{36}\); learning that the sum is 12 changes the chance that the first die shows 6 from 1/6 to 1. Independence asks only whether the *probability* changes: for sum 7 it doesn't (\(P(\text{sum } 7 \mid A) = \frac16 = P(\text{sum } 7)\)), for sum 12 it does.
:::

::: free indep2-v5
Can two events be both disjoint and independent? If yes, say exactly when; if no, say why not.
--- rubric
Yes, but only when at least one of them has probability 0: disjoint gives P(A ∩ B) = 0, independent needs P(A ∩ B) = P(A)P(B), so
P(A)P(B) = 0. Full marks: the condition "at least one has probability 0" with that reason. "Never" with the right reasoning for
positive probabilities is Got it, with the zero-probability case noted as missing. "Yes, always" is Not yet.
:::

### Warm-ups (from lesson 7)

The formula boxes on this page take fractions and expressions: type `1/7` or `(2/36)/(9/36)`; use `*` for ×, `/`, `^` for powers,
`sqrt( )`, `pi`, `exp( )`.

::: number condp-v5 answer=0.1429 tolerance=0.005
Three fair coins are tossed. Given that **at least one** coin shows heads, what is the probability that **all three** show heads?
(A fraction, or a decimal to two places or better.)
--- explain
"At least one head" rules out only TTT, leaving 7 equally likely outcomes, one of which is HHH: \(1/7\). Compare "given that the
*first* coin shows heads": that leaves 4 outcomes and the answer would be \(1/4\). The two conditions are different events.
:::

::: number bayescalc-v2 answer=0.931 tolerance=0.005
*Adapted from Casella & Berger, Example 1.3.6 and Exercise 1.41, numbers changed.* Morse code symbols are dots and dashes in the
proportion 2:3. Interference turns a dot into a dash with probability 1/10, and a dash into a dot with probability 1/10. A dash
is received. What is the probability a dash was sent? (A fraction, decimal or expression.)
--- explain
\(P(\text{dash sent}) = 3/5\), \(P(\text{dot sent}) = 2/5\). \(P(\text{dash recv}) = \frac{9}{10}\cdot\frac35 + \frac1{10}\cdot\frac25 = \frac{29}{50}\).
So \(P(\text{dash sent} \mid \text{dash recv}) = \dfrac{27/50}{29/50} = \dfrac{27}{29} \approx 0.931\).
:::

::: free mutual-v6
\(S = \{1, 2, 3, 4\}\), each outcome with probability \(1/4\). Let \(A = \{1, 2\}\) and \(B = \{1, 3\}\). Find an event \(C\) such that
\(A, B, C\) are pairwise independent but not mutually independent, and check all four product equations.
--- rubric
Two answers work: C = {1,4} or C = {2,3} (each has probability 1/2). Full marks: A, B checked (A ∩ B = {1}, 1/4 = 1/2 · 1/2), both pairs
with C checked (each intersection has one outcome, 1/4), and the triple shown to fail (1/4 ≠ 1/8 for {1,4}; 0 ≠ 1/8 for {2,3}). A
missing check with no false statement is Got it, noting what's missing.
:::

## Day 2: the lesson

Start here on the second day. Each section opens with what it needs from day 1's reading.

### 1 · A random variable is a function (from the reading)

::: recap
**Recap: a probability function and monotonicity.** \(P\) assigns numbers to events (subsets of the sample space \(S\)) obeying the
three axioms: \(P(A) \ge 0\), \(P(S) = 1\), and countable additivity for pairwise disjoint events. One consequence you'll use today
(C&B Theorem 1.2.9c, the ordering warm-up in lesson 7): if \(A \subset B\), then \(P(A) \le P(B)\).
:::

Toss a fair coin three times and count the heads. Before reading the steps: what kind of mathematical object is "the number of heads"?

::: worked
**List the outcomes.** \(S\) has 8 equally likely outcomes: HHH, HHT, HTH, THH, HTT, THT, TTH, TTT.
--- step
**"Number of heads" assigns a number to each outcome.** HHH ↦ 3; HHT, HTH, THH ↦ 2; HTT, THT, TTH ↦ 1; TTT ↦ 0. One outcome in,
one real number out. That's a function \(X : S \to \mathbb{R}\). Nothing about it is random: the randomness lives in which \(s\)
the experiment picks, not in \(X\).
--- step
**Questions about \(X\) are questions about sets of outcomes.** "\(X = 2\)" is shorthand for the event \(\{s \in S : X(s) = 2\} = \{\text{HHT}, \text{HTH}, \text{THH}\}\),
so \(P(X = 2) = 3/8\). In general, for a set \(A\) of real numbers,
$$P_X(X \in A) = P(\{s \in S : X(s) \in A\}).$$
--- step
**Name it.** A **random variable** is a function from a sample space \(S\) into the real numbers (C&B Definition 1.4.1). The
formula above defines the **induced probability function** \(P_X\): a new probability, living on the real line, built from \(P\)
on \(S\). Once you have \(P_X\) you can forget \(S\): every question about \(X\) is answered by \(P_X\).
:::

**Say it this way:** "A random variable is a function on the sample space; \(P(X = 2)\) is the probability of the set of outcomes
\(X\) sends to 2." **Not this:** "a random variable is a number that changes each trial". The *value* \(X(s)\) changes with the
outcome \(s\); \(X\) itself is a fixed function.

::: free rv-v5
From memory, without scrolling up: define a random variable, and write the formula for the probability it induces, \(P_X(X \in A)\), for a set \(A\) of real numbers.
--- rubric
Two points: (1) a random variable is a function from the sample space S into the real numbers; (2) P_X(X ∈ A) = P({s ∈ S : X(s) ∈ A}).
"A number that varies" or "a variable whose value is random" is Not yet. Both points present, small notation slips: Got it.
:::

::: categorize rv-v1
Two fair dice are rolled; \(S\) is the 36 ordered pairs. Which of these are random variables on \(S\)?
- The sum of the two dice > A random variable
- 1 if the dice match, 0 if not > A random variable
- The event "the sum is 7" > Not a random variable
- The probability that the sum is 7 > Not a random variable
--- explain
A random variable takes an outcome and returns a real number. The sum does; so does the match indicator (an *indicator* variable,
which you'll meet constantly). "The sum is 7" is an event: a set of outcomes, not a function. \(P(\text{sum is }7) = 1/6\) is
one number, the same for every outcome: it's what you compute *from* a random variable, not one itself.
:::

::: number rv-v2 answer=0.2778 tolerance=0.005
Two fair dice are rolled, and \(X\) = the absolute difference of the two faces (so (2,5) ↦ 3). What is \(P(X = 1)\)? (A fraction, or a decimal to two places or better.)
--- explain
\(\{X = 1\}\) is the set of pairs whose faces differ by 1: (1,2), (2,3), (3,4), (4,5), (5,6) and their reverses, 10 outcomes.
\(P(X = 1) = 10/36\).
:::

**Why \(P_X\) is a real probability** (the pretest asked this; the book leaves it to Exercise 1.45).
It has to satisfy the three axioms. Countable additivity is the only one with something to check:

::: order rv-v3
*Adapted from Casella & Berger, Exercise 1.45.* Put the steps in order. Claim: if \(A_1, A_2, \dots\) are pairwise disjoint sets of real numbers, then \(P_X(X \in \bigcup_i A_i) = \sum_i P_X(X \in A_i)\).
- Write \(E_i = \{s : X(s) \in A_i\}\), the set of outcomes \(X\) sends into \(A_i\).
- Each outcome \(s\) has a single value \(X(s)\), which can't lie in two disjoint sets, so the \(E_i\) are pairwise disjoint.
- An outcome lands in \(\bigcup_i A_i\) exactly when it lands in some \(A_i\), so \(\{s : X(s) \in \bigcup_i A_i\} = \bigcup_i E_i\).
- By Axiom 3 for \(P\), \(P(\bigcup_i E_i) = \sum_i P(E_i)\), which is \(\sum_i P_X(X \in A_i)\).
--- explain
Two facts about *preimages* (the preimage of a set of numbers is the set of outcomes \(X\) sends into it) carry it: preimages of disjoint sets are disjoint (because \(X\) is a function), and the preimage of a union is
the union of the preimages. Then the original \(P\)'s Axiom 3 does the work.
:::

### 2 · The cdf: one function that describes any random variable (from the reading)

You'd like one object that captures the whole distribution of \(X\), whether \(X\) counts heads or measures a time. Listing
\(P(X = x)\) won't do for a time, since every exact value has probability 0 (the third reading question). What always works is
asking for *intervals* \(P(X \le x)\).

::: worked
**Compute it for the coins.** With \(X\) = heads in three tosses: \(P(X \le x)\) is 0 for \(x < 0\); \(1/8\) for \(0 \le x < 1\)
(just TTT); \(1/8 + 3/8 = 1/2\) for \(1 \le x < 2\); \(7/8\) for \(2 \le x < 3\); and 1 for \(x \ge 3\). It's defined for *every*
real \(x\), not just 0–3: \(P(X \le 1.5) = 1/2\).
--- step
**Look at it.** A staircase: flat between the values \(X\) can take, jumping at 0, 1, 2, 3. The **size of each jump is
\(P(X = x)\)** at that point: \(1/8, 3/8, 3/8, 1/8\).
--- step
**Name it.** The **cumulative distribution function** (cdf) of \(X\) is \(F_X(x) = P_X(X \le x)\) for all real \(x\) (C&B
Definition 1.5.1). For an interval, \(P(a < X \le b) = F_X(b) - F_X(a)\), because \(\{X \le b\}\) is the disjoint union of
\(\{X \le a\}\) and \(\{a < X \le b\}\).
:::

::: plot x="-1:4" y="0:1.1" fns="(1+(x+0.0001)/abs(x+0.0001))/16 + 3*(1+(x-1+0.0001)/abs(x-1+0.0001))/16 + 3*(1+(x-2+0.0001)/abs(x-2+0.0001))/16 + (1+(x-3+0.0001)/abs(x-3+0.0001))/16" xlabel="x" ylabel="F(x)" caption="The cdf of X = number of heads in three fair tosses. Each jump is P(X = x); at a jump, F takes the upper value."
:::

What must every cdf look like? Three things, each with a one-line reason you can rebuild:

::: worked
**Limits 0 and 1.** As \(x \to -\infty\), the events \(\{X \le x\}\) shrink to \(\varnothing\), so \(F(x) \to 0\). As \(x \to \infty\)
they grow to all of \(S\), so \(F(x) \to 1\). (Passing the limit through \(P\) uses continuity of probability, which follows from
Axiom 3; C&B leaves that step to Exercise 1.48.)
--- step
**Nondecreasing.** If \(x < y\), anything with \(X \le x\) also has \(X \le y\). Bigger event, bigger probability. (You'll write
this one properly below.)
--- step
**Right-continuous.** Approach \(x\) from the right: the events \(\{X \le x + 1/n\}\) shrink to \(\{X \le x\}\) itself, so
\(F(x + 1/n) \to F(x)\). From the left, \(\{X \le x - 1/n\}\) grows only to \(\{X < x\}\), which misses the jump \(P(X = x)\). So
\(F\) can jump, but at a jump it takes the *upper* value, as the staircase above does.
--- step
**Name it.** C&B Theorem 1.5.3: \(F(x)\) is a cdf **if and only if** (a) \(\lim_{x\to-\infty}F(x) = 0\) and \(\lim_{x\to\infty}F(x) = 1\);
(b) \(F\) is nondecreasing; (c) \(F\) is right-continuous. The "if" direction (any such \(F\) is the cdf of *some* random variable)
is the deep half; the book leaves the easy half to Exercise 1.48 and skips the hard one. Then: \(X\) is **continuous** if \(F_X\) is continuous, and **discrete** if
\(F_X\) is a step function (Definition 1.5.7).
:::

**Say it this way:** "\(F_X(x)\) is the probability that \(X\) is at most \(x\)." **Not this:** "\(F_X(x)\) is the probability that
\(X\) equals \(x\)". That's the jump, not the height.

::: free cdf-v6
From memory: define the cdf \(F_X\) of a random variable \(X\), and state the three properties that make a function a cdf.
--- rubric
Definition: F_X(x) = P(X ≤ x) for every real x. Properties (C&B Theorem 1.5.3): (a) limits 0 at −∞ and 1 at +∞; (b) nondecreasing;
(c) right-continuous. "≤" written as "<", or "continuous" in place of "right-continuous", is Not yet on that part. All four present: Got it.
:::

::: categorize cdf-v1
*Adapted from Casella & Berger, Exercise 1.47.* Which of these are cdfs?
- \(F(x) = \tfrac12 + \tfrac1\pi \tan^{-1}(x)\) for all real \(x\) > A cdf
- \(F(x) = e^{-e^{-x}}\) for all real \(x\) > A cdf
- \(F(x) = 1 - e^{-x}\) for all real \(x\) > Not a cdf
- \(F(x) = 0\) for negative \(x\), \(F(0) = \tfrac12\), \(F(x) = 1\) for positive \(x\) > Not a cdf
--- explain
The first two are increasing with limits 0 and 1 (\(\tan^{-1}\) runs from \(-\pi/2\) to \(\pi/2\); \(e^{-x}\) runs from \(\infty\)
to 0). \(1 - e^{-x}\) for *all* \(x\) goes to \(-\infty\) on the left, so it fails (a); restricted to \(x \ge 0\) (and 0 below) it
would be a cdf. The last one fails (c): just right of 0 it's 1, but \(F(0) = \tfrac12\), so it isn't right-continuous at the jump.
:::

::: number cdf-v2 answer=0.657 tolerance=0.005
*From Casella & Berger, Example 1.5.4, with \(p\) set.* A coin with \(P(\text{heads}) = 0.3\) is tossed until the first head;
\(X\) = the number of tosses. Its cdf is \(F(x) = 1 - (1-p)^{\lfloor x \rfloor}\) for \(x \ge 1\) (0 for \(x < 1\)), where
\(\lfloor x \rfloor\) is the largest integer \(\le x\). What is \(F(3.7)\)? (A decimal to two places or better, or an expression.)
--- explain
\(\lfloor 3.7 \rfloor = 3\), so \(F(3.7) = 1 - 0.7^3 \approx 0.657\): the chance the first head comes within 3 tosses. The cdf is
flat between integers because \(X\) can't take values there.
:::

::: number cdf-v3 answer=0.3808 tolerance=0.005
*From Casella & Berger, Example 1.5.5.* \(X\) has the logistic cdf \(F(x) = \dfrac{1}{1 + e^{-x}}\). What is \(P(0 < X \le 2)\)?
(A decimal to two places or better, or an expression such as `1/(1+exp(-2))`.)
--- explain
\(P(a < X \le b) = F(b) - F(a) = \frac{1}{1+e^{-2}} - \frac{1}{1+e^{0}} \approx 0.881 - 0.5 = 0.381\).
:::

**Your proof** (the one proof task for this lesson). The pretest answer here was intuition; this time, from the definitions.

::: free cdf-v4
Prove that every cdf is nondecreasing: if \(F_X(x) = P(X \le x)\) and \(x < y\), then \(F_X(x) \le F_X(y)\). Name the set
fact and the probability fact you use.
--- rubric
Two things, each with its reason: (1) the set inclusion {s : X(s) ≤ x} ⊆ {s : X(s) ≤ y}, because X(s) ≤ x < y; (2) monotonicity of
P (A ⊆ B ⇒ P(A) ≤ P(B), C&B Theorem 1.2.9c, itself from Axioms 1 and 3). Full marks: both. Writing it as "more area" or "the cdf
adds probability" without the inclusion is Not yet; a missing citation with both steps present is Got it.
--- explain
Let \(x < y\). If \(X(s) \le x\), then \(X(s) \le y\), so \(\{s : X(s) \le x\} \subseteq \{s : X(s) \le y\}\). Probability is
monotone (if \(A \subseteq B\), then \(B = A \cup (B \cap A^c)\), disjoint, so \(P(B) = P(A) + P(B \cap A^c) \ge P(A)\)). Hence
\(F_X(x) \le F_X(y)\).
:::

### 3 · Pmf or pdf: describing \(X\) point by point (from the reading)

The staircase cdf told you \(P(X = x)\) directly: it's the jump. A continuous cdf has no jumps, so every \(P(X = x)\) is 0. What
replaces it?

::: worked
**Discrete: read off the jumps.** The **probability mass function** (pmf) is \(f_X(x) = P(X = x)\) for all \(x\) (C&B
Definition 1.6.1). For the three coins it's \(1/8, 3/8, 3/8, 1/8\) at 0, 1, 2, 3 and 0 elsewhere. Add it up to get the cdf:
\(F_X(x) = \sum_{k \le x} f_X(k)\).
--- step
**Continuous: replace the sum by an integral.** You want a function that plays the same role: \(F_X(x) = \int_{-\infty}^{x} f_X(t)\,dt\)
for all \(x\). That \(f_X\) is the **probability density function** (pdf) (C&B Definition 1.6.3). Where \(f_X\) is continuous,
\(f_X(x) = F_X'(x)\) by the fundamental theorem of calculus.
--- step
**A density is not a probability.** \(P(x < X \le x + h) = F_X(x + h) - F_X(x) \approx f_X(x)\,h\) for small \(h\): the density is
probability *per unit length*. So it can exceed 1. A density equal to 2 on \((0, \tfrac12)\) and 0 elsewhere (the uniform distribution on that interval) has total area \(2 \cdot \tfrac12 = 1\), so it's a legitimate pdf with values above 1. What can't
exceed 1 is the area under it over any interval.
--- step
**What makes a function a pmf or pdf.** C&B Theorem 1.6.5: \(f_X\) is a pdf (or pmf) of some random variable **if and only if**
(a) \(f_X(x) \ge 0\) for all \(x\), and (b) \(\sum_x f_X(x) = 1\) (pmf) or \(\int_{-\infty}^{\infty} f_X(x)\,dx = 1\) (pdf).
:::

::: plot x="-6:6" y="0:1.05" fns="exp(-x)/(1+exp(-x))^2; 1/(1+exp(-x))" labels="pdf f(x);cdf F(x)" show-area="true" shade="-inf:a" params="a=1:-4:4:0.5" vline="a" xlabel="x" caption="The logistic distribution (C&B Examples 1.5.5 and 1.6.4). Move a: the cdf's height at a equals the area under the pdf to the left of a. (The printed area starts at the left edge, −6, so it falls short of F(a) by F(−6), about 0.002.)"
:::

Theorem 1.6.5 is how you find a **normalizing constant**: a formula known up to a factor \(c\), with \(c\) chosen so that (b) holds.

::: worked
**Example.** \(f(x) = c\,x(1 - x)\) for \(0 < x < 1\), and 0 elsewhere. For which \(c\) is this a pdf?
--- step
**Condition (a):** \(x(1-x) > 0\) on \((0,1)\), so we need \(c \ge 0\).
--- step
**Condition (b):** \(\int_0^1 c\,x(1-x)\,dx = c\left(\tfrac12 - \tfrac13\right) = \tfrac{c}{6}\). Set it to 1: \(c = 6\).
Note the density's peak is \(f(\tfrac12) = 6 \cdot \tfrac14 = 1.5 > 1\), which is fine.
:::

::: categorize pmfpdf-v1
Sort each statement: true of a pmf only, a pdf only, or both?
- Its value at \(x\) is \(P(X = x)\) > Pmf only
- It can take values greater than 1 > Pdf only
- It is nonnegative and its total (sum or integral) is 1 > Both
- Its random variable has \(P(X = x) = 0\) for every \(x\) > Pdf only
--- explain
A pmf *is* point probability, so it's at most 1 and positive where \(X\) has mass. A pdf is probability per unit length: it can
exceed 1, and its random variable gives every single point probability 0. Theorem 1.6.5's two conditions apply to both.
:::

::: number pmfpdf-v2 answer=0 tolerance=0.0001
\(X\) has pdf \(f(x) = 2x\) for \(0 < x < 1\) (and 0 elsewhere), so \(f(0.9) = 1.8\). What is \(P(X = 0.9)\)?
--- explain
0. \(X\) is continuous, so every single value has probability 0: \(P(X = 0.9) \le P(0.9 - h < X \le 0.9) = F(0.9) - F(0.9 - h) \to 0\)
as \(h \to 0\). The 1.8 is a density (probability per unit length near 0.9), not a probability.
:::

::: math normc-v1 answer="1/2"
*Adapted from Casella & Berger, Exercise 1.54(a), interval changed.* \(f(x) = c \sin x\) for \(0 < x < \pi\), and 0 elsewhere.
What value of \(c\) makes \(f\) a pdf? (Type a number or expression, e.g. `2/pi`.)
--- explain
\(\sin x \ge 0\) on \((0, \pi)\), and \(\int_0^\pi \sin x\,dx = [-\cos x]_0^\pi = 2\). So \(2c = 1\), \(c = 1/2\).
:::

::: math normc-v3 answer="2/3"
A discrete \(X\) takes values \(0, 1, 2, \dots\) with pmf \(f(x) = c\,(1/3)^x\). What value of \(c\) makes \(f\) a pmf?
--- explain
A geometric series: \(\sum_{x=0}^{\infty} (1/3)^x = \dfrac{1}{1 - 1/3} = \dfrac32\). So \(c \cdot \frac32 = 1\), \(c = 2/3\). Same
condition as a pdf, with a sum in place of the integral.
:::

## Extra practice (optional)

**From Casella & Berger, Chapter 1 exercises** (easiest first; worked solutions are in the Casella & Berger solutions manual):
1. Exercise 1.50: verify the geometric partial-sum formula the book uses for the cdf in Example 1.5.4.
2. Exercise 1.54 (a) and (b) as printed: two more normalizing constants.
3. Exercise 1.53: the river-flood cdf; check it's a cdf, then find its pdf.
4. Exercise 1.47: prove each of the five listed functions is a cdf.
5. Exercise 1.45: show the induced probability \(P_X\) satisfies all three axioms (the ordering question in section 1 did the third).
6. Exercise 1.48: prove the necessity half of Theorem 1.5.3, all three properties (the limits and right-continuity need
   continuity of probability for monotone sequences of events).

**Extra reading:** John Haigh, *Probability: A Very Short Introduction*, Chapter 4 ("Chance experiments"): discrete and
continuous distributions, with "area represents probability" drawn out.

**Extra article:** Hossein Pishro-Nik, *Introduction to Probability, Statistics, and Random Processes*,
[§4.1.1 "Probability Density Function (PDF)"](https://www.probabilitycourse.com/chapter4/4_1_1_pdf.php). A free textbook
section on why the pmf stops working for a continuous random variable and how the density replaces it, with solved problems.

## Sources
- George Casella and Roger L. Berger, *Statistical Inference*, 2nd ed. (Duxbury, 2002), §1.4–1.6, pp. 27–37: Definitions 1.4.1,
  1.5.1, 1.5.7, 1.5.8, 1.6.1, 1.6.3; Theorems 1.5.3, 1.5.10, 1.6.5; Examples 1.4.3, 1.5.2, 1.5.4, 1.5.5, 1.5.6, 1.6.4; Exercises
  1.47–1.54; §1.2 Theorem 1.2.9 for monotonicity; §1.3 Examples 1.3.6 and Exercise 1.41 for the Morse warm-up.
- John Haigh, *Probability: A Very Short Introduction* (Oxford University Press, 2012), Chapter 4.
- Hossein Pishro-Nik, *Introduction to Probability, Statistics, and Random Processes* (Kappa Research, 2014), §4.1.1, https://www.probabilitycourse.com/chapter4/4_1_1_pdf.php
