---
title: Chapter 1 pretest: probability theory
subtitle: One block (about 25–30 min). No reading first. It decides which Chapter 1 sections need a lesson and which you skip.
crumb: Statistics · Lesson 5 · Chapter 1 pretest
index: Chapter 1 pretest (C&B Ch. 1)
main: data-skip=true
---
## How this works

Casella & Berger, Chapter 1, has six sections. For each one you get **three questions: a concept, a calculation and a short proof.**

- **"I don't know" is the honest answer, not a failure.** It just means that section gets taught. Guessing hurts you: a lucky guess
  skips a lesson you needed. If you guess anyway, say so with the "I guessed" button.
- **Proofs:** 3–6 lines of plain text is fine ("P(A u B)", "A^c", "sum", "integral"). I'm checking the idea and that each step is
  justified, not the typesetting.
- **Math boxes take expressions:** type `*` for ×, `/`, `^` for powers, `sqrt( )`, `exp( )`, and `choose(n, k)` for "n choose k".
  E.g. `0.3*0.2/(0.3*0.2+0.1)`.

Afterwards there is **always a one-lesson summary of the whole chapter**, plus lessons only for the sections you didn't know.

## §1.1 Set theory

::: choice c1-s1-concept
De Morgan's law: for any sets \(A, B\), the complement \((A \cup B)^c\) equals…
- [ ] \(A^c \cup B^c\)
- [x] \(A^c \cap B^c\)
- [ ] \(A \cap B^c\)
- [ ] \((A \cap B)^c\)
--- explain
Not in either set = outside \(A\) **and** outside \(B\). The other law: \((A \cap B)^c = A^c \cup B^c\).
:::

::: number c1-s1-calc answer=7
Sample space \(S = \{1, 2, \dots, 10\}\). \(A\) = the even numbers in \(S\); \(B = \{1, 2, 3, 4\}\). How many elements are in \(A \cup B\)?
--- explain
\(A \cup B = \{1, 2, 3, 4, 6, 8, 10\}\): 7 elements. (Check: \(|A| + |B| - |A \cap B| = 5 + 4 - 2 = 7\).)
:::

::: order c1-s1-proof
Put the steps of the proof that \((A \cup B)^c \subseteq A^c \cap B^c\) in order.
- Let \(x \in (A \cup B)^c\).
- Then \(x \notin A \cup B\).
- So \(x \notin A\) and \(x \notin B\).
- So \(x \in A^c\) and \(x \in B^c\), that is, \(x \in A^c \cap B^c\).
--- explain
Element-chasing: start from an arbitrary element of the left side and show it lands in the right side. The reverse inclusion runs the same steps backwards.
:::

## §1.2 Basics of probability theory (axioms, rules, counting)

::: free c1-s2-concept
State the three axioms of probability (Kolmogorov's axioms) for a probability function \(P\) on a sample space \(S\).
--- rubric
(1) P(A) ≥ 0 for every event A; (2) P(S) = 1; (3) countable additivity: if A1, A2, … are pairwise disjoint, P(∪Ai) = Σ P(Ai)
(C&B Definition 1.2.4). Finite additivity only = partial. Must say "pairwise disjoint".
--- explain
1. \(P(A) \ge 0\) for every event \(A\). 2. \(P(S) = 1\). 3. If \(A_1, A_2, \dots\) are pairwise disjoint, \(P(\bigcup_i A_i) = \sum_i P(A_i)\) (countable additivity). C&B Definition 1.2.4.
:::

::: math c1-s2-calc answer="26^3+26^2"
*Casella & Berger, Exercise 1.16(b).* How many different sets of initials can be formed if every person has one surname and **either one or two given names**? (26 letters; an expression is fine.)
--- explain
Two given names + surname: \(26^3\) ordered triples; one given name + surname: \(26^2\) pairs. The cases don't overlap, so add: \(26^3 + 26^2\) (the book's answer).
:::

