---
title: The three axioms, and what follows from them
subtitle: A short lesson (read ~15 min, lesson ~15 min). One win: state Kolmogorov's axioms from memory and prove things from them alone.
crumb: Statistics · Lesson 6 · C&B §1.2.1–1.2.2
index: The three axioms (reading: C&B pp. 7–11)
main: data-confidence=true
---
## Why this lesson
Your Chapter 1 pretest: the calculations were right, and so was your Bonferroni proof. The one gap in §1.2 was stating the axioms
themselves ("I think I know this but I can't state them from memory"). This lesson is about that and nothing else.

## Block 1: read first

::: reading
### Reading
**Casella & Berger, §1.2.1–1.2.2, pp. 7–11:** from **Definition 1.2.4** through the proof of **Theorem 1.2.9**.

- Skip Definitions 1.2.1–1.2.3 (sigma algebras, pp. 6–7) unless you're curious. One line is enough: **\(\mathcal{B}\) is the
  collection of events** you're allowed to ask the probability of. So "for all \(A \in \mathcal{B}\)" just means "for every event \(A\)".
- Theorem 1.2.6 and Example 1.2.7 (the dart board) are optional.
- Read with paper: after each theorem, cover the proof and try it yourself first.
:::

::: free read-axioms
After reading, close the book and write the three axioms from memory.
--- rubric
(1) P(A) ≥ 0 for every event A; (2) P(S) = 1; (3) if A1, A2, … are pairwise disjoint, P(∪Ai) = Σ P(Ai). Graded only on whether
the three are there; this is the learner's own note.
:::

::: free read-fair
Example 1.2.5 (a fair coin): which step of getting \(P(\{H\}) = P(\{T\}) = 1/2\) comes from the axioms, and which doesn't?
--- rubric
From the axioms: P({H}) + P({T}) = 1 (S = {H} ∪ {T}, disjoint, Axioms 2 and 3). Not from the axioms: P({H}) = P({T}), a symmetry
assumption about this coin. Any nonnegative pair summing to 1 is a legal probability function.
:::

::: free read-cfirst
Theorem 1.2.8: why do the authors prove part (c), \(P(A^c) = 1 - P(A)\), first?
--- rubric
(b) P(A) ≤ 1 follows immediately from (c) plus Axiom 1 (P(Aᶜ) ≥ 0); (a) uses the same partition trick with S = S ∪ ∅.
:::

::: free read-surprise6
One thing that surprised or confused you.
:::

## Block 2: the lesson

### Warm-up (from lesson 4)

::: number wu-pow80 answer=2.8 tolerance=0.06
A two-sided test at \(\alpha = 0.05\) rejects when \(|z| > 1.96\). Roughly how many standard errors must the true effect be for the test to have 80% power? (Hint: \(P(Z > -0.84) = 0.80\).)
--- explain
\(1.96 + 0.84 = 2.8\) standard errors. That's the rule of thumb behind most sample-size calculations.
:::

### 1 · What's the least we must assume? (from the reading)

Think like Andrei Kolmogorov, who set out these axioms in 1933 [2]: you want *every* probability rule you use (complements, unions, Bonferroni) to follow from as few
assumptions as possible. What must a "probability" do, at minimum? Reveal one step at a time.

::: worked
**Nothing has negative probability.** Whatever probability means (long-run frequency, degree of belief), "−0.2 chance" means
nothing. So: \(P(A) \ge 0\) for every event \(A\). *(Axiom 1)*
--- step
**Something certainly happens.** The sample space \(S\) is the set of *all* outcomes, so one of them occurs. Fix the scale so
that certainty is 1: \(P(S) = 1\). *(Axiom 2)*
--- step
**Things that can't happen together add.** If \(A\) and \(B\) can't both occur, the chance of "\(A\) or \(B\)" should be
\(P(A) + P(B)\). Kolmogorov asks for this for *countably many* pairwise disjoint events at once:
\(P\big(\bigcup_{i=1}^\infty A_i\big) = \sum_{i=1}^\infty P(A_i)\). *(Axiom 3, countable additivity)*
--- step
**Why "countably many"?** Toss a coin until the first head. The events "first head on toss 1", "on toss 2", … are disjoint and
there are infinitely many. To get \(\sum_{n} (1/2)^n = 1\) you need additivity for infinitely many events at once. (Finite
additivity alone can't do it; that's the deFinetti debate on p. 9.)
--- step
**That's all.** Everything else is a *theorem*: \(P(A) \le 1\), \(P(A^c) = 1 - P(A)\), \(P(\varnothing) = 0\), the union rule,
Bonferroni. You don't assume them; you prove them.
:::

