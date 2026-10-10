---
title: Staff placement: where you stand against a real rubric
subtitle: Placement (about 45 minutes; fine to split at the timed exercise). One win: you know which staff courses you can shrink, and you have a first sketch of a real design.
crumb: Engineering career · Lesson 1 · SE000 placement
main: data-pretest=true
index: Staff placement (reading: Larson's archetypes; Dropbox IC4 vs IC5)
---
## Why this lesson
You lead cross-team projects, mentor and set direction, but you haven't written design docs yet. Before teaching anything, I need
to know where you already work at staff level and where you don't, so the Staff lane skips what you have. This is a pretest:
"I don't know" and "no evidence yet" are useful answers, not failures.

## Warm-up: Vim (2 minutes)

::: callout
**Practical Vim, tips 1–2: the dot command.** In Vim, turn the start text into the target text with as few keystrokes as you can.
Paste your keystrokes below exactly as typed (write Escape as `<Esc>`). Easiest: record them with `vim -W keys.log drill.txt` and paste the output of `cat -v keys.log` ([how](../reference/vim-drills.md)). I replay them in real Vim and count them; par is 7.

Start:
```
x = 1
y = 2
z = 3
```
Target (a semicolon at the end of every line):
```
x = 1;
y = 2;
z = 3;
```
:::

::: free vim-v01
Your keystrokes (cursor starts on the `x`, Normal mode):
--- rubric
Checked by replaying: python3 scripts/vimcheck.py --drill topics/eng/vim-drills.json v01-dot "<keys>". PASS = the buffer equals
the target. Par 7. The point of the tip: make one change repeatable (A;<Esc>), then repeat it with j and the dot command.
:::

## Block 1: what "staff" means (read first, ~8 minutes)

::: reading
### Reading
1. **Will Larson, "Staff archetypes"** (staffeng.com, free): the four ways staff roles show up. Read it all; it's short.
   <https://staffeng.com/guides/staff-archetypes/>
2. **Dropbox's public engineering career framework:** skim the **IC4 (senior)** page, then the **IC5 (staff)** page. Compare the
   one-line summary at the top of each, then the *Results* and *Direction* lists.
   <https://dropbox.github.io/dbx-career-framework/ic4_software_engineer.html> ·
   <https://dropbox.github.io/dbx-career-framework/ic5_staff_software_engineer.html>

While reading, look for the one or two words that change between IC4 and IC5 in each line you compare.
:::

Start from a real definition. Dropbox writes each level as one sentence in the engineer's voice [2]:

| Level | Their own summary |
|---|---|
| IC4, senior | "I autonomously deliver ongoing business impact across a team, product capability, or technical system" |
| IC5, staff | "I set the multi-year, multi-team technical strategy and deliver it through direct implementation or broad technical leadership" |

Three things change, and everything else on the IC5 page follows from them: **scope** (one team or system → many teams), **time**
(a roadmap for projects → multi-year strategy), and **mode** (deliver → *set* the direction and then deliver it). Notice what does
*not* change: Dropbox says code fluency expectations "do not go beyond L4" at staff [2]. The jump is direction and influence.

::: choice placement-shift
Dropbox's IC4 Direction list includes "I define the technical roadmap for impactful multi-phase projects". What is the closest IC5
counterpart?
- [ ] I define the technical roadmap for impactful projects across several teams and orgs
- [x] I define a long-term strategy for my team that factors in company-wide priorities
- [ ] I define the delivery schedule for impactful multi-phase projects across my whole team
- [ ] I define the technical roadmap for my most impactful multi-phase projects each year
--- explain
IC5's Direction list: "I define a long-term strategy for my team that factors in company-wide priorities, customer needs as well as
the technical limitations and possibilities of Dropbox's software and systems" [2]. The change is roadmap → long-term strategy, and
my team → company-wide priorities: the time and scope shifts from the summaries.
:::

Larson found four shapes the job takes [1]:
- **Tech Lead:** "guides the approach and execution of a particular team."
- **Architect:** "responsible for the direction, quality, and approach within a critical area."
- **Solver:** "digs deep into arbitrarily complex problems and finds an appropriate path forward."
- **Right Hand:** "extends an executive's attention, borrowing their scope and authority to operate particularly complex organizations."

He also notes that the Tech Lead is, "for many folks, their first experience as a Staff engineer" [1].

::: categorize placement-arch
Which archetype is each person working as?
- Owns the long-term direction of the company's storage layer across five teams > Architect
- Is sent from one stuck, messy migration to the next by the VP > Solver
- Guides how one team builds its product and partners with that team's manager > Tech Lead
- Runs a director's cross-org initiatives with the director's authority > Right Hand
--- explain
Each line matches one of Larson's definitions: a critical *area* (Architect), arbitrary hard *problems* (Solver), one *team*
(Tech Lead), an *executive's* scope (Right Hand) [1].
:::

## Block 2: your evidence (~12 minutes)

For each pillar, pick the one IC5 line where you have the **strongest** evidence, and write the evidence: what you did, how many
teams it touched, and what changed because of it. If you have none for a pillar, write "none yet". That's the most useful answer,
because it tells me which course to keep long.

::: free placement-results
**Results.** IC5 example: "I identify and execute on opportunities that have area/group-wide impact" [2]. Your strongest evidence?
--- rubric
Placement, not graded for credit. Record: concrete (a named project), scope (number of teams), outcome (what changed, ideally a
number). Classify as Strong (multi-team, outcome stated) / Partial (team-level or no outcome) / None. Feeds which SE courses shrink.
:::

::: free placement-direction
**Direction.** IC5 example: "I define a long-term strategy for my team that factors in company-wide priorities, customer needs as
well as the technical limitations and possibilities" of the systems [2]. Your strongest evidence? Is any of it *written down*?
--- rubric
Placement. Strong = a strategy or direction that others followed, beyond one project, ideally written. Partial = verbal direction
or one project's roadmap. Note whether it was written: no written artifact → keep SE110 (writing) at full length.
:::

::: free placement-talent
**Talent.** IC5 example: "I invest time to coach and mentor my teammates (particularly ones looking to grow into L4/L5)" [2]. Your
strongest evidence?
--- rubric
Placement. The learner said at setup that they mentor. Strong = named mentees who grew (promotion, new scope). Partial = mentoring
without a visible outcome.
:::

::: free placement-culture
**Culture.** IC5 example: "I build deep cross-functional relationships, facilitate the right conversations, and settle
disagreements by managing different viewpoints" [2]. Your strongest evidence?
--- rubric
Placement. Strong = a concrete disagreement across teams that the learner settled, and how. Partial = coordination without a
contested decision.
:::

::: free placement-archetype
Which of Larson's four archetypes is closest to what you do now, and which do you want? One sentence each.
--- rubric
Placement, no right answer. Record both; the target archetype decides emphasis (Architect → SE120/SE130 depth; Tech Lead → SE140
execution; Solver → system design depth; Right Hand → SE150 strategy).
:::

## Block 3: a timed design exercise (15 minutes, on a real ticket)

Set a timer for **15 minutes** and stop when it rings: the point is to see what you reach for first, not to finish. This is your
own backlog ticket, **3dChessServer #13, "WebSocket move relay for real-time official games"** (checked on GitHub today) [3]:

> Real-time bidirectional move forwarding between two players in an official game. Every move is validated server-side before
> being forwarded.
> - `WS /games/{id}/ws` accepts connections from both players
> - Incoming move payload validated by server engine (SRV-5) before forwarding
> - Illegal move: connection receives `{type: "illegal", move: ...}`; opponent not notified
> - Reconnection within 60s resumes the game; after 60s the disconnecting player forfeits

::: free placement-design
In 15 minutes, sketch the design as bullet points: who holds the game state, how moves are ordered, what happens on a reconnect
and at the 60-second mark, and what breaks when there are many servers. End with the **two questions you'd want answered before
building it**.
--- rubric
Placement at staff depth. Look for: (1) one authority for game state (server-side, single writer per game) and where it lives;
(2) ordering: a move number or sequence id so duplicates and stale moves are rejected (idempotency on reconnect/resend);
(3) validate-then-forward, illegal reply to sender only (from the ticket); (4) reconnect: identify the player (auth), resume from
the last acknowledged move, the 60 s timer is owned by the server, not the client, and forfeit is written durably; (5) many
servers: both sockets of one game may land on different servers → route by game id (sticky) or relay through a pub/sub; (6) failure
modes named (server crash mid-game, both players disconnect, clock skew). Staff signal: states trade-offs and open questions rather
than one answer. Strong = 4+ of these with a trade-off; Partial = 2–3; it's fine to miss most: SE120 teaches them.
:::

## The rep (required before the next Staff lesson)

**Rep 0: make Vim the easy path.** Definition of done: paste the output of these two commands.
1. `git config --global core.editor vim`, then `export EDITOR=vim VISUAL=vim` in your shell rc (and VSCodeVim or IdeaVim in any IDE you use).
2. Run `vimtutor` once (about 30 minutes; it can be another day).

::: free rep0-done
Paste the output of `git config --global core.editor; echo $EDITOR $VISUAL`, and say whether you finished `vimtutor`.
--- rubric
Done = output shows vim for all three, and vimtutor finished. Partial (config set, vimtutor pending) unblocks the lane but stays
on the open-reps list.
:::

Your sketch from Block 3 isn't wasted: when the Staff lane reaches system design (SE120), ticket #13 becomes a full design doc, and
this sketch is its first draft. Questions about anything here: ask me in chat.

## Sources
- Will Larson, "Staff archetypes", staffeng.com: <https://staffeng.com/guides/staff-archetypes/>
- Dropbox Engineering Career Framework, IC4 Software Engineer and IC5 Staff Software Engineer: <https://dropbox.github.io/dbx-career-framework/>
- rahulsanjay18/3dChessServer issue #13, "WebSocket move relay for real-time official games": <https://github.com/rahulsanjay18/3dChessServer/issues/13>
- Drew Neil, *Practical Vim*, 2nd ed. (2015), tips 1–2 (in your library, id 59a28fc891).