::: free c1-s2-proof
Prove **Bonferroni's inequality** for two events: \(P(A \cap B) \ge P(A) + P(B) - 1\). You may use \(P(A \cup B) = P(A) + P(B) - P(A \cap B)\).
--- rubric
Rearrange: P(A∩B) = P(A) + P(B) − P(A∪B); and P(A∪B) ≤ 1 (because A∪B ⊆ S, monotonicity, and P(S) = 1). So P(A∩B) ≥ P(A) + P(B) − 1.
Full marks need the reason P(A∪B) ≤ 1, not just the claim.
--- explain
\(P(A \cap B) = P(A) + P(B) - P(A \cup B)\), and \(P(A \cup B) \le P(S) = 1\) because \(A \cup B \subseteq S\) and \(P\) is monotone. So \(P(A \cap B) \ge P(A) + P(B) - 1\).
:::

## §1.3 Conditional probability and independence

::: choice c1-s3-concept
Three events \(A, B, C\): every *pair* of them is independent. Are \(A, B, C\) mutually independent?
- [x] Not necessarily: triple condition needed
- [ ] Yes: pairs imply the triple
- [ ] Only if they're mutually disjoint
- [ ] Only with a finite space
--- explain
Mutual independence also needs \(P(A \cap B \cap C) = P(A)P(B)P(C)\), which pairwise independence doesn't guarantee (C&B Definition 1.3.12 and the example before it).
:::

::: math c1-s3-calc answer="0.05*0.5/(0.05*0.5+0.0025*0.5)" tolerance=0.001
*Casella & Berger, Exercise 1.33.* 5% of men and 0.25% of women are color-blind. A person is chosen at random and that person is color-blind. What is the probability that the person is male? (Assume equal numbers of men and women. A decimal or an expression.)
--- explain
Bayes: \(P(M \mid C) = \dfrac{P(C \mid M)P(M)}{P(C \mid M)P(M) + P(C \mid W)P(W)}\) with \(P(M) = P(W) = 1/2\).
:::

::: free c1-s3-proof
Derive Bayes' rule, \(P(A \mid B) = \dfrac{P(B \mid A)\,P(A)}{P(B)}\), from the definition of conditional probability. Say what you assume about \(P(A)\) and \(P(B)\).
--- rubric
Definition P(A|B) = P(A∩B)/P(B) for P(B) > 0; likewise P(A∩B) = P(B|A)P(A) for P(A) > 0; substitute. Full marks: both positivity
conditions stated. Bonus (not required): P(B) = P(B|A)P(A) + P(B|Aᶜ)P(Aᶜ) by the law of total probability.
--- explain
For \(P(B) > 0\): \(P(A \mid B) = P(A \cap B)/P(B)\). For \(P(A) > 0\): \(P(A \cap B) = P(B \mid A)P(A)\). Substitute. The denominator often gets expanded as \(P(B \mid A)P(A) + P(B \mid A^c)P(A^c)\).
:::

## §1.4 Random variables

::: choice c1-s4-concept
Formally, a random variable is…
- [x] A function from sample space to reals
- [ ] A number that changes each trial
- [ ] A probability assigned to each outcome
- [ ] A set of possible experiment outcomes
--- explain
\(X: S \to \mathbb{R}\). The randomness lives in which outcome \(s\) happens; \(X\) itself is a fixed function (C&B Definition 1.4.1).
:::

::: number c1-s4-calc answer=0.375 tolerance=0.001
Toss three fair coins. \(X\) = the number of heads. What is \(P(X = 2)\)? (A decimal or a fraction like `3/8`.)
--- explain
The outcomes with two heads are HHT, HTH, THH: 3 of the 8 equally likely outcomes, so \(3/8 = 0.375\).
:::

::: free c1-s4-proof
A random variable \(X\) induces a probability on the real line: \(P_X(X \in A) = P(\{s \in S : X(s) \in A\})\). Sketch why \(P_X\) satisfies the third axiom (countable additivity).
--- rubric
If A1, A2, … are pairwise disjoint subsets of ℝ, their preimages {s : X(s) ∈ Ai} are pairwise disjoint (one s can't map into two
disjoint sets); the preimage of ∪Ai is ∪ of the preimages; apply countable additivity of P. Full marks: both preimage facts.
--- explain
Preimages of disjoint sets are disjoint (each \(s\) has one value \(X(s)\)), and the preimage of a union is the union of the preimages. So \(P_X(\bigcup A_i) = P(\bigcup_i X^{-1}(A_i)) = \sum_i P(X^{-1}(A_i)) = \sum_i P_X(A_i)\).
:::

