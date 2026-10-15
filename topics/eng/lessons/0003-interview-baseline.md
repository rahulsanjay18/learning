---
title: Interview baseline: one coding round, one story, one deep dive
subtitle: Two days: about 55 minutes, then about 20. One win: you know which interview round is your weakest, so practice starts there.
crumb: Engineering career · Lesson 3 · IV000 interview baseline
main: data-pretest=true data-skip=true
index: Interview baseline (reading: Hello Interview's Google L6 and Meta E6 guides)
---
## Why this lesson
This course prepares you for interviews at the hardest common bar: a staff loop at a big tech company. Before practicing anything, I need
to see where you stand on each kind of round, so the practice that follows spends its time on your weakest ones. This page is a
baseline. Nothing here is graded for credit, and "I don't know" is a useful answer.

This is two days of work, not one. **Day 1 (about 55 minutes):** the Vim tip, the reading, and a timed coding problem. **Day 2 (about
20 minutes):** a leadership story, a project deep-dive outline, and a self-rating. The page keeps your answers between days.

## Vim tip (1 minute, optional)

::: callout
**Change inside parentheses: `ci(`.** Drew Neil's tip 52 in *Practical Vim*: text objects work on structure, so `i(` means "everything
inside this pair of parentheses" and `a(` means "the parentheses too". With the cursor anywhere inside `( … )`, `ci(` deletes the
contents and puts you in Insert mode. In the Vim I checked with (9.1), it also works from earlier on the same line: Vim jumps ahead
to the next `(`. Older Vims need `f(` first.

Example, useful in today's coding problem: turn `if in_bounds(x, y, z):` into `if in_bounds(nx, ny, nz):`. With the cursor on the
`i` of `if`: `ci(`, type `nx, ny, nz`, `<Esc>`. The same idea works for `ci"` (inside quotes), `ci[` and `ci{`.

If you want feedback, paste your keys below (or a `vim -W` recording: [how](../reference/vim-drills.md)).
:::

::: free vim-v03
(Optional) Your keys, if you tried it:
--- rubric
Optional, no score pressure. Replay with python3 scripts/vimcheck.py --drill topics/eng/vim-drills.json v03-cib "<keys>" (add --caret
for a cat -v recording). One correction if there's a shorter or more idiomatic way; otherwise say it's right.
:::

## Part 1: what a staff loop looks like (reading, about 10 minutes)

::: reading
### Reading
Two free guides from Hello Interview. For each, read the overview of the process and the section on each interview round. Skip the
sections on pay, leveling negotiation and "how to prepare" lists.
1. *Google L6 (Staff) Software Engineer Interview Guide*: <https://www.hellointerview.com/guides/google/l6>
2. *Meta E6 (Staff) Software Engineer Interview Guide*: <https://www.hellointerview.com/guides/meta/e6>

Both pages describe the common case, not a promise: rounds vary by company, team and recruiter, and Meta's mix of coding rounds was
still changing in 2026. While reading, note which rounds appear in both loops and which appear in only one.
:::

::: free read-iv-both
Which round types appear in both loops? Which appear in only one?
--- rubric
Reading note; reply to it. Both: coding (Google 1–2 onsite, Meta 1–2), system design (2 rounds in each), behavioral/leadership (1 each).
Google only: Role-Related Knowledge, the Google Hiring Assessment questionnaire. Meta only: the project retrospective (optional,
team-dependent), the AI-enabled coding round.
:::

::: free read-iv-ai
How does Meta's AI-enabled coding round differ from its classic coding round, and what is it graded on?
--- rubric
Reading note; reply to it. About 60 minutes in CoderPad with an AI assistant, one larger multi-file problem in stages; graded on the
candidate's own problem solving, code quality and how well they verify the AI's output, not on prompt engineering. Classic: 45
minutes, usually two LeetCode-medium problems, code can't be run.
:::

::: free read-iv-surprise
What surprised or confused you?
--- rubric
Reading note; reply to whatever it raises.
:::

Here is the common shape of each onsite, from the two guides [1][2]:

| Round | Google L6 | Meta E6 |
|---|---|---|
| Coding | 1–2 rounds, 45 min | 1–2 rounds, 45 min, usually two medium problems each; for E6 the 60-minute AI-enabled round typically replaces one |
| System design | 2 rounds, 60 min | 2 rounds, 45 min (System Design for infrastructure roles, Product Architecture for product roles) |
| Behavioral / leadership | 1 round, 45 min ("Googliness and Leadership") | 1 round, 45 min |
| Domain or past work | Role-Related Knowledge, 45–60 min | Project Retrospective, 45 min, optional and team-dependent |

One thing follows from the table and matters for how you practice: **two of the interviews are design rounds in both loops** (out of five or six
in all) [1][2]. Coding still has to be solid, but at staff level it's the floor, not the ceiling.

::: categorize iv-rounds
Match each thing an interviewer is looking for to the round the guides say grades it.
- Clean code under time pressure, with edge cases handled unprompted > Coding
- Trade-offs between architectures and depth on scaling and data > System design
- Influence without formal authority and resolving conflicts > Behavioral
--- explain
From the guides: Meta's classic coding round looks for clean, production-quality code, proactive edge-case handling and clear
communication; both design rounds grade trade-offs and technical depth; Meta's behavioral round emphasizes cross-team work, conflict
and influence without formal authority [1][2].
:::

::: choice iv-level
According to Hello Interview's Meta E6 guide, which rounds most drive the decision between E6 and a lower level?
- [x] The two design rounds
- [ ] The two coding rounds
- [ ] The single behavioral round
- [ ] The single retrospective round
--- hint
Check the Meta guide's section on the design rounds.
--- explain
The guide calls the design rounds "the part of the loop that most drives your E6 level determination" [2]. The phone screen can
signal a down-level early, but it isn't the main decider.
:::

## Part 2: a timed coding round (35 minutes)

*Beyond the reading: the problem is new; the rules of the round come from the Meta guide.*

This is a baseline version of a classic coding round: one medium problem, at most 35 minutes, written in Vim. The real round is
faster: Meta's classic round is usually two medium problems in 45 minutes, so about 20 minutes each [2]. Today 35 minutes is the cap,
and how close you come to 20 is the measurement. In Meta's classic round you can't run your code [2], so
do the same here: **write the whole solution in Vim without running it**, then paste it into the box below to check. Talk through your
choices as you would to an interviewer; the short written plan below stands in for that.

Set a timer for 35 minutes and start it now. Stop when it rings, even if you haven't finished; how far you got is the measurement.

::: callout
**The problem.** A 3D chess board is an \(n \times n \times n\) cube of cells, with coordinates \((x, y, z)\), each from \(0\) to
\(n - 1\). A knight moves **two cells along one axis and one cell along a different axis**, leaving the third coordinate unchanged
(so \((0,0,0)\) can reach \((1,2,0)\) or \((0,1,2)\), but not \((1,1,1)\)). It may not leave the board.

Write `min_knight_moves(n, start, target)`, where `start` and `target` are tuples of three integers on the board. Return the fewest
knight moves from `start` to `target`, `0` if they're the same cell, and `-1` if the knight can never get there. Boards are up to
\(n = 30\).
:::

::: free iv-plan
Before writing code (2–3 minutes): what would you ask the interviewer, which approach will you use and why, and its time and space
cost in terms of \(n\)?
--- rubric
Baseline, ungraded. Strong signals: clarifying questions (is n ≥ 1? can start equal target? are coordinates guaranteed on the board?
is -1 really possible: yes, for n ≤ 2 the knight can't move at all; for n = 3 the center isn't reachable); names BFS because every
move costs the same, so the first time BFS reaches a cell is by a shortest path; counts the moves: 24 (3 choices of axis for the 2-step
× 2 remaining axes for the 1-step × 2 × 2 signs); cost O(n³) cells × 24 moves, O(n³) space for the visited set. Note anything wrong
or missing, e.g. DFS for shortest path, or no visited set.
:::

::: py iv-code timeout=20
Paste the solution you wrote in Vim, then press **Check**. (Run is never scored, but don't run it until you've finished writing.)
--- code
from collections import deque

def min_knight_moves(n, start, target):
    # your solution
    pass
--- check
from collections import deque as _dq
from itertools import product as _prod
import random as _rnd
_dirs = [d for d in _prod(range(-2, 3), repeat=3) if sorted(map(abs, d)) == [0, 1, 2]]
assert len(_dirs) == 24
def _ref(n, s, t):
    s, t = tuple(s), tuple(t)
    if s == t: return 0
    seen = {s}; q = _dq([(s, 0)])
    while q:
        (x, y, z), k = q.popleft()
        for dx, dy, dz in _dirs:
            p = (x+dx, y+dy, z+dz)
            if all(0 <= c < n for c in p) and p not in seen:
                if p == t: return k + 1
                seen.add(p); q.append((p, k + 1))
    return -1
_cases = [(8,(0,0,0),(0,0,0)), (8,(0,0,0),(1,2,0)), (8,(0,0,0),(0,1,2)), (8,(0,0,0),(7,7,7)), (1,(0,0,0),(0,0,0)), (2,(0,0,0),(1,1,1)), (3,(0,0,0),(1,1,1)), (8,(3,3,3),(3,3,4))]
_g = _rnd.Random(7)
for _ in range(40):
    _n = _g.randint(1, 9)
    _cases.append((_n, tuple(_g.randrange(_n) for _ in range(3)), tuple(_g.randrange(_n) for _ in range(3))))
for _n, _s, _t in _cases:
    _got = min_knight_moves(_n, _s, _t)
    assert _got == _ref(_n, _s, _t), f"min_knight_moves({_n}, {_s}, {_t}) returned {_got}, which is not the fewest moves"
_got = min_knight_moves(30, (0, 0, 0), (29, 29, 29))
assert _got == _ref(30, (0, 0, 0), (29, 29, 29)), f"min_knight_moves(30, (0, 0, 0), (29, 29, 29)) returned {_got}"
--- explain
One correct shape, for comparison after you've checked yours: breadth-first search from `start`. Generate the 24 knight moves once
(every vector whose absolute values are 0, 1 and 2 in some order), keep a visited set so each cell is queued once, and return the
distance the first time `target` comes out of the search. If the queue empties first, return `-1`. Each cell is visited at most once
and tries 24 moves, so the cost is \(O(24\, n^3)\) time and \(O(n^3)\) space.
:::

::: free iv-review
When the timer rang (or when you finished): how many minutes did it take, did it pass on the first check, and what would you say if
the interviewer asked "now make it fast for \(n = 1000\)"?
--- rubric
Baseline, ungraded. Record the minutes and whether it passed first try (35 min is today's cap; about 20 min is on pace for the real round).
Follow-up signals: bidirectional BFS (two frontiers of radius about d/2, far fewer cells explored); A* with an admissible lower bound
(a move changes the sum |dx|+|dy|+|dz| by at most 3, so ceil(distance/3) is a lower bound); noting that n³ = 10⁹ cells makes a full
visited array too big, so explore only near the path; symmetry (reflect so the target is in one octant). Any one with a reason is good.
:::

## Part 3: a staff-scope leadership story (day 2, about 8 minutes)

*Partly from the reading (the five competencies are from the Meta guide); STAR and the staff recap are beyond it.*

::: callout
**Recap from the staff placement.** Dropbox's career framework writes the senior-to-staff step as three changes: **scope** (one team →
several teams), **time** (one project's roadmap → a multi-year strategy) and **mode** (delivering → setting the direction and then
delivering it). A behavioral round at staff level listens for exactly those three things in your stories.
:::

Behavioral interviewers expect stories in **STAR** form: the **S**ituation, the **T**ask (what was yours to do), the **A**ctions *you*
took, and the **R**esult, ideally with a number. At staff level, the actions part is where the level shows: whom you had to persuade,
across how many teams, and what you decided when people disagreed. Meta's behavioral round grades five things: resolving conflicts,
driving results, embracing ambiguity, growing continuously and communicating effectively [2].

Spoken, a good story runs about three minutes. Written, that's roughly 300–400 words.

::: free iv-story
Answer this prompt as you would out loud, in STAR form, in about 3 minutes (time yourself; write it, or say it out loud and then
write the outline): **"Tell me about a time you drove a technical decision that other teams had to agree to, without having authority
over them."** Use your strongest real story. If your best one is inside one team, use it anyway and say so.
--- rubric
Baseline, ungraded. Rate each part Strong / Partial / Missing: Situation short (under ~20% of the story); Task says what was the
learner's own; Actions in the first person ("I", not "we"), including how a disagreement was handled; Result measured (a number or a
concrete change); scope: how many teams were involved (staff signal = more than one, plus a direction others followed). Note the
length. Feeds whether IV100 practices behavioral early.
:::

