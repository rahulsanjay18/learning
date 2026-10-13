---
title: Conditional probability, Bayes' rule, and independence
subtitle: Two blocks (read ~25 min, lesson ~25 min). Two wins: derive Bayes' rule and say exactly what it assumes; tell pairwise from mutual independence, with a counterexample.
crumb: Statistics · Lesson 7 · C&B §1.3
index: Conditional probability and independence (reading: C&B §1.3, pp. 20–27)
main: data-confidence=true
---
## Why this lesson
Every statistical method you'll meet later (likelihoods, posteriors, tests, the "independent and identically distributed" sample)
is built from two moves: conditioning on what you've seen, and multiplying probabilities of things that don't affect each
other. Your Chapter 1 pretest showed the calculations are already solid (the color-blindness Bayes problem was right). Two
things weren't: the Bayes' rule proof leaned on independence and never said which probabilities must be positive, and
"pairwise independent" was taken to mean "independent". This lesson fixes exactly those two.

## Block 1: read first

::: reading
### Reading
**Casella & Berger, §1.3, pp. 20–27:** from the start of the section through **Example 1.3.13** (three coin tosses), stopping at §1.4.

- **Read closely:** Definition 1.3.2, equations (1.3.3)–(1.3.5), Theorem 1.3.5 (Bayes' rule), Definition 1.3.7, Theorem 1.3.9,
  Examples 1.3.10 and 1.3.11, Definition 1.3.12.
- **Skim:** the algebra in Example 1.3.3 (only the idea matters: the conditional probability rises as aces are drawn) and the
  coding example 1.3.6 (we redo one like it below).
- **Notation traps.** Equation (1.3.5) is Bayes' rule for two events; Theorem 1.3.5 is the same rule for a whole *partition*
  \(A_1, A_2, \dots\), and its denominator \(\sum_j P(B \mid A_j)P(A_j)\) is just \(P(B)\) written out piece by piece.
  The theorem says "let \(B\) be any set" and leaves the positivity conditions unstated: it needs \(P(B) > 0\) and each \(P(A_j) > 0\),
  or the conditional probabilities in it don't exist. In Definition 1.3.12, "any subcollection" means every pair, every triple, and so on up to all \(n\) events at once.
- Example 1.3.11 (letters): the sample space has 9 outcomes, each with probability \(1/9\). The book's "it is easy to count"
  hides the counting; do it on paper.
:::

::: free read-condp
Definition 1.3.2 requires \(P(B) > 0\). Why, and what does conditioning on \(B\) do to the sample space?
--- rubric
P(B) is the denominator, so P(B) = 0 would divide by zero. Conditioning makes B the new sample space: P(B | B) = 1, and every other
event is measured by the part of it inside B. Graded only on those two points; this is the learner's own note.
:::

::: free read-prisoner
Example 1.3.4 (three prisoners): what exactly was prisoner A's mistake?
--- rubric
A treated "the warden says B dies" (W) as if it were the event "B is not pardoned" (Bᶜ). They differ: when A is pardoned the warden
could have named C instead, so P(W | A) = 1/2, and P(A | W) = 1/3, not 1/2.
:::

::: free read-twofail
Examples 1.3.10 and 1.3.11 each knock out a candidate definition of "A, B, C are independent". Which candidate does each one knock out?
--- rubric
1.3.10 (two dice): the triple product P(A∩B∩C) = P(A)P(B)P(C) holds, but two of the three pairs fail, so the triple product alone is too weak.
1.3.11 (letters): every pair is independent, but the triple product fails, so "all pairs" is too weak too.
:::

::: free read-surprise7
One thing that surprised or confused you.
:::

## Block 2: the lesson

### Warm-up (from lesson 6)

::: recap
**Recap: the three axioms.** A probability function \(P\) satisfies (1) \(P(A) \ge 0\) for every event \(A\); (2) \(P(S) = 1\);
(3) if \(A_1, A_2, \dots\) are pairwise disjoint, \(P(\bigcup_i A_i) = \sum_i P(A_i)\). Everything else, including
\(P(A^c) = 1 - P(A)\) and \(P(A) \le 1\), is a theorem proved from these. Today uses Axiom 3 twice: in the law of total
probability and in the independence of complements.
:::

::: order wu-mono
Put the steps of this proof in order. Claim (C&B Theorem 1.2.9c): if \(A \subset B\), then \(P(A) \le P(B)\).
- Since \(A \subset B\), write \(B = A \cup (B \cap A^c)\); the two pieces are disjoint.
- By Axiom 3, \(P(B) = P(A) + P(B \cap A^c)\).
- Since \(P(B \cap A^c) \ge 0\) by Axiom 1, \(P(B) \ge P(A)\).
--- explain
The same partition trick as the complement rule: split the bigger set into disjoint pieces (\(A \subset B\) is what makes \(A\) one of them), add (Axiom 3), then drop a
nonnegative piece (Axiom 1).
:::

### 1 · Conditioning: shrink the sample space (from the reading)

Two fair dice are rolled. Someone peeks and tells you "the sum is 8". What's the chance you rolled doubles? Reveal one step at a time.

::: worked
**List what's still possible.** Of the 36 equally likely outcomes, only five have sum 8: (2,6), (3,5), (4,4), (5,3), (6,2).
The other 31 are ruled out.
--- step
**They're still equally likely.** Being told "sum is 8" gives no reason to prefer (3,5) over (4,4), so each of the five gets
\(1/5\). Only (4,4) is doubles: the answer is \(1/5\).
--- step
**Write it with the old probabilities.** \(P(\text{doubles and sum 8}) = 1/36\) and \(P(\text{sum 8}) = 5/36\). Their ratio is
\(\dfrac{1/36}{5/36} = \dfrac{1}{5}\): dividing by \(P(B)\) rescales the surviving outcomes so that they total 1 again.
--- step
**Name it.** For events \(A, B\) with \(P(B) > 0\), the **conditional probability of \(A\) given \(B\)** is
$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}.$$
(C&B Definition 1.3.2.) \(B\) becomes the new sample space: \(P(B \mid B) = 1\). Why \(P(B) > 0\)? It's a denominator.
--- step
**A check that it's a real probability.** For fixed \(B\), the function \(A \mapsto P(A \mid B)\) satisfies all three axioms
(C&B Exercise 1.35), so every theorem from lesson 6 (complements, unions, Bonferroni) also holds *given* \(B\).
:::

