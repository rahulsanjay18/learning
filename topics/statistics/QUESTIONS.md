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
