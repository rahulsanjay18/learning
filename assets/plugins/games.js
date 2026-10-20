// Tiny games plugin: tic-tac-toe, Nim and Hex, played against an exact (perfect) solver. Load after assets/lp.js;
// style: assets/plugins/games.css. Boards are drawn from the position, never from images.
//
// Positions (data-position):
//   ttt  "X.O/.X./..O"  rows top to bottom, "." empty. X moves first, so the side to move follows from the counts.
//   nim  "3 4 5"        heap sizes. Normal play: whoever takes the last object wins. Product of (heap+1) at most 20000.
//   hex  "B../.W./..."  an n×n rhombus, rows top to bottom (row r is shifted right by r half-cells). Black moves first and
//                       joins TOP to BOTTOM; White joins LEFT to RIGHT. n ≤ 4, and a 4×4 position needs ≥ 4 stones
//                       (the empty 4×4 board takes the solver ~10 s; 3×3 and fuller 4×4 boards are instant).
// Cell names: columns a, b, c… left to right, rows 1, 2, 3… top to bottom ("b2" is the centre of a 3×3 board).
//
// Play against the solver (unscored):
//   <div class="lp-game" data-game="ttt|nim|hex" [data-position="…"] [data-you="first|second"] [data-hints="true"]
//        [data-caption="…"]></div>
//   data-you: which side the learner plays from the start position (default: the side to move). The solver always picks a
//   best move (fastest win, slowest loss). data-hints="true" adds a "Show move values" toggle: every legal move is labelled
//   W / D / L for the side to move.
// Best-move quiz (scored):
//   <div class="quiz" data-type="game-move" data-id="…" data-game="ttt|nim|hex" data-position="…" [data-hint="…"]>
//     <p class="prompt">X to move: find a move that keeps the win.</p><div class="explain" hidden>…</div></div>
//   No data-answer: the solver decides. Right = any move that keeps the position's best outcome (any winning move when the
//   position is won; any drawing move when it's drawn). The position must have at least one move that is worse (the test
//   checks), and the side to move must not already be lost.
// Pure logic is exported for Node (node scripts/test_games.js): parse, solve, moveValues, bestMoves, describeMove, hexWinner.
(function () {
  "use strict";

  // ---------- games: {parse(str) -> state, key, moves, play, over(state) -> null | "lose" | "draw" (for the side to move)} ----------
  var TTT_LINES = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];
  function cellName(i, n) { return String.fromCharCode(97 + (i % n)) + (Math.floor(i / n) + 1); }

  var ttt = {
    parse: function (s) {
      var cells = String(s == null || s === "" ? "........." : s).replace(/[\/\s]/g, "").toUpperCase().split("");
      if (cells.length !== 9 || cells.some(function (c) { return "XO.".indexOf(c) < 0; })) throw new Error("ttt position needs 9 cells of X, O or .");
      var x = cells.filter(function (c) { return c === "X"; }).length, o = cells.filter(function (c) { return c === "O"; }).length;
      if (x !== o && x !== o + 1) throw new Error("ttt position: X moves first, so X must have as many marks as O or one more");
      return { cells: cells, turn: x === o ? "X" : "O" };
    },
    key: function (s) { return s.cells.join(""); },
    winner: function (s) {
      for (var i = 0; i < TTT_LINES.length; i++) {
        var l = TTT_LINES[i], a = s.cells[l[0]];
        if (a !== "." && a === s.cells[l[1]] && a === s.cells[l[2]]) return a;
      }
      return null;
    },
    over: function (s) {
      var w = ttt.winner(s);
      if (w) return w === s.turn ? "win" : "lose";
      return s.cells.indexOf(".") < 0 ? "draw" : null;
    },
    moves: function (s) { var m = []; s.cells.forEach(function (c, i) { if (c === ".") m.push(i); }); return m; },
    play: function (s, i) { var c = s.cells.slice(); c[i] = s.turn; return { cells: c, turn: s.turn === "X" ? "O" : "X" }; },
    describe: function (s, i) { return s.turn + " on " + cellName(i, 3); },
    sideName: function (s) { return s.turn; }
  };

  var nim = {
    parse: function (s) {
      var h = String(s || "").trim().split(/[\s,]+/).filter(Boolean).map(Number);
      if (!h.length || h.some(function (x) { return !(x >= 0 && x <= 15 && Math.floor(x) === x); })) throw new Error("nim position: heap sizes 0–15, e.g. \"3 4 5\"");
      if (h.reduce(function (p, x) { return p * (x + 1); }, 1) > 20000) throw new Error("nim position too big for the solver");
      return { heaps: h, turn: 0 };
    },
    key: function (s) { return s.heaps.join(","); },     // the value doesn't depend on whose turn it is
    over: function (s) { return s.heaps.every(function (x) { return x === 0; }) ? "lose" : null; },
    moves: function (s) {
      var m = [];
      s.heaps.forEach(function (x, h) { for (var k = 1; k <= x; k++) m.push(h * 100 + k); });
      return m;
    },
    play: function (s, mv) {
      var h = Math.floor(mv / 100), k = mv % 100, hs = s.heaps.slice(); hs[h] -= k;
      return { heaps: hs, turn: 1 - s.turn };
    },
    describe: function (s, mv) { return "take " + (mv % 100) + " from heap " + (Math.floor(mv / 100) + 1); },
    sideName: function (s) { return s.turn === 0 ? "first player" : "second player"; }
  };

  // Hex on bitboards: bit r*n+c. Neighbours of (r,c): (r-1,c) (r-1,c+1) (r,c-1) (r,c+1) (r+1,c-1) (r+1,c).
  function hexNeighbourMasks(n) {
    var out = [];
    for (var i = 0; i < n * n; i++) {
      var r = Math.floor(i / n), c = i % n, m = 0;
      [[-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0]].forEach(function (d) {
        var rr = r + d[0], cc = c + d[1];
        if (rr >= 0 && rr < n && cc >= 0 && cc < n) m |= 1 << (rr * n + cc);
      });
      out.push(m);
    }
    return out;
  }
  var NB = {};
  // Does `stones` (a bitmask) connect the two edges? start/end are edge masks.
  function connects(stones, n, start, end) {
    var nb = NB[n] || (NB[n] = hexNeighbourMasks(n));
    var reach = stones & start, prev = -1;
    while (reach !== prev) {
      if (reach & end) return true;
      prev = reach;
      for (var i = 0; i < n * n; i++) if (reach & (1 << i)) reach |= nb[i] & stones;
    }
    return !!(reach & end);
  }
  function hexEdges(n) {
    var top = 0, bottom = 0, left = 0, right = 0;
    for (var k = 0; k < n; k++) { top |= 1 << k; bottom |= 1 << ((n - 1) * n + k); left |= 1 << (k * n); right |= 1 << (k * n + n - 1); }
    return { top: top, bottom: bottom, left: left, right: right };
  }
  function hexWinner(s) {
    var e = hexEdges(s.n);
    if (connects(s.b, s.n, e.top, e.bottom)) return "B";
    if (connects(s.w, s.n, e.left, e.right)) return "W";
    return null;
  }
  function bits(x) { var c = 0; while (x) { x &= x - 1; c++; } return c; }
  var hex = {
    parse: function (str) {
      var rows = String(str || "").trim().toUpperCase().split(/[\/\s]+/).filter(Boolean);
      var n = rows.length;
      if (n < 2 || n > 4 || rows.some(function (r) { return r.length !== n || /[^BW.]/.test(r); }))
        throw new Error("hex position: 2–4 rows of B, W or ., as many cells per row as rows, e.g. \"B../.W./...\"");
      var b = 0, w = 0;
      rows.join("").split("").forEach(function (ch, i) { if (ch === "B") b |= 1 << i; if (ch === "W") w |= 1 << i; });
      var nb = bits(b), nw = bits(w);
      if (nb !== nw && nb !== nw + 1) throw new Error("hex position: Black moves first, so Black has as many stones as White or one more");
      if (n === 4 && nb + nw < 4) throw new Error("hex position: a 4×4 position needs at least 4 stones (the empty board is too slow to solve live)");
      return { n: n, b: b, w: w, turn: nb === nw ? "B" : "W" };
    },
    key: function (s) { return s.b * 65536 + s.w; },
    over: function (s) { var x = hexWinner(s); return x ? (x === s.turn ? "win" : "lose") : null; },   // no draws in Hex
    moves: function (s) { var m = [], occ = s.b | s.w; for (var i = 0; i < s.n * s.n; i++) if (!(occ & (1 << i))) m.push(i); return m; },
    play: function (s, i) {
      return s.turn === "B" ? { n: s.n, b: s.b | (1 << i), w: s.w, turn: "W" } : { n: s.n, b: s.b, w: s.w | (1 << i), turn: "B" };
    },
    describe: function (s, i) { return (s.turn === "B" ? "Black" : "White") + " on " + cellName(i, s.n); },
    sideName: function (s) { return s.turn === "B" ? "Black" : "White"; }
  };

  var GAMES = { ttt: ttt, nim: nim, hex: hex };
  function game(name) { var g = GAMES[name]; if (!g) throw new Error("data-game must be ttt, nim or hex"); return g; }

  // ---------- solver ----------
  // Value for the side to move: {v: 1 win | 0 draw | -1 loss, d: plies to the end with best play (win fast, lose slow)}.
  var MEMO = { ttt: new Map(), nim: new Map(), hex: new Map() };
  function solve(name, s) {
    var g = game(name), memo = MEMO[name], k = g.key(s);
    if (memo.has(k)) return memo.get(k);
    var o = g.over(s), res;
    if (o === "lose") res = { v: -1, d: 0 };
    else if (o === "win") res = { v: 1, d: 0 };
    else if (o === "draw") res = { v: 0, d: 0 };
    else {
      res = null;
      var ms = g.moves(s);
      for (var i = 0; i < ms.length; i++) {
        var c = solve(name, g.play(s, ms[i])), v = -c.v, d = c.d + 1;
        if (!res || better(v, d, res.v, res.d)) res = { v: v, d: d };
      }
    }
    memo.set(k, res);
    return res;
  }
  function better(v, d, bv, bd) {
    if (v !== bv) return v > bv;
    return v > 0 ? d < bd : v < 0 ? d > bd : d < bd;
  }
  // Each legal move with its value for the mover.
  function moveValues(name, s) {
    var g = game(name);
    return g.moves(s).map(function (m) { var c = solve(name, g.play(s, m)); return { move: m, v: -c.v, d: c.d + 1 }; });
  }
  // Moves that keep the best outcome (all of them, not only the fastest win).
  function bestMoves(name, s) {
    var mv = moveValues(name, s), top = Math.max.apply(null, mv.map(function (x) { return x.v; }));
    return mv.filter(function (x) { return x.v === top; });
  }
  // The solver's own choice: best outcome, then fastest win / slowest loss; ties broken by `rand` (0..1).
  function solverMove(name, s, rand) {
    var mv = moveValues(name, s), best = null;
    mv.forEach(function (x) { if (!best || better(x.v, x.d, best.v, best.d)) best = x; });
    var ties = mv.filter(function (x) { return x.v === best.v && x.d === best.d; });
    return ties[Math.floor((rand == null ? Math.random() : rand) * ties.length) % ties.length].move;
  }
  function outcomeText(v, d) {
    var m = Math.ceil(d / 2);
    if (v > 0) return "wins" + (d > 1 ? " in " + m + " move" + (m > 1 ? "s" : "") : "");
    if (v < 0) return "loses" + (d > 1 ? " (in " + m + " move" + (m > 1 ? "s" : "") + " against best play)" : "");
    return "draws";
  }

  var api = { parse: function (name, s) { return game(name).parse(s); }, solve: solve, moveValues: moveValues, bestMoves: bestMoves,
    solverMove: solverMove, describeMove: function (name, s, m) { return game(name).describe(s, m); }, hexWinner: hexWinner,
    over: function (name, s) { return game(name).over(s); }, play: function (name, s, m) { return game(name).play(s, m); },
    outcomeText: outcomeText, cellName: cellName };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---------- drawing ----------
  var SVGNS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs) { var e = document.createElementNS(SVGNS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
  var VAL = { "1": "W", "0": "D", "-1": "L" };

  // Draws `s` into `box`. onPick(move) is called when the learner picks a legal move (null = board not clickable).
  // labels: {move: "W"|"D"|"L"} shown on each move (hints). mark: a move to highlight (the last one played).
  function draw(box, name, s, onPick, labels, mark) {
    box.textContent = "";
    if (name === "nim") return drawNim(box, s, onPick, labels, mark);
    if (name === "ttt") return drawTtt(box, s, onPick, labels, mark);
    return drawHex(box, s, onPick, labels, mark);
  }
  function drawTtt(box, s, onPick, labels, mark) {
    var grid = document.createElement("div"); grid.className = "gm-ttt";
    s.cells.forEach(function (c, i) {
      var b = document.createElement("button"); b.type = "button";
      b.className = "gm-cell" + (c !== "." ? " filled" : "") + (i === mark ? " last" : "");
      b.textContent = c === "." ? (labels && labels[i] != null ? labels[i] : "") : c;
      if (c === "." && labels && labels[i] != null) b.classList.add("hint", "h" + labels[i]);
      b.setAttribute("aria-label", cellName(i, 3) + (c === "." ? " empty" : " " + c));
      if (c !== "." || !onPick) b.disabled = true; else b.addEventListener("click", function () { onPick(i); });
      grid.appendChild(b);
    });
    box.appendChild(grid);
  }
  function drawNim(box, s, onPick, labels) {
    var wrap = document.createElement("div"); wrap.className = "gm-nim";
    s.heaps.forEach(function (x, h) {
      var row = document.createElement("div"); row.className = "gm-heap";
      var lab = document.createElement("span"); lab.className = "gm-heap-label"; lab.textContent = "Heap " + (h + 1) + " (" + x + ")";
      row.appendChild(lab);
      var toks = document.createElement("span"); toks.className = "gm-tokens";
      for (var j = 0; j < x; j++) (function (j) {
        var k = x - j, mv = h * 100 + k;            // clicking token j takes it and every token to its right
        var b = document.createElement("button"); b.type = "button"; b.className = "gm-token";
        b.setAttribute("aria-label", "Take " + k + " from heap " + (h + 1));
        b.title = "take " + k;
        if (labels && labels[mv] != null) { b.textContent = labels[mv]; b.classList.add("hint", "h" + labels[mv]); }
        if (!onPick) b.disabled = true; else b.addEventListener("click", function () { onPick(mv); });
        toks.appendChild(b);
      })(j);
      row.appendChild(toks);
      wrap.appendChild(row);
    });
    box.appendChild(wrap);
  }
  function drawHex(box, s, onPick, labels, mark) {
    var n = s.n, R = 20, W = Math.sqrt(3) * R, pad = 14;
    var cx = function (r, c) { return pad + W / 2 + c * W + r * W / 2; }, cy = function (r) { return pad + R + r * 1.5 * R; };
    var width = pad * 2 + W * n + W * (n - 1) / 2, height = pad * 2 + R * 2 + 1.5 * R * (n - 1);
    var svg = svgEl("svg", { "class": "gm-hex", viewBox: "0 0 " + width.toFixed(1) + " " + height.toFixed(1), width: Math.round(width * 1.4),
      role: "group", "aria-label": "Hex board, " + n + " by " + n + ". Black joins top and bottom, White joins left and right." });
    function corner(x, y, k) { var a = Math.PI / 180 * (60 * k - 30); return [x + R * Math.cos(a), y + R * Math.sin(a)]; }
    // edge bands: Black's (top/bottom) solid, White's (left/right) dashed
    var e = hexEdges(n);
    for (var i = 0; i < n * n; i++) {
      var r = Math.floor(i / n), c = i % n, x = cx(r, c), y = cy(r);
      var pts = []; for (var k = 0; k < 6; k++) pts.push(corner(x, y, k).map(function (v) { return v.toFixed(1); }).join(","));
      var who = s.b & (1 << i) ? "B" : s.w & (1 << i) ? "W" : ".";
      var poly = svgEl("polygon", { points: pts.join(" "), "class": "gm-hexcell" + (who === "B" ? " black" : who === "W" ? " white" : "") + (i === mark ? " last" : "") });
      var g = svgEl("g", { "class": "gm-hexg" }); g.appendChild(poly);
      var edge = function (k1, k2, cls) { var p = corner(x, y, k1), q = corner(x, y, k2); g.appendChild(svgEl("line", { x1: p[0].toFixed(1), y1: p[1].toFixed(1), x2: q[0].toFixed(1), y2: q[1].toFixed(1), "class": cls })); };
      // corners k = 0..5 at 60k−30°: 0 upper right, 1 lower right, 2 bottom, 3 lower left, 4 upper left, 5 top
      if (e.top & (1 << i)) { edge(4, 5, "gm-edge-b"); edge(5, 0, "gm-edge-b"); }
      if (e.bottom & (1 << i)) { edge(1, 2, "gm-edge-b"); edge(2, 3, "gm-edge-b"); }
      if (e.left & (1 << i)) { edge(3, 4, "gm-edge-w"); if (!(e.bottom & (1 << i))) edge(2, 3, "gm-edge-w"); }
      if (e.right & (1 << i)) { edge(0, 1, "gm-edge-w"); if (!(e.top & (1 << i))) edge(5, 0, "gm-edge-w"); }
      if (who === "." && labels && labels[i] != null) {
        var t = svgEl("text", { x: x.toFixed(1), y: (y + 4).toFixed(1), "class": "gm-hexlabel h" + labels[i], "text-anchor": "middle" }); t.textContent = labels[i]; g.appendChild(t);
      }
      var title = svgEl("title", {}); title.textContent = cellName(i, n); g.appendChild(title);
      if (who === "." && onPick) {
        g.setAttribute("tabindex", "0"); g.setAttribute("role", "button"); g.setAttribute("aria-label", cellName(i, n));
        g.classList.add("open");
        (function (i) {
          g.addEventListener("click", function () { onPick(i); });
          g.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); onPick(i); } });
        })(i);
      }
      svg.appendChild(g);
    }
    box.appendChild(svg);
  }
  function legend(name) {
    if (name === "hex") return "Black (moves first) joins the top and bottom edges (solid); White joins left and right (dashed).";
    if (name === "nim") return "Tap a token to take it and every token to its right. Whoever takes the last token wins.";
    return "Three in a row wins. X moves first.";
  }
  function hintLabels(name, s) {
    var out = {};
    moveValues(name, s).forEach(function (x) { out[x.move] = VAL[String(x.v)]; });
    return out;
  }
  function addCaption(el, text) { if (text) { var c = document.createElement("div"); c.className = "gm-caption"; c.textContent = text; el.appendChild(c); } }

  // ---------- play widget ----------
  function initPlay(el) {
    var name = el.dataset.game, g = game(name), start = g.parse(el.dataset.position || "");
    var startSide = g.sideName(start), you = el.dataset.you === "second" ? "second" : "first";
    var hintsOn = false, s, last = null, busy = false;
    var status = document.createElement("p"); status.className = "gm-status";
    var board = document.createElement("div"); board.className = "gm-board";
    var row = document.createElement("div"); row.className = "gm-controls";
    var reset = document.createElement("button"); reset.type = "button"; reset.textContent = "Start over";
    row.appendChild(reset);
    var hintBtn = null;
    if (el.dataset.hints === "true") { hintBtn = document.createElement("button"); hintBtn.type = "button"; hintBtn.textContent = "Show move values"; row.appendChild(hintBtn); }
    var leg = document.createElement("p"); leg.className = "gm-legend"; leg.textContent = legend(name) + (hintBtn ? " Move values: W = wins, D = draws, L = loses (for the side to move)." : "");
    el.textContent = "";
    el.appendChild(leg); el.appendChild(board); el.appendChild(status); el.appendChild(row);
    addCaption(el, el.dataset.caption);

    function yourTurn() { return (g.sideName(s) === startSide) === (you === "first"); }
    function render() {
      var o = g.over(s);
      var mine = yourTurn();
      draw(board, name, s, !o && mine && !busy ? pick : null, hintsOn && !o && mine ? hintLabels(name, s) : null, last);
      if (o) {
        var youWon = (o === "lose") !== mine;     // "lose" is for the side to move
        status.textContent = o === "draw" ? "Draw." : youWon ? "You win." : "The solver wins.";
      } else if (mine) {
        var v = solve(name, s);
        status.textContent = "Your move (" + g.sideName(s) + ")." + (hintsOn ? " With best play you " + outcomeText(v.v, v.d).replace(/^wins/, "win").replace(/^draws/, "draw").replace(/^loses/, "lose") + "." : "");
      } else status.textContent = "Solver is thinking…";
    }
    function pick(m) {
      s = g.play(s, m); last = m; busy = true; render();
      setTimeout(function () {
        if (!g.over(s)) { var r = solverMove(name, s); s = g.play(s, r); last = r; }
        busy = false; render();
      }, 250);
    }
    function restart() {
      s = start; last = null; busy = false; render();
      if (!yourTurn() && !g.over(s)) { busy = true; render(); setTimeout(function () { var r = solverMove(name, s); s = g.play(s, r); last = r; busy = false; render(); }, 250); }
    }
    reset.addEventListener("click", restart);
    if (hintBtn) hintBtn.addEventListener("click", function () { hintsOn = !hintsOn; hintBtn.textContent = hintsOn ? "Hide move values" : "Show move values"; render(); });
    restart();
  }

  // ---------- best-move quiz ----------
  function initMove(q, ctx) {
    var U = LP.util, name = q.dataset.game, g = game(name), s = g.parse(q.dataset.position || "");
    if (g.over(s)) throw new Error("game-move: the game is already over in this position");
    var best = bestMoves(name, s), all = moveValues(name, s);
    if (best[0].v < 0) throw new Error("game-move: the side to move is lost whatever it plays");
    if (best.length === all.length) throw new Error("game-move: every move is equally good, so there's nothing to find");
    var top = best[0].v, done = false, tries = 0;
    var leg = U.el("p", "gm-legend", legend(name));
    var board = U.el("div", "gm-board");
    U.beforeExplain(q, leg); U.beforeExplain(q, board);
    function render(labels, mark) { draw(board, name, s, done ? null : pick, labels, mark); }
    function pick(m) {
      var mv = all.filter(function (x) { return x.move === m; })[0], ok = mv.v === top, what = g.describe(s, m);
      ctx.result(ok, what);
      tries++;
      if (ok) {
        done = true;
        draw(board, name, g.play(s, m), null, null, m);     // show the position after the learner's move
        ctx.feedback(true, null);
        var note = U.el("p", "gm-status", "Right: " + what + ". With best play from here you " + outcomeText(mv.v, mv.d).replace(/^wins/, "win").replace(/^draws/, "draw").replace(/^loses/, "lose") + ".");
        U.beforeExplain(q, note);
        return;
      }
      var msg = what.charAt(0).toUpperCase() + what.slice(1) + " " + (mv.v < 0 ? "loses: the opponent can now force a win" : "only draws; this position is a win") + ".";
      if (tries >= 2) { msg += " Moves that keep the " + (top > 0 ? "win" : "draw") + " are marked W" + (top > 0 ? "" : "/D") + "."; render(hintLabels(name, s)); }
      else if (q.dataset.hint) msg += " Hint: " + q.dataset.hint;
      ctx.feedback(false, msg);
    }
    render();
    document.addEventListener("lp:event", function (e) {
      var ev = e.detail;
      if (ev.item === ctx.id && (ev.type === "reveal" || ev.kind === "skip") && !done) { done = true; render(hintLabels(name, s)); }
    });
  }

  if (window.LP && LP.register) {
    LP.register({ type: "game", selector: ".lp-game", scored: false, init: initPlay });
    LP.register({ type: "game-move", init: initMove });
  } else {
    var init = function () { document.querySelectorAll(".lp-game").forEach(initPlay); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
