---
title: Chapter 1 summary: independence again, densities, and the whole chapter on one page
subtitle: Two days. Day 1 (about 30 minutes): the reading and Parts 1–3. Day 2 (about 15 minutes): Parts 4–5. Three wins: say what independence means and test it by computing both sides; say what a pdf's value is; state Chapter 1's main results from memory and what each is for.
crumb: Statistics · Lesson 9 · C&B Chapter 1 summary
index: Chapter 1 summary (reading: C&B §1.3 pp. 25–26, §1.5 pp. 33–34)
main: data-confidence=true
---
## Why this lesson
Chapter 1 is the ground everything else stands on. Every later chapter computes expectations, transformations and sampling
distributions, and almost every one assumes the observations are *independent* and *identically distributed*. Before moving on,
this lesson does three things: it fixes the two ideas that haven't landed yet (what independence means, and what a density's value
means), it teaches the one Chapter 1 definition we skipped (identically distributed), and it puts the whole chapter on one page
so you can recall it without the book.

## Read first (about 8 minutes)

::: reading
### Reading
**Casella & Berger, two short slices:**
1. **§1.3, pp. 25–26:** from "In some cases it may happen that the occurrence of a particular event, B, has no effect on the
   probability of another event, A" through the proof of **Theorem 1.3.9**. Stop at "Independence of more than two events".
   That's the motivation for independence, Definition 1.3.7, Example 1.3.8 (de Méré's dice) and Theorem 1.3.9 with its proof of part (a).
2. **§1.5, pp. 33–34:** **Definition 1.5.8**, **Example 1.5.9** and the statement of **Theorem 1.5.10**. Skip the proof of 1.5.10's
   hard direction (the book says it needs more machinery).

**Notation traps.** The scan of this book often prints \(P(A)\) as "peA)" and \(P(B)\) as "PCB)"; in your copy they're ordinary
\(P(A)\), \(P(B)\). In Theorem 1.3.9, \(B^c\) is the complement of \(B\). In Definition 1.5.8, \(\mathcal{B}\) is the collection of
sets of real numbers we're allowed to ask about (intervals, their countable unions and so on); read "every set \(A \in \mathcal{B}\)"
as "every set of numbers you'd ever ask about".

Answer the boxes below as you read, a sentence or two each.
:::

::: free read-motive
Casella & Berger start independence from \(P(A \mid B) = P(A)\), then take \(P(A \cap B) = P(A)P(B)\) as the definition. In your own
words: what does the first form *say*, and why do they prefer the second as the definition?
--- rubric
Reading note; reply to it. First form: learning that B happened leaves the probability of A unchanged. They prefer the product form
because it treats A and B symmetrically, generalizes to more than two events, and (beyond the reading) needs no P(B) > 0.
:::

::: free read-same
In Example 1.5.9, \(X\) and \(Y\) are identically distributed, but the book says "for no sample points do we have \(X(s) = Y(s)\)".
How can both be true?
--- rubric
Reading note; reply to it. Identically distributed is about probabilities: P(X ∈ A) = P(Y ∈ A) for every set A (same cdf). It says
nothing about the two functions agreeing outcome by outcome. With three tosses, heads = tails would need 1.5 of each, so X(s) ≠ Y(s) always.
:::

::: free read-proof
Which earlier theorem does the book's proof of Theorem 1.3.9(a) use in its first step, and what does that step give?
--- rubric
Reading note; reply to it. Theorem 1.2.9(a): P(A ∩ Bᶜ) = P(A) − P(A ∩ B). Then independence replaces P(A ∩ B) with P(A)P(B), and
factoring gives P(A)(1 − P(B)) = P(A)P(Bᶜ).
:::

::: free read-surprise9
One thing that surprised or confused you.
:::

## Part 1 · Independence means the probability doesn't change (re-teach, about 10 minutes)

*From the reading, with an example beyond it.* Lesson 8 separated *disjoint* from *independent*. This part is about the definition
itself. A common wrong reading is "independent means both can happen; dependent means one *forces* the other". That's a statement
about which outcomes go together. Independence is a statement about
**probabilities**, and the two come apart. Here is the example where they come apart.

