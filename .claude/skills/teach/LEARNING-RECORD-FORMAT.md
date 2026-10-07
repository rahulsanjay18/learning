# Learning Record Format

Learning records live in `./learning-records/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily: only when the first record is written.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions. They are used to calculate the zone of proximal development.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

That is the whole format. A learning record can be a single paragraph. The value is recording _that_ this is now known and _why_ it changes what to teach next, not in filling out sections.

## Optional sections

Only include these when they add genuine value. Most records won't need them.

- **Status** frontmatter (`active | superseded by LR-NNNN`): useful when an earlier understanding turns out to be wrong and is replaced.
- **Evidence**: how the user demonstrated the understanding (a question answered, an exercise completed, prior experience cited). Useful when the claim might be revisited.
- **Implications**: what this unlocks or rules out for future sessions. Worth recording when non-obvious.

## Numbering

Scan `./learning-records/` for the highest existing number and increment by one.

## When to write a learning record

Write one when any of these is true:

1. **The user demonstrated genuine understanding of something non-trivial**: not just exposure, but evidence they can use the concept correctly. This sets a new floor for what to teach next.
2. **The user disclosed prior knowledge**: "I already know X." Record it so future sessions don't re-teach it. Also record the _depth_ claimed.
3. **A misconception was corrected**: the user previously believed something wrong and now sees why. These are high-value: they predict future stumbling blocks for related topics.
4. **The mission shifted in response to learning**: the user discovered they cared about something different than they thought. Cross-link to [[MISSION.md]] and update it.

### What does _not_ qualify

- Material that was merely covered. Coverage is not learning. Wait for evidence.
- Anything already captured tersely in [[GLOSSARY.md]] as a term definition. Don't duplicate.
- Session-by-session activity logs. Learning records are not a journal: they are decision-grade insights.

## Writing rules (adapted from pi-observational-memory's observer and reflector prompts)

Records are the only memory a future session has of the learner, so write them so they can't be misread
(github.com/elpapi42/pi-observational-memory, `src/agents/observer/prompts.ts`, `reflector/prompts.ts`; MIT):

- **Assertions vs questions.** "Learner stated they learned type I/II errors as false positive/negative" is not the same as
  "Learner asked what type I error means". A statement about themselves is authoritative; a later question doesn't undo it.
- **Quote the learner's own terms** when they're non-standard ("I usually remember them as false positive and false negative").
- **Frame changes as supersession**: "now reads p-values correctly (previously read p as P(H0 is true))", so both states are visible.
- **Mark completions**: "completed: 0006 objectives 1–2 Got it", so nothing is re-taught by accident.
- **One fact per line.** Split compound findings; a future "did they get X?" should match one line.
- **Cite the evidence** by id: the lesson and quiz `data-id`, the QUESTIONS.md entry or the grading result.
- **Only durable facts.** Before writing, ask: would a future session make a wrong decision, redo work or break a learner
  preference without this? If not, it isn't a record (scores and due dates live on the progress server).

## Supersession

When a later record contradicts an earlier one (the user's understanding deepened or corrected), mark the old record `Status: superseded by LR-NNNN` rather than deleting it. The history of how understanding evolved is itself useful signal.