**Say it this way:** "\(P(A \mid B)\) is the probability of \(A\) once we know \(B\) happened." **Not this:** "the probability
that \(A\) causes \(B\)", or "\(P(A\) and \(B)\)". Conditioning is about information, not causes, and \(P(A \mid B)\) is
never smaller than \(P(A \cap B)\), since you divide by \(P(B) \le 1\).

The formula boxes below take fractions and expressions: type `3/7` or `(2/36)/(9/36)`; use `*` for ×, `/`, `^` for powers.

::: number condp-v1 answer=0.4545 tolerance=0.0005
Two fair dice are rolled. Given that at least one die shows a 6, what is the probability that the sum is 10 or more? (A fraction or a decimal.)
--- explain
Outcomes with at least one 6: 6 + 6 − 1 = 11 (the pair (6,6) is counted once). Of those, the sum is at least 10 for (4,6), (6,4),
(5,6), (6,5), (6,6): 5 of them. So the answer is \(5/11\). Same as the formula: \(\frac{5/36}{11/36}\).
:::

### 2 · Bayes' rule, and exactly what it assumes (from the reading)

You know \(P(B \mid A)\) and want \(P(A \mid B)\): "turn the conditioning around". Before reading the steps, try it: what's the
one definition you're allowed to use?

::: worked
**Write the intersection two ways.** If \(P(B) > 0\), Definition 1.3.2 multiplied out gives \(P(A \cap B) = P(A \mid B)\,P(B)\).
If \(P(A) > 0\), the same definition with the roles swapped gives \(P(A \cap B) = P(B \mid A)\,P(A)\). (C&B (1.3.3) and (1.3.4).)
--- step
**Both equal the same number.** So \(P(A \mid B)\,P(B) = P(B \mid A)\,P(A)\). Divide by \(P(B)\), allowed because \(P(B) > 0\):
$$P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)}.$$
--- step
**Count the assumptions.** \(P(B) > 0\) so that \(P(A \mid B)\) exists and we can divide. \(P(A) > 0\) so that \(P(B \mid A)\)
exists at all. **Nothing else.** In particular, no independence: if \(A\) and \(B\) were independent, \(P(A \mid B)\) would just
be \(P(A)\) and the rule would have nothing to tell you.
--- step
**Fill in the denominator.** Often \(P(B)\) isn't given directly. Split \(B\) along a partition \(A_1, A_2, \dots\) of \(S\)
(disjoint, union \(S\)): \(B = \bigcup_j (B \cap A_j)\), and the pieces are disjoint, so Axiom 3 gives
\(P(B) = \sum_j P(B \cap A_j) = \sum_j P(B \mid A_j)\,P(A_j)\) (each \(P(A_j) > 0\)). This is the **law of total probability**.
--- step
**Name it.** Putting the two together is C&B Theorem 1.3.5, **Bayes' rule**: for a partition \(A_1, A_2, \dots\) with each \(P(A_j) > 0\), and any \(B\) with \(P(B) > 0\),
$$P(A_i \mid B) = \frac{P(B \mid A_i)\,P(A_i)}{\sum_j P(B \mid A_j)\,P(A_j)}.$$
:::

