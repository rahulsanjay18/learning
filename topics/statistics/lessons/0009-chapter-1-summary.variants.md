## hyp

::: find-error hyp-v2
Two fair dice. \(A\) = the first die shows 1, \(B\) = the first die shows 2. Which step is wrong?
- \(P(A) = 1/6\) and \(P(B) = 1/6\).
- [x] Rolls of fair dice are independent, so \(P(A \cap B) = P(A)P(B) = 1/36\).
- So the probability that the first die shows both 1 and 2 is 1/36.
--- explain
The product rule needs \(A\) and \(B\) to be independent, and these are disjoint events with positive probability, which are never
independent: \(A \cap B = \varnothing\), so \(P(A \cap B) = 0\), but \(P(A)P(B) = 1/36\). "Dice rolls are independent" is about *different* rolls, not two events
about the same die.
:::

::: free hyp-v3
From memory: before you write "by Axiom 3, \(P(\bigcup_i E_i) = \sum_i P(E_i)\)", what must you have shown about the \(E_i\), and what
goes wrong without it? Give a two-event example.
--- rubric
Got it: the E_i must be pairwise disjoint; without it, outcomes in an overlap get counted twice and the sum can exceed the true
probability (e.g. two dice, A = first die 6, B = sum 12: 1/6 + 1/36 ≠ P(A ∪ B) = 1/6; any correct example). Not yet: names a different
condition (independence, equal probabilities) or no condition.
:::

## iddist

::: free iddist-v3
From memory: define "\(X\) and \(Y\) are identically distributed", give the equivalent condition in terms of cdfs, and give an example
where they are identically distributed but \(X \ne Y\).
--- rubric
Got it: P(X ∈ A) = P(Y ∈ A) for every (Borel) set A; equivalently F_X(x) = F_Y(x) for every x (Theorem 1.5.10); an example such as heads
vs. tails in n fair tosses. Not yet: "X and Y take the same values" or "X = Y with probability 1" as the definition.
:::

## pmfpdf

::: number pmfpdf-v6 answer=4
\(X\) is uniform on \([0, \tfrac14]\). What is the value of its pdf at \(x = 0.1\)? (A number.)
--- explain
A uniform pdf is constant on its interval with total area 1, so \(f = 1/(1/4) = 4\) there. A density can be 4; the probability of the
single point 0.1 is still 0, and \(P(0.1 < X \le 0.1 + h) = 4h\) for small \(h\).
:::
