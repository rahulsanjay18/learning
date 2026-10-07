# Shared lesson library: author reference

Every lesson and reference page in every topic uses these files. **Read this file, not the JS source**, when writing a lesson.
Live examples of every widget: `assets/gallery.html`.

## Writing lessons in Markdown (preferred: fewer tokens, same HTML)
Write `topics/<slug>/lessons/NNNN-name.md`, then `python3 scripts/render_lesson.py <that .md> [--course S150]`. It writes the
`.html` next to it (shell, crumbs, plugin tags picked from what the page uses), appends the lesson to `index.html`, and with
`--course` records it in the major's `curriculum.json`. Edit the `.md` and re-render; never hand-edit a generated `.html`.

```
---
title: Power: how often a real effect gets caught
subtitle: Two blocks … One win: …
crumb: Statistics · Lesson 4          (optional; default "<Topic> · Lesson N")
index: Power (reading: C&B §8.3.1)     (optional index.html text; default the title)
main: data-skip=true                    (optional attributes on <main>: pretests, data-confidence=true)
---
## Headings, paragraphs, - lists, 1. lists, **bold**, *em*, `code`, [links](url), > quotes. Raw HTML lines pass through.
Write math naturally: \( a < b \), $$ … $$ (the renderer escapes < > &).

::: choice wu-size                      quiz: ::: <type> <data-id> key=value key="a b" …  (keys become data-*)
Prompt text (Markdown).
- [ ] wrong option
- [x] right option                      choice: mark the answer with [x]
--- hint
Shown after a miss.
--- explain
Shown once right.
:::
```
- `order`: list items in the correct order. `categorize`: `- item > Bucket`. `find-error`: steps as a list, `[x]` on the wrong one.
  `free`: `--- rubric` section. `py`: `--- code` and `--- check`. Other types: attributes as usual (`::: number n1 answer=64`).
- Diagrams and containers: `::: board fen=…`, `go`, `plot`, `timeline`, `map`, `game`, `xiangqi`, `shogi`, `python` (body = code),
  `video`, `sim`, `diagram` (list lines = data, see Plugins), `worked` (steps split by `--- step`), `reading`, `callout`, any other word = a div with that class.
  Nest with longer fences: `:::: deck` … `::: card c1` … `:::` … `::::`.
