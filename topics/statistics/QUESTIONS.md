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

## 2026-10-05 · "I don't understand: 'with huge samples, tiny effects get tiny p-values' and 'p = 0.01 means a bigger effect than p = 0.20' (a misreading)"
**One formula behind both:** p depends on z = effect / SE, and SE shrinks like 1/√n. Small p can mean a big effect *or* lots of data.

- Same tiny lift (5.00% → 5.05%): 12,000 per arm → z 0.18, p 0.86; 5,000,000 per arm → z 3.62, p 0.0003.
- Study A: lift 2.00 pts, 500 per arm → p 0.18. Study B: lift 0.15 pts, 300,000 per arm → p 0.008. Smaller p, 13× smaller effect.
- So report the effect size (better: a confidence interval) with every p-value. ASA principle 5: a p-value "does not measure the size of an effect or the importance of a result".

Numbers: pooled two-proportion z-test, two-sided, computed in Python. Source for principle 5: Bruce, Bruce & Gedeck p. 108 (ASA statement).

## 2026-10-05 · "I don't know if you explained 'with huge samples, tiny effects get tiny p-values'" (intuition, no formula)
A coin that lands heads 50.5% of the time (tiny bias).
- 100 flips: noise ≈ ±5 heads (SD = 0.5√n); bias adds 0.5 heads → z ≈ 0.1, p ≈ 0.9. Indistinguishable from fair.
- 1,000,000 flips: noise ≈ ±500 heads; bias adds 5,000 heads → z ≈ 10, p astronomically small.
- The bias grows in proportion to n; the noise only grows with √n. Enough data makes *any* nonzero effect "significant".
- "Statistically significant" = detectably not zero, **not** big or important.

## 2026-10-05 · Casella & Berger Example 9.1.3: "why is 1/4 in the denominator? I thought the SD formula has √(number of samples)"
**It does. √(1/4) is σ/√n, written as √(σ²/n).** The example's setup (stated in Example 9.1.2, one example earlier) is a sample of
**n = 4** from a normal with **σ = 1**, i.e. X₁, …, X₄ iid n(μ, 1).

- Var(X̄) = σ²/n = 1/4, so SD(X̄) = √(σ²/n) = √(1/4) = 1/2. Same number as σ/√n = 1/√4 = 1/2. Casella & Berger write the
  variance under the root, which hides the √n.
