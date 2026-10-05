# Program layer: skills, tokens, server, and tools

*Written 2026-10-05. Follow-up to `teaching-a-full-major.md`. Answers five questions.*

## TL;DR

1. **Skills:** a skill is a folder holding a Markdown file of instructions plus optional scripts. You decide *what it should do*; I write it; we test it together. Your `/teach` skill is already one.
2. **Tokens:** the subagents are Claude, not local models. The biggest savings come from **code doing the mechanical work** (rendering pages, scheduling reviews, scoring quizzes), not from small LLMs. I'd skip local chat LLMs for now.
3. **Non-math majors:** the design doesn't depend on subject. What changes is the *activity types* (essays, source analysis, flashcards…), and free-response grading becomes the main thing I'm needed for.
4. **Your server:** yes, and more than progress. It can be the **backend for the whole program**: progress, review scheduling, search over your history, nightly jobs (see §6). Keep the book server itself read-only and add services next to it.
5. **RAG / tools:** you already have keyword RAG (SQLite FTS5). The bigger win is a **shared component library + a lesson renderer + a code-driven review page**, so I write *content* and scripts write the *HTML*.

---

## 1. How a skill works (walkthrough)

A skill is just a folder: `.claude/skills/<name>/SKILL.md`, plus optional supporting files and scripts [1]. Typing `/<name>` loads that Markdown into my context as instructions [1].

Your `/teach` skill is exactly this: `.claude/skills/teach/SKILL.md` with frontmatter on top [2]:

```yaml
---
name: teach
description: Teach the user a new skill or concept, within this workspace.
disable-model-invocation: true      # only YOU can trigger it, by typing /teach
argument-hint: "What would you like to learn about?"
---
(plain-English instructions follow)
```

Three features matter for saving tokens [1]:

| Feature | What it does | Why it matters here |
|---|---|---|
| Bundled scripts (`${CLAUDE_SKILL_DIR}/scripts/x.py`) | I *run* the script; its source never enters my context | `next.py`, the renderer, the scheduler cost almost nothing to use |
| `` !`command` `` in SKILL.md | Runs a command *before* the skill loads and pastes in its output | `` !`python3 next.py` `` → I start every session already knowing "where you are" without reading files |
| `model:` / `context: fork` | Run the skill on a cheaper model, or in an isolated subagent | Mechanical skills can run on a smaller Claude model |

**What a first `/program` skill could look like** (sketch, not final):

```
.claude/skills/program/
  SKILL.md            # "Read the status block below. If a placement test is due, run it. Otherwise hand off to /teach for the next lesson."
  scripts/next.py     # reads programs/<major>/curriculum.yaml + progress server → prints ~10 lines
  scripts/render.py   # lesson spec → HTML
```

**How we'd build it together:**
1. You answer ~5 questions: what should `/program` do at session start, on a placement test, when finishing a course, and so on.
2. I draft `SKILL.md` + scripts and commit them.
3. You run `/program` in a new session. Whatever's wrong ("it re-read too much", "it skipped the review"), you tell me, and I edit the Markdown.

You never have to write YAML or Python yourself. A skill-creator skill is also available in this environment to help structure and test skills.

## 2. Saving tokens: subagents vs. local LLMs

**What the subagents are:** separate Claude instances, each with its **own context window**. They start with a fresh context, do the work, and send back a summary [3]. You can pin a cheaper model per subagent (`model:` in `.claude/agents/<name>.md`) [3].

**Important caveat:** subagents save *main-conversation context*, not necessarily *total tokens*. Each one starts cold and has to re-read what it needs. They're worth it only for **"read a lot, report a little"** jobs (searching books, checking 30 lessons for a concept). They're not worth it for small tasks.

**Where tokens actually go, and the fix for each:**

| Cost | Fix | Who does it |
|---|---|---|
| Re-generating HTML/CSS/JS each lesson | Shared assets + renderer (§5) | code |
| Reading many files to figure out "what's next" | `next.py` injected via `` !`…` `` | code |
| Daily spaced review | Review page built from a question bank | code: **zero model tokens** |
| Scoring multiple-choice / numeric answers | Deterministic check in the browser | code |
| Big book searches | FTS search on your server, top-k snippets only | server |
| Writing explanations, writing good questions, grading essays, spotting misconceptions | — | **me** (the "ambiguous NLP") |