**Say it this way:** "Bayes' rule follows from the definition of conditional probability alone, for any events with
\(P(A) > 0\) and \(P(B) > 0\)." **Not this:** "Bayes' rule assumes \(A\) and \(B\) are independent."

::: categorize bayes-v1
Deriving \(P(A \mid B) = P(B \mid A)P(A)/P(B)\) from the definition of conditional probability: which of these does the derivation need?
- \(P(B)\) is positive > Needed
- \(P(A)\) is positive > Needed
- \(A\) and \(B\) independent > Not needed
- \(A\) and \(B\) disjoint > Not needed
--- explain
Only the two positivity conditions: \(P(B) > 0\) for \(P(A \mid B)\) to exist and for the division, \(P(A) > 0\) for \(P(B \mid A)\)
to exist. Independence would make the rule trivial; disjointness would make both sides 0.
:::

::: find-error bayes-v2
A student "proves" Bayes' rule. Which step is wrong?
- Assume \(P(A) > 0\) and \(P(B) > 0\).
- By the definition, \(P(A \mid B) = P(A \cap B)/P(B)\).
- [x] Since \(P(A \cap B) = P(A)P(B)\), this is \(P(A)P(B)/P(B)\).
- And \(P(B \mid A) = P(A \cap B)/P(A)\), so \(P(A \cap B) = P(B \mid A)P(A)\); substitute into the second line.
--- explain
\(P(A \cap B) = P(A)P(B)\) is independence, which isn't given (and would make the result just \(P(A \mid B) = P(A)\)). The last
line is the right move: rewrite \(P(A \cap B)\) using the *other* conditional probability.
:::

Now a calculation, the kind Bayes' rule is for. Here's one fully worked first, then yours.

::: worked
**Example (adapted from C&B Exercise 1.34).** Litter 1 has 2 brown and 1 gray pup; litter 2 has 3 brown and 2 gray. Pick a
litter at random (each \(1/2\)), then a pup at random from it. The pup is brown. Which litter did it come from?
--- step
**Partition:** \(L_1, L_2\), each probability \(1/2\). **Likelihoods:** \(P(\text{brown} \mid L_1) = 2/3\), \(P(\text{brown} \mid L_2) = 3/5\).
--- step
**Total probability:** \(P(\text{brown}) = \frac{2}{3}\cdot\frac12 + \frac35\cdot\frac12 = \frac13 + \frac{3}{10} = \frac{19}{30}\).
--- step
**Bayes:** \(P(L_1 \mid \text{brown}) = \dfrac{1/3}{19/30} = \dfrac{10}{19} \approx 0.53\). A brown pup is slight evidence for litter 1,
because brown is a slightly larger share there.
:::

