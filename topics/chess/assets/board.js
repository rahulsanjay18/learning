// Static chess diagram from a FEN string. No dependencies.
// Usage in HTML: <div class="board-wrap" data-fen="..." data-hl="e5 c6" data-arrows="f3-e5" data-caption="White to move"></div>
// then include this script; every .board-wrap[data-fen] is rendered on load.
(function () {
  var GLYPH = { k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟" };
  var VS15 = "︎"; // ask for text (not emoji) presentation
  var FILES = "abcdefgh";

  function sqIndex(name) { // "e5" -> {file:4, rank:4} (rank 0 = rank 1)
    return { file: FILES.indexOf(name[0]), rank: parseInt(name[1], 10) - 1 };
  }

  function parsePlacement(fen) {
    var rows = fen.split(" ")[0].split("/"), grid = [];
    for (var r = 0; r < 8; r++) {
      var row = [];
      for (var i = 0; i < rows[r].length; i++) {
        var c = rows[r][i];
        if (/\d/.test(c)) for (var k = 0; k < +c; k++) row.push(null);
        else row.push(c);
      }
      grid.push(row); // grid[0] is rank 8
    }
    return grid;
  }

  function render(wrap) {
    var fen = wrap.getAttribute("data-fen");
    var flip = wrap.getAttribute("data-flip") === "true";
    var hl = (wrap.getAttribute("data-hl") || "").split(/\s+/).filter(Boolean);
    var arrows = (wrap.getAttribute("data-arrows") || "").split(/\s+/).filter(Boolean);
    var grid = parsePlacement(fen);
    var board = document.createElement("div");
    board.className = "board";
    board.setAttribute("role", "img");
    board.setAttribute("aria-label", "Chess position " + fen);

    for (var vr = 0; vr < 8; vr++) {
      for (var vf = 0; vf < 8; vf++) {
        var rankIdx = flip ? vr : 7 - vr; // 0-based rank shown in this visual row
        var fileIdx = flip ? 7 - vf : vf;
        var name = FILES[fileIdx] + (rankIdx + 1);
        var sq = document.createElement("div");
        sq.className = "sq " + ((fileIdx + rankIdx) % 2 === 1 ? "l" : "d") + (hl.indexOf(name) >= 0 ? " hl" : "");
        var p = grid[7 - rankIdx][fileIdx];
        if (p) {
          var span = document.createElement("span");
          span.className = "pc " + (p === p.toUpperCase() ? "w" : "b");
          span.textContent = GLYPH[p.toLowerCase()] + VS15;
          sq.appendChild(span);
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

    wrap.innerHTML = "";
    wrap.appendChild(board);
    var cap = wrap.getAttribute("data-caption");
    if (cap) { var c = document.createElement("div"); c.className = "board-caption"; c.textContent = cap; wrap.appendChild(c); }
  }

  window.ChessBoard = { render: render };
  function init() { document.querySelectorAll(".board-wrap[data-fen]").forEach(render); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