::: recap
**Recap: conditional probability (lesson 7).** \(P(B \mid A) = P(A \cap B)/P(A)\) when \(P(A) > 0\): the probability of \(B\) once you
know \(A\) happened, computed by shrinking the sample space to \(A\).
:::

::: worked
**The setup.** Roll two fair dice. \(A\) = the first die shows 6. \(B\) = the sum is 7. Once you know \(A\), the sum is 7 exactly
when the second die shows 1. So knowing \(A\) tells you *which* second roll you need. Does that make \(A\) and \(B\) dependent?
--- step
**Compute the probability of \(B\) with no information.** Six of the 36 equally likely rolls sum to 7: (1,6), (2,5), (3,4), (4,3),
(5,2), (6,1). So \(P(B) = 6/36 = 1/6\).
--- step
**Compute it again after learning \(A\).** Shrink to the 6 rolls with first die 6; one of them, (6,1), sums to 7. So
\(P(B \mid A) = 1/6\). **The same number.** Learning \(A\) changed *which* outcome you need, but not the *chance* of getting it. So
\(A\) and \(B\) are independent. (Product check: \(P(A \cap B) = 1/36 = \frac16 \cdot \frac16\).)
--- step
**Now the sum is 12.** With no information, \(P(\text{sum } 12) = 1/36\): only (6,6). After learning \(A\), the sum is 12 exactly when the
second die shows 6, so \(P(\text{sum } 12 \mid A) = 1/6\). The chance went from 1/36 to 1/6. **Dependent.**
--- step
**Why the difference?** In both cases, knowing \(A\) pins down which second roll is needed, and in both cases that roll has
probability 1/6. What differs is the *before*: every first-die value has exactly one partner that makes 7, so "sum is 7" was already
1/6; only one first-die value can make 12, so "sum is 12" was much rarer. Dependence is a change in probability, and you can only
see it by computing both numbers.
:::

**Say it this way:** "A and B are independent when learning that A happened doesn't change the probability of B:
\(P(B \mid A) = P(B)\), or equivalently \(P(A \cap B) = P(A)P(B)\)." **Not this:** "A and B are independent when they can happen
together", or "dependent means one forces the other". The test is always arithmetic: compute both sides.

::: number indep2-v6 answer=0.1667 tolerance=0.003
Two fair dice are rolled. \(A\) = the first die shows an even number. \(B\) = the sum is 8. What is \(P(B \mid A)\)? (A fraction,
a decimal to three places, or an expression such as `3/18`; `*` for ×, `/` for division.)
--- explain
Of the 18 rolls with an even first die, three sum to 8: (2,6), (4,4), (6,2). So \(P(B \mid A) = 3/18 = 1/6\). With no information,
\(P(B) = 5/36\) (five rolls sum to 8), so learning \(A\) raised the chance from \(5/36 \approx 0.139\) to \(1/6 \approx 0.167\): these
events are **dependent**, even though neither forces the other.
:::

::: choice indep2-v7
A fair 12-sided die has faces 1 to 12. \(E\) = the roll is even; \(M\) = the roll is a multiple of 3. Are \(E\) and \(M\) independent?
- [x] Independent: P(M given E) = 2/6 = P(M)
- [ ] Dependent: P(M given E) = 2/6 ≠ P(M)
- [ ] Dependent: P(M given E) = 1/2 ≠ P(M)
- [ ] Independent: P(E ∩ M) = 0 = P(E) P(M)
--- hint
Count the even faces, and how many of them are multiples of 3. Then compute \(P(M)\) on its own.
--- explain
\(P(E) = 6/12\), \(P(M) = 4/12\) (3, 6, 9, 12), and \(E \cap M = \{6, 12\}\), so \(P(E \cap M) = 2/12 = \frac12 \cdot \frac13\).
Independent. Sharing outcomes doesn't make events dependent (independent events with positive probability *must* share some), and
knowing \(E\) does change which faces are possible: what matters is whether the *probability* of \(M\) changes. Here it stays 1/3.
:::

