# Shared widgets + how you can help the platform

*Written 2026-10-05. Third in the series after `teaching-a-full-major.md` and `program-layer-build-plan.md`.*

## TL;DR
- **Widgets:** build one shared, dependency-free widget library at the repo root (`assets/`). It keeps the pattern your topics already use (write HTML with `data-` attributes, a script brings it to life) and adds a **core** that gives every answer a stable ID and reports it to your server. Subject-specific widgets (chess board, pixel canvas) become **plugins**. The same library serves "a CS degree" and "get better at chess".
- **How you can help:** give me *text I can read* (transcripts, PDFs, syllabi), *signals about you* (a one-tap difficulty rating per lesson, your chess games, photos of your drawings), and *server jobs* (transcription, indexing, storage).
- **Server is public** → every write endpoint needs a token. That's easy with a per-device token stored in your browser.

---

## Part A: the shared widget library

### What exists today (and why it's worth consolidating)
Your topics already use a good pattern. A lesson writes plain HTML like
`<div class="quiz" data-type="choice" data-answer="…" data-options="a|b|c">`, and a small dependency-free script brings every such element to life on page load [1]. But each topic has its own copy:

- `quiz.js`: chess and pixel-art are identical; military-strategy added a self-graded `recall` type ("Adapted from topics/chess"); nasm-cpt is a third variant [1].
- `style.css`: 4 different versions [1].
- `board.js` (chess FEN diagrams) and `pixels.js` (pixel drawing drills with an automatic checker) are already subject-specific plugins in all but name [1].

So: same idea, re-derived each time, slowly drifting apart. That's the token cost and the inconsistency you mentioned.

### Design: core + generic widgets + plugins

```
assets/                       (repo root, served by GitHub Pages)
  lp.css                      one stylesheet; per-topic accent color via a CSS variable
  lp-core.js                  finds widgets, score bar, item IDs, event bus, reporter
  widgets/                    generic: work for any subject
  plugins/chess.js            board + "find the move"
  plugins/pixels.js           moved from topics/pixel-art
  plugins/…                   added only when a topic needs one
```

Lessons stay self-contained HTML with **relative links** (`../../../assets/lp-core.js`), as your `CLAUDE.md` requires [2].

**`lp-core.js` (the part every widget shares):**
- **Stable item IDs:** `topic/lesson/item` (or an explicit `data-id`). Spaced repetition and progress tracking depend on this.
- **One event for every answer:** `{item_id, kind, correct, answer, ms, ts}` where `kind` = `auto` (graded by code), `self` (you mark yourself), or `deferred` (sent to me for grading).
- **Reporter:** sends events to your server with your device token. With no token or no network, it queues them in `localStorage` and sends them later. The page still works fully without the server.
- **Lesson footer:** a one-tap **too easy / just right / too hard** rating plus a **"this confused me"** button. It's the cheapest possible signal for picking what to teach next [3].
- **Plugin registry:** `LP.register("chess-move", initFn)`, so new widgets never touch the core.

**Generic widgets (subject-agnostic)**, each tied to what the /teach skill asks for:

| Widget | Grading | Good for | Skill basis |
|---|---|---|---|
| `choice` (MC) | auto | anything | retrieval practice [3] |
| `exact` (number/short text, tolerance or accepted forms) | auto | facts, numbers, vocab | retrieval [3] |
| `recall` (write from memory, reveal, mark yourself) | self | definitions, arguments, chess ideas | already in military-strategy [1] |
| `cloze` (fill blanks in a passage) | auto | languages, terminology, history | retrieval |
| `match` / `categorize` (drag into buckets) | auto | taxonomies, "which era/school/opening?" | interleaving [3] |
| `order` (put steps/events in sequence) | auto | processes, timelines, move orders | |
| `flashcards` (deck from the question bank) | self | review sessions | spacing [3] |
| `steps` / `checklist` (real-world tasks, timer optional) | self | yoga, drawing exercises, workouts, play-a-game tasks | "real-world steps" lessons [3] |
| `worked` (step-through worked example, predict each next step) | self | math, proofs, chess analysis, critiques | |
| `free` (short answer / essay + hidden rubric) | deferred → Claude | humanities, design, explanations | the "ambiguous NLP" stays with me |
| `video` (YouTube embed, start/end times, question checkpoints) | — | lecture series | primary-source recommendation [3] |

**Plugins (domain-specific), examples:**
- **Chess:** the current static board + an interactive **"find the move"** widget that checks legality and the answer, and **tactics review decks** (puzzles back on a spaced schedule). Could use `chess.js` from an allowed CDN instead of writing move rules ourselves.
- **Art:** pixel drills (exists), image **hotspot/label**, side-by-side **"compare to reference"**, and an **upload-your-attempt** button that goes to the server for my critique.
- **Later as needed:** code runner (Pyodide), math rendering (KaTeX), audio for languages/music.

