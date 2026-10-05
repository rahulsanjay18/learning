// Pixel-art widgets for lessons. No dependencies. Works in Node too (exports PixelLine for tests).
//
// Static picture:   <div class="px" data-art="....##|..##..|##...." data-caption="..."></div>
//   Rows are separated by "|". "." = empty, "#" = ink, "!" = flagged ink (drawn in red), "o" = endpoint (accent).
//   Optional data-cell="18" sets the on-screen size of one pixel (CSS px).
//
// Drawing drill:    <div class="px-draw" data-w="16" data-h="9" data-a="1,7" data-b="14,1"
//                        data-check="line" data-slope="2" data-caption="..."></div>
//   The learner paints pixels from A to B; "Check" runs PixelLine.check and highlights problems.
//   data-check="line": every segment must have the same slope (data-slope, if given: 2 = two across per step down).
//   data-check="curve": slopes must change progressively, leaving A flat and arriving at B steep.
//   Optional data-example="<art rows>" adds a "Show an example" button.
(function (root) {
  "use strict";

  // ---------- Pure line checker (no DOM) ----------
  var PixelLine = {};
  function key(x, y) { return x + "," + y; }

  // Pixels that make a right-angle corner: they touch the line both sideways and up/down.
  // In a 1px line these are "doubles": removing them keeps the line connected.
  PixelLine.doubles = function (set) {
    var out = [];
    set.forEach(function (k) {
      var p = k.split(",").map(Number), x = p[0], y = p[1];
      var h = set.has(key(x - 1, y)) || set.has(key(x + 1, y));
      var v = set.has(key(x, y - 1)) || set.has(key(x, y + 1));
      if (h && v) out.push(k);
    });
    return out;
  };

  function neighbors(set, k) {
    var p = k.split(",").map(Number), out = [];
    for (var dy = -1; dy <= 1; dy++) for (var dx = -1; dx <= 1; dx++) {
      if (!dx && !dy) continue;
      var n = key(p[0] + dx, p[1] + dy);
      if (set.has(n)) out.push(n);
    }
    return out;
  }

  // Split an ordered path into segments: straight runs joined by diagonal steps.
  // Each segment gets a slope = pixels across per pixel down (h run of 3 -> 3, v run of 3 -> 1/3, single pixel -> 1).
  PixelLine.segments = function (path) {
    var segs = [], cur = [path[0]], dir = null;
    for (var i = 1; i < path.length; i++) {
      var dx = path[i][0] - path[i - 1][0], dy = path[i][1] - path[i - 1][1];
      var d = (dx && dy) ? "d" : (dx ? "h" : "v");
      if (d !== "d" && (dir === null || dir === d)) { cur.push(path[i]); dir = d; continue; }
      segs.push({ pixels: cur, dir: dir });
      // A diagonal step starts a new segment; an orthogonal turn (only possible with a double) does too.
      cur = [path[i]]; dir = d === "d" ? null : d;
    }
    segs.push({ pixels: cur, dir: dir });
    segs.forEach(function (s) {
      var n = s.pixels.length;
      s.len = n;
      s.slope = n === 1 ? 1 : (s.dir === "h" ? n : 1 / n);
    });
    return segs;
  };

  // Slope as "across:down", e.g. 2:1 = segments 2 pixels long lying flat.
  function fmt(s) { return s >= 1 ? Math.round(s) + ":1" : "1:" + Math.round(1 / s); }

  // Returns {ok, msg, bad: [keys to highlight], segments}
  PixelLine.check = function (pixelKeys, a, b, mode, slope) {
    var set = new Set(pixelKeys), A = key(a[0], a[1]), B = key(b[0], b[1]);
    set.add(A); set.add(B);
    var dbl = PixelLine.doubles(set);
    if (dbl.length) return { ok: false, kind: "double", bad: dbl,
      msg: "Double found: the red pixels make a right-angle corner (an L shape). Remove one pixel from each corner so the line connects only diagonally." };

    var branch = [];
    set.forEach(function (k) {
      var n = neighbors(set, k).length;
      if ((k === A || k === B) ? n !== 1 : n !== 2) branch.push(k);
    });
    // Walk from A.
    var path = [A], seen = new Set([A]), at = A;
    while (at !== B) {
      var next = neighbors(set, at).filter(function (n) { return !seen.has(n); });
      if (next.length !== 1) break;
      at = next[0]; seen.add(at); path.push(at);
    }
    if (at !== B || seen.size !== set.size) {
      var stray = []; set.forEach(function (k) { if (!seen.has(k)) stray.push(k); });
      var bad = branch.length ? branch : stray;
      if (at !== B && !branch.length) bad = bad.concat([at]);
      return { ok: false, kind: "broken", bad: bad,
        msg: "This isn't one unbroken 1px line from A to B yet. Look for a gap, a stray pixel, or a fork (red)." };
    }
    var pts = path.map(function (k) { return k.split(",").map(Number); });
    var sx = Math.sign(b[0] - a[0]), sy = Math.sign(b[1] - a[1]);
    for (var i = 1; i < pts.length; i++) {
      var dx = pts[i][0] - pts[i - 1][0], dy = pts[i][1] - pts[i - 1][1];
      if ((dx && Math.sign(dx) !== sx) || (dy && Math.sign(dy) !== sy))
        return { ok: false, kind: "backtrack", bad: [path[i]], msg: "The line doubles back on itself (red). Keep heading from A toward B." };
    }
    var segs = PixelLine.segments(pts), slopes = segs.map(function (s) { return s.slope; });
    var lens = segs.map(function (s) { return s.len; }).join(", ");

    if (mode === "line") {
      var first = slopes[0];
      var odd = segs.filter(function (s) { return s.slope !== first; });
      if (odd.length) return { ok: false, kind: "jaggy", segments: segs,
        bad: odd.reduce(function (acc, s) { return acc.concat(s.pixels.map(function (p) { return key(p[0], p[1]); })); }, []),
        msg: "Jaggy: your segment lengths are " + lens + ". A straight line needs every segment the same length. Segments that differ from the first are in red." };
      if (slope && Math.abs(first - slope) > 1e-9) return { ok: false, kind: "slope", segments: segs, bad: [],
        msg: "Clean and even, but the slope is " + fmt(first) + ". This drill asks for " + fmt(slope) + "." };
      return { ok: true, segments: segs, bad: [],
        msg: "Clean. " + segs.length + " segments, all length " + segs[0].len + ": a perfect " + fmt(first) + " line." };
    }
    // curve
    var badAt = -1;
    for (var j = 1; j < slopes.length; j++) if (slopes[j] > slopes[j - 1] + 1e-9) { badAt = j; break; }
    if (badAt > 0) return { ok: false, kind: "jaggy", segments: segs,
      bad: segs[badAt - 1].pixels.concat(segs[badAt].pixels).map(function (p) { return key(p[0], p[1]); }),
      msg: "Jaggy: segments go " + lens + ". In a curve, segments should get steadily shorter toward the diagonal and longer again after it. The red pair breaks that pattern." };
    if (!(slopes[0] > 1) || !(slopes[slopes.length - 1] < 1)) return { ok: false, kind: "flat", segments: segs, bad: [],
      msg: "No jaggies, but this is not a curve yet. It should leave A heading sideways (a long flat segment) and reach B heading down (a long upright segment)." };
    return { ok: true, segments: segs, bad: [],
      msg: "Clean curve. Segments go " + lens + ": steadily shorter toward the diagonal, then longer again." };
  };

  PixelLine.parseArt = function (art) {
    return art.split("|").map(function (r) { return r.trim(); });
  };

  if (typeof module !== "undefined" && module.exports) { module.exports = PixelLine; return; }
  root.PixelLine = PixelLine;

  // ---------- DOM widgets ----------
  var NS = "http://www.w3.org/2000/svg";
  function el(name, attrs, parent) {
    var e = document.createElementNS(NS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function gridSvg(w, h, cell) {
    var svg = el("svg", { viewBox: "0 0 " + w + " " + h, width: w * cell, height: h * cell, "class": "px-svg",
      "shape-rendering": "crispEdges" });
    el("rect", { x: 0, y: 0, width: w, height: h, "class": "px-bg" }, svg);
    var g = el("g", { "class": "px-gridlines" }, svg);
    for (var x = 1; x < w; x++) el("line", { x1: x, y1: 0, x2: x, y2: h }, g);
    for (var y = 1; y < h; y++) el("line", { x1: 0, y1: y, x2: w, y2: y }, g);
    return svg;
  }
  function caption(host) {
    if (!host.dataset.caption) return;
    var c = document.createElement("div"); c.className = "px-caption"; c.textContent = host.dataset.caption;
    host.appendChild(c);
  }

  function renderStatic(host) {
    var rows = PixelLine.parseArt(host.dataset.art), h = rows.length, w = rows[0].length;
    var cell = Number(host.dataset.cell) || Math.max(8, Math.min(20, Math.floor(320 / w)));
    var svg = gridSvg(w, h, cell);
    var ink = el("g", {}, svg);
    svg.insertBefore(ink, svg.querySelector(".px-gridlines"));
    rows.forEach(function (r, y) {
      r.split("").forEach(function (c, x) {
        if (c === ".") return;
        el("rect", { x: x, y: y, width: 1, height: 1, "class": c === "!" ? "px-bad" : (c === "o" ? "px-end" : "px-ink") }, ink);
      });
    });
    host.appendChild(svg);
    caption(host);
  }

  function renderDraw(host) {
    var w = Number(host.dataset.w), h = Number(host.dataset.h);
    var a = host.dataset.a.split(",").map(Number), b = host.dataset.b.split(",").map(Number);
    var A = key(a[0], a[1]), B = key(b[0], b[1]);
    var cell = Math.max(14, Math.min(26, Math.floor(400 / w)));
    var svg = gridSvg(w, h, cell);
    var ink = el("g", {}, svg), marks = el("g", {}, svg);
    svg.insertBefore(ink, svg.querySelector(".px-gridlines"));
    var on = new Set(), rects = {};

    function paint(k, val) {
      if (k === A || k === B) return;
      if (val && !on.has(k)) {
        on.add(k);
        var p = k.split(",").map(Number);
        rects[k] = el("rect", { x: p[0], y: p[1], width: 1, height: 1, "class": "px-ink" }, ink);
      } else if (!val && on.has(k)) {
        on.delete(k); ink.removeChild(rects[k]); delete rects[k];
      }
      clearMarks(); preview();
    }
    [a, b].forEach(function (p, i) {
      el("rect", { x: p[0], y: p[1], width: 1, height: 1, "class": "px-end" }, ink);
      var t = el("text", { x: p[0] + 0.5, y: p[1] + 0.72, "class": "px-label", "text-anchor": "middle" }, marks.parentNode);
      t.textContent = i ? "B" : "A";
    });
    function clearMarks() { while (marks.firstChild) marks.removeChild(marks.firstChild); fb.textContent = ""; fb.className = "px-feedback"; }

    var mode = null;
    function cellAt(ev) {
      var r = svg.getBoundingClientRect();
      var x = Math.floor((ev.clientX - r.left) / r.width * w), y = Math.floor((ev.clientY - r.top) / r.height * h);
      if (x < 0 || y < 0 || x >= w || y >= h) return null;
      return key(x, y);
    }
    svg.addEventListener("pointerdown", function (ev) {
      var k = cellAt(ev); if (!k) return;
      ev.preventDefault(); svg.setPointerCapture(ev.pointerId);
      mode = (ev.button === 2 || on.has(k)) ? false : true;
      paint(k, mode);
    });
    svg.addEventListener("pointermove", function (ev) { if (mode === null) return; var k = cellAt(ev); if (k) paint(k, mode); });
    svg.addEventListener("pointerup", function () { mode = null; });
    svg.addEventListener("contextmenu", function (ev) { ev.preventDefault(); });

    var wrap = document.createElement("div"); wrap.className = "px-draw-row";
    wrap.appendChild(svg);
    var side = document.createElement("div"); side.className = "px-side";
    var pv = document.createElement("canvas"); pv.width = w; pv.height = h; pv.className = "px-preview";
    pv.style.width = (w * 3) + "px"; pv.style.height = (h * 3) + "px";
    var pvl = document.createElement("div"); pvl.className = "px-caption"; pvl.textContent = "at 3× size";
    side.appendChild(pv); side.appendChild(pvl);
    wrap.appendChild(side);
    host.appendChild(wrap);
    function preview() {
      var ctx = pv.getContext("2d"); ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = getComputedStyle(host).getPropertyValue("--px-ink") || "#222";
      on.forEach(function (k) { var p = k.split(",").map(Number); ctx.fillRect(p[0], p[1], 1, 1); });
      [a, b].forEach(function (p) { ctx.fillRect(p[0], p[1], 1, 1); });
    }

    var bar = document.createElement("div"); bar.className = "px-buttons";
    function button(label, fn) { var x = document.createElement("button"); x.type = "button"; x.textContent = label; x.onclick = fn; bar.appendChild(x); return x; }
    button("Check", function () {
      var res = PixelLine.check(Array.from(on), a, b, host.dataset.check, Number(host.dataset.slope) || 0);
      clearMarks();
      res.bad.forEach(function (k) {
        var p = k.split(",").map(Number);
        el("rect", { x: p[0] + 0.12, y: p[1] + 0.12, width: 0.76, height: 0.76, "class": "px-mark" }, marks);
      });
      fb.textContent = res.msg; fb.className = "px-feedback " + (res.ok ? "ok" : "no");
    });
    button("Clear", function () { Array.from(on).forEach(function (k) { paint(k, false); }); });
    if (host.dataset.example) {
      var ex = null;
      button("Show an example", function () {
        if (ex) { ex.remove(); ex = null; return; }
        ex = document.createElement("div"); ex.className = "px"; ex.dataset.art = host.dataset.example;
        ex.dataset.caption = "One clean answer (others exist)";
        host.appendChild(ex); renderStatic(ex);
      });
    }
    host.appendChild(bar);
    var fb = document.createElement("div"); fb.className = "px-feedback"; host.appendChild(fb);
    caption(host);
    preview();
    if (window.matchMedia) matchMedia("(prefers-color-scheme: dark)").addEventListener("change", preview);
  }

  function init() {
    document.querySelectorAll(".px[data-art]").forEach(renderStatic);
    document.querySelectorAll(".px-draw").forEach(renderDraw);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})(this);
