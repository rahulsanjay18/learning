# Lesson 7 (conditional probability, independence): both objectives Got it; two supporting ideas Not yet

**Objective 1, tell pairwise from mutual independence: Got it** (the counterexample part not yet shown). `read-twofail` named
exactly which candidate definition each book example breaks, `mutual-v1` (letters, sorting) right first try. `mutual-v2` answered
10 for the number of equations for four events (it is 11): a count slip, probably the four-way equation left out. `mutual-v3`
(build a counterexample on {1,2,3,4}) not answered ("I am tired"): warm-up in lesson 8.

**Objective 2, derive Bayes' rule stating what it assumes: Got it.** `bayes-v3` stated P(Ai) > 0 and P(B) > 0 and used no
independence: the exact pretest gap is closed. The route was unusual and valid (rewrite each term as P(Aj | B)P(B), then
Σ P(Aj | B) = P(S | B) = 1). False side clauses, not about the objective (TEACHING-LOG rule 25): "P(S ∩ B) = P(S) = 1" (it is
P(B)); additivity cited as Definition 1.3.12 (mutual independence) instead of Axiom 3; ∩ written for ∪. Score 0.8.

**Not yet (supporting ideas, re-teach 5 min each at the top of lesson 8):**
- `condp-v1`: answered 1/2 for P(sum ≥ 10 | at least one 6); 1/2 is P(sum ≥ 10 | *the first* die is 6). "At least one 6" has 11
  outcomes, not 6 or 12: the same "what exactly were you told" trap as the three prisoners.
- `indep2-v2`: "disjoint events with positive probabilities are independent: yes". Disjoint is maximal dependence.

**Platform, not the learner:** `indep2-v1` was right (`1-(35/36)^24`, and later 0.49); number boxes didn't evaluate expressions
and the tolerance was 0.0005 while the prompt asked for "a decimal". Fixed (lp.js evaluates expressions with math.js; the renderer
loads math.js for `number`; tolerance 0.005 for answers above 0.2; prompts say the precision). Counted as Got it.
`bayescalc-v1`: the first answer recorded was 3/10 + 1/7 = P(brown), the denominator, not P(litter 1 | brown). Can't tell
(maybe an unfinished expression): one warm-up in lesson 8.

Reading notes: `read-condp` 1.0, `read-prisoner` 0.9 (calculation right; the first sentence states A's mistake as if it were
right: "the warden says B dies" is narrower than "B is not pardoned"), `read-twofail` 1.0.

**Evidence:** lp-results 2026-10-13 (pasted, sync off; 4/15 first try, 1 unanswered), free responses in the same paste.
**Implications:** lesson 8 opens with the two re-teaches and warm-ups `mutual-v3` and a `bayescalc` variant, then §1.4–1.6 as planned.

**Update (same evening):** the learner says they sometimes misread a question. `condp-v1` ("at least one 6" answered as if "the
first die is 6") could be a misread as easily as a misconception, so it moves from Not yet to Can't tell: one warm-up in lesson 8
(a miss there makes it Not yet). `indep2-v2` stays Not yet (the chosen option states the misconception). Standing convention: a
"misread <id>" in the results note counts that miss as a slip.
**Update 2:** learner reports `condp-v1` was right on the second try (typed, after a bare "wrong"): a slip, so Can't tell stands
(one warm-up, no re-teach). `indep2-v2` was not right on the second try: Not yet stands.
