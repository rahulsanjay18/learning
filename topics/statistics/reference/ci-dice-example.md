# A 95% confidence interval, start to finish: the loaded die

*Saved 2026-10-05 from a question ("describe creating a 95% CI from dice whose face probabilities you don't know"). One example, every step.*

## The setup
Someone hands you a die. It might be loaded. You want to know **θ = P(the die shows a six)**.
- θ is a **fixed number**. You just don't know it. (For the record, the simulated die below secretly has θ = 0.25. A fair die has 1/6 ≈ 0.167.)
- You can't look inside the die, but you can roll it.

## Step 1: Collect data
Roll it **n = 600** times and count the sixes. Each roll is "six" (1) or "not six" (0): a Bernoulli(θ) trial.

The first 20 rolls: `3 2 5 1 4 3 1 4 1 3 1 1 3 6 1 2 5 6 4 3` (two sixes so far).
After all 600: **146 sixes**.

## Step 2: The point estimate
θ̂ = 146 / 600 = **0.243**.

This is your best single guess. But it's almost surely not *exactly* θ: roll another 600 and you'd get a different count.
(This is Casella & Berger's point in §9.1: a point estimate is exactly right with probability 0.)

## Step 3: How much does θ̂ wobble? (the standard error)
θ̂ is an average of 600 zeros and ones.
- One roll has variance θ(1 − θ). That's the Bernoulli variance, so the mean fixes the spread and you need no separate SD.
- An average of n independent rolls has variance θ(1 − θ)/n.
- So SD(θ̂) = √(θ(1 − θ)/n).

Problem: that formula contains θ, which is what we don't know. **Plug in the estimate** instead:

SE = √(0.243 × 0.757 / 600) = **0.0175**

(The true value, √(0.25 × 0.75 / 600) = 0.0177, is almost the same. The plug-in is fine when n is large.)

## Step 4: What shape does the wobble have?
By the central limit theorem, an average of many independent rolls is approximately normal: θ̂ ≈ Normal(θ, SE²).

A normal variable lands within 1.96 SDs of its mean 95% of the time:

P(θ − 1.96·SE ≤ θ̂ ≤ θ + 1.96·SE) ≈ 0.95

## Step 5: Flip it into an interval for θ
"θ̂ is within 1.96·SE of θ" is the same statement as "θ is within 1.96·SE of θ̂". So

**θ̂ ± 1.96 × SE = 0.243 ± 1.96 × 0.0175 = 0.243 ± 0.034 = [0.209, 0.278]**

That's the 95% confidence interval. (Same algebra as Casella & Berger Example 9.1.3, where they rearrange P(X̄ − 1 ≤ μ ≤ X̄ + 1).)

## Step 6: Read it
- **Say:** "Rolling this way, intervals built by this method catch the true P(six) 95% of the time. This one is [0.209, 0.278]."
- **Don't say:** "There's a 95% chance θ is in [0.209, 0.278]." θ isn't random. It's either in this interval or not (here it is: 0.25). The 95% belongs to the procedure.
- **Use it:** a fair die's 1/6 = 0.167 is **outside** the interval, so the data are good evidence the die is loaded toward six. That matches a two-sided test at α = 0.05 rejecting "fair".

## Step 7: Check the "95%" by brute force
Repeat the whole experiment 10,000 times (600 rolls each, same loaded die), building an interval every time.
**94.8%** of the intervals contained 0.25. That's what "95% confidence" means.

## What changes with fewer rolls
With only **n = 60** rolls: 19 sixes, θ̂ = 0.317, interval **[0.199, 0.434]**.
- It's about 3.2 times wider (√(600/60) = √10 ≈ 3.2): the width shrinks like 1/√n.
- Now the fair value 0.167 is barely outside.
- With small n or θ near 0 or 1, this simple ("Wald") interval covers less often than 95%. Better intervals exist (Wilson, or inverting a test as in Casella & Berger §9.2.1), and you'll meet them in Chapter 9.

## The recipe in one line
**estimate ± 1.96 × √(estimate × (1 − estimate) / n)**, valid when n is large and the estimate isn't near 0 or 1.

## Sources
- Casella & Berger, *Statistical Inference*, 2nd ed.:
  - §9.1, pp. 417–419: interval estimators, coverage probability, "the interval is the random quantity", Example 9.1.3.
  - §3.2: Bernoulli and binomial.
  - §5.5.3: convergence in distribution and the central limit theorem.
  - §9.2.1: inverting a test statistic.

  In collection (grade A).
- Brown, Cai & DasGupta (2001), "Interval Estimation for a Binomial Proportion", *Statistical Science* 16(2), 101–133: the simple interval's poor coverage for small n (cited from memory).
- Every number above came from a seeded Python simulation (die weights 0.15 × 5, 0.25 for six; n = 600; 10,000 repeats for coverage).

---

# Part 2: "But how do you know it's 95% if θ stays secret?"
*Follow-up question, same day.*

## The key point
Steps 1–6 above **never used θ**. They used only the rolls: count, θ̂, SE, interval. θ = 0.25 appeared only in step 7, as a check.

**You know it's 95% because the guarantee was proved for every possible θ before you rolled.** If the method covers 95% of the
time whatever θ is, it covers 95% of the time for *your* θ, without your ever learning it.

## A die with a truly secret θ
The computer picked θ at random between 0.1 and 0.4 and hid it. Then:
- 600 rolls, **72 sixes**, θ̂ = 0.120, SE = √(0.12 × 0.88 / 600) = 0.0133.
- Interval: **0.120 ± 0.026 = [0.094, 0.146]**.
- Again, nothing here needed θ.

## Why the procedure works for every θ
For a fixed θ, the chance that the interval catches it, P_θ(θ̂ − 1.96·SE ≤ θ ≤ θ̂ + 1.96·SE), can be computed exactly by adding up
binomial probabilities. This is the **coverage probability** (Casella & Berger, Definition 9.1.4). Do it for many candidate θs:

| If the secret θ were… | 0.02 | 0.05 | 0.10 | 1/6 | 0.25 | 0.40 | 0.50 |
|---|---|---|---|---|---|---|---|
| Coverage, **n = 600** | 0.945 | 0.937 | 0.939 | 0.949 | 0.946 | 0.950 | 0.945 |
| Coverage, n = 60 | 0.701 | 0.806 | 0.941 | 0.932 | 0.939 | 0.934 | 0.948 |

- With 600 rolls the method catches θ about 94–95% of the time **whichever θ it is**. So you don't need to know which one is yours.
- Casella & Berger call the worst case over all θ the **confidence coefficient** (Definition 9.1.5). It's the honest guarantee:
  "at least this often, no matter what θ is."
- With 60 rolls the guarantee breaks for θ near 0 (70% at θ = 0.02). For those cases, "95%" would be false advertising. That's why
  Chapter 9 builds better intervals.

## So what does one interval tell you?
The method is a machine that's right about 95% of the time, for any die. You ran it once and got [0.094, 0.146]. You can't know
whether this run was one of the 95% or one of the 5%. "95% confident" is your trust in the machine, not a probability about this
one interval. (The reveal: the secret θ was **0.136**, inside. But the next die could be the 1 in 20.)

## Sources (part 2)
- Casella & Berger, *Statistical Inference*, 2nd ed., §9.1, pp. 417–419: Definition 9.1.4 (coverage probability) and Definition
  9.1.5 (confidence coefficient = infimum of coverage over θ). In collection (grade A).
- Coverage table: exact binomial sums for the Wald interval, computed in Python. The secret-θ demo: seeded Python simulation, θ
  drawn uniformly on [0.1, 0.4] and printed only after the interval.