**Local LLMs on your server:** I'd skip them for now. Nearly everything worth offloading is *deterministic* (rendering, scheduling, scoring), and plain code does that better and for free. The one place a small local *model* helps is **embeddings** for semantic search (§5). That's a small embedding model, not a chat LLM. Revisit a local chat model only if you later want something like auto-generated flashcards between sessions. Even then, quality would need checking.

## 3. Non-math majors

Nothing in the program layer is math-specific. What changes:

- **Activity types.** Besides MC/numeric quizzes: cloze (fill-in-the-blank), matching, ordering/timelines, primary-source analysis, short-answer and essay with a rubric, case studies, flashcards, and for languages listening/typing drills.
- **Grading.** More free-response means more of my judgment. Free-response answers go to the progress server, and I grade them in batches at the start of the next session against a rubric written at lesson time. That's cheaper than grading live.
- **Library.** Your collection is broad. `MANIFEST.csv` includes 620 *Very Short Introductions*, 289 Religious, 189 Foreign Languages and 117 Social Sciences entries [4]. The A/B/C/F grade rules still apply; the equation rules just come up less [5].

## 4. Using your server for progress

**What's there now** [6]: `book-server/app.py` is a FastAPI app over SQLite. It is **read-only by design** (opens the DB with `mode=ro`), uses a bearer token, and has `GET` endpoints for `/search`, `/read`, `/toc`, `/book`, `/books`. A test `POST` from this cloud session got `405 Method Not Allowed` back *from the app*. So the session's network proxy passes POSTs through, and a write endpoint would be reachable from here.

**Proposal: a separate `progress` service** (its own container + its own SQLite DB), so the book server stays read-only:

```
POST /attempts      {course, lesson, item_id, correct, answer_text?, ts}     ← lesson pages
GET  /summary?course=X    → ~20 lines: mastery per unit, weak items, ungraded free-responses  ← me
GET  /due                 → review items due today (spaced-repetition schedule)          ← review page + next.py
POST /grades        {attempt_id, score, feedback}                            ← me, after grading
```

The point of `/summary`: I read a **20-line digest**, never raw logs.

**One design problem to settle:** lessons are public GitHub Pages, so a page **can't contain a secret token**. Options:
- **(a) Recommended:** the progress service is reachable only on your tailnet. You enter a personal token once per device, it's stored in that browser's `localStorage`, and the page sends it with each POST. You also need CORS allowing `https://rahulsanjay18.github.io`.
- (b) Paste a score line at the start of each session. Works today, but it's manual.

I need one fact from you: **is `books.tail59e10.ts.net` reachable from the public internet (Tailscale Funnel / reverse proxy), or only on your tailnet?** That decides how your phone/laptop reaches the progress service.

## 5. RAG and learning tools

**RAG: you already have it, in keyword form.** `build_index.py` builds an FTS5 table (`tokenize='porter unicode61'`) and `/search` ranks passages by BM25 [6]. Two upgrades, in order of value:

1. **Search your own learning history** (lessons, learning records, glossary) with the same FTS approach. At degree scale, "have we covered X, and how did you do?" becomes a common question. A cheap search beats me reading folders.
2. **Hybrid semantic search over books** (later): add `sqlite-vec` + a small local embedding model and merge the results with BM25. It helps most in non-math subjects, where the same idea gets described with different words. Add it when keyword search starts missing things, not before.

**Tools to build (biggest token win first):**