- A `## Sources` heading followed by a list becomes the numbered `<ol class="sources">`.
- Tested by `python3 scripts/test_render.py` (fixture: `scripts/fixtures/render-sample.md`, which shows every shorthand).

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
- **"How sure were you?"** After a first-try right answer on an auto-graded quiz, the learner picks *I knew it* or *I guessed*. A guess counts as not known: it leaves "right first try", is listed as `guessed:` in the results line, and its review resets to tomorrow (in the browser and on the progress server). **On by default on pretest pages and in the review deck**; elsewhere set `data-confidence="true"` on `<main>` or one quiz (`"false"` turns it off). Use it wherever a guess could pass: multiple choice, sorting, ordering, game moves.
- Pretests: `<main data-skip="true" data-pretest="true">` (Markdown: `main: data-skip=true data-pretest=true`). **`data-pretest` keeps every answer on the page out of spaced review** (browser, server, review deck and `/quiz-me`): a pretest measures what hasn't been taught yet. `data-skip` adds an **I don't know** button to every scored quiz (or set `data-skip` on one quiz). A skip counts as not known, reveals the `.explain`, and is listed as `skipped:` in the results line. After a wrong try the button becomes **Show me the answer** (reveals without scoring again; logged as a `reveal` event); it disappears once answered right.
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
| `card` | flashcard: front = `.prompt`, back = `.explain`; "Show answer" then "I knew it / I didn't". Wrap several in `<div class="lp-deck">` to show one at a time with a counter and an end summary | self |
| `estimate` | `data-answer="1526"` `[data-level="90"]` `[data-unit]` `[data-max-width]`: the learner types a low and high end they're 90% sure of; right = the range contains the answer (and isn't wider than max-width). A running calibration score is kept in the browser. Good for dates, magnitudes, Fermi questions | auto |
| `find-error` | `<ol class="steps"><li>…</li></ol>` + `data-answer="4"` (the wrong step's number): click the faulty step of a proof, derivation or argument | auto |
| `highlight` | `<div class="passage">` with the evidence marked `[[like this]]`; the rest splits into clickable sentences. Right = exactly the marked pieces. For source analysis ("which lines support the claim?") | auto |
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
- **Math** (`plugins/math.js` + `plugins/math.css`; KaTeX is vendored and loaded automatically):
  - Typeset with `\( inline \)`, `$$ display $$` or `\[ display \]` anywhere in the page. **A single `$` is never math**, so prices are safe. Add class `no-math` to skip an element.
  - Formula answer: `<div class="quiz" data-type="math" data-id="…" data-answer="p(1-p)" [data-forbid="(|)"] [data-tolerance="0.001"]>`. The learner types plain math (`2x^2+3`, `sqrt(2)/2`, `e^(-x)`, `sin(t)^2`, greek names like `theta`) and sees it typeset live. Any form equal at random sample points is accepted. `data-forbid` rejects listed substrings (e.g. `(|)` forces an expanded form) without scoring the attempt. `data-tolerance` is an absolute tolerance for numeric answers.
  - Functions: `sin cos tan asin acos atan sinh cosh tanh exp ln log sqrt abs`, `fact(n)` (n!) and `choose(n, k)`.
  - `node scripts/test_math.js` checks that every math quiz's answer parses.
- **Plot** (`plugins/plot.js` + `plugins/plot.css`; **load `plugins/math.js` first**, plot.js uses its parser): SVG function plots with sliders.
  - Plot: `<div class="lp-plot" data-x="-4:4" data-y="0:0.8" data-fns="exp(-(x-mu)^2/(2 sigma^2))/(sigma sqrt(2pi))" [data-params="mu=0:-2:2:0.1 | sigma=1:0.5:2:0.1"] [data-labels="Demand;Supply"] [data-vline="mu"] [data-shade="mu-sigma:mu+sigma"] [data-show-area="true"] [data-points="1,2;3,4"] [data-discrete="true"] data-xlabel="x" data-ylabel="density" data-caption="…"></div>`
  - `data-fns`: formulas in `x` (math-plugin syntax), several separated by `;`, drawn solid/dashed in `--accent`/`--fg`; `data-labels` adds a legend. `data-params`: `name=value:min:max:step`, `|`-separated, one slider each. **Parameter names must be one letter or a greek name** (`mu`, `sigma`, `lambda`…), never `x`.
  - `data-shade="a:b"` shades under the **first** formula between two expressions of the parameters (`-inf`/`inf` = the plot's edge); `data-show-area="true"` prints the area (trapezoid rule). `data-discrete="true"` draws whole `x` as bars, e.g. Binomial `choose(n,x) p^x (1-p)^(n-x)`; shading then sums the shaded bars. `data-vline` takes `;`-separated expressions.
  - Set the sliders: `<div class="quiz" data-type="plot-set" data-id="…" …plot attributes… data-target="mu=1.5" [data-tolerance="0.11"]>`. Right = every target parameter within tolerance (default half a slider step) when the learner presses Check. Pick a target the slider steps can reach.
  - `node scripts/test_plot.js` checks the plotting math and that every plot's formulas, sliders and targets are valid.
- **Timeline** (`plugins/timeline.js` + `plugins/timeline.css`): horizontal SVG timelines (History, any dated sequence).
  - Diagram: `<div class="lp-timeline" data-range="-600:1950" data-spans="c-321:-185:Maurya Empire|1526:1857:Mughal Empire" data-events="c-268:Ashoka's reign begins|1947:Independence" data-caption="…"></div>`. Spans are `start:end:label` (thin bars; overlaps stack in lanes), events `year:label` (dots; labels stack below the axis).
  - Years are whole numbers, **negative = BCE, and there is no year 0** (−1 is 1 BCE, 1 is 1 CE; 0 is rejected). Labels read "322 BCE"; "CE" appears only when the range spans both eras. Prefix `c` for approximate dates (`c-268` shows "c. 268 BCE"): **mark every uncertain date this way.**
  - Place it: `<div class="quiz" data-type="timeline-place" data-id="…" data-range="1500:1950" data-answer="1757" [data-tolerance="10"] [data-spans/data-events as context]>`. The learner taps the axis or types a year ("1757", "320 BCE") and presses Check; right = within `data-tolerance` years. A miss says "too early/late"; the true position is drawn once right or after a second miss. **Don't put the answer in the context events** (the test checks).
- **Map** (`plugins/map.js` + `plugins/map.css`): offline outline maps, Natural Earth 1:50m borders (vendored in `vendor/world-atlas/`, loaded on first use; no tiles or web services).
  - Diagram: `<div class="lp-map" data-view="60,5,100,38" data-points="28.61,77.21:New Delhi|19.08,72.88:Mumbai" [data-highlight="India|586"] data-caption="…"></div>`. Points are `lat,lon:label` (decimal degrees, north/east positive). `data-view` is `lonW,latS,lonE,latN` (South Asia: `60,5,100,38`; default: the world). `data-highlight` tints countries by world-atlas name ("India", "Pakistan") or ISO 3166-1 **numeric** code ("356"); there are no alpha-3 codes like "IND".
  - Locate it: `<div class="quiz" data-type="map-locate" data-id="…" data-view="…" data-answer="25.59,85.14" [data-tolerance-km="250"] [data-choices="25.59,85.14:Patna|28.61,77.21:New Delhi|…"]>`. The learner taps the map (or a candidate button) and presses Check; right = great-circle distance ≤ tolerance. A miss reports "off by N km" and the direction; the true point is drawn once right or after a second miss. Without `data-choices` the quiz says it needs a mouse or touch screen. With choices, exactly one must be within tolerance (the test checks). **Take coordinates from a source** (Wikipedia infobox) and cite it.
  - Borders are Natural Earth's de facto lines (e.g. Kashmir); say so in the caption where it matters.
  - `node scripts/test_timeline_map.js` checks year/BCE logic, ticks, lanes, haversine, projection, TopoJSON decoding, and that every timeline and map in the repo is valid.
- **Python** (`plugins/python.js` + `plugins/python.css`): runnable Python in the page via Pyodide (CPython in WebAssembly), pinned and loaded from jsDelivr on the first Run (~10 MB once, then cached; **needs a connection**, it is not vendored).
  - Snippet: `<div class="lp-py" [data-packages="numpy"] [data-timeout="10"]><pre class="code">print(sum(range(10)))</pre></div>`. Editable code box (Tab indents, Ctrl/Cmd+Enter runs), Run, Reset, and an output panel (stdout, plus errors in `--bad`). Unscored.
  - Exercise: `<div class="quiz" data-type="py" data-id="…" [data-packages="numpy"]><p class="prompt">…</p><pre class="code">starter code</pre><script type="text/python" class="check">assert abs(mean([1, 2, 3]) - 2) < 1e-9, "mean([1, 2, 3]) should be 2"</script><div class="explain" hidden>…</div></div>`. **Check** runs the learner's code, then the check in the same namespace; right = no exception. A miss shows only the exception message (write a helpful `assert …, "message"`), never the check source. Syntax errors, timeouts and load failures aren't scored. Run is never scored.
  - **Escaping:** the `<pre>` is HTML, so write `<` as `&lt;` and `&` as `&amp;` there. The check `<script>` is raw text: write `<` and `&` as is. Both are dedented.
  - Each run gets a fresh namespace. Runs happen in a worker; one that runs past `data-timeout` seconds (default 10) is stopped and Python restarts. Text output only: no `input()`, no plots. Packages are Pyodide's (`numpy`, `scipy`, `pandas`, …), loaded per page on first use. **Run the check with real Python against a right and a wrong answer before publishing.**
  - `node scripts/test_python.js` checks the helpers and that every Python widget has its code (and check).
- **Pixel art** (`plugins/pixels.js` + `plugins/pixels.css`): `.px` pictures and `.px-draw` drills. Usage is in the header comment of `plugins/pixels.js`.
- **Tiny games** (`plugins/games.js` + `plugins/games.css`): tic-tac-toe, Nim and Hex against an **exact solver** (minimax over every position), so feedback is ground truth. Boards are drawn from the position.
  - Positions: `ttt` rows top to bottom, `"X.O/.X./..O"` (X moves first; side to move from the counts). `nim` heap sizes `"3 4 5"` (normal play: taking the last object wins; heaps ≤ 15, product of (heap+1) ≤ 20000). `hex` an n×n rhombus `"B../.W./..."`, n ≤ 4; **Black moves first and joins top to bottom, White joins left to right**; a 4×4 position needs ≥ 4 stones (the empty 4×4 board takes ~10 s). Cells: `a1` = top-left, letters for columns, numbers for rows from the top.
  - Play: `<div class="lp-game" data-game="ttt|nim|hex" [data-position="…"] [data-you="first|second"] [data-hints="true"] data-caption="…"></div>`. Unscored. The solver plays the best move (fastest win, slowest loss); `data-hints` adds a toggle that labels every move W/D/L for the side to move.
  - Find a good move: `<div class="quiz" data-type="game-move" data-id="…" data-game="…" data-position="…" [data-hint="…"]>`. **No `data-answer`**: right = any move that keeps the position's best outcome (any winning move, or any drawing move in a drawn position). A wrong move says whether it loses or only draws; after two misses the good moves are marked. The position must not be lost for the mover and must have at least one worse move (the test checks).
  - `node scripts/test_games.js` checks the solver (Nim against the nim-sum theorem, Hex's no-draw property) and every game widget in the repo.
- **Xiangqi** (`plugins/xiangqi.js` + `plugins/xiangqi.css`): our own rules engine, checked against published perft counts.
  - Position: FEN from Black's back rank (rank 9) to Red's (rank 0), then `w`/`b`; the start is the default. Uppercase Red (moves first), lowercase Black: K general, A advisor, E elephant (B ok), H horse (N ok), R chariot, C cannon, P soldier. Squares: files `a`–`i` from Red's left, ranks `0`–`9` from Red's side; moves like `h2e2`.
  - Diagram / sandbox: `<div class="xq-board" [data-fen] [data-hl="e2 e9"] [data-arrows="h2-e2"] [data-flip="true"] [data-play="true"] [data-labels="latin"] data-caption="…"></div>`. `data-play` lets the learner move both sides with legal-move dots, Undo and Start over. Pieces show their characters (帥將…); `data-labels="latin"` shows letters.
  - Find the move: `<div class="quiz" data-type="xiangqi-move" data-id="…" data-fen="…" data-answer="a8a9|a8e8">`. Only legal moves can be played; a legal wrong move is a scored miss.
  - Rules worth flagging in lessons: generals may not face on an open file; **no legal move loses (stalemate is a loss, unlike chess)**; repetition rules are not enforced.
- **Shogi** (`plugins/shogi.js` + `plugins/shogi.css`): our own engine, checked by perft and against python-shogi.
  - Position: SFEN `board side hands`, e.g. `7nk/7p1/8G/9/9/9/9/9/K8 b PG 1`; the start is the default. Uppercase Sente (▲, moves first), lowercase Gote; `+` promoted. Moves in USI: `7g7f`, `8h2b+`, drops `P*5e`.
  - Diagram / sandbox: `<div class="shogi-board" [data-sfen] [data-hl] [data-arrows="8h-2b"] [data-flip] [data-play="true"] [data-labels="latin"] data-caption="…"></div>`. Hands are drawn above and below; click a piece in hand to drop it. When promotion is optional the board asks.
  - Find the move: `<div class="quiz" data-type="shogi-move" data-id="…" data-sfen="…" data-answer="G*1b">`. Answers are USI. Illegal moves (nifu, pawn-drop mate, leaving the king in check, a piece that could never move) are never offered.
  - `node scripts/test_xiangqi_shogi.js` (about 10 s; `--quick` skips depth 4) runs the perfts and rule tests and checks every answer in the repo is legal.
- **Simulations** (`plugins/sim.js` + `plugins/sim.css`): statistics labs, unscored; follow one with a quiz.
  - `<div class="lp-sim" data-sim="ci-coverage" [data-n="5"] [data-level="0.95"] [data-method="t|z|z-plugin"]>`: intervals for a normal mean, misses in red, running coverage. `z-plugin` (sample s with the z value) visibly under-covers for small n.
  - `<div class="lp-sim" data-sim="sampling-mean" [data-pop="exponential|uniform|normal|bimodal"] [data-n="2"]>`: 1,000 sample means, slider for n, sd(x̄) vs σ/√n (the CLT).
  - `<div class="lp-sim" data-sim="multiple-testing" [data-k="20"] [data-alpha="0.05"]>`: k null tests per experiment; how often at least one p < α; Bonferroni toggle.
  - `node scripts/test_sim.js` checks the z/t quantiles against tables and the coverage rates against theory.
- **Diagram** (`plugins/diagram.js` + `plugins/diagram.css`): code-drawn templates; you give the facts, the code lays them out.
  - Graph (dependency map, flow, tree; must be acyclic): `<div class="lp-diagram" data-kind="graph" data-nodes="ax:The three axioms|comp:P(Aᶜ) = 1 − P(A)" data-edges="ax>comp:label|comp>le1|a~>b" [data-dir="down|right"] [data-hl="comp"] data-caption="…"></div>`. Nodes are `id:label` (an edge end with no node entry is labelled by its id); edges `from>to[:label]`, `~>` dashed. Layered layout with crossing reduction; labels wrap at ~20 characters. More than 12 nodes fails the test: split it.
  - Sequence: `<div class="lp-diagram" data-kind="sequence" data-actors="Client|Server" data-steps="Client>Server:SYN|Server~>Client:SYN-ACK|Server>Server:check">`. `~>` dashed (a reply); `A>A` is a self-step.
  - Venn: `<div class="lp-diagram" data-kind="venn" data-sets="A|B|C" [data-universe="S"] [data-shade="(A ∪ B)ᶜ ∩ C"]>`. 2 or 3 sets. Shade syntax: `∩ & and`, `∪ | + or`, complement `!A`, `not A`, `A'`, `Aᶜ`, `A^c`, difference `A \ B` or `A − B`, parentheses.
  - Markdown: `::: diagram kind=graph caption="…"` with list lines: `- id: label` (nodes), `- a > b: label` (edges or steps), `- A` (sets or actors).
  - **Look at it before committing:** `node scripts/snap.mjs <page.html> [selector] [--dark] [--width 380]` saves PNGs of each diagram. `node scripts/test_diagram.js` checks layout, set algebra and every diagram in the repo.
- New plugin: `LP.register({type, init(el, ctx), scored, selector})`. In `init`, call `ctx.result(ok, answer, kind)` once per attempt (first call is scored) and `ctx.feedback(ok, msg)`. Helpers: `LP.util`.

## Daily review deck (`assets/review.html`)
- Every scored answer updates a spaced schedule in the learner's browser (`localStorage["lp.review"]`, same 1/3/7/16/35/80/180-day boxes as the progress server). Misses and skips come back the next day.
- The review page re-asks due questions **pulled live from their original lesson pages**, interleaved across topics, max 20 per session. With sync on it also merges the server's `/due` list (other devices).
- So: **keep `data-id`s stable** (changing one orphans its schedule), and keep a question self-contained. If it depends on a diagram, put the diagram directly before the quiz or list its element ids in `data-context="id1 id2"`.
- Every lesson footer links to it. **New plugin? Add its `<link>` and `<script>` to `review.html` too**, or its quizzes can't come back in review.

## Results and sync
- Every answer, rating and note is logged to `localStorage["lp.queue"]` on the learner's device.
- **Copy my results** gives one line the learner pastes into the next session, e.g.
  `lp-results chess/0003-forks | 7/9 right first try | missed: fork-2,pin-1 | rating: too-hard`, plus any free-response answers.
- If sync is configured ("Sync settings": server URL + device token), events are POSTed as `{"events":[…]}` to `<url>/events` with `Authorization: Bearer <token>`. Server: `progress-server/` (pair a device via `assets/sync.html`).

## Checks (run before committing a lesson)
```sh
python3 scripts/lint_lessons.py          # structure, answers, links, equal-length options
node scripts/test_widgets.mjs            # opens every page in headless Chromium and drives the gallery
node scripts/test_math.js                # math parser/equivalence + every math answer parses
node scripts/test_plot.js                # plot ticks/areas/paths + every plot and plot-set is valid
node scripts/test_go_rules.js            # Go rules + every go-move problem's line is legal
node scripts/test_timeline_map.js        # timeline years/ticks/lanes, map distance/projection/basemap + every timeline and map is valid
node scripts/test_python.js              # python helpers (dedent, error messages) + every Python snippet/exercise is well formed
node scripts/test_sync_e2e.mjs           # lesson page -> progress server round trip (needs fastapi + uvicorn)
```