::: number bayescalc-v1 answer=0.6774 tolerance=0.0005
*Adapted from Casella & Berger, Exercise 1.34, numbers changed.* Litter 1 has 3 brown and 2 gray pups; litter 2 has 2 brown and
5 gray. A litter is chosen at random (each with probability 1/2), then a pup at random from that litter. The pup is brown.
What is the probability it came from litter 1? (A fraction, decimal or expression.)
--- explain
\(P(\text{brown}) = \frac12\cdot\frac35 + \frac12\cdot\frac27 = \frac{31}{70}\), so \(P(L_1 \mid \text{brown}) = \dfrac{3/10}{31/70} = \dfrac{21}{31}\approx 0.677\).
:::

**Your proof** (the one proof task for this lesson):

::: free bayes-v3
Prove Bayes' rule in its partition form (C&B Theorem 1.3.5): if \(A_1, A_2, \dots\) partition \(S\), each \(P(A_j) > 0\), and
\(P(B) > 0\), then \(P(A_i \mid B) = \dfrac{P(B \mid A_i)P(A_i)}{\sum_j P(B \mid A_j)P(A_j)}\). Use only the definition of
conditional probability and the axioms, and say where each assumption is used.
--- rubric
Full marks needs four things, each with its reason: (1) numerator: P(A_i ∩ B) = P(B | A_i)P(A_i), by the definition, needs
P(A_i) > 0; (2) B = ∪_j (B ∩ A_j) because the A_j cover S; (3) the pieces are disjoint because the A_j are, so P(B) = Σ_j P(B ∩ A_j)
by Axiom 3 (countable additivity); (4) each piece rewritten as P(B | A_j)P(A_j), then divide using P(B) > 0. Using independence
anywhere is a false step (Not yet). A proof that skips a reason but has no false step is Got it with the reason noted.
--- explain
\(P(A_i \mid B) = P(A_i \cap B)/P(B)\) (definition; \(P(B) > 0\)). Numerator: \(P(A_i \cap B) = P(B \mid A_i)P(A_i)\) (definition;
\(P(A_i) > 0\)). Denominator: since the \(A_j\) cover \(S\), \(B = \bigcup_j (B \cap A_j)\); since they are disjoint, so are the
\(B \cap A_j\), and Axiom 3 gives \(P(B) = \sum_j P(B \cap A_j) = \sum_j P(B \mid A_j)P(A_j)\). Substitute both.
:::

### 3 · Independence of two events (from the reading)

::: worked
**Start from what "no effect" should mean.** Learning \(B\) happened doesn't change the chance of \(A\): \(P(A \mid B) = P(A)\).
--- step
**Multiply out.** With \(P(B) > 0\), that's \(P(A \cap B)/P(B) = P(A)\), i.e. \(P(A \cap B) = P(A)P(B)\).
--- step
**Why make the product the definition?** It's symmetric in \(A\) and \(B\) (no "given" direction), it needs no positivity
condition, and it extends to more events. So C&B Definition 1.3.7: \(A\) and \(B\) are **(statistically) independent** if
\(P(A \cap B) = P(A)P(B)\).
--- step
**It survives complements** (C&B Theorem 1.3.9): if \(A, B\) are independent, so are \(A, B^c\); \(A^c, B\); and \(A^c, B^c\).
Proof of the first: \(P(A \cap B^c) = P(A) - P(A \cap B) = P(A) - P(A)P(B) = P(A)P(B^c)\).
:::

**Say it this way:** "Independent means knowing one tells you nothing about the other." **Not this:** "independent means they
can't happen together"; that's *disjoint*, and for events with positive probability it's the opposite of independence.

