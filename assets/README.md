# Shared lesson library: author reference

Every lesson and reference page in every topic uses these files. **Read this file, not the JS source**, when writing a lesson.
Live examples of every widget: `assets/gallery.html`.

## Page skeleton (a lesson at `topics/<slug>/lessons/NNNN-name.html`)

```html
<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>…</title>
<link rel="stylesheet" href="../../../assets/lp.css">
<!-- only if needed: plugin CSS, then ../assets/topic.css for topic-only styles -->
</head><body><main>
<nav class="crumbs"><a href="../../../index.html">All topics</a> · …</nav>
<h1>…</h1><p class="subtitle">…</p>
…content and widgets…
<ol class="sources">…</ol>
</main>
<script src="../../../assets/lp.js"></script>
<!-- plugins after lp.js, e.g. <script src="../../../assets/plugins/chess.js"></script> -->
</body></html>
```

- `lp.js` adds the score bar and, on lesson pages, the footer: difficulty rating, "anything confusing?" note, **Copy my results**, and sync settings.
- Give every quiz a short `data-id` that is unique within the page. IDs stay stable when you edit the page and feed spaced review: `chess/0003-forks#fork-1`.
- Topic-only styles go in `topics/<slug>/assets/topic.css`. Don't copy `lp.css`/`lp.js` into a topic. Add a widget here instead.
- Keep CSS plain: one column, serif text, thin rules. No shadows, gradients or animation.

## Scored widgets: `<div class="quiz" data-type="…" data-id="…">`
Common children: `<p class="prompt">` (the question) and `<div class="explain" hidden>` (shown once right). Common attribute: `data-hint` (shown on a wrong answer).

| type | attributes / children | graded |
|---|---|---|
| `choice` | `data-options="a\|b\|c"` `data-answer="b"` `[data-shuffle="true"]`. **All options the same word count** (lint warns). | auto |
| `number` | `data-answer="5"` `[data-tolerance="0.1"]`. Numeric keyboard on phones. | auto |
| `exact` | `data-answer="Paris\|Paris, France"` (accepted forms) `[data-case="true"]` | auto |
| `cloze` | blanks inline in `.prompt`: `boils at [[100]] °C … [[0\|zero]]` | auto |
| `order` | `data-items="first\|second\|third"` in the **correct** order; shown shuffled | auto |
| `categorize` | `data-buckets="A\|B"` `data-items="item>A\|other item>B"`; doubles as matching | auto |
| `recall` | write from memory → reveal `.explain` → "I had it / I missed some" | self |
| `checklist` | an `<ol>`/`<ul>` of real-world steps inside the quiz; done when all ticked | self |
| `free` | `<div class="rubric">` (hidden, for the grader) + optional `.explain` model answer shown after submitting | teacher, next session |

## Unscored widgets
- **Video:** `<div class="lp-video" data-youtube="VIDEO_ID" [data-start="90"] [data-end="300"] data-caption="Speaker, “Title”"></div>`. Privacy-enhanced embed plus an "open on YouTube" link. Put checkpoint quizzes right after it.
- **Worked example:** `<div class="lp-worked"><div class="step">…</div><div class="step">…</div></div>` reveals one step per click.

## Plugins
- **Chess** (`plugins/chess.js` + `plugins/chess.css`):
  - Diagram: `<div class="board-wrap" data-fen="…" data-hl="e5 c6" data-arrows="f3-e5" data-caption="…" [data-flip="true"]></div>`
  - Find the move: `<div class="quiz" data-type="chess-move" data-id="…" data-fen="…" data-answer="d1d8|Rd8#">`. The answer is UCI or SAN, with several separated by `|`. Legality comes from the vendored chess.js (`vendor/`). **Verify the answer with chess.js before publishing.**
- **Go** (`plugins/go.js` + `plugins/go.css`): columns A–T without I, rows counted from the bottom.
  - Diagram: `<div class="go-board" data-size="9|13|19" data-black="C3 D4" data-white="E5" [data-marks="E5"] [data-labels="D6:a"] [data-view="A1:J8"] [data-coords="false"] data-caption="…"></div>`. `data-view` crops to a corner or side.
  - Problem: `<div class="quiz" data-type="go-move" data-id="…" data-size="9" data-black="…" data-white="…" [data-to-play="W"] data-answer="E4|F3">` for one move, **or** `data-solution="E7 E4 E3"`, a line where the learner's moves alternate with scripted replies. Illegal moves (occupied, suicide, ko) are refused and not scored. A wrong move counts as a miss; "Start over" resets.
  - `node scripts/test_go_rules.js` checks that every problem's line is legal. **Whether it's the best move is your job**: read it out, and use an engine (e.g. KataGo) for anything non-trivial.
- **Pixel art** (`plugins/pixels.js` + `plugins/pixels.css`): `.px` pictures and `.px-draw` drills. Usage is in the header comment of `plugins/pixels.js`.
- New plugin: `LP.register({type, init(el, ctx), scored, selector})`. In `init`, call `ctx.result(ok, answer, kind)` once per attempt (first call is scored) and `ctx.feedback(ok, msg)`. Helpers: `LP.util`.

## Results and sync
- Every answer, rating and note is logged to `localStorage["lp.queue"]` on the learner's device.
- **Copy my results** gives one line the learner pastes into the next session, e.g.
  `lp-results chess/0003-forks | 7/9 right first try | missed: fork-2,pin-1 | rating: too-hard`, plus any free-response answers.
- If sync is configured ("Sync settings": server URL + device token), events are POSTed as `{"events":[…]}` to `<url>/events` with `Authorization: Bearer <token>`. Server: `progress-server/` (pair a device via `assets/sync.html`).

## Checks (run before committing a lesson)
```sh
python3 scripts/lint_lessons.py          # structure, answers, links, equal-length options
node scripts/test_widgets.mjs            # opens every page in headless Chromium and drives the gallery
node scripts/test_go_rules.js            # Go rules + every go-move problem's line is legal
node scripts/test_sync_e2e.mjs           # lesson page -> progress server round trip (needs fastapi + uvicorn)
```
