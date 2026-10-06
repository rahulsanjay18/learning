# The learning platform: fully realized system (as planned 2026-10-06)

Solid boxes exist today. **Dashed boxes are planned** (`notes/slm-offload-plan.md`). Rule throughout: every task goes to the
cheapest component that has passed that task's quality bar; anything uncertain escalates to the big model.

## 1. Architecture

```mermaid
flowchart TB
  subgraph YOU["You (browser / phone)"]
    L["Lesson pages<br/>quizzes, reading boxes, free responses"]
    R["Daily review deck<br/>(review.html)"]
  end

  subgraph GH["GitHub"]
    REPO["Repo (main)<br/>lessons · SYLLABUS.md · curriculum.json<br/>TEACHING-LOG · QUESTIONS · HANDOFF"]
    PAGES["GitHub Pages<br/>serves lessons + shared assets"]
    REPO --> PAGES
  end

  subgraph SRV["Your server (Tailscale) · 32 GB RAM · RTX 5070 Ti 16 GB"]
    OTHER["Your other services<br/>(always have priority)"]
    PS["Progress server<br/>events · scores · review schedule · grades"]
    BS["Book server<br/>today: keyword search (FTS5 / BM25)"]
    HY["Hybrid retrieval<br/>keywords + embeddings, fused (RRF)<br/>section chunks · book outlines · reranker"]
    W["LLM worker<br/>job queue · night window<br/>checks free VRAM first"]
    OL["Ollama<br/>small LLM (8–14B, 4-bit) on GPU<br/>embedding model on CPU/GPU<br/>unloads after each job"]
    BS -.-> HY
    W -.-> OL
    HY -.-> OL
    OTHER ~~~ OL
  end

  subgraph CC["Claude Code cloud session (the big model; swappable)"]
    SK["Skills<br/>/program · /teach · /quiz-me<br/>/game-review · /new-books"]
    SC["Scripts<br/>status · render_lesson · grade<br/>books · lp_results · check_all"]
    RT["Routines (scheduled sessions)<br/>weekly lesson batch"]
    SK --> SC
    RT -.-> SK
  end

  PAGES --> L
  PAGES --> R
  L -- "answers, ratings, notes (sync)" --> PS
  R -- "review answers" --> PS
  PS -- "what's due" --> R

  SC -- "status digest, grades" --> PS
  SC -- "search / read passages" --> BS
  SK -- "commit + push lessons, syllabi" --> REPO

  W -. "pull ungraded answers<br/>post confident grades" .-> PS
  W -. "uncertain → 'needs Claude' list" .-> PS

  classDef planned stroke-dasharray: 6 4
  class HY,W,OL,RT planned
```

## 2. Who does what (the cascade)

```mermaid
flowchart LR
  T["A task"] --> Q1{"Deterministic?<br/>(scheduling, rendering,<br/>status, lint)"}
  Q1 -- yes --> S["Script / service<br/>cost ≈ 0"]
  Q1 -- no --> Q2{"Has a small model passed<br/>this task's test set?"}
  Q2 -- yes --> M["Small local model<br/>(overnight)"]
  Q2 -- "no, or needs judgment<br/>(syllabi, lessons, research,<br/>fact-checking, claims)" --> C["Big model (Claude)"]
  M --> G{"Confident, and<br/>two runs agree?"}
  G -- yes --> OUT["Result stored"]
  G -- no --> C
  C --> OUT
  OUT -. "random 10% audit<br/>(first month after adopting)" .-> C

  classDef planned stroke-dasharray: 6 4
  class M,G planned
```

## 3. A day in the loop

```mermaid
sequenceDiagram
  autonumber
  participant You
  participant Pages as Lesson pages
  participant PS as Progress server
  participant W as LLM worker (planned)
  participant C as Claude session
  participant BS as Book server
  You->>Pages: review deck, then today's lessons (reading first)
  Pages->>PS: answers sync automatically
  Note over W,PS: night window, only if the GPU is free
  W->>PS: fetch ungraded free responses
  W->>W: grade twice by objective (Got it / Not yet)
  W->>PS: confident grades (grader = slm)
  W->>PS: uncertain items → "needs Claude"
  You->>C: /program
  C->>PS: status digest (what's done, due, escalated)
  C->>C: grade escalated items · mastery rule (Not yet → 5-min re-teach)
  C->>BS: retrieve exact passages for the next syllabus lessons
  C->>C: write lessons (Markdown → render → checks)
  C->>Pages: push to main → live
  C-->>You: today's plan: review, block 1, block 2
```

## Quality gates (from the plan)
| Task | Test set | Bar to adopt |
|---|---|---|
| Book search | questions whose passages Claude already found | right passage in top 3, ≥ 90% |
| Grading | answers Claude already graded | ≥ 90% agreement on Got it / Not yet, per subject |
| Question drafts | — | lint + Claude spot-check before publishing |