::: choice indep2-v2 shuffle=true
Events \(A\) and \(B\) are disjoint, with \(P(A) = 0.3\) and \(P(B) = 0.4\). Are \(A\) and \(B\) independent?
- [x] No, they are dependent
- [ ] Yes, they are independent
- [ ] Can't tell from this
--- hint
Compare \(P(A \cap B)\) for disjoint events with \(P(A)P(B)\).
--- explain
Disjoint means \(P(A \cap B) = 0\), but \(P(A)P(B) = 0.12\). Learning \(A\) happened tells you \(B\) certainly didn't: that's maximal
dependence. Disjoint events with positive probabilities are never independent (C&B Exercise 1.39).
:::

::: number indep2-v1 answer=0.4914 tolerance=0.0005
*Beyond the reading: a second dice bet, the companion to C&B Example 1.3.8.* A pair of fair dice is thrown 24 times, independently.
What is the probability of at least one double six? Answer as a decimal (0.10 means 10%); expressions like `1-(5/6)^4` are fine.
--- explain
"At least one" is the complement of "none". Each throw misses double six with probability \(35/36\), and independence turns
"all 24 miss" into a product: \(1 - (35/36)^{24} \approx 0.491\). Just under a half, so it loses at even money,
even though 4 rolls of one die (C&B Example 1.3.8) wins.
:::

### 4 · Three or more events: pairwise is not mutual (from the reading, plus one example beyond it)

This is the main event. You want a definition of "\(A, B, C\) are independent" that lets you multiply any of them together. Let's
try the two obvious candidates and break both, the way the book does.