::: free indep2-v8
Two fair dice. Given that the first die shows 3, the sum is 7 exactly when the second die shows 4. Explain, **using
probabilities**, why "the first die shows 3" and "the sum is 7" are still independent.
--- rubric
Got it: computes (or states) P(sum 7) = 6/36 = 1/6 and P(sum 7 | first die 3) = 1/6 (only (3,4)), and concludes independent because
the probability doesn't change (or the product check 1/36 = 1/6 · 1/6). Not yet: argues from "it can happen" / "it doesn't force"
without the two probabilities, or calls them dependent because the first die decides which second roll is needed.
:::

### Proof: complements of independent events
*From the reading.* Theorem 1.3.9 says that if \(A\) and \(B\) are independent, so are \(A\) and \(B^c\); the book proves this part
(a) with Theorem 1.2.9(a), \(P(A \cap B^c) = P(A) - P(A \cap B)\).

::: recap
**Recap: Theorem 1.2.9(a) (lesson 6).** For any events, \(P(B \cap A^c) = P(B) - P(A \cap B)\): split \(B\) into the disjoint pieces
\(B \cap A\) and \(B \cap A^c\) and use Axiom 3.
:::

::: free indep-proof
*Casella & Berger, Exercise 1.40 (part b).* Prove: if \(A\) and \(B\) are independent, then \(A^c\) and \(B\) are independent.
Name each fact you use.
--- rubric
Full marks: P(Aᶜ ∩ B) = P(B) − P(A ∩ B) (Theorem 1.2.9a, or the disjoint split of B with Axiom 3) = P(B) − P(A)P(B) (independence)
= P(B)(1 − P(A)) = P(B)P(Aᶜ) (complement rule). Got it: all steps present, a citation missing. Not yet: assumes what is to be proved
(uses P(Aᶜ ∩ B) = P(Aᶜ)P(B) along the way), or argues in words that "complements carry no information" without the algebra.
--- explain
\(P(A^c \cap B) = P(B) - P(A \cap B) = P(B) - P(A)P(B) = P(B)\,(1 - P(A)) = P(A^c)\,P(B)\). The first step is Theorem 1.2.9(a), the
second is independence of \(A\) and \(B\), the last is the complement rule.
:::

## Part 2 · A pdf's value is a density, not a probability (re-teach, about 6 minutes)

*From lesson 8's reading (§1.6), with an example beyond it.* A pdf's value is often mistaken for \(P(X = x)\). That's true of a pmf
only. The key fact is from §1.6: for a continuous random variable, \(P(X = x) = 0\) at every \(x\). So the pdf's value can't be that probability; if it were, the pdf would be 0 everywhere.

::: worked
**A density bigger than 1.** Let \(X\) be uniform on \([0, \tfrac12]\): its pdf is \(f(x) = 2\) there and 0 elsewhere (the area,
\(2 \times \tfrac12\), is 1). So \(f(0.3) = 2\). That can't be a probability.
--- step
**What it is.** Take a short interval starting at 0.3: \(P(0.3 < X \le 0.3 + h) = 2h\) for small \(h\). The probability of a short
interval is about **density × length**. So \(f(x)\) is probability *per unit length* near \(x\), the way kilograms per litre is
mass per unit volume.
--- step
**And a single point.** Shrink the interval to nothing: \(h \to 0\) gives \(P(X = 0.3) = 0\), while \(f(0.3)\) stays 2. Point
probability and density are different quantities; only the pmf, for a discrete \(X\), is point probability.
:::

**Say it this way:** "A pdf's value is a density: probability per unit length. Probabilities come from areas under it." **Not this:**
"\(f(x)\) is the probability that \(X = x\)."

::: choice pmfpdf-v4
A continuous random variable \(X\) has pdf \(f\) with \(f(0.4) = 1.5\), and \(f\) is continuous near 0.4. Which statement is true?
- [x] P(0.4 < X ≤ 0.41) is about 0.015
- [ ] P(X = 0.4) is equal to 1.5
- [ ] P(X = 0.4) is close to 0.015
- [ ] No pdf can have the value 1.5
--- hint
Density times length gives the probability of a short interval. What is the length here?
--- explain
For a short interval, probability ≈ density × length = \(1.5 \times 0.01 = 0.015\). A single point has probability 0 for a
continuous \(X\), and a density may exceed 1 as long as the total area is 1.
:::

