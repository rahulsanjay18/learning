## condp

::: number condp-v2 answer=0.0449 tolerance=0.0005
*Adapted from Casella & Berger, Example 1.3.3 (four aces), changed to hearts.* Four cards are dealt from the top of a
well-shuffled 52-card deck. Given that the first two cards are both hearts, what is the probability that all four are hearts?
(A fraction, a decimal to three significant figures, or an expression such as `choose(5,2)/choose(9,2)`.)
--- explain
Once two hearts are gone, 50 cards remain, 11 of them hearts, and the last two cards are a random pair from those 50:
\(\binom{11}{2}/\binom{50}{2} = 55/1225 \approx 0.045\). Equivalently \(\frac{11}{50}\cdot\frac{10}{49}\).
:::

::: number condp-v3 answer=0.7903 tolerance=0.005
*Adapted from Casella & Berger, Exercise 1.36, numbers changed.* Each shot hits a target with probability 0.3, and 8 shots are
fired independently. Given that the target is hit at least once, what is the probability it is hit at least twice? (A decimal,
or an expression: `*` for ×, `/`, `^` for powers.)
--- explain
\(P(\ge 1) = 1 - 0.7^8\) and \(P(\ge 2) = 1 - 0.7^8 - 8(0.3)(0.7)^7\). Since "at least twice" is inside "at least once",
\(P(\ge 2 \mid \ge 1) = P(\ge 2)/P(\ge 1)\).
:::

::: find-error condp-v4
A student computes the probability that two fair dice show doubles, given that the sum is 6. Which step is wrong?
- The outcomes with sum 6 are (1,5), (2,4), (3,3), (4,2), (5,1), so \(P(\text{sum } 6) = 5/36\).
- The only doubles with sum 6 is (3,3), so \(P(\text{doubles and sum } 6) = 1/36\).
- [x] So \(P(\text{doubles} \mid \text{sum } 6) = P(\text{doubles and sum } 6)/P(\text{doubles}) = (1/36)/(1/6) = 1/6\).
- So the answer is \(1/6\).
--- explain
The denominator must be the probability of the event conditioned on, the sum being 6: \((1/36)/(5/36) = 1/5\). Dividing by
\(P(\text{doubles})\) computes \(P(\text{sum } 6 \mid \text{doubles})\) instead.
:::

## bayes

::: recall bayes-v4
State Bayes' rule for two events, and the exact conditions under which it holds. Then reveal.
--- explain
\(P(A \mid B) = P(B \mid A)P(A)/P(B)\), for any events with \(P(A) > 0\) and \(P(B) > 0\). Nothing else is assumed: no
independence. It comes from writing \(P(A \cap B)\) two ways with the definition of conditional probability.
:::

## bayescalc

::: number bayescalc-v2 answer=0.931 tolerance=0.005
*Adapted from Casella & Berger, Example 1.3.6 and Exercise 1.41, numbers changed.* Morse code symbols are dots and dashes in the
proportion 2:3. Interference turns a dot into a dash with probability 1/10, and a dash into a dot with probability 1/10. A dash
is received. What is the probability a dash was sent? (A fraction, decimal or expression.)
--- explain
\(P(\text{dash sent}) = 3/5\), \(P(\text{dot sent}) = 2/5\). \(P(\text{dash recv}) = \frac{9}{10}\cdot\frac35 + \frac1{10}\cdot\frac25 = \frac{29}{50}\).
So \(P(\text{dash sent} \mid \text{dash recv}) = \dfrac{27/50}{29/50} = \dfrac{27}{29} \approx 0.931\).
:::

::: number bayescalc-v3 answer=0.2687 tolerance=0.005
A condition affects 2% of people. A test detects it 90% of the time when it's present (so its false negative rate is 10%), and
gives a false positive 5% of the time when it's absent. A randomly chosen person tests positive. What is the probability they
have the condition? (A decimal or an expression.)
--- explain
\(P(+) = 0.9(0.02) + 0.05(0.98) = 0.067\), so \(P(\text{condition} \mid +) = 0.018/0.067 \approx 0.269\). Most positives are false
positives because the condition is rare: the prior matters.
:::

## indep2

::: number indep2-v3 answer=0.55 tolerance=0.005
\(A\) and \(B\) are independent events with \(P(A) = 0.4\) and \(P(B) = 0.25\). What is \(P(A \cup B)\)? (A decimal.)
--- explain
By C&B Theorem 1.3.9, \(A^c\) and \(B^c\) are independent too, so \(P(A \cup B) = 1 - P(A^c \cap B^c) = 1 - 0.6 \cdot 0.75 = 0.55\).
(Or \(P(A) + P(B) - P(A)P(B)\).)
:::

## mutual

::: choice mutual-v4 shuffle=true
Events \(A, B, C\) satisfy \(P(A \cap B \cap C) = P(A)P(B)P(C)\). What follows *in general* about the pairs?
- [x] No pairwise equation follows from it
- [ ] Every pairwise equation follows from it
- [ ] Mutual independence of all three follows
- [ ] One pairwise equation follows from it
--- hint
Think of the two-dice example with \(A\) = doubles, \(B\) = sum between 7 and 10, \(C\) = sum is 2, 7 or 8.
--- explain
Nothing follows in general. In C&B Example 1.3.10 the triple product holds but \(P(A \cap B) \ne P(A)P(B)\) and \(P(B \cap C) \ne P(B)P(C)\) (the pair \(A, C\) happens to hold there,
but nothing forces it). Mutual independence needs every subcollection, pairs included.
:::

::: number mutual-v5 answer=0.0556 tolerance=0.0005
*From Casella & Berger, Example 1.3.10.* Two fair dice are tossed. \(A\) = doubles appear; \(B\) = the sum is between 7 and 10
(inclusive). What is \(P(A \cap B)\)? (A fraction, or a decimal to three significant figures.) Then compare it with \(P(A)P(B) = \frac16 \cdot \frac12\).
--- explain
Doubles with sum 7 to 10: (4,4) and (5,5), so \(P(A \cap B) = 2/36 = 1/18\), while \(P(A)P(B) = 1/12\). Not independent, even
though \(P(A \cap B \cap C) = P(A)P(B)P(C)\) for \(C\) = sum 2, 7 or 8.
:::