::: worked
**Candidate 1: the triple product,** \(P(A \cap B \cap C) = P(A)P(B)P(C)\). C&B Example 1.3.10 (two dice; \(A\) = doubles,
\(B\) = sum between 7 and 10, \(C\) = sum is 2, 7 or 8) satisfies it: \(1/36 = \frac16\cdot\frac12\cdot\frac13\). But
\(P(B \cap C) = P(\text{sum 7 or 8}) = 11/36 \ne \frac12\cdot\frac13\), and \(A, B\) fails too (only \(A, C\) happens to hold). The triple product can hold while pairs fail. **Too weak.**
--- step
**Candidate 2: all pairs independent.** (Beyond the reading: a smaller example than the book's.) Try the smallest example there is. Toss a fair coin twice. \(A\) = first toss heads,
\(B\) = second toss heads, \(C\) = the two tosses match. Each has probability \(1/2\). Before revealing: is each pair
independent? Is the triple?
--- step
**Pairs: yes.** \(A \cap B = \{HH\}\), \(A \cap C = \{HH\}\), \(B \cap C = \{HH\}\): each has probability \(1/4 = \frac12\cdot\frac12\).
--- step
**Triple: no.** \(A \cap B \cap C = \{HH\}\), probability \(1/4\), but \(P(A)P(B)P(C) = 1/8\). Why: once you know \(A\) and
\(B\), you know \(C\) for certain. Any two of these events say nothing about the third alone, but together they settle it.
**Too weak as well.** (C&B Example 1.3.11, the letters, is the same phenomenon with 9 outcomes.)
--- step
**Name it.** \(A_1, \dots, A_n\) are **mutually independent** if *every* subcollection multiplies:
\(P(A_{i_1} \cap \dots \cap A_{i_k}) = P(A_{i_1}) \cdots P(A_{i_k})\) for every choice of \(2 \le k \le n\) distinct indices
(C&B Definition 1.3.12). For three events that is four equations: three pairs and the triple. **Pairwise independent** means
only the pair equations hold.
:::

**Say it this way:** "Pairwise independent is weaker than mutually independent: every pair can be independent while the events
together are not." **Not this:** "If every pair is independent, they're independent." When a statistics book calls a
collection of events "independent" without a qualifier, it means *mutually*.

::: categorize mutual-v1
*From Casella & Berger, Example 1.3.11.* The sample space is the nine strings aaa, bbb, ccc, abc, bca, cba, acb, bac, cab, each
with probability \(1/9\). \(A_i\) = the \(i\)th letter is a. Sort each equation.
- \(P(A_1 \cap A_2) = P(A_1)P(A_2)\) > Holds
- \(P(A_1 \cap A_3) = P(A_1)P(A_3)\) > Holds
- \(P(A_2 \cap A_3) = P(A_2)P(A_3)\) > Holds
- \(P(A_1 \cap A_2 \cap A_3) = P(A_1)P(A_2)P(A_3)\) > Fails
--- explain
Each \(A_i\) has three strings (aaa and two permutations), so \(P(A_i) = 1/3\). Any two of them meet only in aaa: \(1/9 = \frac13\cdot\frac13\).
All three also meet only in aaa: \(1/9 \ne 1/27\). Pairwise independent, not mutually independent.
:::

::: number mutual-v2 answer=11
How many product equations must be checked to show that four events \(A_1, A_2, A_3, A_4\) are mutually independent?
--- hint
Count the subcollections of size 2, 3 and 4.
--- explain
One equation per subcollection of size at least 2: \(\binom42 + \binom43 + \binom44 = 6 + 4 + 1 = 11\), which is \(2^4 - 4 - 1\).
:::

::: free mutual-v3
*Your counterexample.* Let \(S = \{1, 2, 3, 4\}\) with each outcome having probability \(1/4\) (a fair four-sided die). Find three
events \(A, B, C\) that are pairwise independent but not mutually independent, and check all four equations.
--- rubric
Any valid triple, with all four equations checked. Standard answer: A = {1,2}, B = {1,3}, C = {1,4}; each has probability 1/2, every
pairwise intersection is {1} with probability 1/4 = (1/2)(1/2), but A∩B∩C = {1} has probability 1/4 ≠ 1/8. Full marks: three pair
checks and the failed triple. Missing one pair check but no false statement: Got it, note what's missing.
--- explain
One answer: \(A = \{1,2\}\), \(B = \{1,3\}\), \(C = \{1,4\}\). Each has probability \(1/2\); every pair meets in \(\{1\}\), probability
\(1/4 = \frac12\cdot\frac12\); but \(A \cap B \cap C = \{1\}\) too, probability \(1/4 \ne 1/8\).
:::

## Extra practice (optional)

**From Casella & Berger, Chapter 1 exercises** (easiest first; worked solutions are in the Casella & Berger solutions manual):
1. Exercise 1.38 (a)–(d): four short identities for conditional probability.
2. Exercise 1.40: finish Theorem 1.3.9 by proving parts (b) and (c).
3. Exercise 1.36: shots at a target; "at least twice, given at least once".
4. Exercise 1.37 (a): the three prisoners when the warden is not indifferent. For which values of \(\gamma\) does A's chance change?
5. Exercise 1.35: prove that \(P(\cdot \mid B)\) satisfies Kolmogorov's axioms.

**Extra reading:** John Haigh, *Probability: A Very Short Introduction*, Chapter 2 ("The workings of probability"), the sections
"The Multiplication Law" through "More than two events". The same ideas told with cards and coins, with no measure theory.

**Extra article:** Grant Sanderson (3Blue1Brown), ["Bayes' theorem"](https://www.3blue1brown.com/lessons/bayes-theorem).
Bayes' rule as a picture: a unit square, a strip of width \(P(H)\), and evidence that cuts the square down. It starts from
Kahneman and Tversky's "Steve the librarian" puzzle, which is a good test of whether you'd use the prior without being told to.

## Sources
- George Casella and Roger L. Berger, *Statistical Inference*, 2nd ed. (Duxbury, 2002), §1.3, pp. 20–27: Definitions 1.3.2,
  1.3.7, 1.3.12; Theorems 1.3.5, 1.3.9; Examples 1.3.1–1.3.13; Exercises 1.33–1.41, p. 42–43; §1.2 Theorem 1.2.9 for the warm-up.
- John Haigh, *Probability: A Very Short Introduction* (Oxford University Press, 2012), Chapter 2.
- Grant Sanderson, "Bayes' theorem", 3Blue1Brown, https://www.3blue1brown.com/lessons/bayes-theorem
- The two-coin example of pairwise but not mutual independence is a standard one, usually credited to S. N. Bernstein.