::: number pmfpdf-v5 answer=0.091 tolerance=0.002
\(X\) has pdf \(f(x) = 3x^2\) on \([0, 1]\) (and 0 elsewhere), so its cdf there is \(F(x) = x^3\). What is \(P(0.5 < X \le 0.6)\)?
(A decimal to three places or an expression such as `0.6^3-0.5^3`.)
--- explain
\(F(0.6) - F(0.5) = 0.216 - 0.125 = 0.091\). Compare density × length at the left end, \(f(0.5) \times 0.1 = 0.075\), and at the right
end, \(f(0.6) \times 0.1 = 0.108\): the exact answer sits between, because the density rises across the interval.
:::

## Part 3 · Warm-ups (about 6 minutes)

These come back from lessons 7 and 8: two conditional-probability calculations, and one question on checking a theorem's hypothesis before using it.

::: number condp-v6 answer=0.0909 tolerance=0.002
Two fair dice are rolled. Given that **at least one** die shows 6, what is the probability that **both** show 6? (A fraction, a
decimal to three places, or an expression such as `2/22`; `/` for division.)
--- explain
"At least one 6" contains 11 of the 36 rolls (6 with the first die 6, 6 with the second, minus (6,6) counted twice); one of them is
(6,6). So \(1/11 \approx 0.091\). Compare "given the *first* die shows 6": 6 rolls, answer \(1/6\). Different conditions, different answers.
:::

::: number bayescalc-v4 answer=0.7059 tolerance=0.005
*Adapted from Casella & Berger, Example 1.3.6 and Exercise 1.41, numbers changed.* Telegraph dots and dashes are sent in the proportion
5:3 (dots more common). Interference turns a dot into a dash with probability 1/5, and a dash into a dot with probability 1/5. A
dash is received. What is the probability a dash was sent? (A fraction, a decimal to two places or better, or an expression;
`*` for ×, `/` for division.)
--- explain
\(P(\text{dash sent}) = 3/8\), \(P(\text{dot sent}) = 5/8\). \(P(\text{dash received}) = \frac45\cdot\frac38 + \frac15\cdot\frac58 = \frac{12}{40} + \frac{5}{40} = \frac{17}{40}\).
So \(P(\text{dash sent} \mid \text{dash received}) = \dfrac{12/40}{17/40} = \dfrac{12}{17} \approx 0.706\). The numerator alone,
\(\frac45 \cdot \frac38\), is the probability of "dash sent *and* dash received"; dividing by \(P(\text{dash received})\) is what makes it conditional.
:::

::: find-error hyp-v1
Two fair dice. \(A\) = the first die shows 6, \(B\) = the sum is 12. Which step is wrong?
- \(P(A) = 6/36 = 1/6\) and \(P(B) = 1/36\).
- [x] By Axiom 3, \(P(A \cup B) = P(A) + P(B) = 7/36\).
- So the probability that the first die shows 6 or the sum is 12 is 7/36.
--- explain
Axiom 3 adds probabilities only for **disjoint** events, and these aren't: (6,6) is in both (in fact \(B \subseteq A\)). Check a
theorem's hypothesis before using it. Here \(A \cup B = A\), so the right answer is \(1/6 = 6/36\), not \(7/36\). The same check is why,
in a proof, "the sets are pairwise disjoint" has to come *before* "by Axiom 3".
:::

**Day 2 starts here.**

## Part 4 · Identically distributed (new, about 4 minutes)

*From the reading.* One Chapter 1 idea we skipped, and it matters from Chapter 5 on, where a sample is "\(X_1, \dots, X_n\),
identically distributed".

::: worked
**Two different functions.** Toss a fair coin three times. \(X\) = number of heads, \(Y\) = number of tails. On the outcome HHT,
\(X = 2\) and \(Y = 1\). They're different functions on \(S\); in fact \(X(s) + Y(s) = 3\) for every outcome.
--- step
**Same probabilities.** \(P(X = k)\) and \(P(Y = k)\) are both \(1, 3, 3, 1\) out of 8 for \(k = 0, 1, 2, 3\) (swap H and T in each
outcome). So for every set \(A\) of numbers, \(P(X \in A) = P(Y \in A)\).
--- step
**Name it.** That is **Definition 1.5.8**: \(X\) and \(Y\) are *identically distributed*. **Theorem 1.5.10** says this is the same as
having the same cdf, \(F_X(x) = F_Y(x)\) for every \(x\). It does **not** say \(X = Y\): here they're never equal.
:::