## Part 4: a project deep-dive outline (about 6 minutes)

*From the reading: both guides describe this round.*

Meta's project retrospective and Google's Role-Related Knowledge round both ask you to walk through real work in depth: the technical
decisions, what you owned, the impact, and what you'd do differently [1][2]. Interviewers probe hard on what *you* decided, so pick a
project where the design decisions were yours: a day-job project you led first, or a part of the 3D chess platform where you made
the calls.

::: free iv-deepdive
Outline a 15-minute deep dive in five bullets: (1) the problem and why it mattered, (2) what you owned, (3) the architecture in two or
three sentences, (4) one hard decision, with the options you rejected and why, (5) the result and what you'd change now.
--- rubric
Baseline, ungraded. Strong: bullet 4 names at least two real alternatives and a reason tied to a constraint (cost, latency, team
time); bullet 5 has a measured outcome and an honest "what I'd change"; bullet 2 separates the learner's work from the team's.
Partial: decisions without alternatives, or no result. Feeds the project deep-dive round type in IV100.
:::

## Part 5: rate yourself (about 3 minutes)

*Beyond the reading.* Two of the round types below aren't in these two guides' main lists. **ML system design** is a design round
about an ML product (the data, the model, training, serving and monitoring); it appears in staff loops for ML roles. **Project deep
dive** is the retrospective or role-related round from Part 4.