| # | Tool | What it replaces | Evidence it's needed |
|---|---|---|---|
| 1 | **Shared component library** at repo root `assets/` (style, quiz, cloze, matching, ordering, flashcards, essay+rubric box, timeline) | Rewriting widgets per topic | Your 4 topics have **3 different `quiz.js` files and 4 different `style.css` files**; each was rebuilt from scratch [7] |
| 2 | **Lesson renderer** (`render.py`): I write a short Markdown/YAML lesson spec → script emits the HTML with the shared template, nav links, citations block, "ask me questions" footer | Me writing full HTML each time | The skill requires those parts in *every* lesson [2] |
| 3 | **Question bank + review page**: each course keeps `questions.yaml`; a script builds a daily review page from `/due` items | Model-generated review sessions | Spacing/retrieval are core skill goals [2] |
| 4 | **Progress service** (§4) | Manual score reporting | Feedback-loop requirement [2] |
| 5 | **`next.py` + generated `index.html`** | Me reading many folders; hand-editing the index | |
| 6 | **Lint script** (equal-length quiz options, broken links, missing citations) | Me re-checking by eye | Skill rule on equal-length answers [2] |

**Division of labor:** I decide *what* to teach and *write* the words, questions, rubrics and grades. Scripts handle *layout, scheduling, scoring and bookkeeping*.

## 6. Your server as the general backend (not just the library)

Today this session reaches only the library, but the server can host whatever we build. The rule of thumb for splitting the work:

| Lives in the **repo** (versioned, runs in my session) | Lives on the **server** (stateful, always on) |
|---|---|
| Lesson specs, rendered lessons (GitHub Pages serves them) | Progress DB: attempts, grades, mastery |
| `render.py`, shared `assets/`, lint script | Spaced-repetition scheduler + `/due` |
| `curriculum.yaml`, MISSION/NOTES, learning records | **Nightly jobs**: build tomorrow's review page, recompute mastery summaries, rebuild search indexes |
| Skills and subagent definitions | Search over books **and** your own lessons/records (FTS now, embeddings later) |
| | One `/status` endpoint returning the ~10-line "where you are" block |

What this buys:
- **`/program` boots off one HTTP call.** The skill injects `` !`curl …/status` `` [1], so a session starts with the digest already computed server-side. Zero file reading.
- **Daily reviews need no Claude session at all.** The server builds the review page from the question bank and your due items, and you just open it.
- **Overnight batch work is where a local model *could* earn its place**: e.g. a first-pass sort of free-response answers ("clearly right / clearly wrong / needs Claude"), so I only grade the ambiguous ones. It's optional and can come later; everything else above is plain code.

**Practical wiring detail:** this cloud environment's network proxy attaches your credential automatically for **`books.tail59e10.ts.net` only** (the environment's proxy config). If the new services sit on the **same hostname under path prefixes** (e.g. `/progress/…`, `/status`) behind your reverse proxy, my sessions can use them with no environment changes. A new hostname would need adding to the environment's network/credential settings. Recommendation: same host, path prefixes, and one auth scheme.

## Suggested build order
1. Shared assets + renderer (pays off immediately for your existing 4 topics)
2. Server backend v1: progress + `/status` + `/due`, same hostname under path prefixes (needs your answer about server reachability)
3. `/program` skill + `next.py` + curriculum for a chosen major
4. Question bank + review page
5. Hybrid search, only if needed

---

## Sources
1. Claude Code docs, *Skills*: https://code.claude.com/docs/en/skills (skill folder layout; frontmatter fields `disable-model-invocation`, `model`, `context: fork`; bundled scripts "executed, not loaded"; `` !`command` `` context injection).
2. `.claude/skills/teach/SKILL.md` (this repo). Frontmatter L1–6; spacing/retrieval L41–45; lesson requirements L55–61; feedback loop L108; equal-length answers L110.
3. Claude Code docs, *Subagents*: https://code.claude.com/docs/en/sub-agents (own context window; fresh start; `.claude/agents/` files with `model:` field).
4. `library/MANIFEST.csv` (this repo), category counts via `cut -d, -f4 | sort | uniq -c`.
5. `library/README.md` (this repo), grade rules and equation rule 4.
6. `book-server/app.py` and `book-server/build_index.py` (this repo); live check: `GET /books` → 200, `POST /books` → 405 from the app.
7. `topics/*/assets/` (this repo); `md5sum` of `quiz.js` and `style.css` across the 4 topics.
