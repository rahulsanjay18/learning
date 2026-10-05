// Chess plugin: static diagrams + "find the move" quizzes. Load after assets/lp.js; style: assets/plugins/chess.css.
// Static diagram: <div class="board-wrap" data-fen="..." data-hl="e5 c6" data-arrows="f3-e5" data-caption="White to move" [data-flip="true"]></div>
// Find the move:  <div class="quiz" data-type="chess-move" data-fen="..." data-answer="f3e5|Nxe5" [data-flip="true"] [data-hint="..."]>
//                   <p class="prompt">White to move: win material.</p><div class="explain" hidden>...</div></div>
//   Click a piece, then its destination (or type the move). Answers may be UCI (f3e5, e7e8q) or SAN (Nxe5); several separated by "|".
//   Legality is checked with chess.js (assets/vendor/chess.js, loaded on first use); if that fails to load, only UCI answers can be matched.
(function () {
  "use strict";
  var GLYPH = { k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟" };
  var VS15 = "︎"; // ask for text (not emoji) presentation
  var FILES = "abcdefgh";
  var CHESS_JS = new URL("../vendor/chess.js", document.currentScript ? document.currentScript.src : location.href).href;
  var chessLib = null;
  function loadChess() {
    if (!chessLib) chessLib = import(CHESS_JS).then(function (m) { return m.Chess; }).catch(function () { return null; });
    return chessLib;
  }

  function sqIndex(name) { return { file: FILES.indexOf(name[0]), rank: parseInt(name[1], 10) - 1 }; }

  function parsePlacement(fen) {
    var rows = fen.split(" ")[0].split("/"), grid = [];
    for (var r = 0; r < 8; r++) {
      var row = [];
      for (var i = 0; i < rows[r].length; i++) {
        var c = rows[r][i];
        if (/\d/.test(c)) for (var k = 0; k < +c; k++) row.push(null); else row.push(c);
      }
      grid.push(row); // grid[0] is rank 8
    }
    return grid;
  }

  // Builds the board element. Squares carry data-sq="e4".
  function buildBoard(fen, opts) {
    opts = opts || {};
    var flip = !!opts.flip, hl = opts.hl || [], arrows = opts.arrows || [];
    var grid = parsePlacement(fen);
    var board = document.createElement("div");
    board.className = "board";
    board.setAttribute("role", opts.interactive ? "group" : "img");
    board.setAttribute("aria-label", "Chess position " + fen);
    for (var vr = 0; vr < 8; vr++) {
      for (var vf = 0; vf < 8; vf++) {
        var rankIdx = flip ? vr : 7 - vr, fileIdx = flip ? 7 - vf : vf;
        var name = FILES[fileIdx] + (rankIdx + 1);
        var sq = document.createElement("div");
        sq.className = "sq " + ((fileIdx + rankIdx) % 2 === 1 ? "l" : "d") + (hl.indexOf(name) >= 0 ? " hl" : "");
        sq.dataset.sq = name;
        var p = grid[7 - rankIdx][fileIdx];
        if (p) {
          var span = document.createElement("span");
          span.className = "pc " + (p === p.toUpperCase() ? "w" : "b");
          span.textContent = GLYPH[p.toLowerCase()] + VS15;
          sq.appendChild(span);
          sq.dataset.pc = p;
        }
        if (vr === 7) { var f = document.createElement("span"); f.className = "coord file"; f.textContent = FILES[fileIdx]; sq.appendChild(f); }
        if (vf === 0) { var r = document.createElement("span"); r.className = "coord rank"; r.textContent = rankIdx + 1; sq.appendChild(r); }
        board.appendChild(sq);
      }
    }
    if (arrows.length) {
      var ns = "http://www.w3.org/2000/svg";
      var svg = document.createElementNS(ns, "svg");
      svg.setAttribute("class", "arrows");
      svg.setAttribute("viewBox", "0 0 8 8");
      var defs = document.createElementNS(ns, "defs");
      defs.innerHTML = '<marker id="ah" viewBox="0 0 4 4" refX="2" refY="2" markerWidth="2.2" markerHeight="2.2" orient="auto">' +
        '<path d="M0,0 L4,2 L0,4 z" fill="var(--arrow)"/></marker>';
      svg.appendChild(defs);
      arrows.forEach(function (a) {
        var parts = a.split("-"), s = sqIndex(parts[0]), t = sqIndex(parts[1]);
        function xy(q) { var x = flip ? 7 - q.file : q.file, y = flip ? q.rank : 7 - q.rank; return [x + .5, y + .5]; }
        var p0 = xy(s), p1 = xy(t), dx = p1[0] - p0[0], dy = p1[1] - p0[1], len = Math.hypot(dx, dy);
        var line = document.createElementNS(ns, "line");
        line.setAttribute("x1", p0[0]); line.setAttribute("y1", p0[1]);
        line.setAttribute("x2", p1[0] - dx / len * .35); line.setAttribute("y2", p1[1] - dy / len * .35);
        line.setAttribute("stroke", "var(--arrow)"); line.setAttribute("stroke-width", ".14");
        line.setAttribute("stroke-linecap", "round"); line.setAttribute("marker-end", "url(#ah)");
        svg.appendChild(line);
      });
      board.appendChild(svg);
    }
    return board;
  }

  function words(s) { return (s || "").split(/\s+/).filter(Boolean); }

  function render(wrap) {
    var board = buildBoard(wrap.getAttribute("data-fen"), {
      flip: wrap.getAttribute("data-flip") === "true", hl: words(wrap.getAttribute("data-hl")), arrows: words(wrap.getAttribute("data-arrows"))
    });
    wrap.innerHTML = "";
    wrap.appendChild(board);
    var cap = wrap.getAttribute("data-caption");
    if (cap) { var c = document.createElement("div"); c.className = "board-caption"; c.textContent = cap; wrap.appendChild(c); }
  }
  window.ChessBoard = { render: render, build: buildBoard };

  function cleanSan(s) { return s.replace(/[+#!?]/g, "").replace(/=/, "").toLowerCase(); }

  function initMove(q, ctx) {
    var U = LP.util, fen = q.dataset.fen, flip = q.dataset.flip === "true";
    var accepted = U.split(q.dataset.answer), toMove = (fen.split(" ")[1] || "w");
    var wrap = U.el("div", "board-wrap interactive"), selected = null, locked = false;
    function draw(f, hl) {
      wrap.innerHTML = "";
      wrap.appendChild(buildBoard(f, { flip: flip, hl: hl || [], interactive: true }));
    }
    draw(fen);

    var row = U.el("div", "choices"), input = U.el("input"), go = U.el("button", null, "Play");
    input.type = "text"; input.placeholder = "or type: Nxe5"; input.setAttribute("aria-label", "type your move");
    input.style.width = "9rem";
    row.appendChild(input); row.appendChild(go);
    U.beforeExplain(q, wrap); U.beforeExplain(q, row);

    function isAccepted(uci, san) {
      return accepted.some(function (a) {
        if (/^[a-h][1-8][a-h][1-8][qrbn]?$/i.test(a)) return a.toLowerCase() === uci || (a.length === 4 && a.toLowerCase() === uci.slice(0, 4));
        return san && cleanSan(a) === cleanSan(san);
      });
    }

    function attempt(from, to, typed) {
      if (locked) return;
      loadChess().then(function (Chess) {
        var uci, san = null, after = null;
        if (Chess) {
          var game = new Chess(fen), mv = null;
          try { mv = typed ? game.move(typed, { strict: false }) : game.move({ from: from, to: to, promotion: "q" }); } catch (e) { mv = null; }
          if (!mv) { ctx.feedback(false, "That move isn't legal here."); draw(fen); return; }
          uci = mv.from + mv.to + (mv.promotion || ""); san = mv.san; after = game.fen();
        } else {
          if (typed && !/^[a-h][1-8][a-h][1-8][qrbn]?$/i.test(typed)) { ctx.feedback(false, "Type the move as from-square + to-square, like f3e5."); return; }
          uci = typed ? typed.toLowerCase() : from + to;
        }
        var ok = isAccepted(uci, san);
        ctx.result(ok, san || uci);
        if (ok) {
          locked = true; go.disabled = true; input.disabled = true;
          draw(after || moveGlyph(fen, uci), [uci.slice(0, 2), uci.slice(2, 4)]);
        } else {
          draw(fen, [uci.slice(0, 2), uci.slice(2, 4)]);
        }
        ctx.feedback(ok);
      });
    }

    wrap.addEventListener("click", function (e) {
      var sq = e.target.closest && e.target.closest(".sq");
      if (!sq || locked) return;
      var pc = sq.dataset.pc, own = pc && ((pc === pc.toUpperCase()) === (toMove === "w"));
      if (own) {
        wrap.querySelectorAll(".sq.sel").forEach(function (x) { x.classList.remove("sel"); });
        sq.classList.add("sel"); selected = sq.dataset.sq; return;
      }
      if (selected) { var from = selected; selected = null; attempt(from, sq.dataset.sq); }
    });
    function typedMove() { var t = input.value.trim(); if (t) attempt(null, null, t); }
    go.addEventListener("click", typedMove);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") typedMove(); });
    loadChess(); // start fetching early
  }

  // Fallback board update without chess.js: just move the piece.
  function moveGlyph(fen, uci) {
    var g = parsePlacement(fen), f = sqIndex(uci.slice(0, 2)), t = sqIndex(uci.slice(2, 4));
    var p = g[7 - f.rank][f.file]; g[7 - f.rank][f.file] = null; g[7 - t.rank][t.file] = p;
    return g.map(function (row) {
      var s = "", n = 0;
      row.forEach(function (c) { if (c) { if (n) s += n; n = 0; s += c; } else n++; });
      return s + (n || "");
    }).join("/");
  }

  function init() { document.querySelectorAll(".board-wrap[data-fen]").forEach(render); }
  if (window.LP && LP.register) {
    LP.register({ type: "chess-board", selector: ".board-wrap[data-fen]", scored: false, init: render });
    LP.register({ type: "chess-move", init: initMove });
  } else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
