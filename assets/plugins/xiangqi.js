// Xiangqi (Chinese chess) plugin: diagrams, a legal-move sandbox, and "find the move" quizzes. Load after assets/lp.js;
// style: assets/plugins/xiangqi.css. Own rules engine, checked against published perft counts (node scripts/test_xiangqi_shogi.js).
//
// Position: FEN, rows from Black's back rank (rank 9) down to Red's (rank 0), then the side to move:
//   "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w"  (the start; also the default)
//   Uppercase = Red (moves first, "w"), lowercase = Black ("b"). K general, A advisor, E elephant (B accepted), H horse
//   (N accepted), R chariot, C cannon, P soldier.
// Squares: files a–i left to right from Red's side, ranks 0–9 from Red's back rank. Moves: "h2e2" (from, to), "h2e2|b2e2" for several.
// Rules: the generals may never face each other on an open file ("flying general"); a side with no legal move loses (checkmate
// and stalemate both lose). Repetition rules (perpetual check/chase) are not enforced.
//
// Diagram:  <div class="xq-board" data-fen="…" [data-hl="e2 e9"] [data-arrows="h2-e2"] [data-flip="true"]
//                [data-play="true"] [data-labels="latin"] [data-caption="…"]></div>
//   data-play="true": a sandbox. Click a piece to see its legal moves, then a destination; both sides move in turn. Undo, Start over.
//   data-labels="latin": letters (K A E H R C P) instead of the characters 帥仕相傌俥炮兵 / 將士象馬車砲卒.
// Quiz:     <div class="quiz" data-type="xiangqi-move" data-id="…" data-fen="…" data-answer="h2e2|b2e2" [data-flip] [data-labels] [data-hint]>
//             <p class="prompt">Red to move: …</p><div class="explain" hidden>…</div></div>
//   Only legal moves can be played; any listed answer is right. node scripts/test_xiangqi_shogi.js checks every answer is legal.
(function () {
  "use strict";
  var FILES = "abcdefghi";
  var START = "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w";

  // ---------- engine: board[rank * 9 + file], rank 0 = Red's back rank ----------
  function norm(ch) { var m = { B: "E", b: "e", N: "H", n: "h" }; return m[ch] || ch; }
  function colorOf(p) { return p === p.toUpperCase() ? "w" : "b"; }
  function parse(fen) {
    var parts = String(fen || START).trim().split(/\s+/), rows = parts[0].split("/");
    if (rows.length !== 10) throw new Error("xiangqi FEN needs 10 rows");
    var board = new Array(90).fill(null);
    rows.forEach(function (row, i) {
      var rank = 9 - i, f = 0;
      for (var k = 0; k < row.length; k++) {
        var ch = row[k];
        if (/\d/.test(ch)) { f += +ch; continue; }
        var p = norm(ch);
        if ("KAEHRCPkaehrcp".indexOf(p) < 0) throw new Error("xiangqi FEN: unknown piece " + ch);
        if (f > 8) throw new Error("xiangqi FEN: row " + (i + 1) + " too long");
        board[rank * 9 + f] = p; f++;
      }
      if (f !== 9) throw new Error("xiangqi FEN: row " + (i + 1) + " has " + f + " files, not 9");
    });
    var pos = { board: board, turn: parts[1] === "b" ? "b" : "w" };
    if (findKing(pos.board, "w") < 0 || findKing(pos.board, "b") < 0) throw new Error("xiangqi FEN: each side needs a general");
    return pos;
  }
  function toFen(pos) {
    var rows = [];
    for (var rank = 9; rank >= 0; rank--) {
      var s = "", e = 0;
      for (var f = 0; f < 9; f++) { var p = pos.board[rank * 9 + f]; if (!p) e++; else { if (e) s += e; e = 0; s += p; } }
      rows.push(s + (e ? e : ""));
    }
    return rows.join("/") + " " + pos.turn;
  }
  function sqName(i) { return FILES[i % 9] + Math.floor(i / 9); }
  function sqIndex(n) { var f = FILES.indexOf(n[0]), r = parseInt(n.slice(1), 10); return f < 0 || !(r >= 0 && r <= 9) ? -1 : r * 9 + f; }
  function inPalace(r, f, c) { return f >= 3 && f <= 5 && (c === "w" ? r <= 2 : r >= 7); }
  function findKing(b, c) { var k = c === "w" ? "K" : "k"; for (var i = 0; i < 90; i++) if (b[i] === k) return i; return -1; }
  var ORTH = [[1, 0], [-1, 0], [0, 1], [0, -1]], DIAG = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
  // horse: [leg dr, leg df, target dr, target df]
  var HORSE = [[1, 0, 2, 1], [1, 0, 2, -1], [-1, 0, -2, 1], [-1, 0, -2, -1], [0, 1, 1, 2], [0, 1, -1, 2], [0, -1, 1, -2], [0, -1, -1, -2]];

  function pseudo(b, from) {
    var p = b[from], c = colorOf(p), t = p.toUpperCase(), r = Math.floor(from / 9), f = from % 9, out = [];
    function add(rr, ff) {
      if (rr < 0 || rr > 9 || ff < 0 || ff > 8) return;
      var q = b[rr * 9 + ff];
      if (!q || colorOf(q) !== c) out.push(rr * 9 + ff);
    }
    if (t === "K") ORTH.forEach(function (d) { if (inPalace(r + d[0], f + d[1], c)) add(r + d[0], f + d[1]); });
    else if (t === "A") DIAG.forEach(function (d) { if (inPalace(r + d[0], f + d[1], c)) add(r + d[0], f + d[1]); });
    else if (t === "E") DIAG.forEach(function (d) {
      var rr = r + 2 * d[0], ff = f + 2 * d[1];
      if (rr < 0 || rr > 9 || ff < 0 || ff > 8) return;
      if (c === "w" ? rr > 4 : rr < 5) return;                       // elephants never cross the river
      if (!b[(r + d[0]) * 9 + f + d[1]]) add(rr, ff);                // blocked at the "eye"
    });
    else if (t === "H") HORSE.forEach(function (h) {
      var lr = r + h[0], lf = f + h[1];
      if (lr < 0 || lr > 9 || lf < 0 || lf > 8 || b[lr * 9 + lf]) return;   // hobbled at the leg
      add(r + h[2], f + h[3]);
    });
    else if (t === "R" || t === "C") ORTH.forEach(function (d) {
      var rr = r + d[0], ff = f + d[1], screen = false;
      while (rr >= 0 && rr <= 9 && ff >= 0 && ff <= 8) {
        var q = b[rr * 9 + ff];
        if (t === "R") { if (!q) out.push(rr * 9 + ff); else { if (colorOf(q) !== c) out.push(rr * 9 + ff); break; } }
        else if (!screen) { if (!q) out.push(rr * 9 + ff); else screen = true; }
        else if (q) { if (colorOf(q) !== c) out.push(rr * 9 + ff); break; }
        rr += d[0]; ff += d[1];
      }
    });
    else if (t === "P") {
      var fwd = c === "w" ? 1 : -1, crossed = c === "w" ? r >= 5 : r <= 4;
      add(r + fwd, f);
      if (crossed) { add(r, f - 1); add(r, f + 1); }
    }
    return out;
  }

  // Is square sq attacked by side `by`? (Also catches the generals facing each other.)
  function attacked(b, sq, by) {
    var r = Math.floor(sq / 9), f = sq % 9;
    for (var k = 0; k < 4; k++) {
      var d = ORTH[k], rr = r + d[0], ff = f + d[1], seen = 0;
      while (rr >= 0 && rr <= 9 && ff >= 0 && ff <= 8) {
        var q = b[rr * 9 + ff];
        if (q) {
          var mine = colorOf(q) === by, t = q.toUpperCase();
          if (seen === 0) {
            if (mine && (t === "R" || (t === "K" && d[1] === 0))) return true;
            seen = 1;
          } else { if (mine && t === "C") return true; break; }
        }
        rr += d[0]; ff += d[1];
      }
    }
    for (var h = 0; h < 8; h++) {                // a horse at sq - target, whose leg is free
      var H = HORSE[h], hr = r - H[2], hf = f - H[3];
      if (hr < 0 || hr > 9 || hf < 0 || hf > 8) continue;
      var hp = b[hr * 9 + hf];
      if (!hp || hp.toUpperCase() !== "H" || colorOf(hp) !== by) continue;
      if (!b[(hr + H[0]) * 9 + hf + H[1]]) return true;
    }
    var P = by === "w" ? "P" : "p", back = by === "w" ? -1 : 1;
    if (r + back >= 0 && r + back <= 9 && b[(r + back) * 9 + f] === P) return true;        // soldier straight ahead
    var sideOk = by === "w" ? r >= 5 : r <= 4;                                             // sideways after crossing
    if (sideOk && ((f > 0 && b[sq - 1] === P) || (f < 8 && b[sq + 1] === P))) return true;
    return false;
  }
  function inCheck(pos, c) { return attacked(pos.board, findKing(pos.board, c), c === "w" ? "b" : "w"); }

  function legalMoves(pos, from) {
    var b = pos.board, c = pos.turn, out = [], them = c === "w" ? "b" : "w";
    for (var s = 0; s < 90; s++) {
      if (from != null && s !== from) continue;
      if (!b[s] || colorOf(b[s]) !== c) continue;
      var ts = pseudo(b, s);
      for (var i = 0; i < ts.length; i++) {
        var to = ts[i], cap = b[to];
        b[to] = b[s]; b[s] = null;
        var ok = !attacked(b, findKing(b, c), them);
        b[s] = b[to]; b[to] = cap;
        if (ok) out.push({ from: s, to: to, uci: sqName(s) + sqName(to) });
      }
    }
    return out;
  }
  function play(pos, mv) {
    var b = pos.board.slice(); b[mv.to] = b[mv.from]; b[mv.from] = null;
    return { board: b, turn: pos.turn === "w" ? "b" : "w" };
  }
  function perft(pos, depth) {
    if (depth === 0) return 1;
    var ms = legalMoves(pos), n = 0;
    if (depth === 1) return ms.length;
    var b = pos.board;
    for (var i = 0; i < ms.length; i++) {
      var m = ms[i], cap = b[m.to];
      b[m.to] = b[m.from]; b[m.from] = null; pos.turn = pos.turn === "w" ? "b" : "w";
      n += perft(pos, depth - 1);
      pos.turn = pos.turn === "w" ? "b" : "w"; b[m.from] = b[m.to]; b[m.to] = cap;
    }
    return n;
  }
  function status(pos) {
    var any = legalMoves(pos).length > 0, chk = inCheck(pos, pos.turn), side = pos.turn === "w" ? "Red" : "Black", other = pos.turn === "w" ? "Black" : "Red";
    if (!any) return { over: true, text: (chk ? "Checkmate" : "No legal move (stalemate)") + ": " + other + " wins." };
    return { over: false, check: chk, text: side + " to move" + (chk ? ": check!" : ".") };
  }
  function findMove(pos, uci) {
    uci = String(uci || "").trim().toLowerCase();
    return legalMoves(pos).filter(function (m) { return m.uci === uci; })[0] || null;
  }

  var api = { START: START, parse: parse, toFen: toFen, legalMoves: legalMoves, play: play, perft: perft, inCheck: inCheck,
    status: status, findMove: findMove, sqName: sqName, sqIndex: sqIndex };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---------- drawing ----------
  var HANZI = { K: "帥", A: "仕", E: "相", H: "傌", R: "俥", C: "炮", P: "兵", k: "將", a: "士", e: "象", h: "馬", r: "車", c: "砲", p: "卒" };
  var NAMES = { K: "general", A: "advisor", E: "elephant", H: "horse", R: "chariot", C: "cannon", P: "soldier" };
  var SVGNS = "http://www.w3.org/2000/svg";
  function svg(tag, a) { var e = document.createElementNS(SVGNS, tag); for (var k in a) e.setAttribute(k, a[k]); return e; }
  var S = 40, M = 32;   // spacing, margin

  // opts: {flip, labels, hl: [sq], arrows: [[from,to]], sel, targets: [sq], last: {from,to}, onClick(sq)}
  function draw(box, pos, opts) {
    opts = opts || {};
    var flip = !!opts.flip;
    function xy(sq) { var f = sq % 9, r = Math.floor(sq / 9); if (flip) { f = 8 - f; r = 9 - r; } return [M + f * S, M + (9 - r) * S]; }
    var W = 2 * M + 8 * S, H = 2 * M + 9 * S + 12;   // extra room below for the file letters
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, "class": "xq-svg", role: "img",
      "aria-label": "Xiangqi position " + toFen(pos) });
    var g = svg("g", { "class": "xq-lines" });
    for (var r = 0; r < 10; r++) g.appendChild(svg("line", { x1: M, y1: M + r * S, x2: M + 8 * S, y2: M + r * S }));
    for (var f = 0; f < 9; f++) {
      if (f === 0 || f === 8) g.appendChild(svg("line", { x1: M + f * S, y1: M, x2: M + f * S, y2: M + 9 * S }));
      else { g.appendChild(svg("line", { x1: M + f * S, y1: M, x2: M + f * S, y2: M + 4 * S })); g.appendChild(svg("line", { x1: M + f * S, y1: M + 5 * S, x2: M + f * S, y2: M + 9 * S })); }
    }
    [[0, 2], [7, 9]].forEach(function (pr) {      // palace diagonals (symmetric, so flipping doesn't matter)
      var y0 = M + (9 - pr[1]) * S, y1 = M + (9 - pr[0]) * S;
      g.appendChild(svg("line", { x1: M + 3 * S, y1: y0, x2: M + 5 * S, y2: y1 }));
      g.appendChild(svg("line", { x1: M + 5 * S, y1: y0, x2: M + 3 * S, y2: y1 }));
    });
    root.appendChild(g);
    var river = svg("text", { x: W / 2, y: M + 4.5 * S + 5, "class": "xq-river", "text-anchor": "middle" }); river.textContent = "river"; root.appendChild(river);
    for (var i = 0; i < 9; i++) {                  // coordinates
      var fl = flip ? 8 - i : i, t = svg("text", { x: M + i * S, y: H - 4, "class": "xq-coord", "text-anchor": "middle" }); t.textContent = FILES[fl]; root.appendChild(t);
    }
    for (var j = 0; j < 10; j++) {
      var rk = flip ? j : 9 - j, t2 = svg("text", { x: 9, y: M + j * S + 4, "class": "xq-coord", "text-anchor": "middle" }); t2.textContent = rk; root.appendChild(t2);
    }
    function ring(sq, cls) { var p = xy(sq); root.appendChild(svg("circle", { cx: p[0], cy: p[1], r: S * 0.47, "class": cls })); }
    (opts.hl || []).forEach(function (sq) { ring(sq, "xq-hl"); });
    if (opts.last) { ring(opts.last.from, "xq-last"); ring(opts.last.to, "xq-last"); }
    pos.board.forEach(function (p, sq) {
      var xyp = xy(sq);
      var hit = svg("g", { "class": "xq-pt" + (opts.onClick ? " live" : ""), "data-sq": sqName(sq) });
      hit.appendChild(svg("circle", { cx: xyp[0], cy: xyp[1], r: S * 0.48, "class": "xq-hit" }));
      if (p) {
        var c = colorOf(p);
        hit.appendChild(svg("circle", { cx: xyp[0], cy: xyp[1], r: S * 0.42, "class": "xq-pc " + (c === "w" ? "red" : "black") + (opts.sel === sq ? " sel" : "") }));
        var tx = svg("text", { x: xyp[0], y: xyp[1] + (opts.labels === "latin" ? 6 : 7), "class": "xq-ch " + (c === "w" ? "red" : "black") + (opts.labels === "latin" ? " latin" : ""), "text-anchor": "middle" });
        tx.textContent = opts.labels === "latin" ? p.toUpperCase() : HANZI[p];
        hit.appendChild(tx);
        var ti = svg("title", {}); ti.textContent = (c === "w" ? "Red " : "Black ") + NAMES[p.toUpperCase()] + " on " + sqName(sq); hit.appendChild(ti);
      }
      if (opts.targets && opts.targets.indexOf(sq) >= 0) hit.appendChild(svg("circle", { cx: xyp[0], cy: xyp[1], r: p ? S * 0.46 : S * 0.12, "class": p ? "xq-cap" : "xq-dot" }));
      if (opts.onClick) hit.addEventListener("click", function () { opts.onClick(sq); });
      root.appendChild(hit);
    });
    (opts.arrows || []).forEach(function (a) {
      var p = xy(a[0]), q = xy(a[1]), dx = q[0] - p[0], dy = q[1] - p[1], L = Math.sqrt(dx * dx + dy * dy) || 1;
      var ex = q[0] - dx / L * 10, ey = q[1] - dy / L * 10;
      root.appendChild(svg("line", { x1: p[0], y1: p[1], x2: ex, y2: ey, "class": "xq-arrow" }));
      var nx = -dy / L, ny = dx / L;
      root.appendChild(svg("polygon", { points: [q[0], q[1], ex + nx * 6, ey + ny * 6, ex - nx * 6, ey - ny * 6].join(" "), "class": "xq-arrowhead" }));
    });
    box.textContent = ""; box.appendChild(root);
  }
  function listSq(s) { return String(s || "").split(/[\s,]+/).filter(Boolean).map(sqIndex).filter(function (i) { return i >= 0; }); }
  function listArrows(s) { return String(s || "").split(/[\s,]+/).filter(Boolean).map(function (a) { var p = a.split("-"); return [sqIndex(p[0]), sqIndex(p[1])]; }).filter(function (a) { return a[0] >= 0 && a[1] >= 0; }); }
  function legend(labels) {
    return labels === "latin" ? "K general · A advisor · E elephant · H horse · R chariot · C cannon · P soldier. Red moves first."
      : "帥將 general · 仕士 advisor · 相象 elephant · 傌馬 horse · 俥車 chariot · 炮砲 cannon · 兵卒 soldier. Red moves first.";
  }

  // Click-to-move controller shared by the sandbox and the quiz. onMove(move) returns false to refuse.
  function clicker(box, getPos, opts, onMove) {
    var sel = null;
    function render(extra) {
      var pos = getPos(), targets = sel != null ? legalMoves(pos, sel).map(function (m) { return m.to; }) : [];
      draw(box, pos, Object.assign({}, opts, extra || {}, { sel: sel, targets: targets, onClick: opts.locked && opts.locked() ? null : click }));
    }
    function click(sq) {
      var pos = getPos(), p = pos.board[sq];
      if (sel != null) {
        var m = legalMoves(pos, sel).filter(function (x) { return x.to === sq; })[0];
        if (m) { sel = null; onMove(m); return; }
      }
      sel = p && colorOf(p) === pos.turn && sel !== sq ? sq : null;
      render();
    }
    return render;
  }

  function initDiagram(el) {
    var d = el.dataset, start = parse(d.fen || START), opts = { flip: d.flip === "true", labels: d.labels, hl: listSq(d.hl), arrows: listArrows(d.arrows) };
    el.textContent = "";
    var box = document.createElement("div"); box.className = "xq-box"; el.appendChild(box);
    var cap = document.createElement("div"); cap.className = "xq-caption";
    if (d.play !== "true") {
      draw(box, start, opts);
      if (d.caption) { cap.textContent = d.caption; el.appendChild(cap); }
      return;
    }
    var hist = [start], last = null, st = document.createElement("p"); st.className = "xq-status";
    var row = document.createElement("div"); row.className = "xq-controls";
    var undo = document.createElement("button"); undo.type = "button"; undo.textContent = "Undo";
    var reset = document.createElement("button"); reset.type = "button"; reset.textContent = "Start over";
    row.appendChild(undo); row.appendChild(reset);
    var leg = document.createElement("p"); leg.className = "xq-legend"; leg.textContent = legend(d.labels);
    el.insertBefore(leg, box); el.appendChild(st); el.appendChild(row);
    if (d.caption) { cap.textContent = d.caption; el.appendChild(cap); }
    opts.hl = [];
    var cur = function () { return hist[hist.length - 1]; };
    var render = clicker(box, cur, opts, function (m) { hist.push(play(cur(), m)); last = m; update(); });
    function update() { var s = status(cur()); st.textContent = s.text; render({ last: last }); }
    undo.addEventListener("click", function () { if (hist.length > 1) { hist.pop(); last = null; update(); } });
    reset.addEventListener("click", function () { hist = [start]; last = null; update(); });
    update();
  }

  function initMove(q, ctx) {
    var d = q.dataset, pos = parse(d.fen || START), U = LP.util;
    var answers = String(d.answer || "").split("|").map(function (s) { return s.trim().toLowerCase(); }).filter(Boolean);
    if (!answers.length) throw new Error("xiangqi-move needs data-answer");
    answers.forEach(function (a) { if (!findMove(pos, a)) throw new Error("xiangqi-move: answer " + a + " is not legal here"); });
    var done = false, played = null;
    var leg = U.el("p", "xq-legend", legend(d.labels)), box = U.el("div", "xq-box");
    U.beforeExplain(q, leg); U.beforeExplain(q, box);
    var opts = { flip: d.flip === "true", labels: d.labels, hl: listSq(d.hl), locked: function () { return done; } };
    var render = clicker(box, function () { return played ? play(pos, played) : pos; }, opts, function (m) {
      var ok = answers.indexOf(m.uci) >= 0;
      ctx.result(ok, m.uci);
      if (ok) { done = true; played = m; render({ last: m }); ctx.feedback(true, null); }
      else { render({ last: null }); ctx.feedback(false, sqName(m.from) + "–" + sqName(m.to) + " is legal, but not the move we're after." + (d.hint ? " Hint: " + d.hint : "")); }
    });
    render();
    document.addEventListener("lp:event", function (e) {
      var ev = e.detail;
      if (ev.item === ctx.id && (ev.type === "reveal" || ev.kind === "skip") && !done) {
        done = true; var m = findMove(pos, answers[0]); render({ arrows: [[m.from, m.to]] });
      }
    });
  }

  if (window.LP && LP.register) {
    LP.register({ type: "xiangqi", selector: ".xq-board", scored: false, init: initDiagram });
    LP.register({ type: "xiangqi-move", init: initMove });
  } else {
    var init = function () { document.querySelectorAll(".xq-board").forEach(initDiagram); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