## §1.5 Distribution functions

::: free c1-s5-concept
What three properties must a function \(F(x)\) have to be a cumulative distribution function (cdf)?
--- rubric
(1) lim F(x) = 0 as x → −∞ and = 1 as x → +∞; (2) nondecreasing; (3) right-continuous. (C&B §1.5.) Partial: two of three, or
"continuous" instead of "right-continuous".
--- explain
Limits 0 at \(-\infty\) and 1 at \(+\infty\); nondecreasing; right-continuous (\(\lim_{x \downarrow x_0} F(x) = F(x_0)\)). Right-continuity is what lets a discrete cdf jump.
:::

::: math c1-s5-calc answer="3/16" tolerance=0.0001
*Adapted from Casella & Berger, Exercise 1.53.* A river's yearly high-water mark \(Y\) has cdf \(F_Y(y) = 1 - 1/y^2\) for \(y \ge 1\) (and 0 for \(y < 1\)). What is \(P(2 < Y \le 4)\)?
--- explain
\(P(a < Y \le b) = F_Y(b) - F_Y(a)\), here \((1 - 1/16) - (1 - 1/4)\).
:::

::: free c1-s5-proof
Show that any cdf \(F(x) = P(X \le x)\) is nondecreasing.
--- rubric
For x < y: {X ≤ x} ⊆ {X ≤ y}, so P(X ≤ x) ≤ P(X ≤ y) by monotonicity of P (A ⊆ B ⇒ P(A) ≤ P(B), C&B Theorem 1.2.9c). Full marks:
the set inclusion and the monotonicity fact both stated.
--- explain
If \(x < y\), every outcome with \(X \le x\) also has \(X \le y\): \(\{X \le x\} \subseteq \{X \le y\}\). Probability is monotone (\(A \subseteq B \Rightarrow P(A) \le P(B)\)), so \(F(x) \le F(y)\).
:::

## §1.6 Density and mass functions

::: choice c1-s6-concept
Which can take values greater than 1: a probability mass function (pmf) or a probability density function (pdf)?
- [x] A pdf can; a pmf can't
- [ ] A pmf can; a pdf can't
- [ ] Both can, for some distributions only
- [ ] Neither can, since both are probabilities
--- explain
A pmf value is a probability, so at most 1. A pdf value is a density: only its integral is a probability. Uniform on \([0, 0.5]\) has density 2.
:::

::: math c1-s6-calc answer=3
\(f(x) = c\,x^2\) for \(0 \le x \le 1\) (and 0 elsewhere). What constant \(c\) makes \(f\) a pdf?
--- explain
\(\int_0^1 c x^2\,dx = c/3 = 1\), so \(c = 3\).
:::

::: free c1-s6-proof
\(X\) is continuous, with a continuous cdf \(F\). Show that \(P(X = x) = 0\) for every \(x\). (Hint: compare \(\{X = x\}\) with \(\{x - \varepsilon < X \le x\}\).)
--- rubric
{X = x} ⊆ {x − ε < X ≤ x} for every ε > 0, so 0 ≤ P(X = x) ≤ F(x) − F(x − ε); let ε → 0: continuity of F gives F(x − ε) → F(x),
so P(X = x) = 0. Full marks: the inclusion, the bound, and continuity used for the limit.
--- explain
For every \(\varepsilon > 0\): \(0 \le P(X = x) \le P(x - \varepsilon < X \le x) = F(x) - F(x - \varepsilon)\). As \(\varepsilon \to 0\) the right side goes to 0 because \(F\) is continuous. So \(P(X = x) = 0\).
:::

## Next

Your results decide the plan: a **Chapter 1 summary lesson** (always), then lessons only for sections where you missed the concept or calculation, a short proof lesson where only proofs were missing, then the chapter check. Press **Copy my results** below and paste it to me (or just let sync send it).

## Sources
- George Casella & Roger L. Berger, *Statistical Inference*, 2nd ed., Chapter 1 (§1.1–1.6; Exercises 1.16, 1.33, 1.53; Definition 1.2.4, Theorem 1.2.9, Definition 1.3.12, Definition 1.4.1). In your library (id f9dc4d1d4c).
