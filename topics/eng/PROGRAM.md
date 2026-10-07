# Engineering career: one continuous major, practiced on 3D chess

*Set 2026-10-07. Replaces the separate C/C++, Staff, Career and AWS ML plans (originals in `reference/`; their reasoning and
sources still apply). Full weight: it takes the AWS ML major's 4 blocks a week (Mon, Wed, Thu, Fri).*

## The idea: explore vs. exploit (your framing, 2026-10-07)
Think of this major as a bandit problem:
- **Exploit (3 of 4 weekly blocks: staff, tech, interview).** Spend most of the time on what's *known* to pay: senior → staff, interviews at
  the big-tech staff bar, AWS, CUDA/inference, Spark. Apply it to projects you already care about (3D chess), so the skills get used
  for real. Shipping the game could also become **side income**: its backlog already has monetization work (skins, subscriptions,
  ads, a Steam release).
- **A second practice project: this learning platform** (your idea, 2026-10-07). **3D chess stays the main project**; the platform is an extra option when a lesson fits it better. It's a real staff-scope system: two servers, a
  library pipeline, and several AI sessions working on one repo, which is a coordination problem. It has already produced a real
  incident (two sessions both wrote lesson 1). Its backlog items (postmortem, a coordination design doc, a design review of the
  small-model offload plan, a platform strategy, SLOs) are in `backlog.json` alongside the 3D chess tickets.
- **Where a skill gets practiced** (your point: not every profitable skill fits 3D chess). Each rep picks the best venue: a 3D chess
  ticket first, then a learning-platform item, then a **standalone lab** built for that skill (an AWS sandbox exercise, Spark on a
  public dataset, a timed LeetCode set, an open-source issue,), then your day job (sanitized). The lesson says which venue and why.
- **Explore (1 of 4 blocks: interest).** Topics you find interesting that *might* pay off but don't have to. That makes ε = 1/4.
- **Update the estimates.** When an explored topic shows pay or demand evidence (in `catalog.json`), or you want to go deep, it's
  **promoted** into the tech lane. A tech topic whose evidence fades drops back to explore. These moves are reviewed at each catalog
  refresh and logged in `CHANGES.md`.

