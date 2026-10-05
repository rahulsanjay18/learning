# Turning this into a sellable, model-agnostic platform

*Written 2026-10-05. Fourth in the series. Not legal advice: talk to a lawyer before selling anything that touches third-party content.*

## TL;DR
- **Most of what we're building is already model-free:** widgets, renderer, progress/review backend, search. Only the "teacher brain" uses an LLM.
- **Keep the LLM part portable** by sticking to open formats. **Agent Skills** (the `SKILL.md` format) is an open standard that many model-agnostic agents support [1]. The backend should be a plain **HTTP API + an MCP server**, which any agent can call [2]. Open-weight models can be served behind an OpenAI-compatible API, e.g. with vLLM, which also supports tool calling [3].
- **Make the content layer "bring your own library":** a small adapter interface, with your book server as just one adapter.
- **Licensing is the real product risk:** MIT OCW is **non-commercial** [4]; YouTube can be embedded but not downloaded [5]. Your `/teach` skill is MIT-licensed, so commercial use is fine with attribution [6].
- **"Just as good" has to be measured.** Start an eval set now; your own lesson ratings are free labels.

---

## 1. Three layers, and what each depends on

| Layer | Examples | Depends on an LLM? | Portability plan |
|---|---|---|---|
| **Delivery** | widgets, lesson renderer, review pages | No | Already portable (static HTML/JS) |
| **Backend** | progress, scheduling, `/status`, search, uploads | No | HTTP API + MCP server [2]; multi-user auth |
| **Teacher brain** | curriculum design, writing lessons, grading free response | **Yes** | Agent Skills format [1] + backend tools; swap the model/harness |

**Rule that keeps us portable:** anything *essential* lives in a script or the API. `SKILL.md` only holds plain-English instructions. Claude Code–specific conveniences go in optional adapters, never in the core. Examples:
- `` !`command` `` context injection;
- `disable-model-invocation`;
- `context: fork` subagents;
- this cloud environment's credential-injecting proxy;
- Artifacts.

Agents listed as supporting Agent Skills include model-agnostic/open-source ones such as OpenCode, Goose, OpenHands and Hermes Agent, alongside Claude Code [1].

## 2. Generic content: "bring your own library"

Your book server becomes **one implementation** of a small interface:

```
search(query, k)        → passages {source_id, title, location, snippet, quality}
read(source_id, range)  → text slice (capped)
toc(source_id)          → headings
meta(source_id)         → title, license, quality grade, owner (private|shared)
```

Adapters a product could ship:
- **User's private files** (what you have now, generalized): upload/convert, auto-graded A/B/C/F. Your conversion-quality grading is itself a feature.
- **Open educational resources** whose licenses allow commercial reuse. Check each source's license; OpenStax books, for example, are mostly CC BY, with some exceptions.
- **Public domain** collections and **Wikipedia** (CC BY-SA: share-alike obligations apply).
- **Transcripts** of a user's own purchased courses, stored privately per user.

## 3. Licensing checklist (the part that can sink a product)

| Source | Personal use (now) | In a paid product |
|---|---|---|
| Your books / purchased courses | Fine (your copies) | **Never shipped**; at most, a user's own private uploads |
| MIT OCW | Fine: CC BY-NC-SA 4.0 [4] | **No commercial use** [4]. Link to it; don't bundle it. Get legal advice even for "derived" curricula |
| YouTube | Link/embed | Embed via YouTube's player only; downloading is forbidden without authorization [5] |
| Open Syllabus data | Free tools | Check their terms for commercial use |
| `/teach` skill | Fine | MIT license: commercial use OK, keep the copyright notice [6] |
| Syllabi you collect | Fine for study | Topic lists are mostly facts; don't redistribute the documents themselves |

**Repo hygiene:** eventually split into a **platform** repo (generic code) and this **personal** repo (your mission files, library manifest, progress).

## 4. Making "just as good" measurable

You'd want to swap models with evidence, not vibes. Build evals from day one:
- **Grading agreement:** free-response answers with known-good grades. Compare model grades to them.
- **Lesson quality:** a rubric covering accuracy, citations present, equal-length options, "single tangible win" (SKILL.md requirements). Use an LLM judge plus spot checks.
- **Learner outcomes:** your "too easy / just right / too hard" and "confused" clicks, plus quiz results. These are free labels from your own use.
- Run the same suite against Claude and any open-weight candidate. Per-learner cost (tokens or GPU time) is the other axis, which makes the token-saving work also *margin* work.

## 5. What changes in our near-term plan
Very little, if we decide now:
1. **Widgets:** neutral naming, no model coupling (already the plan).
2. **Server:** grow into a `platform-api` with **source adapters** and **per-user data**. The book server becomes one adapter. Expose it as REST + MCP.
3. **Skills:** keep the core in portable Agent Skills form, with Claude-only extras isolated.
4. **Evals:** log ratings/attempts in a form that doubles as an eval dataset.
5. **Multi-user basics later:** accounts, data isolation, privacy policy, and age rules if minors could sign up.

---

## Sources
1. Agent Skills: https://agentskills.io ("originally developed by Anthropic, released as an open standard"; client list incl. OpenCode, Goose, OpenHands, Hermes Agent, Claude Code).
2. Model Context Protocol: https://modelcontextprotocol.io (open protocol for connecting agents to tools/data).
3. vLLM online serving: https://docs.vllm.ai/en/latest/serving/online_serving/ ("HTTP server that is compatible with many interfaces"; tool calling via `parallel_tool_calls`).
4. MIT OCW terms: https://ocw.mit.edu/pages/privacy-and-terms-of-use/ (CC BY-NC-SA 4.0; "You may not use the material for commercial purposes").
5. YouTube Terms of Service: https://www.youtube.com/static?template=terms.
6. `.claude/skills/teach/LICENSE` (this repo): MIT License, © 2026 Matt Pocock.
