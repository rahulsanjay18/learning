# Practice that doesn't just repeat the same question (proposal, 2026-10-08)

*Written because review re-asks the exact question you missed. Status: phase 1 (question families) is the convention from now on;
phase 2 (the review deck picks a sibling) is a to-do in HANDOFF, not built yet.*

## TL;DR
- **The problem:** today a missed question comes back word for word the next day (`assets/README.md`, "Daily review deck"). By the
  third time you can answer from memory of *that question* ("it was the second option") without the idea.
- **What the research says (summary, sources below):** retrieval practice helps you remember; practice that is **varied** and
  includes **new questions on the same idea** builds knowledge you can use in new situations, not only the practiced response
  [1][2][3]. Same-question repetition still helps you remember the fact. So keep some repetition, but add variety.
- **The fix:** every objective gets a **question family**, 3–5 questions testing the same idea in different ways. A miss brings back
  a *different* member of the family (a sibling), and the original comes back later. That way a correct answer shows you know the
  idea, not that you recognized the question.

## Phase 1: question families (convention now, no code needed)
1. A family = one objective × several surface forms. Name them with a shared prefix: `data-id="axioms-v1"`, `axioms-v2`, …
   (`<family>-v<n>`). Ids stay stable forever (review schedules hang off them).
2. Kinds of variant, from closest to furthest:
   - **Isomorphic:** same structure, new numbers or a new context (die → cards). Catches "memorized the number".
   - **Format switch:** the same idea asked as recall instead of choice, or choice → typed answer, or "find the error in this
     worked solution". Rule 8 says multiple choice only measures recognition; a format switch checks recall.
   - **Reverse:** give the answer, ask for the setup ("which test has this rejection region?").
   - **Transfer:** the idea in a situation the lesson never showed (Butler's "new inferential questions" [2]).
   - **Discriminate:** a near-miss that only differs in the confusable detail (Type I vs II). Interleaving works best on
     confusable pairs [see notes/evidence-spacing-and-variety.md].
3. Where they live: v1 (and often v2) in the lesson; the rest in a later lesson's warm-up or review day, or in the family bank
   at `topics/<t>/lessons/NNNN-name.variants.md` (Markdown quiz blocks, same syntax as lessons) for phase 2 to draw from.
4. Every variant obeys the question rules (TEACHING-LOG rules 2, 3, 5, 6, 8, 11, 16, 18, 19, 23, 25; self-contained, unambiguous,
   options equal in length).

## Phase 2: the review deck uses families (to build; HANDOFF)
- When a family member is due after a miss, `review.html` shows an **unseen sibling** first; the missed item returns a box later.
- After two right answers on *different* members, the family counts as known (the mastery rule, rule 20, gets a cleaner signal).
- Numeric questions can be **parametric**: a template with random parameters and an answer formula, checked by the math plugin, so
  there is always a fresh isomorphic variant.
- `quiz.py` (chat review) and the progress server's `/due` need to understand families too.

## Sources and their limits
1. Brown, Roediger & McDaniel, *Make It Stick* (2014), ch. 3 "Mix Up Your Practice" (in your library, grade A, `cb24c0244c`):
   "Practice that's spaced out, interleaved with other learning, and varied produces better mastery, longer retention, and more
   versatility." A popular-science synthesis of the research. Good map, not primary evidence.
2. Butler (2010), "Repeated testing produces superior transfer of learning relative to repeated studying", *JEP: Learning, Memory,
   and Cognition* 36(5):1118–1133. Final tests used the same questions, new inferential questions in the same domain, and in new
   domains; testing beat restudying on all of them. Replicated (van Eersel et al. 2016, via the FORRT replication atlas).
   https://profiles.wustl.edu/en/publications/repeated-testing-produces-superior-transfer-of-learning-relative-/ ;
   https://forrt.org/flora-replication-atlas/doi/10.1037/a0019902/ . **Limit:** prose passages and college students; it compares
   testing with restudying, not same-question with varied-question practice directly.
3. Pan & Rickard (2018), "Transfer of test-enhanced learning: Meta-analytic review and synthesis", *Psychological Bulletin*
   144(7):710–756, doi:10.1037/bul0000151. Testing does transfer to new contexts on average, but not uniformly; I haven't read the
   moderator tables, so I don't claim effect sizes from it. A related Pan study found little transfer between different cue
   combinations of the same word triplet, which is a reason to **test the variants on you** rather than assume they work.
   https://escholarship.org/content/qt45x0w7t8/qt45x0w7t8.pdf
- **My judgment, not evidence:** the five variant kinds above, and "two right on different members = known".
