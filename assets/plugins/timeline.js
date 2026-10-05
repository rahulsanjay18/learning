// Timeline plugin: horizontal SVG timelines with spans and events, and a "place it on the timeline" quiz. Load after assets/lp.js;
// style: assets/plugins/timeline.css.
//
// Years are whole numbers on the historical scale: negative = BCE, positive = CE. There is NO year 0 (1 BCE is followed by 1 CE):
// a year of 0 is rejected, the axis tick that would fall on 0 is labelled "1 CE", and distances across the era boundary drop the
// missing year (yearsBetween(-1, 1) = 1). Positions on the axis treat years as a plain number line, so −1 and 1 are drawn
// 2 units apart; that one-year drift is invisible at any useful zoom.
// Labels read "322 BCE"; "CE" is added only when the range spans both eras ("1526" vs "1526 CE").
// Prefix a year with "c" to mark it approximate ("c-321" shows as "c. 321 BCE").
//
// Diagram (unscored):
//   <div class="lp-timeline" data-range="-600:1950"
//        data-spans="c-321:-185:Maurya Empire|1526:1857:Mughal Empire"     start:end:label, "|"-separated (thin labelled bars;
//                                                                         overlapping ones stack in lanes)
//        data-events="c-268:Ashoka's reign begins|1947:Independence"       year:label (dots on the axis, labels stacked below)
//        [data-caption="…"]></div>
// Quiz (scored):
//   <div class="quiz" data-type="timeline-place" data-id="…" data-range="1500:1950" data-answer="1757" [data-tolerance="10"]
//        [data-spans/data-events as context, never the answer itself]>
//     <p class="prompt">Place the Battle of Plassey.</p><div class="explain" hidden>…</div></div>
//   The learner taps the axis (or types a year such as "1757" or "320 BCE" into the box) and presses Check. Right = within
//   data-tolerance years (default 0). A wrong try says "too early/late"; the true position is drawn once right or after a second miss.
// Pure helpers are exported for Node (node scripts/test_timeline_map.js): formatYear, formatRange, parseYear, yearsBetween,
// niceYearTicks, assignLanes (span lanes), placeEventRows (event label rows whose leaders cross no label), scale, yearAt.
(function () {
  "use strict";

  // ---------- pure logic ----------
  // "c-321" -> {year: -321, approx: true}; "1947" -> {year: 1947, approx: false}; 0 or junk -> null
  function parseYear(s) {
    var m = /^\s*(c\.?\s*)?([-+]?\d+)\s*$/i.exec(String(s == null ? "" : s));
    if (!m) return null;
    var y = parseInt(m[2], 10);
    return y === 0 ? null : { year: y, approx: !!m[1] };
  }
  // What a learner types: "1757", "1757 CE", "AD 1757", "320 BCE", "320 BC", "-320", "c. 320 BCE". Returns an integer year or null.
  function parseYearInput(s) {
    var t = String(s || "").trim().replace(/^c(irca)?\.?\s*/i, "").replace(/\./g, "").replace(/,/g, "");
    var m = /^(ad|ce)?\s*([-+]?\d+)\s*(bce|bc|ce|ad)?$/i.exec(t);
    if (!m) return null;
    var y = parseInt(m[2], 10);
    if (m[3] && /^bc/i.test(m[3])) { if (y < 0) return null; y = -y; }
    return y === 0 ? null : y;
  }
  // Number of years from a to b, skipping the nonexistent year 0.
  function yearsBetween(a, b) {
    var d = Math.abs(b - a);
    return (a < 0 && b > 0) || (b < 0 && a > 0) ? d - 1 : d;
  }
  // bothEras: true when the range spans BCE and CE, so CE years need their suffix.
  function formatYear(y, bothEras, approx) {
    var s = y < 0 ? (-y) + " BCE" : y + (bothEras ? " CE" : "");
    return (approx ? "c. " : "") + s;
  }
  // "321–185 BCE", "1526–1857 CE" (or "1526–1857"), "200 BCE – 100 CE"
  function formatRange(a, b, bothEras, approxA, approxB) {
    if (a < 0 && b < 0) return (approxA ? "c. " : "") + (-a) + "–" + (approxB && !approxA ? "c. " : "") + (-b) + " BCE";
    if (a > 0 && b > 0) return (approxA ? "c. " : "") + a + "–" + (approxB && !approxA ? "c. " : "") + b + (bothEras ? " CE" : "");
    return formatYear(a, true, approxA) + " – " + formatYear(b, true, approxB);
  }
  // Whole-year ticks at 1, 2, 2.5 (×10 and up only), 5 × 10^n: the smallest step that gives at most maxTicks ticks.
  // A tick that would land on the nonexistent year 0 is moved to 1 (labelled "1 CE").
  function niceYearTicks(lo, hi, maxTicks) {
    maxTicks = Math.max(2, maxTicks || 6);
    if (!(hi > lo)) return { step: 1, ticks: [lo] };
    var steps = [];
    for (var p = 1; p <= 1e6; p *= 10) [1, 2, 2.5, 5].forEach(function (m) { var s = m * p; if (s === Math.round(s)) steps.push(s); });
    var step = steps[steps.length - 1], ticks;
    for (var i = 0; i < steps.length; i++) {
      var n = Math.floor(hi / steps[i]) - Math.ceil(lo / steps[i]) + 1;
      if (n <= maxTicks) { step = steps[i]; break; }
    }
    ticks = [];
    for (var k = Math.ceil(lo / step); k * step <= hi; k++) ticks.push(k * step === 0 ? 1 : k * step);
    return { step: step, ticks: ticks };
  }
  // Greedy interval stacking. items: [{start, end}] in any unit (callers pass pixel extents including the label).
  // Two items share a lane only if the later one starts more than `gap` after the earlier one ends (touching = overlapping).
  // Returns the lane index for each item, in the input order, plus the lane count.
  function assignLanes(items, gap) {
    gap = gap || 0;
    var order = items.map(function (it, i) { return i; }).sort(function (a, b) { return items[a].start - items[b].start || items[a].end - items[b].end; });
    var ends = [], lanes = new Array(items.length);
    order.forEach(function (i) {
      var it = items[i], lane = -1;
      for (var l = 0; l < ends.length; l++) if (it.start > ends[l] + gap) { lane = l; break; }
      if (lane < 0) { lane = ends.length; ends.push(-Infinity); }
      ends[lane] = it.end; lanes[i] = lane;
    });
    return { lanes: lanes, count: ends.length };
  }
  // Linear year <-> pixel mapping on [x0, x1].
  function scale(lo, hi, x0, x1) {
    var k = (x1 - x0) / (hi - lo);
    return { x: function (y) { return x0 + (y - lo) * k; }, lo: lo, hi: hi, x0: x0, x1: x1 };
  }
  // Hit-test: the whole year under pixel x, clamped to the range; never 0.
  function yearAt(sc, x) {
    var y = Math.round(sc.lo + (x - sc.x0) / (sc.x(sc.hi) - sc.x0) * (sc.hi - sc.lo));
    y = Math.max(sc.lo, Math.min(sc.hi, y));
    if (y === 0) y = (x >= sc.x(0)) ? 1 : -1;
    return y;
  }
  // Rows and positions for event labels hanging below the axis. items: [{x, w}] (dot position, label width); labels stay inside
  // [lo, hi]. Each label may sit centred under its dot, to the left of it, or to the right of it. Items (left to right) take the
  // first row + position where the label overlaps no other label (with `gap`), its leader (a vertical line at x down to its row)
  // crosses no label in a row above, and the label covers no leader that runs further down. If nothing qualifies (e.g. two
  // events in one year) only label overlap is avoided. Returns {rows, starts, count}.
  function placeEventRows(items, lo, hi, gap) {
    gap = gap || 0;
    var placed = [], rows = new Array(items.length), starts = new Array(items.length), count = 0;
    var order = items.map(function (it, i) { return i; }).sort(function (a, b) { return items[a].x - items[b].x; });
    var clamp = function (s, w) { return Math.max(lo, Math.min(s, hi - w)); };
    order.forEach(function (i) {
      var it = items[i], cands = [clamp(it.x - it.w / 2, it.w), clamp(it.x + 8 - it.w, it.w), clamp(it.x - 8, it.w)];
      // prefer positions that cover fewer other dots, so their leaders can still drop past this label
      var covers = function (s) { return items.filter(function (o) { return o !== it && o.x >= s - 2 && o.x <= s + it.w + 2; }).length; };
      cands = cands.map(function (s, k) { return { s: s, k: k, n: covers(s) }; })
        .sort(function (a, b) { return a.n - b.n || a.k - b.k; }).map(function (c) { return c.s; });
      for (var pass = 0; pass < 2 && rows[i] == null; pass++)
        for (var r = 0; r <= items.length && rows[i] == null; r++)
          for (var c = 0; c < cands.length; c++) {
            var s = cands[c], e = s + it.w;
            var ok = placed.every(function (p) {
              if (p.row === r) return s > p.end + gap || e < p.start - gap;
              if (pass) return true;
              if (p.row < r) return it.x < p.start - 2 || it.x > p.end + 2;          // my leader passes their label
              return p.x < s - 2 || p.x > e + 2;                                     // their leader passes my label
            });
            if (ok) { rows[i] = r; starts[i] = s; placed.push({ x: it.x, start: s, end: e, row: r }); count = Math.max(count, r + 1); break; }
          }
    });
    return { rows: rows, starts: starts, count: count };
  }
  function parseRange(s) {
    var p = String(s || "").split(":").map(function (t) { return parseYear(t); });
    if (p.length !== 2 || !p[0] || !p[1] || !(p[1].year > p[0].year)) throw new Error("data-range must be start:end with start < end, e.g. -600:1950");
    return [p[0].year, p[1].year];
  }
  function parseSpans(s) {
    return split(s).map(function (t) {
      var parts = t.split(":"), a = parseYear(parts[0]), b = parseYear(parts[1]);
      if (parts.length < 3 || !a || !b || b.year < a.year) throw new Error("bad span “" + t + "” (want start:end:label)");
      return { start: a.year, end: b.year, approxStart: a.approx, approxEnd: b.approx, label: parts.slice(2).join(":").trim() };
    });
  }
  function parseEvents(s) {
    return split(s).map(function (t) {
      var i = t.indexOf(":"), a = i > 0 ? parseYear(t.slice(0, i)) : null;
      if (!a) throw new Error("bad event “" + t + "” (want year:label)");
      return { year: a.year, approx: a.approx, label: t.slice(i + 1).trim() };
    });
  }
  function split(s) { return String(s || "").split("|").map(function (x) { return x.trim(); }).filter(Boolean); }
  // Rough text width in px for the plugin's system-ui labels (no DOM in Node).
  function textWidth(s, px) { return String(s).length * (px || 12) * 0.6; }

  var api = { parseYear: parseYear, parseYearInput: parseYearInput, yearsBetween: yearsBetween, formatYear: formatYear,
    formatRange: formatRange, niceYearTicks: niceYearTicks, assignLanes: assignLanes, placeEventRows: placeEventRows, scale: scale, yearAt: yearAt,
    parseRange: parseRange, parseSpans: parseSpans, parseEvents: parseEvents, textWidth: textWidth };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  window.LPTimeline = api;

  // ---------- drawing ----------
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function r1(v) { return Math.round(v * 10) / 10; }
  var MIN_W = 300, PAD = 8, LANE = 30, ROW = 30, FS = 12;

  // Builds the timeline into `frame` (a .tl-scroll div). Returns {sc, svg, H, axisY} for interactive overlays.
  function draw(frame, cfg, extra) {
    var W = Math.max(MIN_W, Math.round(frame.clientWidth) || 560), range = cfg.range, both = range[0] < 0 && range[1] > 0;
    var sc = scale(range[0], range[1], PAD + 4, W - PAD - 4);

    // spans: label (name + years) above a thin bar, both inside the lane; lanes from pixel extents incl. the label
    var spanItems = cfg.spans.map(function (s) {
      var x0 = sc.x(s.start), x1 = Math.max(sc.x(s.end), x0 + 3);
      var years = formatRange(s.start, s.end, both, s.approxStart, s.approxEnd);
      var w = textWidth(s.label, FS) + 6 + textWidth(years, FS - 1);
      var lx = Math.max(PAD, Math.min(x0, W - PAD - w));
      return { s: s, x0: x0, x1: x1, lx: lx, years: years, start: Math.min(x0, lx), end: Math.max(x1, lx + w) };
    });
    var sl = assignLanes(spanItems, 8);
    var top = 6, spansH = sl.count * LANE, tickY = top + spansH + 14, axisY = tickY + 8;

    // events: dot on the axis, two-line label (name, then year) in rows below; rows from pixel extents
    var evItems = cfg.events.map(function (e) {
      var x = sc.x(e.year), yr = formatYear(e.year, both, e.approx);
      var w = Math.max(textWidth(e.label, FS), textWidth(yr, FS - 1));
      return { e: e, x: x, w: w, yr: yr };
    });
    var el = placeEventRows(evItems, PAD, W - PAD, 10);
    evItems.forEach(function (it, i) { it.lx = el.starts[i]; });
    var evTop = axisY + 16, H = Math.ceil(evTop + el.count * ROW + (el.count ? 2 : 0) + (cfg.interactive ? 18 : 0));

    var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, "class": "tl-svg", role: cfg.interactive ? "group" : "img",
      "aria-label": cfg.aria || ("Timeline, " + formatYear(range[0], both) + " to " + formatYear(range[1], both)) });
    frame.style.setProperty("--tl-w", W + "px");

    // axis + ticks
    var g = svgEl("g", { "class": "tl-axis" });
    g.appendChild(svgEl("line", { x1: sc.x0 - 4, x2: sc.x1 + 4, y1: axisY, y2: axisY }));
    // fewest-step ticks whose labels (with their edge anchoring) leave at least 10px between neighbours
    var tickLabels = function (maxT) {
      return niceYearTicks(range[0], range[1], maxT).ticks.map(function (t) {
        var x = r1(sc.x(t)), text = formatYear(t, both), w = textWidth(text, 11);
        var anchor = x < sc.x0 + 20 ? "start" : x > sc.x1 - 20 ? "end" : "middle";
        var left = anchor === "start" ? x : anchor === "end" ? x - w : x - w / 2;
        return { x: x, text: text, anchor: anchor, left: left, right: left + w };
      });
    };
    var maxT = Math.max(2, Math.floor((sc.x1 - sc.x0) / (both ? 70 : 50)) + 1), labels = tickLabels(maxT);
    while (maxT > 2 && labels.some(function (l, i) { return i && l.left < labels[i - 1].right + 10; })) labels = tickLabels(--maxT);
    labels.forEach(function (l) {
      g.appendChild(svgEl("line", { "class": "tick", x1: l.x, x2: l.x, y1: axisY - 4, y2: axisY + 4 }));
      g.appendChild(svgEl("text", { x: l.x, y: tickY, "text-anchor": l.anchor }, l.text));
    });

    // spans (guides first, so labels and tick years sit on top of them)
    var guides = svgEl("g", { "class": "tl-guides" }), gs = svgEl("g", { "class": "tl-spans" });
    svg.appendChild(guides);
    spanItems.forEach(function (it, i) {
      var y = top + sl.lanes[i] * LANE, s = it.s;
      var t = svgEl("text", { x: r1(it.lx), y: y + 12, "class": "tl-span-label" });
      t.appendChild(svgEl("tspan", {}, s.label));
      t.appendChild(svgEl("tspan", { "class": "tl-years", dx: 6 }, it.years));
      gs.appendChild(t);
      var bar = svgEl("rect", { x: r1(it.x0), y: y + 17, width: r1(it.x1 - it.x0), height: 5, "class": "tl-bar" + (s.approxStart || s.approxEnd ? " approx" : "") });
      bar.appendChild(svgEl("title", {}, s.label + ": " + it.years));
      gs.appendChild(bar);
      // faint guides from the bar's ends to the axis
      [it.x0, it.x1].forEach(function (x) { guides.appendChild(svgEl("line", { "class": "tl-guide", x1: r1(x), x2: r1(x), y1: y + 22, y2: axisY })); });
    });
    svg.appendChild(gs);
    svg.appendChild(g);

    // events
    var ge = svgEl("g", { "class": "tl-events" });
    evItems.forEach(function (it, i) {
      var rowY = evTop + el.rows[i] * ROW, cx = it.lx + it.w / 2;
      ge.appendChild(svgEl("path", { "class": "tl-leader", d: "M" + r1(it.x) + "," + axisY + "V" + (rowY - 1) + (Math.abs(cx - it.x) > 1 ? "H" + r1(Math.max(it.lx, Math.min(it.x, it.lx + it.w))) : "") }));
      var dot = svgEl("circle", { cx: r1(it.x), cy: axisY, r: 3.5, "class": "tl-dot" });
      dot.appendChild(svgEl("title", {}, it.e.label + ", " + it.yr));
      ge.appendChild(dot);
      ge.appendChild(svgEl("text", { x: r1(cx), y: rowY + 11, "text-anchor": "middle", "class": "tl-event-label" }, it.e.label));
      ge.appendChild(svgEl("text", { x: r1(cx), y: rowY + 24, "text-anchor": "middle", "class": "tl-years" }, it.yr));
    });
    svg.appendChild(ge);

    frame.innerHTML = "";
    frame.appendChild(svg);
    return { sc: sc, svg: svg, W: W, H: H, axisY: axisY, both: both, top: top };
  }

  function config(el) {
    return { range: parseRange(el.dataset.range), spans: parseSpans(el.dataset.spans), events: parseEvents(el.dataset.events) };
  }
  function redrawOnResize(frame, fn) {
    var lastW = frame.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(function () {
      if (frame.clientWidth && Math.round(frame.clientWidth) !== Math.round(lastW)) { lastW = frame.clientWidth; fn(); }
    }).observe(frame);
  }

  function initDiagram(el) {
    var cfg = config(el), frame = document.createElement("div");
    frame.className = "tl-scroll";
    el.innerHTML = "";
    el.appendChild(frame);
    if (el.dataset.caption) { var c = document.createElement("div"); c.className = "tl-caption"; c.textContent = el.dataset.caption; el.appendChild(c); }
    var go = function () { draw(frame, cfg); };
    go(); redrawOnResize(frame, go);
  }

  function initPlace(q, ctx) {
    var U = LP.util, cfg = config(q), d = q.dataset;
    var answer = parseYearInput(d.answer);
    if (answer == null) throw new Error("data-answer must be a year, e.g. 1757 or -268");
    if (answer < cfg.range[0] || answer > cfg.range[1]) throw new Error("data-answer is outside data-range");
    var tol = parseFloat(d.tolerance || "0") || 0, both = cfg.range[0] < 0 && cfg.range[1] > 0;
    cfg.interactive = true;
    cfg.aria = "Timeline: tap a point on the axis to choose a year";
    var guess = null, misses = 0, done = false, reveal = false, view = null;

    var frame = U.el("div", "tl-scroll interactive");
    var row = U.el("div", "tl-controls"), lab = U.el("label", "tl-input"), input = U.el("input"), check = U.el("button", null, "Check");
    input.type = "text"; input.inputMode = "text"; input.autocomplete = "off";
    input.placeholder = both ? "e.g. 320 BCE" : "year";
    input.setAttribute("aria-label", "Year (type it, or tap the timeline)");
    lab.appendChild(document.createTextNode("Year ")); lab.appendChild(input);
    row.appendChild(lab); row.appendChild(check);
    U.beforeExplain(q, frame); U.beforeExplain(q, row);

    function marker(svg, y, cls, text, side) {
      var x = r1(view.sc.x(y)), g = svgEl("g", { "class": "tl-marker " + cls });
      g.appendChild(svgEl("line", { x1: x, x2: x, y1: view.top, y2: view.H - 16 }));
      g.appendChild(svgEl("path", { d: "M" + (x - 5) + "," + (view.axisY - 9) + "h10l-5,7z" }));
      var anchor = side || (x < 60 ? "start" : x > view.W - 60 ? "end" : "middle");
      g.appendChild(svgEl("text", { x: x + (anchor === "start" ? 4 : anchor === "end" ? -4 : 0), y: view.H - 4, "text-anchor": anchor }, text));
      svg.appendChild(g);
    }
    function render() {
      view = draw(frame, cfg);
      var svg = view.svg;
      if (!done) {
        var hit = svgEl("rect", { x: 0, y: 0, width: view.W, height: view.H, "class": "tl-hit" });
        svg.appendChild(hit);
      }
      // when both labels are shown and close together, push them apart (left one ends at its line, right one starts at its line)
      var gx = guess != null ? view.sc.x(guess) : null, ax = view.sc.x(answer), near = reveal && gx != null && Math.abs(gx - ax) < 110;
      if (guess != null && !(reveal && guess === answer))
        marker(svg, guess, "guess", (reveal ? "you: " : "") + formatYear(guess, both), near ? (gx <= ax ? "end" : "start") : null);
      if (reveal) marker(svg, answer, "truth", formatYear(answer, both), near ? (gx <= ax ? "start" : "end") : null);
    }
    function pick(y) {
      if (done) return;
      guess = y; input.value = formatYear(y, both); input.classList.remove("no");
      render();
    }
    frame.addEventListener("click", function (e) {
      if (done || !view) return;
      var r = view.svg.getBoundingClientRect();
      pick(yearAt(view.sc, (e.clientX - r.left) * view.W / r.width));
    });
    input.addEventListener("input", function () {
      var y = parseYearInput(input.value);
      if (y != null && y >= cfg.range[0] && y <= cfg.range[1]) { guess = y; render(); }
    });
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") check.click(); });
    function finish() { done = true; reveal = true; input.disabled = true; check.disabled = true; render(); }
    check.addEventListener("click", function () {
      var typed = parseYearInput(input.value);
      if (typed == null) { ctx.feedback(false, "Tap the timeline or type a year, like 1757 or 320 BCE."); input.classList.add("no"); return; }
      if (typed < cfg.range[0] || typed > cfg.range[1]) { ctx.feedback(false, "Pick a year between " + formatYear(cfg.range[0], both) + " and " + formatYear(cfg.range[1], both) + "."); return; }
      guess = typed;
      var off = yearsBetween(guess, answer), ok = off <= tol;
      ctx.result(ok, formatYear(guess, true));
      if (ok) {
        input.classList.remove("no"); input.classList.add("ok"); finish();
        ctx.feedback(true, null);
        var fb = q.querySelector(":scope > .feedback .verdict");
        if (fb) fb.textContent = "Right" + (off ? " (off by " + off + (off === 1 ? " year" : " years") + "). " : ". ");
        return;
      }
      misses++;
      input.classList.add("no");
      var dir = guess < answer ? "too early" : "too late", msg = "About " + off + " years " + dir + ".";
      if (misses >= 2) { finish(); msg += " The true date is marked: " + formatYear(answer, both) + "."; }
      else { render(); msg += " " + (d.hint || "Try again."); }
      ctx.feedback(false, msg);
    });
    // "I don't know" / "Show me the answer" (pretests) reveal the true position too.
    document.addEventListener("lp:event", function (e) {
      var ev = e.detail;
      if (ev.item === ctx.id && (ev.type === "reveal" || ev.kind === "skip")) finish();
    });
    render(); redrawOnResize(frame, render);
  }

  if (window.LP && LP.register) {
    LP.register({ type: "timeline", selector: ".lp-timeline", scored: false, init: initDiagram });
    LP.register({ type: "timeline-place", init: initPlace });
  } else {
    var init = function () { document.querySelectorAll(".lp-timeline").forEach(initDiagram); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