::: number iddist-v1 answer=6
A fair coin is tossed **four** times. \(X\) = number of heads, \(Y\) = number of tails. They're identically distributed. For how
many of the 16 equally likely outcomes is \(X(s) = Y(s)\)?
--- explain
\(X = Y\) means two heads and two tails: \(\binom{4}{2} = 6\) outcomes. So \(P(X = Y) = 6/16\), not 1: identically distributed
variables can agree on some outcomes, on none (three tosses), or on all, and none of that is part of the definition.
:::

::: choice iddist-v2
\(X\) and \(Y\) are identically distributed random variables. Which statement must be true?
- [x] F_X(x) = F_Y(x) for every real number x
- [ ] F_X(x) = F_Y(x) for at least one x
- [ ] X and Y are equal with probability 1
- [ ] F_X(x) = 1 − F_Y(x) for every real x
--- explain
Theorem 1.5.10: identically distributed is equivalent to equal cdfs at *every* \(x\); agreeing at one point isn't enough. It never
requires \(X = Y\) (three-toss heads and tails are never equal), and \(1 - F_Y\) isn't even a cdf (it falls from 1 to 0).
:::

## Part 5 · Chapter 1 on one page (about 8 minutes)

*Beyond the reading: a map of the whole chapter.* Each arrow points from an idea to one built on it; the dashed arrow is Theorem 1.5.10.

::: diagram kind=graph dir=down caption="Chapter 1 of Casella & Berger: each arrow points from an idea to one built on it."
- ax: Three axioms
- calc: Complement rule, monotonicity (Thms 1.2.8–1.2.9)
- cond: Conditional probability, Bayes' rule
- ind: Independence
- rv: Random variable (a function on S)
- px: Induced probability P_X
- cdf: Cdf: three properties
- pdf: Pmf or pdf
- idd: Identically distributed
- ax > calc
- ax > cond
- cond > ind
- rv > px
- ax > px
- px > cdf
- cdf > pdf
- px > idd
- cdf ~> idd
:::

Now recall each one from memory. Say it out loud or write it, then flip the card and mark yourself honestly.

:::: deck
::: card sum-axioms
State Kolmogorov's three axioms, and say what they're for.
--- explain
For every event \(A\): (1) \(P(A) \ge 0\); (2) \(P(S) = 1\); (3) for pairwise disjoint \(A_1, A_2, \dots\), \(P(\bigcup A_i) = \sum P(A_i)\).
**For:** every other rule in probability is proved from these three.
:::
::: card sum-calc
State the complement rule and monotonicity, and say what each is for.
--- explain
\(P(A^c) = 1 - P(A)\) (Theorem 1.2.8c); if \(A \subseteq B\) then \(P(A) \le P(B)\) (Theorem 1.2.9c). **For:** "at least one" problems (take the complement
of "none"), and bounds (a cdf is nondecreasing because of monotonicity).
:::
::: card sum-cond
Define conditional probability and state Bayes' rule, including what it assumes.
--- explain
\(P(A \mid B) = P(A \cap B)/P(B)\), for \(P(B) > 0\). Bayes: if \(A_1, A_2, \dots\) partition \(S\) and \(P(B) > 0\),
\(P(A_i \mid B) = P(B \mid A_i)P(A_i) \big/ \sum_j P(B \mid A_j)P(A_j)\). **For:** turning "probability of the evidence given the
cause" into "probability of the cause given the evidence" (the Morse code problem).
:::
::: card sum-ind
Define independence of two events, and say how mutual independence of three differs from pairwise.
--- explain
\(P(A \cap B) = P(A)P(B)\): learning one doesn't change the probability of the other. Three events are mutually independent when every
pair *and* the triple satisfy the product rule; pairwise alone isn't enough (the \(S = \{1,2,3,4\}\) counterexample). **For:** computing
joint probabilities by multiplying, as in de Méré's dice and every "independent sample" later.
:::
::: card sum-rv
Define a random variable and the probability it induces.
--- explain
A function \(X: S \to \mathbb{R}\). Induced probability: \(P_X(X \in A) = P(\{s \in S : X(s) \in A\})\). **For:** moving from events to
numbers, which is the language of the rest of the book.
:::
::: card sum-cdf
Define the cdf and state the three properties that characterize cdfs.
--- explain
\(F_X(x) = P(X \le x)\) for every real \(x\). A function is a cdf exactly when (a) its limits are 0 at \(-\infty\) and 1 at
\(+\infty\), (b) it is nondecreasing, (c) it is right-continuous (Theorem 1.5.3). **For:** one function that describes *any* random
variable, discrete, continuous or mixed; \(P(a < X \le b) = F(b) - F(a)\).
:::
::: card sum-pdf
Say what a pmf and a pdf are, and the two conditions that make a function one (Theorem 1.6.5).
--- explain
Pmf: \(f(x) = P(X = x)\) (discrete). Pdf: \(F(x) = \int_{-\infty}^x f(t)\,dt\) (continuous); \(f\) is a density, not a probability.
Both: \(f \ge 0\), and the total (sum or integral) is 1. **For:** computing probabilities by summing or integrating, and checking a
proposed model is a real distribution (normalizing constants).
:::
::: card sum-idd
Define "identically distributed" and say what it does not mean.
--- explain
\(P(X \in A) = P(Y \in A)\) for every set \(A\), equivalently \(F_X = F_Y\) (Theorem 1.5.10). It does not mean \(X = Y\). **For:** the
"identically distributed" half of every random sample from Chapter 5 on.
:::
::::