- So the step is just standardizing: X̄ − μ ranges over [−1, 1]; dividing by SD(X̄) = 1/2 turns that into [−2, 2] in z-units.
- Then P(−2 ≤ Z ≤ 2) = 0.9545 (the book's .9544 comes from table rounding).
- **The general version:** P(μ ∈ [X̄ − c, X̄ + c]) = P(|Z| ≤ c√n/σ). Here c = 1, n = 4, σ = 1, so it's 2. With n = 16, the same
  ±1 interval would cover with P(|Z| ≤ 4) ≈ 0.99994: more data means the same width buys more confidence.

Check: simulated 200,000 samples of size 4 from n(0, 1): SD of X̄ = 0.501, coverage of [X̄ − 1, X̄ + 1] = 0.954 (Python).
Source: Casella & Berger, *Statistical Inference*, 2nd ed., §9.1, Examples 9.1.2–9.1.3, pp. 417–418 (the reading for lesson 3);
Var(X̄) = σ²/n is their Theorem 5.2.6 (§5.2) [section number from memory: book server was down, re-check].

## 2026-10-05 · Lesson 3: "How do you know the standard error? Don't you need the sample SD? Was it given?"
**It wasn't given: the lesson just stated "SE 0.29". That was a gap (teaching log entry 16).** For a conversion rate you don't need a
separate sample SD, because a 0/1 outcome's variance is fixed by its rate.

- Each user converts (1) or not (0): Bernoulli(p), variance p(1 − p). A rate is an average of n of these, so Var(p̂) = p(1 − p)/n.
  The mean pins down the spread; that's special to 0/1 data (for, say, revenue per user you *would* need the sample SD).
- The two groups are independent, so the variance of the difference is the sum (you got Var(aX + bY) right on the pretest):
  SE = √(0.050 × 0.950 / 12,000 + 0.056 × 0.944 / 12,000) = 0.00289 = **0.29 percentage points**.
- 95% CI: 0.6 ± 1.96 × 0.29 = [0.03, 1.17] points.
- In `ci-lower` (estimate 2.0, SE 0.5) the SE *was* given.

Check: computed in Python (unpooled SE 0.002892). Formula on the formula sheet; Bernoulli variance: Casella & Berger §3.2.

## 2026-10-05 · "Is lesson 3 based on the reading or an extension of it?"
**Both, and the lesson didn't say which part was which.** From the reading (C&B §9.1): what an interval estimator is, coverage
probability, why the interval (not μ) is random: sections 3–4. Beyond the reading (applied, from *Practical Statistics for Data
Scientists*): effect size, "significant vs. worth it", deciding with an interval: sections 1, 2, 5. The page now labels each section.
From Chapter 1 on (the cover-to-cover program), lessons are built from the reading; applied extensions will be marked as such.

## 2026-10-05 · Replies to the lesson 3 reading notes
- **read-gain** ("P(sample mean is exactly a given number) is 0; with an interval we gain some confidence the true mean is in it"):
  right. The sharper version: the *point estimate* X̄ equals μ with probability 0, while the interval [X̄ − 1, X̄ + 1] covers μ with
  a **known** probability, .9544. The gain is a number you can state, not just "some confidence". (0.8)
- **read-coverage** ("the probability that the true parameter is in the interval estimator"): exactly Definition 9.1.4. One addition:
  it's computed over repeated samples, and it can depend on θ; the confidence coefficient is its worst case (infimum) over θ. (1.0)
- **read-random** ("the parameter is fixed but unknown; the endpoints are random variables, so the interval is random"): right. The
  second half of the question was why that matters for phrasing: since μ isn't random, "95%" describes the *method* across samples,
  not "a 95% chance μ is in this one interval". Once you have the interval [0.03, 1.17], μ is either in it or not. (0.7)

## 2026-10-05 · "Describe creating a 95% CI from dice whose face probabilities you don't know: one cohesive example"
Full walk-through in `reference/ci-dice-example.md`. In short: roll 600 times, 146 sixes, θ̂ = 0.243, plug-in SE = √(θ̂(1 − θ̂)/n) =
0.0175, CLT makes θ̂ ≈ normal, so θ̂ ± 1.96·SE = [0.209, 0.278]. Fair 1/6 is outside, which is evidence of loading. 10,000 repeats: 94.8% of
intervals covered the true 0.25.

## 2026-10-05 · "What if θ is kept secret? How do you know you have a 95% interval?"
Because the interval's steps never use θ, and the 95% is a property proved for **every** θ: exact coverage at n = 600 is 0.94–0.95
for θ from 0.02 to 0.5, so it holds for whichever θ is yours. The worst case over θ is the confidence coefficient (C&B Def. 9.1.5).
One interval is either right or wrong; "95%" is trust in the method. Details and a secret-θ demo: `reference/ci-dice-example.md` part 2.

## 2026-10-06 · Pretest free response: "Ice cream and drownings: why not causal, and how would you get at causation?" (graded 0.75)
**You named the confounder (summer), which is the key step.** The remedy is the weak part: "track people who got ice cream and then
drowned" is still observational, so summer confounds it in exactly the same way (people eat ice cream *and* swim on hot days).
- **Better remedies:** compare within the same weather (stratify, or regress drownings on ice-cream sales *and* temperature, and see
  whether the ice-cream coefficient survives), or, the gold standard, randomize who gets ice cream.
- **The sentence to reuse:** "The correlation is explained by a common cause, hot weather; holding temperature fixed, I'd expect the
  association to vanish." Not: "correlation does not imply causation" alone, which names the problem without diagnosing it.