::: free iv-selfrate
Rate yourself 1–4 on each round type (1 = would fail it today, 4 = would pass it at staff level today): coding, system design,
behavioral, ML system design, AI-assisted coding, project deep dive. Then name the one you most want to practice first.
--- rubric
Baseline. Record the six ratings and the pick. Compare with the evidence on this page (coding time and pass, story parts, deep-dive
alternatives) and with the staff placement's design sketch (missed ordering, the server-owned timer and cross-server routing, so
system design is likely 1–2). IV100 practices the weakest type twice as often; where self-rating and evidence disagree, say which
one wins and why.
:::

## The rep (required before the next interview lesson)

**Write the Part 3 story in your brag document in STAR form.** A brag document is a running list of what you did and what changed
because of it, kept for reviews and interviews. Keep it wherever you keep notes; it doesn't have to be shared.

Definition of done: the story is in the document, with a number in the Result if one exists. Paste it below (or a link). If the
story is from your day job, change any confidential names first. You do all of this one; there's no code part.

::: free rep-iv-story
Paste the story from your brag document (or a link to it).
--- rubric
Done = a STAR story with Result stated. Give one concrete edit that would make it read more like staff scope (usually: more on the
disagreement and how it was settled, or a number in the Result).
:::

## Extra practice (optional)
None of this is needed for later lessons.