That's Chapter 1. The chapter check comes next: recall questions across all six sections and one proof.

## Extra practice (optional)

**From Casella & Berger, Chapter 1 exercises** (easiest first; worked solutions are in the Casella & Berger solutions manual):
1. Exercise 1.38 (a) and (b): conditional probability when \(P(B) = 1\) and when \(A \subseteq B\).
2. Exercise 1.39: prove that events with positive probability can't be both mutually exclusive and independent.
3. Exercise 1.40 (c): finish Theorem 1.3.9 by proving \(A^c\) and \(B^c\) are independent (part b is the proof in Part 1).
4. Exercise 1.44: a 20-question multiple-choice test with independent guessing; at least 10 right.

**Extra reading:** John Haigh, *Probability: A Very Short Introduction*, Chapter 2 ("The workings of probability"), the section
"Independence" (about 2 pages, in your library). It has a die where independence is not obvious, and asks you to redo it with
eight- and ten-sided dice: one gives independent events, the other doesn't.

**Extra article:** Adam Molnar, "High school mathematics teachers' understanding of independent events" (ICME-13, 2016):
<https://fpce.uc.pt/iase-web/documents/papers/icme13/ICME13_L9_Molnar.pdf>. Of 25 high-school math teachers asked whether two
events in a table were independent, only three gave a correctly explained answer, and many were confident in wrong ones. It traces
the confusion to the other meanings of "independent", including algebra's independent variable, which fixes the dependent one exactly.

## Sources
- George Casella and Roger L. Berger, *Statistical Inference*, 2nd ed. (Duxbury, 2002): §1.3 pp. 25–26 (Definition 1.3.7,
  Example 1.3.8, Theorem 1.3.9); §1.5 pp. 33–34 (Definition 1.5.8, Example 1.5.9, Theorem 1.5.10); Theorems 1.2.9, 1.5.3, 1.6.5;
  Example 1.3.6 and Exercises 1.38–1.41, 1.44; Theorem 1.2.8 for the complement rule. In your library (id f9dc4d1d4c).
- John Haigh, *Probability: A Very Short Introduction* (Oxford University Press, 2012), Chapter 2, "Independence". In your library (a53c1f767c).
- Adam Molnar, "High school mathematics teachers' understanding of independent events", 13th International Congress on Mathematical
  Education, Hamburg, 2016: https://fpce.uc.pt/iase-web/documents/papers/icme13/ICME13_L9_Molnar.pdf