## TL;DR
- **Four lanes, one per weekly block** (revised 2026-10-07): **Mon staff · Wed tech · Thu interview · Fri interest.** The Today page shows
  only that day's lane.
  - **Staff (SE):** placement → what staff is → writing design docs → system/ML design → software design → execution → strategy → getting the title.
  - **Tech:** AWS first (AW: placement → foundations → ML on AWS → MLA-C02 exam), then CUDA (CP320), Spark (CR170), C/C++ (CP), security (CR330) and so on.
  - **Interview (IV):** interview skills at the **big-tech staff bar** (your words: big tech isn't the goal, but it has the highest bar).
    A baseline, then continuous mock rounds rotating through the loop's round types; the weakest type comes up twice as often.
  - **Interest (IN):** things you find interesting, for their own sake. Reps are optional here.
- **Every lesson ends with a required rep: a real ticket from your 3D chess backlog** (`backlog.json`, 36 mapped so far out of 119 open
  issues). The next lesson in that lane isn't written until the rep is **shipped** (a PR or doc link) or **skipped with a reason**.
  `/program` shows open reps and how old they are.
- **Who does what:** you do the staff-level part of the ticket: design doc, ADR, decision, prioritization, threat model, PR review and
  merge. I write the code as a PR for you to review. When the lesson's skill *is* the code (C, C++, CUDA, Spark), you write it and I review.
- **Vim, every lesson:** a 2-minute drill from *Practical Vim* (in your library). You paste your keystrokes, and I replay them in real Vim to check
  the result and count them (`scripts/vimcheck.py`). Your reps are edited in Vim too.
- **Never empty:** when a course ends, the next one in its lane starts at once.
- **Self-updating:** the cert/skill/pay catalog (`catalog.json`) re-checks itself (`scripts/catalog.py`), and each rep's ticket is
  re-checked on GitHub before it's assigned.

## 1. The lanes
| Lane | Order | Reps from the backlog (examples) |
|---|---|---|
| **Staff** | SE000 placement → SE101 → SE110 writing → SE120 system/ML design → SE130 software design → SE140 execution → SE150 strategy → SE160 evidence and leveling | MuZero-lite decision doc (RL #54); offline-mode ADR (Desktop #15); design docs for the WebSocket move relay, matchmaking and the MCTS job queue (Server #13, #9, #15); the broken-main incident write-up and dependency policy (Web #71); re-prioritize the RL tracker (RL #69); a one-page platform strategy (Web #50) |
| **Tech: AWS** | AW000 placement + exam date → AW101 foundations through the RL training fleet → AW201 ML on AWS (MLA-C02 domains, each contrasted with SageMaker) → AW290 exam | Terraform state, import, spot template, OIDC plan gate (RL #141–#144); Tailscale bridge (#110); first distributed PPO run (#101); MLflow + inference on AWS (#124); Prometheus on AWS (#151) |
| **Tech: CUDA / inference** | CP101 → CP320 CUDA → CR140 inference | batched GPU leaf eval for MCTS, **you write it** (RL #47); torch.compile + AMP profile (#46); inference service and endpoint (RL #123, Server #14); wire format (RL #129) |
| **Tech: Spark** | CR170 | self-play analytics in PySpark, **you write it** (proposed ticket; I'll ask before filing it) |
| **Tech: C/C++** | CP101 → CP120 → CP201 → CP202 → CP203 → CP204 | adopt `count_legal_moves` at the C API boundary (RL #44); engine hot-path profile with one measured speedup (proposed, 3dChessInC) |
| **Tech: MLOps / eval** | CR100, CR110, CR380 | Airflow pipeline design (RL #140); observability SLOs (#118); Glicko-2 audit and tournament power analysis (#65, #66: uses your Statistics major) |
| **Tech: security** | CR330 | auth token transport and ad-SDK isolation threat models (Web #34, #39); Electron security review (Desktop #7) |
| **Safety net** | CR325 actuary, CR327 patent agent | not in rotation; there if needed |

The ordering after AWS is a default. Say the word and a different tech course goes next.

### 1a. The interview bar
A big-tech staff loop, as 2026 prep guides describe it (exact rounds vary by company, team and recruiter):
- **Google L6:** a hiring assessment and phone screens, then about 5–6 interviews: coding, **two system design rounds**, role-related
  knowledge, and a leadership/"Googliness" round. A hiring committee decides, then team matching [1].
- **Meta E6:** 1–2 coding rounds (now one is **AI-assisted**), **two design rounds** (infrastructure or product architecture track),
  a behavioral round focused on scope and influence, and sometimes a project retrospective [2][3]. One guide says failing either
  design round is usually disqualifying at staff level (a single-source claim).
- **Staff ML loops** add ML system design and ML fundamentals/coding, plus a deep dive on past ML projects [4].

**Own projects first, standard prompts too.** Interview practice uses prompts from your projects (relay, matchmaking, RL training
platform, the learning platform) because you care about them. But real loops ask the standard ones ("design a URL shortener / news
feed / rate limiter"), so roughly one mock in three uses a standard prompt, and the last weeks before a real loop use mostly
standard ones (my judgment: practice should end up looking like the test).

So IV100 rotates through six round types: **coding (timed, in Vim) · system design · behavioral/leadership · ML system design ·
AI-assisted coding · project deep dive.** The 3D chess platform supplies design prompts and a project to deep-dive (the RL training
platform is a good staff-scope story).

### 1b. Things I find interesting (1 active + 2 queued)
You have lots of interests; the point of this lane is real progress on a few. So it holds **one active topic and two queued**.
Everything else goes to the parking lot in `notes/ideas.md`, and comes in only one-in-one-out.
1. **Active:** how chess engines search (alpha-beta, transposition tables, NNUE) and what changes on an 8×8×8 board.
2. Queued: AlphaZero and MuZero, read as papers (feeds the MuZero-lite decision, RL #54).
3. Queued: branching factor and game length of your variant, measured with your engine (feeds the Games major).

Parked for now (in `notes/ideas.md`): the mini-PC HPC cluster, astrophotography on it, WebAssembly, the research service, and 3D
chess as a side income. The cluster is the strongest candidate for the next swap, because it feeds 3D chess self-play.

## 2. One lesson (one ~25-minute block; placements and mock rounds run longer, ~45 min)
1. **Vim drill (2 min):** one *Practical Vim* tip, as a start text and a target text. You send your keystrokes; `vimcheck.py` replays them.
2. **Reading (~10 min):** a slice of the course's primary book, with a reading guide.
3. **The idea (~8 min)**, tied to the ticket you're about to work.
4. **Practice:** a graded free response (a doc section, a design critique, a decision record).
5. **The rep (required):** one ticket, with a definition of done and who does what. It ships when there's a PR or doc link.

## 3. The force, honestly
I can't make you do anything. What I can do:
- **Block the lane.** No new lesson in that lane until the rep ships or you skip it with a reason (which gets logged).
- **Show it every day.** `/program` lists open reps and their age at the top of each session.
- **Check rather than trust.** Vim keystrokes are replayed; PRs and docs are links I can open; tickets are re-checked on GitHub.
- **Vim:** the first rep sets Vim as the only editor (see §4), so the easy path becomes Vim.

## 4. Rep 0 (setup, before lesson 1)
1. Vim everywhere:
   - `git config --global core.editor vim`
   - `export EDITOR=vim VISUAL=vim` in your shell rc
   - turn on Vim keybindings in any IDE you use (VSCodeVim for VS Code, IdeaVim for JetBrains)
2. Run `vimtutor` once (about 30 minutes).
3. Give this session push access to the 3D chess repos when we start a code rep. They're attached read-only now.

## 5. Books
The staff books are yours (add them to the book server so lessons can quote them). Also: *DDIA* 2nd ed., *Designing ML Systems*,
*PMPP* 4th ed., *Practical Vim*, *Modern C* and *C++ Primer* are all in your library. Buy *C++ Concurrency in Action* before CP204.
Full list: `library/WANTED.md`.

## Sources
1. Hello Interview, *Google L6 (Staff) Software Engineer Interview Guide*. https://www.hellointerview.com/guides/google/l6
2. Hello Interview, *Meta E6 Interview Guides & Questions (2026)*. https://www.hellointerview.com/guides/meta/e6
3. PracHub, *Meta E6 Software Engineer Interview Guide 2026*. https://prachub.com/resources/meta-e6-software-engineer-interview-guide-2026-coding-system-design-leadership-and-leveling
4. Interview Kickstart, *Senior Machine Learning Engineer Interview Process Guide (2026)*. https://interviewkickstart.com/blogs/articles/senior-machine-learning-engineer-interview-process
5. Larson, *Staff archetypes*. https://staffeng.com/guides/staff-archetypes/

## Files
`curriculum.json` (courses and lanes) · `backlog.json` (tickets → courses, rep state) · `catalog.json` + `CHANGES.md` (self-updating
cert/skill/pay evidence) · `vim-drills.json` · `reference/` (the original C/C++, Staff and Career plans with their sources).
