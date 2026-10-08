# Tech lead at team scope; wants the Solver path; staff evidence is thin outside one team

Staff placement (eng 0001, 2026-10-08, graded on the progress server). One line per finding:

- Learner stated they are a tech lead ("one of my informal titles for both of the programs I work on"), not yet doing staff-scope work.
- Results: none at staff scope; turns stakeholder requirements into issues for their team (after the staff engineer's initial gathering).
- Direction: partial. Deep command of the system and its metrics ("yes it is written down"); no written long-horizon strategy.
- Talent: partial. Assigns issues, answers questions, leads debugging; no named mentee growth.
- Culture: partial. Status to management, metrics to stakeholders; "people do generally just agree with me"; no contested cross-team decisions yet.
- Target archetype: Solver (learner's words: deep work, "war stories" for moving jobs, "the go to Smart Guy" for job security).
- Design sketch (Server #13): asked staff-level questions (latency/volume, async games); server-canonical state right. Missed move ordering /
  idempotency, the server-owned 60 s forfeit timer, cross-server routing of one game's sockets, and crash recovery of live games; proposed
  batching validations (misplaced optimization).
- Vim: knows basics (hjkl, dd, dw, yy, yw); walked to line ends with w/l rather than `A`. Asked to be taught as they go; drills felt excessive.

**Implications:** nothing in the Staff lane shrinks. SE120 (system design) matters most for the Solver target; SE110 (writing) stays full
(no written strategy). Vim switches to one shown tip per lesson (TEACHING-LOG rule 30). Rep 0 waived.
