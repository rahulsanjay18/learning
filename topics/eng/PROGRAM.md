# Engineering career: one continuous major, practiced on 3D chess

*Set 2026-10-07. Replaces the separate C/C++, Staff, Career and AWS ML plans (originals in `reference/`; their reasoning and
sources still apply). Full weight: it takes the AWS ML major's 4 blocks a week (Mon, Wed, Thu, Fri).*

## TL;DR
- **Two lanes are always active, and blocks alternate between them:**
  - **Staff lane (SE):** placement → what staff is → writing design docs → system/ML design → software design → execution → strategy → getting the title.
  - **Tech lane:** AWS first (AW: placement → foundations → ML on AWS → MLA-C02 exam), then CUDA (CP320), Spark (CR170), C/C++ (CP), security (CR330) and so on.
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

## 2. One lesson (one ~25-minute block)
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

## Files
`curriculum.json` (courses and lanes) · `backlog.json` (tickets → courses, rep state) · `catalog.json` + `CHANGES.md` (self-updating
cert/skill/pay evidence) · `vim-drills.json` · `reference/` (the original C/C++, Staff and Career plans with their sources).
