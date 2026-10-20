// Plot plugin: function plots with live parameter sliders (Statistics, Economics), drawn as inline SVG.
// Load order: assets/lp.js, then plugins/math.js (formulas are parsed by window.LPMath), then plugins/plot.js. Style: plugins/plot.css.
//
// Plot (unscored):
//   <div class="lp-plot" data-x="-4:4" data-y="0:0.8"
//        data-fns="exp(-(x-mu)^2/(2s^2))/(s sqrt(2pi))"     one or more formulas in x, separated by ";"
//        [data-labels="Demand;Supply"]                       legend, one label per formula
//        [data-params="mu=0:-2:2:0.1 | s=1:0.5:2:0.1"]       name=value:min:max:step, "|"-separated; one slider each
//        [data-points="1,2;3,4"] [data-vline="mu"]           scatter points; dashed vertical line(s) at expressions (";"-separated)
//        [data-shade="mu-s:mu+s"] [data-show-area="true"]    shade under the FIRST formula between two expressions; print its area
//        [data-discrete="true"]                              draw at whole x as bars (PMFs); shading then sums the shaded bars
//        [data-xlabel="x"] [data-ylabel="density"] [data-caption="…"]></div>
//   Formulas use the math plugin's syntax (2x^2, sqrt(), exp(), e^-x, pi, fact(n), choose(n,k)). Parameter names must be
//   single letters or greek names (mu, sigma, lambda, …), never x. In data-shade, "-inf"/"inf" mean the plot's left/right edge.
// Quiz (scored): <div class="quiz" data-type="plot-set" data-id="…" …same attributes… data-target="mu=1.5 | s=1" [data-tolerance="0.11"]>
//                  <p class="prompt">…</p><div class="explain" hidden>…</div></div>
//   The learner moves the sliders and presses Check. Right = every target parameter within tolerance (default: half a slider step).
// Pure helpers are exported for Node (node scripts/test_plot.js): niceTicks, sample, segments, pathD, trapezoid, discreteSum, …
(function () {
  "use strict";
  var M = (typeof window !== "undefined" && window.LPMath) || (typeof require === "function" ? require("./math.js") : null);

  // ---------- pure plotting math ----------
  // "Nice" axis ticks (steps of 1, 2, 2.5 or 5 × 10^n) covering [lo, hi], about maxTicks of them.
  function niceTicks(lo, hi, maxTicks) {
    maxTicks = Math.max(2, maxTicks || 6);
    var range = hi - lo;
    if (!(range > 0)) return { step: 1, decimals: 0, ticks: [lo] };
    var rough = range / maxTicks, mag = Math.pow(10, Math.floor(Math.log10(rough))), r = rough / mag;
    var nice = r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10;
    var step = nice * mag, decimals = Math.max(0, -Math.floor(Math.log10(step) + 1e-9) + (nice === 2.5 ? 1 : 0));
    var ticks = [];
    for (var k = Math.ceil(lo / step - 1e-9); k * step <= hi + step * 1e-9; k++) ticks.push(Number((k * step).toFixed(decimals)) || 0);
    return { step: step, decimals: decimals, ticks: ticks };
  }

  // n+1 evenly spaced samples [[x, y], …] of f on [x0, x1]; y may be NaN/±Infinity.
  function sample(f, x0, x1, n) {
    var out = [];
    for (var i = 0; i <= n; i++) { var x = x0 + (x1 - x0) * i / n; out.push([x, f(x)]); }
    return out;
  }
  // f at every whole number in [x0, x1].
  function sampleDiscrete(f, x0, x1) {
    var out = [];
    for (var k = Math.ceil(x0 - 1e-9); k <= x1 + 1e-9; k++) out.push([k, f(k)]);
    return out;
  }

  // Split samples into drawable runs: break at non-finite y, and where the curve jumps from above the view to below it
  // (or back) between two samples (asymptotes like 1/x or tan x). Far-off values are clamped so the SVG stays sane.
  function segments(points, yMin, yMax) {
    var R = (yMax - yMin) || 1, lo = yMin - 10 * R, hi = yMax + 10 * R, out = [], cur = [], prev = null;
    points.forEach(function (p) {
      var y = p[1];
      if (!isFinite(y)) { if (cur.length) out.push(cur); cur = []; prev = null; return; }
      if (prev !== null && ((prev > yMax && y < yMin) || (prev < yMin && y > yMax))) { if (cur.length) out.push(cur); cur = []; }
      cur.push([p[0], Math.min(hi, Math.max(lo, y))]);
      prev = y;
    });
    if (cur.length) out.push(cur);
    return out;
  }

  // SVG path data for runs of points, mapped to pixels by X and Y. Single-point runs are skipped.
  function pathD(runs, X, Y) {
    return runs.filter(function (r) { return r.length > 1; }).map(function (r) {
      return r.map(function (p, i) { return (i ? "L" : "M") + px(X(p[0])) + "," + px(Y(p[1])); }).join("");
    }).join("");
  }
  function px(v) { return Math.round(v * 10) / 10; }

  // Trapezoid rule for ∫_a^b f (signed: b < a gives a negative area). NaN if f is undefined somewhere on the grid.
  function trapezoid(f, a, b, n) {
    n = n || 2000;
    if (a === b) return 0;
    var h = (b - a) / n, s = (f(a) + f(b)) / 2;
    for (var i = 1; i < n; i++) s += f(a + i * h);
    return s * h;
  }
  // Σ f(k) over whole k in [a, b].
  function discreteSum(f, a, b) {
    var s = 0;
    for (var k = Math.ceil(Math.min(a, b) - 1e-9); k <= Math.max(a, b) + 1e-9; k++) s += f(k);
    return s;
  }

  // "mu=0:-2:2:0.1 | s=1:0.3:3:0.1" -> [{name, value, min, max, step}]
  function parseParams(s) {
    return (s || "").split("|").map(function (t) { return t.trim(); }).filter(Boolean).map(function (t) {
      var m = /^([a-z_]+)\s*=\s*(.+)$/i.exec(t);
      if (!m) throw new Error("bad parameter “" + t + "” (want name=value:min:max:step)");
      var v = m[2].split(":").map(function (x) { return parseFloat(x); });
      if (v.length !== 4 || v.some(isNaN) || !(v[2] > v[1]) || !(v[3] > 0)) throw new Error("bad parameter “" + t + "” (want name=value:min:max:step)");
      return { name: m[1], value: v[0], min: v[1], max: v[2], step: v[3] };
    });
  }
  // "mu=1.5 | s=1" -> {mu: 1.5, s: 1}
  function parseTargets(s) {
    var out = {};
    (s || "").split("|").map(function (t) { return t.trim(); }).filter(Boolean).forEach(function (t) {
      var m = /^([a-z_]+)\s*=\s*(-?[\d.]+(?:e[-+]?\d+)?)$/i.exec(t);
      if (!m) throw new Error("bad target “" + t + "” (want name=value)");
      out[m[1]] = parseFloat(m[2]);
    });
    return out;
  }
  // "a:b" -> [-1, 0] style range
  function parseRange(s, fallback) {
    var v = String(s || "").split(":").map(function (x) { return parseFloat(x); });
    return v.length === 2 && isFinite(v[0]) && isFinite(v[1]) && v[1] > v[0] ? v : fallback;
  }
  function decimals(step) { var s = String(step), i = s.indexOf("."); return i < 0 ? 0 : s.length - i - 1; }
  function within(values, targets, tol) {
    return Object.keys(targets).every(function (k) { return k in values && Math.abs(values[k] - targets[k]) <= tol(k) + 1e-9; });
  }

  // Compile a formula with the math plugin's parser: returns f(env) -> number.
  function compile(src) {
    if (!M) throw new Error("load plugins/math.js before plugins/plot.js");
    var ast = M.parse(src);
    return function (env) { return M.evaluate(ast, env); };
  }
  function checkName(name) {
    var ok = false;
    try { var a = M.parse(name); ok = a.t === "var" && a.n === name && name !== "x"; } catch (e) { /* not a name */ }
    if (!ok) throw new Error("parameter name “" + name + "” must be a single letter or a greek name (mu, sigma, …), not x");
  }

  var engine = { niceTicks: niceTicks, sample: sample, sampleDiscrete: sampleDiscrete, segments: segments, pathD: pathD,
    trapezoid: trapezoid, discreteSum: discreteSum, parseParams: parseParams, parseTargets: parseTargets, parseRange: parseRange,
    decimals: decimals, within: within, compile: compile };
  if (typeof module !== "undefined" && module.exports) { module.exports = engine; return; }
  window.LPPlot = engine;

  // ---------- drawing ----------
  var NS = "http://www.w3.org/2000/svg", uid = 0;
  var GREEK = { alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε", theta: "θ", lambda: "λ", mu: "μ", sigma: "σ",
    tau: "τ", phi: "φ", omega: "ω", rho: "ρ", nu: "ν", kappa: "κ" };
  function svgEl(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function num(v, dec) { return (v < 0 ? "−" : "") + Math.abs(v).toFixed(dec); }
  function list(s) { return (s || "").split(";").map(function (t) { return t.trim(); }).filter(Boolean); }

  // Builds the plot inside `el` (before its .explain, if any). Returns {values, lock()}.
  function build(el) {
    var U = LP.util, d = el.dataset;
    var fns = list(d.fns).map(compile);
    if (!fns.length) throw new Error("data-fns is empty");
    var params = parseParams(d.params);
    params.forEach(function (p) { checkName(p.name); });
    var vlines = list(d.vline).map(compile), labels = list(d.labels);
    var shade = d.shade ? d.shade.split(":").map(function (t) { t = t.trim(); return /^-?inf$/i.test(t) ? t.toLowerCase() : compile(t); }) : null;
    if (shade && shade.length !== 2) throw new Error("data-shade wants a:b");
    var points = list(d.points).map(function (t) { return t.split(",").map(parseFloat); }).filter(function (p) { return p.length === 2 && isFinite(p[0]) && isFinite(p[1]); });
    var xr = parseRange(d.x, [-5, 5]), yr = parseRange(d.y, [-5, 5]), discrete = d.discrete === "true";
    var values = {}; params.forEach(function (p) { values[p.name] = p.value; });
    var clipId = "lp-plot-clip-" + (++uid);

    var frame = U.el("div", "plot-frame"), host = U.el("div", "plot-svg");
    frame.appendChild(host);
    if (!el.classList.contains("quiz")) el.innerHTML = "";
    U.beforeExplain(el, frame);

    if (labels.length) {
      var leg = U.el("div", "plot-legend");
      labels.forEach(function (l, i) {
        var item = U.el("span", "plot-key"), sw = svgEl("svg", { width: 28, height: 10, "aria-hidden": "true" });
        sw.appendChild(svgEl("line", { x1: 1, x2: 27, y1: 5, y2: 5, "class": "plot-curve c" + (i % 4) }));
        item.appendChild(sw); item.appendChild(document.createTextNode(l));
        leg.appendChild(item);
      });
      U.beforeExplain(el, leg);
    }

    var inputs = [];
    if (params.length) {
      var box = U.el("div", "plot-params");
      params.forEach(function (p) {
        var row = U.el("label", "plot-param"), name = U.el("span", "name", GREEK[p.name] || p.name);
        if (!GREEK[p.name]) name.classList.add("var");
        var input = U.el("input"), out = U.el("output", null, num(p.value, decimals(p.step)));
        input.type = "range"; input.min = p.min; input.max = p.max; input.step = p.step; input.value = p.value;
        input.dataset.param = p.name;
        input.setAttribute("aria-label", p.name);
        input.addEventListener("input", function () {
          values[p.name] = parseFloat(input.value);
          out.textContent = num(values[p.name], decimals(p.step));
          draw();
        });
        row.appendChild(name); row.appendChild(input); row.appendChild(out);
        box.appendChild(row); inputs.push(input);
      });
      U.beforeExplain(el, box);
    }

    var cap = null, areaEl = null;
    if (d.caption || d.showArea === "true") {
      cap = U.el("div", "plot-caption", d.caption || null);
      if (d.showArea === "true") { areaEl = U.el("span", "plot-area"); areaEl.setAttribute("aria-live", "polite"); cap.appendChild(areaEl); }
      U.beforeExplain(el, cap);
    }

    function env(x) { var e = { x: x }; for (var k in values) e[k] = values[k]; return e; }
    function fx(f) { return function (x) { return f(env(x)); }; }
    function bound(b) { return b === "-inf" ? xr[0] : b === "inf" ? xr[1] : b(env(NaN)); }

    var lastW = 0;
    function draw() {
      var W = Math.round(host.clientWidth) || 560;
      lastW = W;
      var H = Math.round(Math.min(380, Math.max(220, W * 0.62)));
      var L = 46, R = 12, T = d.ylabel ? 26 : 12, B = d.xlabel ? 44 : 28;
      var pw = W - L - R, ph = H - T - B;
      var X = function (x) { return L + (x - xr[0]) / (xr[1] - xr[0]) * pw; };
      var Y = function (y) { return T + (yr[1] - y) / (yr[1] - yr[0]) * ph; };
      var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, "class": "plot", role: "img",
        "aria-label": d.caption || ("Plot of " + list(d.fns).join("; ")) });

      // grid + ticks
      var xt = niceTicks(xr[0], xr[1], Math.max(3, Math.floor(pw / 64))), yt = niceTicks(yr[0], yr[1], Math.max(3, Math.floor(ph / 34)));
      var grid = svgEl("g", { "class": "plot-grid" }), labs = svgEl("g", { "class": "plot-ticks" });
      xt.ticks.forEach(function (t) {
        grid.appendChild(svgEl("line", { x1: px(X(t)), x2: px(X(t)), y1: T, y2: T + ph }));
        labs.appendChild(svgEl("text", { x: px(X(t)), y: T + ph + 16, "text-anchor": "middle" }, num(t, xt.decimals)));
      });
      yt.ticks.forEach(function (t) {
        grid.appendChild(svgEl("line", { y1: px(Y(t)), y2: px(Y(t)), x1: L, x2: L + pw }));
        labs.appendChild(svgEl("text", { x: L - 6, y: px(Y(t)) + 4, "text-anchor": "end" }, num(t, yt.decimals)));
      });
      svg.appendChild(grid); svg.appendChild(labs);
      var axes = svgEl("g", { "class": "plot-axes" });
      axes.appendChild(svgEl("line", { x1: L, x2: L + pw, y1: T + ph, y2: T + ph }));
      axes.appendChild(svgEl("line", { x1: L, x2: L, y1: T, y2: T + ph }));
      if (yr[0] < 0 && yr[1] > 0) axes.appendChild(svgEl("line", { "class": "zero", x1: L, x2: L + pw, y1: px(Y(0)), y2: px(Y(0)) }));
      svg.appendChild(axes);
      if (d.xlabel) svg.appendChild(svgEl("text", { "class": "plot-label", x: L + pw / 2, y: H - 6, "text-anchor": "middle" }, d.xlabel));
      if (d.ylabel) svg.appendChild(svgEl("text", { "class": "plot-label", x: 4, y: 14, "text-anchor": "start" }, d.ylabel));

      var clip = svgEl("clipPath", { id: clipId });
      clip.appendChild(svgEl("rect", { x: L, y: T - 1, width: pw, height: ph + 2 }));
      svg.appendChild(clip);
      var g = svgEl("g", { "clip-path": "url(#" + clipId + ")" });
      svg.appendChild(g);

      // shading under the first curve
      var lo = null, hi = null, base = Y(Math.min(yr[1], Math.max(yr[0], 0)));
      if (shade) {
        lo = bound(shade[0]); hi = bound(shade[1]);
        if (isFinite(lo) && isFinite(hi) && lo > hi) { var tmp = lo; lo = hi; hi = tmp; }
      }
      var f0 = fx(fns[0]), haveShade = shade && isFinite(lo) && isFinite(hi);
      if (haveShade && !discrete) {
        var a = Math.max(lo, xr[0]), b = Math.min(hi, xr[1]);
        if (b > a) {
          var pts = sample(f0, a, b, Math.max(60, Math.round((b - a) / (xr[1] - xr[0]) * pw)));
          var dd = "M" + px(X(a)) + "," + px(base);
          pts.forEach(function (p) { var y = isFinite(p[1]) ? p[1] : 0; dd += "L" + px(X(p[0])) + "," + px(Math.max(T - 2, Math.min(T + ph + 2, Y(y)))); });
          dd += "L" + px(X(b)) + "," + px(base) + "Z";
          g.appendChild(svgEl("path", { "class": "plot-shade", d: dd }));
        }
      }

      // curves
      var unit = pw / (xr[1] - xr[0]), bw = Math.max(2, Math.min(28, unit * 0.7));
      fns.forEach(function (f, i) {
        var cls = "plot-curve c" + (i % 4), fxi = fx(f);
        if (!discrete) {
          var dPath = pathD(segments(sample(fxi, xr[0], xr[1], Math.max(200, Math.round(pw * 1.5))), yr[0], yr[1]), X, Y);
          g.appendChild(svgEl("path", { "class": cls, d: dPath || "M0,0" }));
          return;
        }
        var pts = sampleDiscrete(fxi, xr[0], xr[1]).filter(function (p) { return isFinite(p[1]); });
        if (i === 0) {   // bars; shaded bars filled
          var out = "", inn = "";
          pts.forEach(function (p) {
            var yv = Math.max(yr[0] - 1, Math.min(yr[1] + 1, p[1]));
            if (Math.abs(Y(yv) - base) < 0.5) return;   // zero-height bar: nothing to draw
            var r = "M" + px(X(p[0]) - bw / 2) + "," + px(base) + "V" + px(Y(yv)) + "h" + px(bw) + "V" + px(base) + "Z";
            if (haveShade && p[0] >= lo - 1e-9 && p[0] <= hi + 1e-9) inn += r; else out += r;
          });
          g.appendChild(svgEl("path", { "class": "plot-bars c0", d: out || "M0,0" }));
          if (haveShade) g.appendChild(svgEl("path", { "class": "plot-bars c0 in", d: inn || "M0,0" }));
        } else {         // later formulas as lollipops, offset a little so they don't hide the bars
          var off = Math.min(bw / 2 + 3, unit * 0.45), stems = "", dots = [];
          pts.forEach(function (p) {
            var yv = Math.max(yr[0] - 1, Math.min(yr[1] + 1, p[1]));
            stems += "M" + px(X(p[0]) + off) + "," + px(base) + "V" + px(Y(yv));
            dots.push(svgEl("circle", { "class": "plot-dot c" + (i % 4), cx: px(X(p[0]) + off), cy: px(Y(yv)), r: 3 }));
          });
          g.appendChild(svgEl("path", { "class": cls, d: stems || "M0,0" }));
          dots.forEach(function (c) { g.appendChild(c); });
        }
      });

      vlines.forEach(function (v) {
        var xv = v(env(NaN));
        if (isFinite(xv)) g.appendChild(svgEl("line", { "class": "plot-vline", x1: px(X(xv)), x2: px(X(xv)), y1: T, y2: T + ph }));
      });
      points.forEach(function (p) { g.appendChild(svgEl("circle", { "class": "plot-point", cx: px(X(p[0])), cy: px(Y(p[1])), r: 3.5 })); });

      if (areaEl) {
        var area = !haveShade ? NaN : discrete ? discreteSum(f0, lo, hi) : trapezoid(f0, lo, hi, 2000);
        areaEl.textContent = (discrete ? "Shaded total" : "Shaded area") + (haveShade ? " from " + num(lo, 2) + " to " + num(hi, 2) : "") +
          (isFinite(area) ? (discrete ? " = " : " ≈ ") + area.toFixed(4) : ": undefined");
      }
      host.innerHTML = "";
      host.appendChild(svg);
    }

    draw();
    if (window.ResizeObserver) new ResizeObserver(function () { if (Math.round(host.clientWidth) !== lastW && host.clientWidth) draw(); }).observe(host);
    return {
      values: values, params: params,
      lock: function () { inputs.forEach(function (i) { i.disabled = true; }); }
    };
  }

  function initPlot(el) { build(el); }

  function initSet(q, ctx) {
    var U = LP.util, targets = parseTargets(q.dataset.target);
    if (!Object.keys(targets).length) throw new Error("data-target is empty");
    var plot = build(q), steps = {};
    plot.params.forEach(function (p) { steps[p.name] = p.step; });
    Object.keys(targets).forEach(function (k) { if (!(k in steps)) throw new Error("target “" + k + "” is not a slider"); });
    var tolAttr = q.dataset.tolerance ? parseFloat(q.dataset.tolerance) : null;
    var row = U.el("div", "choices"), b = U.el("button", null, "Check");
    row.appendChild(b); U.beforeExplain(q, row);
    b.addEventListener("click", function () {
      var ok = within(plot.values, targets, function (k) { return tolAttr != null ? tolAttr : steps[k] / 2; });
      var answer = Object.keys(targets).map(function (k) { return k + "=" + plot.values[k]; }).join(" | ");
      ctx.result(ok, answer);
      ctx.feedback(ok, ok ? null : q.dataset.hint || "Not there yet. Adjust the sliders and check again.");
      if (ok) { plot.lock(); b.disabled = true; }
    });
  }

  if (!window.LP || !LP.register) return;
  LP.register({ type: "plot", selector: ".lp-plot", scored: false, init: initPlot });
  LP.register({ type: "plot-set", init: initSet });
})();
