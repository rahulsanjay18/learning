# Statistics: questions asked, with answers

## 2026-10-05 · "p = 0.038, so ~4% chance it's luck and 96% chance it's the website?"
**Short answer:** the "no" is right, but the reasoning is the exact trap lesson 2 is about.

- **What p = 0.038 says:** *if* the new page made no difference, a lift this big or bigger would happen about 4% of the time.
  That's P(data this extreme | no effect).
- **What "4% chance it's luck" says:** P(no effect | this data). That's the conditional flipped, and the ASA statement's
  second principle names it directly: p-values do not measure "the probability that the data were produced by random chance alone" [1].
- **Same structure as the disease problem you got right:** P(positive | healthy) = 5% did *not* mean P(healthy | positive) = 5%;
  it was ~85%, because the disease was rare. Here, P(lift | no effect) ≈ 4% doesn't make P(no effect | lift) ≈ 4%.
- **What P(the page really works | this result) depends on:** how often ideas like this work in the first place (the base rate),
  and the test's power. In lesson 2's worked example (10% of ideas work, α = 0.05, power 0.8), 36% of significant results are
  duds, so "it's real" is about 64%, not 96%. With a long-shot idea it can be far lower.
- **How to say it to the PM:** "If the page did nothing, we'd rarely see a lift this big (about 4% of the time). That's decent
  evidence against 'no effect', but how sure we should be that it works depends on how often changes like this pan out. 96% is
  overselling it."

Sources: [1] Wasserstein & Lazar (2016), ASA statement on p-values, as quoted in Bruce, Bruce & Gedeck, *Practical Statistics
for Data Scientists*, p. 108 (in collection). Base-rate arithmetic: lesson 2 worked example; Ioannidis (2005), PLOS Medicine.

## 2026-10-05 · "How do I say it using the 96%? 96% chance this data appears given we changed the website?"
**No:** both 4% and 96% are computed in the world where the page makes **no** difference.

- Thought experiment: the page truly does nothing; rerun the A/B test 100 times. In ~4 reruns the gap is as big as 0.6 points or
  bigger (either direction, since the test is two-sided): that's p = 0.038. In ~96 the gap is smaller.
- Correct sentence with 96%: "If the new page made no difference, 96% of the time we'd see a smaller gap than this one."
- "Given we changed the website" would be the *other* world (a real effect). How likely the data is there is a different
  number (related to power), not 96%.
- In practice don't quote 96%. Say: "If the page did nothing, a lift this big would be rare (about 4%). That's evidence it helps,
  not '96% sure it works'."

Basis: definition of the p-value as P(result at least this extreme | H0) (Casella & Berger §8.3.4; Bruce, Bruce & Gedeck p. 108).

## 2026-10-05 · "So what is 1 − P(data | H0)?"
**1 − p = P(a result *less* extreme than ours | H0).** Still conditioned on H0: taking the complement flips the *event*, never the condition.

- Rule: P(A | B) + P(not A | B) = 1. Same condition B on both sides.
- Here A = "gap at least as big as ours", B = "no effect". So 1 − 0.038 = 0.962 = P(gap smaller than ours | no effect).
- What people *want* is P(H1 | data) = 1 − P(H0 | data). That flips the condition, a different quantity that needs a base rate (Bayes).
- Good wording that uses 96%: **"Our gap is bigger than 96% of the gaps a do-nothing page would produce."** It's the percentile of our
  result in the null distribution: true, and exactly as strong as the p-value, no stronger.
- Small precision: p is P(data *at least this extreme* | H0), not P(this exact data | H0); a single exact outcome has probability ≈ 0.

## 2026-10-05 · "Is there an equivalent P(data | H1), the probability of the data if the site did make a difference?"
**Yes, but H1 must name an effect size δ**: "some difference" is many hypotheses, each predicting different data.

For the lesson-2 A/B test (12,000 per arm, 5.0% → 5.6%, z ≈ 2.08):

| True lift δ | Likelihood ratio P(data | δ) / P(data | H0) | Power P(significant | δ) |
|---|---|---|
| 0.3 pts | 5.0 | 0.18 |
| 0.5 pts | 8.1 | 0.41 |
| 0.6 pts (observed) | 8.6 (maximum, = e^{z²/2}) | 0.55 |
| 0.8 pts | 6.8 | 0.79 |

- The **likelihood ratio** is the evidence: how many times better δ explains the data than "no effect".
- Bayes: posterior odds = prior odds × likelihood ratio. Using the most favourable ratio (8.6):
  P(page works | data) ≤ 0.49 if 10% of such ideas work; ≤ 0.90 if 50% do. So p = 0.038 ≠ "96% sure".
- Power is the same idea used before the test: P(reject | δ). Here the test only had ~55% power for a 0.6-point lift.

Method: normal approximation, z-statistic ~ N(δ/SE, 1) under δ; ratio of normal densities at the observed z; computed in Python.
Read: Casella & Berger §8.2.1 "Likelihood Ratio Tests" and §8.5.2 "Likelihood Ratio As Evidence".