1. **Two follow-ups to the coding problem**, easiest first. (a) Some cells are blocked (a set of coordinates the knight may not land
   on); change your solution. (b) Write the bidirectional version: search from both ends and stop when the frontiers meet. Paste
   either in chat if you want a review.
2. **Extra reading:** *Practical Vim*, tip 53 ("Delete Around, or Change Inside"), which pairs `d` with the "around" objects and `c`
   with the "inside" ones (in your library).
3. **Extra article:** Steve Yegge, "Get That Job at Google" (2008): <https://steve-yegge.blogspot.com/2008/03/get-that-job-at-google.html>.
   Old, opinionated and long, and much of it still holds: what interviewers at a big company look for, why good people get rejected
   anyway, and the core algorithms he says to know cold (graph search among them).

## Sources
- Hello Interview, *Google L6 (Staff) Software Engineer Interview Guide* (2026): <https://www.hellointerview.com/guides/google/l6>
- Hello Interview, *Meta E6 (Staff) Software Engineer Interview Guide* (2026): <https://www.hellointerview.com/guides/meta/e6>
- Dropbox Engineering Career Framework, IC4 and IC5 pages: <https://dropbox.github.io/dbx-career-framework/>
- Drew Neil, *Practical Vim*, 2nd ed. (2015), tips 52–53, pp. 126–129 (in your library, id 59a28fc891).
- Steve Yegge, "Get That Job at Google" (2008): <https://steve-yegge.blogspot.com/2008/03/get-that-job-at-google.html>
