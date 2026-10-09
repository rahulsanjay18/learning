# Plan: an ensemble of services and models, with quality gates

*Proposed 2026-10-06. Not urgent: deploy when convenient. Goal: a learning platform I can use for years, where Claude (the
expensive model) only does the work that needs judgment.*

## The principle (revised 2026-10-06: quality first, cost second)
**Every task goes to the cheapest component that meets that task's measured quality bar; anything uncertain escalates.** This is
an "LLM cascade": research shows a tuned cascade can match the best single model at a fraction of the cost, or beat it at the same
cost [3]. Quality is never traded away: a component only gets a task after passing that task's test set.

**Model-agnostic:** every model sits behind one adapter (an OpenAI-style chat API with JSON-schema outputs). The "big model" is
Claude today but could be anything; the small ones are whatever runs well on the server. Swapping a model = re-run its test sets.

Layers, cheapest first:
1. **Scripts and services** do anything deterministic (scheduling, rendering, status, lint). Already true (CLAUDE.md rule).
2. **A small local model (SLM)** does easy, checkable language work, in the background, overnight.
3. **Claude** does design, research, fact-checking, and anything the SLM flags as unsure.

## Which jobs go where

| Job | Who | Why |
|---|---|---|
| Spaced review scheduling, progress, status | script / server | deterministic (already done) |
| **Semantic book search**: return the 20 relevant lines instead of me reading 200 | SLM (embedding model) | biggest token saver: book reading is a large share of each lesson's cost |
| **First-pass grading** of free responses → Got it / Not yet + 1–2 sentence feedback | SLM, with escalation | repetitive, rubric-driven; uncertain cases go to Claude |
| Drafting extra review/flashcard questions from a lesson | SLM draft → lint script → Claude spot-check | easy to generate, easy to check |
| Summarising my notes/answers into learning-record drafts | SLM draft → Claude edits | saves reading raw event logs |
| Designing majors, syllabi, lessons; judging historical claims; research; verifying facts | Claude | needs judgment and accuracy; an SLM's errors here would teach me wrong things |

## How it would work
- **Runtime:** Ollama on the server, serving models through its OpenAI-compatible API (`http://localhost:11434/v1`) with
  **structured outputs** (answers forced into a JSON schema, so scripts can parse them) [1][2].
- **A small "worker" service** next to the progress server: a SQLite job queue. Jobs: `grade`, `embed_book`, `search`,
  `draft_questions`. It runs overnight (cron) and writes results back to the progress server (e.g. grades with `grader: "slm"`).
- **Escalation:** the SLM returns a confidence field; it also grades each answer twice. If the two disagree or confidence is
  low, the item goes to a "needs Claude" list that `status.py` shows. Claude only sees those.
- **Book search:** embed every book once (chunked by section heading), then `books.py search` asks the worker for the top
  passages. The ungraded books (grade B/C) keep their library/README.md restrictions.

## Quality gates (mastery rule, applied to the models)
Each task type has a **test set**, a **bar**, and an **escalation trigger**:

| Task | Test set | Bar to adopt | Escalate when |
|---|---|---|---|
| Book search | questions whose answer passages Claude already found | right passage in top 3, ≥ 90% | no passage scores above threshold |
| Grading | answers Claude already graded (progress server) | ≥ 90% agreement on Got it / Not yet, per subject | two runs disagree, or low confidence |
| Question drafts | — | every draft passes lint + Claude spot-check | always reviewed before publishing |

Keep Claude re-checking a random 10% for the first month after adopting, and log every escalation: if one task escalates a lot,
the bar is wrong or the model is too small. Re-run the test sets whenever a model changes.

## Hardware (learner's server, 2026-10-06): 32 GB RAM, 1× RTX 5070 Ti (16 GB GDDR7 [4])
- **Enough for every stage.** Rough VRAM need ≈ parameters × bits ÷ 8, plus ~1–2 GB for context: an 8B model at 4-bit ≈ 5–6 GB,
  a 14B at 4-bit ≈ 9–10 GB; embedding models are well under 1 GB and can run on the CPU.
- **A second 5070 Ti: not now.** These jobs are small and run overnight in batches, so speed doesn't matter. A second card only
  pays off if the grading test set shows we need a ~30B model (32 GB across two cards). Decide from the test results, not before.
- **The other services come first:**
  - jobs run only in a night window, one at a time;
  - `keep_alive: 0` so a model unloads the moment a job finishes (Ollama's default keeps it 5 minutes) [5];
  - `OLLAMA_MAX_LOADED_MODELS=1` (default 3) [5];
  - the worker checks free VRAM (`nvidia-smi`) before each job and skips the night if another service is using the GPU;
  - embeddings on the CPU if the GPU is ever contended.
- Open question: which other services use the GPU, and when (e.g. media transcoding)? That sets the night window.

## What I (the learner) need to do
1. Install Ollama and the worker (Claude writes the worker code, tests and a compose snippet, like progress-server/).
2. Nothing else changes: same web pages, same review deck, same /program.

## Order (when the time comes)
1. Semantic book search (most tokens saved, lowest risk: a bad search result costs a re-search, not a wrong grade).
2. First-pass grading with escalation, after the agreement test.
3. Question drafting, then learning-record drafts.

## Update 2026-10-09: grading moves first; the test set is the bottleneck
The learner is building the grader first (grading felt like the biggest token cost), ahead of book search. Fine: the order
above was a guess, and the learner sees the bills.

**Problem: the agreement test has almost no data yet.** The progress server holds about 10 Claude-graded free responses
(IH 0002–0003, stats, eng 0001; from `/summary`). With that few, a 95% exact (Clopper-Pearson) lower bound on agreement is:

| graded items n | agreements | 95% lower bound |
|---|---|---|
| 10 | 9 | 0.56 |
| 10 | 10 | 0.69 |
| 30 | 28 | 0.78 |
| 50 | 47 | 0.84 |
| 100 | 94 | 0.87 |

(Computed by binary search on the binomial tail, 2026-10-09.) So "≥ 90% agreement" can't be shown until ~100 items. Until then:
1. **Shadow mode:** the grader writes its grade beside Claude's (e.g. `grader: "slm"`, not counted for review); each Claude
   grade becomes one more test item. Adopt per subject once the lower bound clears the bar you choose.
2. **Cut the queue, not just the cost:** reflection prompts with no rubric (e.g. IH 0002 `read-surprise`) need no grading at
   all; auto-credit them and keep them out of spaced review (the learner flagged this 2026-10-09).
3. Interface to match: read `GET /progress/ungraded`, build the packet like `scripts/grade.py`, write
   `POST /progress/grades` (`[{event, score 0..1, feedback}]`; 0.7+ counts as known). Add a `grader` field to the server.

## Sources
1. Ollama, "Structured outputs" (Dec 2024): https://registry.ollama.ai/blog/structured-outputs
2. UCSF, "Using Ollama through the OpenAI API": https://researchai.ucsf.edu/class/lma/openai_ollama_python
3. Chen, Zaharia & Zou, "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance" (2023):
   up to 98% cost reduction at the best single model's accuracy, or +4% accuracy at equal cost. https://arxiv.org/abs/2305.05176
4. RTX 5070 Ti specs (16 GB GDDR7, 256-bit, 896 GB/s): https://www.tomsguide.com/computing/nvidia-reveals-full-rtx-5070-ti-and-rtx-5070-specs-what-you-need-to-know
5. Ollama FAQ (keep_alive default 5 min, OLLAMA_MAX_LOADED_MODELS default 3): https://ollama.readthedocs.io/en/faq/