**Built-in quality rules** (a lint script, not my eyes): equal-length answer options (skill rule [3]), every item has an ID, citations present, links valid. A **Playwright smoke test** opens every lesson in headless Chromium (already installed in these cloud sessions) to catch a widget change that breaks old lessons.

**Migration:** the old attribute names (`data-type="choice|number|recall"`) keep working, so the 5 existing lessons switch to the shared assets just by changing their `<script>`/`<link>` tags.

**Build vs. buy:** H5P [4] is the mature open-source option for interactive content (quizzes, drag-and-drop, interactive video). But it needs a host platform and a GUI-driven authoring flow. Your current approach (plain HTML I can write in a few lines, no build step, static hosting) is a better fit for me authoring lessons and for saving tokens. Recommendation: custom and lightweight, borrowing H5P's widget *ideas*.

### Same platform, chess vs. a degree
| | "Get better at chess" | "Psych major" (example) |
|---|---|---|
| Unit of work | a tactic/plan theme | a course unit |
| Main widgets | find-the-move, recall, steps ("play 3 rapid games, then…") | cloze, categorize, free-response |
| Review deck | missed puzzles | missed concepts |
| Real-world signal | your actual games (e.g. pulled from your Lichess/Chess.com account) | essays you write |
| "What's next" | weakest theme in your games + due reviews | next course in the prerequisite graph + due reviews |

The only difference is whether there's a **curriculum graph** on top. The widgets, progress and review machinery are the same.

---

## Part B: how you can help me teach well

### 1. Videos (YouTube, purchased courses)
- **I can't watch video; I can read text.** Transcripts are what make videos usable to me.
- **YouTube:** **link or embed** with timestamps (the `video` widget). Its Terms of Service forbid downloading unless the service authorizes it or you have written permission [5], so I'd avoid downloading.
- **MIT OCW** material is CC BY-NC-SA 4.0 [6]: copying and redistribution are allowed for non-commercial use. Personal study is fine.
- **Your purchased art courses:** check each course's license. It's typically fine for your own study. Keep them **private on your server**, never in this repo or on GitHub Pages (both public). A server job can **transcribe** them locally (e.g. a Whisper-class speech-to-text model) and add the transcripts to the same search index as your books. I'd then search lecture text the same way I search books.

### 2. Syllabi from many colleges (yes, this is a great idea)
- **Syllabus triangulation:** for each course, collect ~5–10 syllabi from different schools. I extract weekly topics and assigned readings. Topics that appear in most syllabi are the **core**; the rest are optional. That's better than any single school's list, MIT included.
- **Open Syllabus** has catalogued 32.9M syllabi and offers free tools (Analytics, Co-Assignment Galaxy) for seeing which texts and topics get taught most often [7].
- You can help by dropping syllabus PDFs/links into a server folder. Syllabi are text, so the same index applies.

### 3. Signals about you (cheap for you, very valuable for me)
- The one-tap difficulty / "confused" buttons in each lesson.
- Real-world output: chess games, photos of drawings, essays. The server stores them, and I review them in batches.
- A short note when life changes your available time (that goes into `NOTES.md`).

### 4. Server jobs you can host
Transcription, indexing (books + transcripts + syllabi + your lesson history), progress and review scheduling, file uploads, nightly review-page builds.

### Security note (server is publicly reachable)
- Every **write** endpoint requires a token.
- Use a **per-device token** entered once and stored in your browser, plus CORS restricted to `https://rahulsanjay18.github.io`. Add basic rate limiting.
- Keep the book server read-only. Purchased content is served only with auth, never to public pages.

---

## Decisions for you
1. **Migrate the 4 existing topics** onto the shared library (recommended), or start only with new topics?
2. **One visual style** across topics with a per-topic accent color (recommended), or keep each topic's own look?
3. **First plugin to build:** chess "find the move" (fits a live topic now), or art upload/critique?

---

## Sources
1. `topics/*/assets/quiz.js`, `board.js`, `pixels.js`, `style.css` (this repo): header comments, `diff`, `md5sum`.
2. `CLAUDE.md` (this repo): lessons self-contained / relative links only.
3. `.claude/skills/teach/SKILL.md` (this repo): retrieval/spacing/interleaving L41–45; real-world-steps lessons L105–108; equal-length answers L110; primary source L59.
4. H5P: https://h5p.org (open-source interactive HTML5 content framework).
5. YouTube Terms of Service: https://www.youtube.com/static?template=terms ("access, reproduce, download… except: (a) as expressly authorized by the Service; or (b) with prior written permission").
6. MIT OCW terms of use: https://ocw.mit.edu/pages/privacy-and-terms-of-use/ (CC BY-NC-SA 4.0).
7. Open Syllabus: https://www.opensyllabus.org/ (32.9M syllabi; Analytics, Course Matcher, Co-Assignment Galaxy).
