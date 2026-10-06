# Plan: offload easy work to a small language model on my server

*Proposed 2026-10-06. Not urgent: deploy when convenient. Goal: a learning platform I can use for years, where Claude (the
expensive model) only does the work that needs judgment.*

## The principle
Three layers, cheapest first:
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

## Trust it only after it's measured (mastery rule, applied to the grader)
1. Build a test set from answers Claude already graded (the grades posted on the progress server).
2. Run the SLM on them; measure agreement on Got it / Not yet.
3. **Adopt for a subject only at ≥ 90% agreement**, and keep Claude re-grading a random 10% for the first month.
   Re-measure whenever the model changes. Statistics and history may land differently; that's fine.

## What I (the learner) need to decide or do
1. **Server hardware:** GPU (model, VRAM)? RAM? This decides the model size (a ~3–8B-parameter model on a modest GPU or a
   recent CPU; embeddings run fine on CPU). Pick specific models when deploying, after checking current benchmarks.
2. Install Ollama and the worker (Claude writes the worker code, tests and a compose snippet, like progress-server/).
3. Nothing else changes: same web pages, same review deck, same /program.

## Order (when the time comes)
1. Semantic book search (most tokens saved, lowest risk: a bad search result costs a re-search, not a wrong grade).
2. First-pass grading with escalation, after the agreement test.
3. Question drafting, then learning-record drafts.

## Sources
1. Ollama, "Structured outputs" (Dec 2024): https://registry.ollama.ai/blog/structured-outputs
2. UCSF, "Using Ollama through the OpenAI API": https://researchai.ucsf.edu/class/lma/openai_ollama_python