**Say it this way:** "A probability function is any \(P\) on the events with \(P(A) \ge 0\), \(P(S) = 1\), and countable
additivity over pairwise disjoint events." **Not this:** "Probabilities are between 0 and 1 and the complement is 1 minus" (true,
but those are consequences, not the axioms).

::: categorize ax-or-thm
Axiom or theorem? Sort each statement.
- \(P(A) \ge 0\) > Axiom
- \(P(S) = 1\) > Axiom
- \(P(A) \le 1\) > Theorem
- \(P(A^c) = 1 - P(A)\) > Theorem
--- explain
Only nonnegativity, \(P(S) = 1\) and countable additivity are assumed. The upper bound and the complement rule are Theorem 1.2.8 (b) and (c).
:::

::: recall ax-recall
Write the three axioms from memory, then reveal.
--- explain
1. \(P(A) \ge 0\) for every event \(A\). 2. \(P(S) = 1\). 3. If \(A_1, A_2, \dots\) are pairwise disjoint, \(P(\bigcup_i A_i) = \sum_i P(A_i)\). (C&B Definition 1.2.4.)
:::

### 2 · Proving things from the axioms alone (from the reading)

The book proves Theorem 1.2.8 (c) and (b). Here is (a), done the same way. Watch the move: **split something into disjoint pieces, then use Axiom 3.**

::: order empty-proof
Put the steps of the proof that \(P(\varnothing) = 0\) in order.
- \(S = S \cup \varnothing\), and \(S\) and \(\varnothing\) are disjoint.
- So by Axiom 3, \(P(S) = P(S) + P(\varnothing)\).
- \(P(S) = 1\) is a finite number (Axiom 2), so subtract it from both sides.
- Therefore \(P(\varnothing) = 0\).
--- explain
Partition, apply additivity, cancel. Theorem 1.2.9 (a) and (b) use exactly the same move with \(B = (B \cap A) \cup (B \cap A^c)\).
:::

### 3 · Your proof (a book exercise)

::: free ex-1-13
*Adapted from Casella & Berger, Exercise 1.13.* If \(P(A) = 1/3\) and \(P(B^c) = 1/4\), can \(A\) and \(B\) be disjoint? Explain, citing which axiom or theorem each step uses.
--- rubric
P(B) = 1 − P(Bᶜ) = 3/4 (complement rule, Thm 1.2.8c). If A and B were disjoint, P(A ∪ B) = P(A) + P(B) = 1/3 + 3/4 = 13/12
(additivity, Axiom 3), but P(A ∪ B) ≤ 1 (Thm 1.2.8b, or monotonicity). Contradiction, so they can't be disjoint. Full marks: the
complement step, the additivity step and the bound, each with its reason.
:::

## Optional homework
*Casella & Berger, Exercise 1.12(a):* show that countable additivity implies finite additivity. (Hint: pad a finite list of disjoint
sets with empty sets, and use \(P(\varnothing) = 0\).) Nothing later depends on it.

## Next
Lesson 7: conditional probability and independence (§1.3), including the difference between pairwise and mutual independence.

## Sources
- George Casella & Roger L. Berger, *Statistical Inference*, 2nd ed., §1.2.1–1.2.2, pp. 7–11 (Definition 1.2.4, Example 1.2.5, Theorems 1.2.8–1.2.9; the Axiom of Finite Additivity, p. 9); Exercises 1.12, 1.13. In your library (id f9dc4d1d4c).
