// Go (weiqi/baduk) plugin: board diagrams + "play the move" problems. Load after assets/lp.js; style: assets/plugins/go.css.
// Coordinates: columns A–T without I, rows 1–19 counted from the bottom (as on most Go servers), e.g. "D4", "Q16".
//
// Diagram:  <div class="go-board" data-size="9" data-black="C3 D4" data-white="E5 F5" [data-marks="D4 E5"] [data-labels="C5:a D6:b"]
//                [data-view="A1:J10"] [data-coords="false"] data-caption="..."></div>
//   data-marks draws triangles; data-labels writes letters/numbers on points; data-view crops to a rectangle (corner problems on 19×19).
// Problem:  <div class="quiz" data-type="go-move" data-id="..." data-size="9" data-black="..." data-white="..." [data-to-play="B"]
//                data-answer="E4|F3">               one move; any listed point is right
//           or data-solution="E7 E4 E3">            a line: learner's moves alternate with scripted replies (here: B E7, W E4, B E3)
//             <p class="prompt">Black to play: capture.</p><div class="explain" hidden>...</div></div>
//   Illegal moves (occupied, suicide, retaking a ko) are refused and don't count. The first wrong move counts as a miss.
// Rules are in GoRules (exported for Node: node scripts/test_go_rules.js).
(function () {
  "use strict";
  var COLS = "ABCDEFGHJKLMNOPQRST";

  // ---------- rules ----------
  function GoRules(size) { this.size = size; this.grid = {}; this.ko = null; }
  GoRules.parse = function (name, size) {
    var m = /^([A-HJ-T])(\d{1,2})$/i.exec(String(name).trim());
    if (!m) return null;
    var x = COLS.indexOf(m[1].toUpperCase()), y = parseInt(m[2], 10) - 1;
    return x < size && y >= 0 && y < size ? { x: x, y: y } : null;
  };
  GoRules.label = function (p) { return COLS[p.x] + (p.y + 1); };
  GoRules.prototype.key = function (p) { return p.x + "," + p.y; };
  GoRules.prototype.get = function (p) { return this.grid[this.key(p)] || null; };
  GoRules.prototype.set = function (p, c) { if (c) this.grid[this.key(p)] = c; else delete this.grid[this.key(p)]; };
  GoRules.prototype.neighbors = function (p) {
    var s = this.size;
    return [[1, 0], [-1, 0], [0, 1], [0, -1]].map(function (d) { return { x: p.x + d[0], y: p.y + d[1] }; })
      .filter(function (q) { return q.x >= 0 && q.y >= 0 && q.x < s && q.y < s; });
  };
  // The connected group containing p and its liberties.
  GoRules.prototype.group = function (p) {
    var color = this.get(p), stones = [], libs = {}, seen = {}, stack = [p], self = this;
    seen[this.key(p)] = 1;
    while (stack.length) {
      var q = stack.pop(); stones.push(q);
      this.neighbors(q).forEach(function (n) {
        var k = self.key(n), c = self.get(n);
        if (!c) libs[k] = n;
        else if (c === color && !seen[k]) { seen[k] = 1; stack.push(n); }
      });
    }
    return { color: color, stones: stones, liberties: Object.keys(libs).map(function (k) { return libs[k]; }) };
  };
  // Plays color ("B"/"W") at point p. Returns {ok, captured:[points], reason}.
  GoRules.prototype.play = function (color, p) {
    if (!p) return { ok: false, reason: "That isn't a point on this board." };
    if (this.get(p)) return { ok: false, reason: "That point is already taken." };
    if (this.ko && this.ko.x === p.x && this.ko.y === p.y) return { ok: false, reason: "Ko: you can't retake immediately. Play elsewhere first." };
    var other = color === "B" ? "W" : "B", self = this, captured = [];
    this.set(p, color);
    this.neighbors(p).forEach(function (n) {
      if (self.get(n) === other) {
        var g = self.group(n);
        if (!g.liberties.length) g.stones.forEach(function (s) { if (self.get(s)) { self.set(s, null); captured.push(s); } });
      }
    });
    var mine = this.group(p);
    if (!mine.liberties.length) { this.set(p, null); return { ok: false, reason: "Suicide: that stone would have no liberties." }; }
    this.ko = captured.length === 1 && mine.stones.length === 1 && mine.liberties.length === 1 ? captured[0] : null;
    return { ok: true, captured: captured };
  };
  GoRules.prototype.load = function (black, white) {
    var self = this;
    [["B", black], ["W", white]].forEach(function (cv) {
      (cv[1] || "").split(/\s+/).filter(Boolean).forEach(function (n) { var p = GoRules.parse(n, self.size); if (p) self.set(p, cv[0]); });
    });
    return this;
  };

  if (typeof module !== "undefined" && module.exports) { module.exports = GoRules; return; }
  window.GoRules = GoRules;

  // ---------- drawing (SVG, 1 unit = 1 grid step) ----------
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function stars(size) {
    if (size === 19) return [3, 9, 15].reduce(function (a, x) { return a.concat([3, 9, 15].map(function (y) { return [x, y]; })); }, []);
    if (size === 13) return [[3, 3], [3, 9], [9, 3], [9, 9], [6, 6]];
    if (size === 9) return [[2, 2], [2, 6], [6, 2], [6, 6], [4, 4]];
    return [];
  }
  function view(el, size) {
    var v = (el.dataset.view || "").split(":"), a = v[0] && GoRules.parse(v[0], size), b = v[1] && GoRules.parse(v[1], size);
    if (!a || !b) return { x0: 0, x1: size - 1, y0: 0, y1: size - 1 };
    return { x0: Math.min(a.x, b.x), x1: Math.max(a.x, b.x), y0: Math.min(a.y, b.y), y1: Math.max(a.y, b.y) };
  }
  function pairs(s) {
    var out = {};
    (s || "").split(/\s+/).filter(Boolean).forEach(function (t) { var i = t.indexOf(":"); if (i > 0) out[t.slice(0, i).toUpperCase()] = t.slice(i + 1); });
    return out;
  }

  // Draws the position in `rules` into `host`. opts: {marks:[names], labels:{name:text}, last:point, interactive}
  function draw(host, rules, el, opts) {
    opts = opts || {};
    var size = rules.size, v = view(el, size), coords = el.dataset.coords !== "false";
    var pad = coords ? 1.1 : 0.7, w = v.x1 - v.x0, h = v.y1 - v.y0;
    var X = function (x) { return x - v.x0 + pad; }, Y = function (y) { return v.y1 - y + 0.7; };
    var svg = svgEl("svg", { viewBox: "0 0 " + (w + pad + 0.7) + " " + (h + 0.7 + pad), "class": "go-svg", role: opts.interactive ? "group" : "img",
      "aria-label": "Go position, " + size + "×" + size });
    svg.appendChild(svgEl("rect", { x: 0, y: 0, width: w + pad + 0.7, height: h + 0.7 + pad, "class": "go-wood" }));
    var lines = svgEl("g", { "class": "go-lines" });
    // Lines stop at real board edges; at a crop edge they run half a step past it.
    var ext = function (atEdge) { return atEdge ? 0 : 0.5; };
    for (var x = v.x0; x <= v.x1; x++)
      lines.appendChild(svgEl("line", { x1: X(x), x2: X(x), y1: Y(v.y1) - ext(v.y1 === size - 1), y2: Y(v.y0) + ext(v.y0 === 0) }));
    for (var y = v.y0; y <= v.y1; y++)
      lines.appendChild(svgEl("line", { y1: Y(y), y2: Y(y), x1: X(v.x0) - ext(v.x0 === 0), x2: X(v.x1) + ext(v.x1 === size - 1) }));
    svg.appendChild(lines);
    stars(size).forEach(function (s) {
      if (s[0] >= v.x0 && s[0] <= v.x1 && s[1] >= v.y0 && s[1] <= v.y1) svg.appendChild(svgEl("circle", { cx: X(s[0]), cy: Y(s[1]), r: 0.1, "class": "go-star" }));
    });
    if (coords) {
      for (x = v.x0; x <= v.x1; x++) { var t = svgEl("text", { x: X(x), y: Y(v.y0) + 0.95, "class": "go-coord" }); t.textContent = COLS[x]; svg.appendChild(t); }
      for (y = v.y0; y <= v.y1; y++) { var u = svgEl("text", { x: 0.45, y: Y(y) + 0.13, "class": "go-coord" }); u.textContent = y + 1; svg.appendChild(u); }
    }
    for (x = v.x0; x <= v.x1; x++) for (y = v.y0; y <= v.y1; y++) {
      var p = { x: x, y: y }, c = rules.get(p), name = GoRules.label(p);
      if (c) svg.appendChild(svgEl("circle", { cx: X(x), cy: Y(y), r: 0.47, "class": "go-stone " + (c === "B" ? "b" : "w") }));
      var onDark = c === "B" ? " on-b" : "";
      if (opts.last && opts.last.x === x && opts.last.y === y) svg.appendChild(svgEl("circle", { cx: X(x), cy: Y(y), r: 0.2, "class": "go-last" + onDark }));
      if ((opts.marks || []).indexOf(name) >= 0)
        svg.appendChild(svgEl("path", { d: "M" + X(x) + "," + (Y(y) - 0.25) + " l0.22,0.38 h-0.44 z", "class": "go-mark" + onDark }));
      var label = (opts.labels || {})[name];
      if (label) {
        if (!c) svg.appendChild(svgEl("circle", { cx: X(x), cy: Y(y), r: 0.3, "class": "go-label-bg" }));
        var lt = svgEl("text", { x: X(x), y: Y(y) + 0.15, "class": "go-label" + onDark }); lt.textContent = label; svg.appendChild(lt);
      }
      if (opts.interactive) {
        var hit = svgEl("rect", { x: X(x) - 0.5, y: Y(y) - 0.5, width: 1, height: 1, "class": "go-hit" });
        hit.dataset.pt = name; svg.appendChild(hit);
      }
    }
    host.innerHTML = "";
    host.appendChild(svg);
  }

  function setup(el) {
    var size = parseInt(el.dataset.size, 10) || 19;
    return new GoRules(size).load(el.dataset.black, el.dataset.white);
  }

  function renderDiagram(el) {
    var rules = setup(el), host = document.createElement("div");
    host.className = "go-frame";
    el.innerHTML = "";
    el.appendChild(host);
    draw(host, rules, el, { marks: (el.dataset.marks || "").toUpperCase().split(/\s+/).filter(Boolean), labels: pairs(el.dataset.labels) });
    if (el.dataset.caption) { var c = document.createElement("div"); c.className = "go-caption"; c.textContent = el.dataset.caption; el.appendChild(c); }
  }

  function initMove(q, ctx) {
    var U = LP.util, rules = setup(q), toPlay = (q.dataset.toPlay || "B").toUpperCase().charAt(0);
    var solution = (q.dataset.solution || "").toUpperCase().split(/\s+/).filter(Boolean);
    var answers = U.split((q.dataset.answer || "").toUpperCase());
    var step = 0, color = toPlay, locked = false, last = null, scored = false;
    var host = U.el("div", "go-frame interactive");
    var wrap = U.el("div", "go-board"); wrap.appendChild(host);
    var row = U.el("div", "choices"), reset = U.el("button", null, "Start over");
    row.appendChild(reset);
    U.beforeExplain(q, wrap); U.beforeExplain(q, row);
    function redraw() { draw(host, rules, q, { last: last, interactive: !locked }); }
    function restart() {
      rules = setup(q); step = 0; color = toPlay; last = null; locked = false; redraw();
    }
    function other(c) { return c === "B" ? "W" : "B"; }
    function expected() { return solution.length ? [solution[step]] : answers; }

    host.addEventListener("click", function (e) {
      var pt = e.target.dataset && e.target.dataset.pt;
      if (!pt || locked) return;
      var right = expected().indexOf(pt) >= 0;
      var res = rules.play(color, GoRules.parse(pt, rules.size));
      if (!res.ok) { ctx.feedback(false, res.reason); return; }
      last = GoRules.parse(pt, rules.size);
      if (!right) {
        if (!scored) { scored = true; ctx.result(false, pt); }
        locked = true; redraw();
        ctx.feedback(false, (q.dataset.hint || "That isn't it.") + " Press “Start over” to try again.");
        return;
      }
      step++;
      var finished = !solution.length || step >= solution.length;
      if (!finished) {
        // scripted reply
        var reply = GoRules.parse(solution[step], rules.size), r2 = rules.play(other(color), reply);
        if (r2.ok) last = reply;
        step++;
        finished = step >= solution.length;
      }
      if (finished) {
        locked = true; redraw();
        if (!scored) { scored = true; ctx.result(true, solution.length ? solution.join(" ") : pt); }
        ctx.feedback(true);
      } else redraw();
    });
    reset.addEventListener("click", function () {
      restart();
      var fb = q.querySelector(":scope > .feedback"); if (fb && !fb.querySelector(".verdict.ok")) fb.remove();
    });
    redraw();
  }

  if (window.LP && LP.register) {
    LP.register({ type: "go-board", selector: ".go-board[data-size]:not(.quiz)", scored: false, init: renderDiagram });
    LP.register({ type: "go-move", init: initMove });
  } else {
    var init = function () { document.querySelectorAll(".go-board[data-size]:not(.quiz)").forEach(renderDiagram); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
