// Simulation plugin: small statistics labs drawn from formulas (no images). Load after assets/lp.js; style: plugins/sim.css.
//
//   <div class="lp-sim" data-sim="ci-coverage" [data-n="10"] [data-level="0.95"] [data-method="t|z|z-plugin"] [data-caption]></div>
//       Draws confidence intervals for a normal mean (μ = 0, σ = 1), 20 at a time; misses are marked. Methods: "z" (σ known),
//       "z-plugin" (sample s with the z value: under-covers for small n), "t" (sample s with the t value: correct).
//   <div class="lp-sim" data-sim="sampling-mean" [data-pop="exponential|uniform|normal|bimodal"] [data-n="5"]></div>
//       1,000 sample means of size n from a population; histogram vs the population; slider for n; shows sd(x̄) vs σ/√n.
//   <div class="lp-sim" data-sim="multiple-testing" [data-k="20"] [data-alpha="0.05"]></div>
//       Experiments of k independent tests where every null is true; how often at least one p < α. Toggle Bonferroni.
// Unscored: put a quiz after it ("what fraction do you expect to miss?"). Pure helpers are exported for Node
// (node scripts/test_sim.js): rng, normal, tQuantile, zQuantile, ciCoverage, familywise.
(function () {
  "use strict";
  // ---------- pure ----------
  function rng(seed) {                     // mulberry32
    var a = seed >>> 0;
    return function () { a |= 0; a = a + 0x6D2B79F5 | 0; var t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }
  function normal(r) { var u = 0, v = 0; while (u === 0) u = r(); while (v === 0) v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function erf(x) {                        // Abramowitz-Stegun 7.1.26 is too coarse for quantiles; use a series/continued fraction mix
    var s = x < 0 ? -1 : 1; x = Math.abs(x);
    if (x < 3) { var sum = x, term = x, n = 0; do { n++; term *= -x * x / n; sum += term / (2 * n + 1); } while (Math.abs(term) > 1e-16 * Math.abs(sum) && n < 200); return s * 2 / Math.sqrt(Math.PI) * sum; }
    var f = 0; for (var k = 60; k >= 1; k--) f = k / 2 / (x + f);      // erfc continued fraction
    return s * (1 - Math.exp(-x * x) / Math.sqrt(Math.PI) / (x + f));
  }
  function zCdf(z) { return 0.5 * (1 + erf(z / Math.SQRT2)); }
  function bisect(f, target, lo, hi) { for (var i = 0; i < 200; i++) { var m = (lo + hi) / 2; if (f(m) < target) lo = m; else hi = m; } return (lo + hi) / 2; }
  function zQuantile(p) { return bisect(zCdf, p, -40, 40); }
  function lgamma(x) {                     // Lanczos
    var g = 7, c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313, -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
    if (x < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * x)) - lgamma(1 - x);
    x -= 1; var a = c[0], t = x + g + 0.5; for (var i = 1; i < 9; i++) a += c[i] / (x + i);
    return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
  }
  function betacf(a, b, x) {               // Numerical Recipes continued fraction for the incomplete beta
    var qab = a + b, qap = a + 1, qam = a - 1, c = 1, d = 1 - qab * x / qap; if (Math.abs(d) < 1e-300) d = 1e-300; d = 1 / d; var h = d;
    for (var m = 1; m <= 300; m++) {
      var m2 = 2 * m, aa = m * (b - m) * x / ((qam + m2) * (a + m2));
      d = 1 + aa * d; if (Math.abs(d) < 1e-300) d = 1e-300; c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d; h *= d * c;
      aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
      d = 1 + aa * d; if (Math.abs(d) < 1e-300) d = 1e-300; c = 1 + aa / c; if (Math.abs(c) < 1e-300) c = 1e-300; d = 1 / d;
      var del = d * c; h *= del; if (Math.abs(del - 1) < 1e-14) break;
    }
    return h;
  }
  function ibeta(a, b, x) {
    if (x <= 0) return 0; if (x >= 1) return 1;
    var bt = Math.exp(lgamma(a + b) - lgamma(a) - lgamma(b) + a * Math.log(x) + b * Math.log(1 - x));
    return x < (a + 1) / (a + b + 2) ? bt * betacf(a, b, x) / a : 1 - bt * betacf(b, a, 1 - x) / b;
  }
  function tCdf(t, df) { var x = df / (df + t * t), p = 0.5 * ibeta(df / 2, 0.5, x); return t >= 0 ? 1 - p : p; }
  function tQuantile(p, df) { return bisect(function (t) { return tCdf(t, df); }, p, -1000, 1000); }
  // One interval for a sample of size n from N(0,1). Returns {lo, hi, hit}.
  function interval(r, n, level, method) {
    var xs = [], sum = 0; for (var i = 0; i < n; i++) { var x = normal(r); xs.push(x); sum += x; }
    var mean = sum / n, s = 1;
    if (method !== "z") { var ss = 0; xs.forEach(function (x) { ss += (x - mean) * (x - mean); }); s = Math.sqrt(ss / (n - 1)); }
    var crit = method === "t" ? tQuantile(1 - (1 - level) / 2, n - 1) : zQuantile(1 - (1 - level) / 2);
    var half = crit * s / Math.sqrt(n);
    return { lo: mean - half, hi: mean + half, hit: mean - half <= 0 && 0 <= mean + half };
  }
  function ciCoverage(seed, reps, n, level, method) {
    var r = rng(seed), hits = 0; for (var i = 0; i < reps; i++) if (interval(r, n, level, method).hit) hits++;
    return hits / reps;
  }
  function familywise(k, alpha, bonferroni) { var a = bonferroni ? alpha / k : alpha; return 1 - Math.pow(1 - a, k); }
  var POPS = {
    normal: { draw: function (r) { return normal(r); }, mean: 0, sd: 1, range: [-4, 4] },
    uniform: { draw: function (r) { return r(); }, mean: 0.5, sd: Math.sqrt(1 / 12), range: [0, 1] },
    exponential: { draw: function (r) { return -Math.log(1 - r()); }, mean: 1, sd: 1, range: [0, 6] },
    bimodal: { draw: function (r) { return (r() < 0.5 ? -2 : 2) + 0.6 * normal(r); }, mean: 0, sd: Math.sqrt(4 + 0.36), range: [-4.5, 4.5] }
  };

  var api = { rng: rng, normal: normal, zQuantile: zQuantile, tQuantile: tQuantile, tCdf: tCdf, zCdf: zCdf, interval: interval,
    ciCoverage: ciCoverage, familywise: familywise, POPS: POPS };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---------- UI ----------
  var SVGNS = "http://www.w3.org/2000/svg";
  function svg(tag, a) { var e = document.createElementNS(SVGNS, tag); for (var k in a) e.setAttribute(k, a[k]); return e; }
  function h(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; if (tag === "button") e.type = "button"; return e; }
  function pct(x) { return (100 * x).toFixed(1) + "%"; }
  var seedCounter = Date.now() % 100000;

  function ciSim(el) {
    var d = el.dataset, n = parseInt(d.n || "10", 10), level = parseFloat(d.level || "0.95"), method = d.method || "t";
    var r = rng(seedCounter++), all = [], W = 320, H = 260;
    var names = { z: "σ known, z value", "z-plugin": "sample s with the z value", t: "sample s with the t value" };
    var info = h("p", "sim-info"), box = h("div", "sim-plot"), row = h("div", "sim-controls");
    var more = h("button", null, "Draw 20 intervals"), lots = h("button", null, "Draw 1,000"), reset = h("button", null, "Reset");
    var sel = h("select"); Object.keys(names).forEach(function (k) { var o = h("option", null, names[k]); o.value = k; if (k === method) o.selected = true; sel.appendChild(o); });
    row.appendChild(more); row.appendChild(lots); row.appendChild(reset); row.appendChild(sel);
    function draw() {
      var shown = all.slice(-40), root = svg("svg", { viewBox: "0 0 " + W + " " + H, "class": "sim-svg", role: "img", "aria-label": "Confidence intervals" });
      var x = function (v) { return W / 2 + v * (W / 2 - 10) / 2.5; };
      root.appendChild(svg("line", { x1: x(0), y1: 0, x2: x(0), y2: H - 14, "class": "sim-truth" }));
      var t = svg("text", { x: x(0) + 4, y: H - 3, "class": "sim-label" }); t.textContent = "true μ = 0"; root.appendChild(t);
      shown.forEach(function (c, i) {
        var y = 6 + i * ((H - 24) / 40);
        root.appendChild(svg("line", { x1: x(Math.max(c.lo, -2.5)), y1: y, x2: x(Math.min(c.hi, 2.5)), y2: y, "class": c.hit ? "sim-ci" : "sim-ci miss" }));
      });
      box.textContent = ""; box.appendChild(root);
      var hits = all.filter(function (c) { return c.hit; }).length;
      info.textContent = all.length ? hits + " of " + all.length + " intervals contain μ (" + pct(hits / all.length) + "). Target: " + pct(level) +
        ". Sample size n = " + n + "; method: " + names[method] + "." : "Each line is one " + pct(level) + " interval from a fresh sample of n = " + n + ". Draw some.";
    }
    function add(k) { for (var i = 0; i < k; i++) all.push(interval(r, n, level, method)); draw(); }
    more.addEventListener("click", function () { add(20); });
    lots.addEventListener("click", function () { add(1000); });
    reset.addEventListener("click", function () { all = []; draw(); });
    sel.addEventListener("change", function () { method = sel.value; all = []; draw(); });
    el.appendChild(box); el.appendChild(info); el.appendChild(row); draw();
  }

  function meanSim(el) {
    var d = el.dataset, pop = POPS[d.pop || "exponential"] || POPS.exponential, n = parseInt(d.n || "5", 10), r = rng(seedCounter++), W = 320, H = 180;
    var info = h("p", "sim-info"), box = h("div", "sim-plot"), row = h("div", "sim-controls");
    var lab = h("label", null, "n = "), out = h("output", null, String(n)), slider = h("input"); slider.type = "range"; slider.min = 1; slider.max = 50; slider.value = n;
    lab.appendChild(out); row.appendChild(lab); row.appendChild(slider);
    function draw() {
      var means = []; for (var i = 0; i < 1000; i++) { var s = 0; for (var j = 0; j < n; j++) s += pop.draw(r); means.push(s / n); }
      var lo = pop.range[0], hi = pop.range[1], bins = 40, cnt = new Array(bins).fill(0);
      means.forEach(function (m) { var b = Math.floor((m - lo) / (hi - lo) * bins); if (b >= 0 && b < bins) cnt[b]++; });
      var mx = Math.max.apply(null, cnt), root = svg("svg", { viewBox: "0 0 " + W + " " + H, "class": "sim-svg", role: "img", "aria-label": "Histogram of sample means" });
      cnt.forEach(function (c, b) { var bh = (H - 20) * c / mx; root.appendChild(svg("rect", { x: 10 + b * (W - 20) / bins, y: H - 16 - bh, width: (W - 20) / bins - 1, height: bh, "class": "sim-bar" })); });
      [lo, (lo + hi) / 2, hi].forEach(function (v) { var t = svg("text", { x: 10 + (v - lo) / (hi - lo) * (W - 20), y: H - 3, "class": "sim-label", "text-anchor": "middle" }); t.textContent = +v.toFixed(2); root.appendChild(t); });
      box.textContent = ""; box.appendChild(root);
      var mu = means.reduce(function (a, b) { return a + b; }, 0) / 1000, sd = Math.sqrt(means.reduce(function (a, b) { return a + (b - mu) * (b - mu); }, 0) / 999);
      info.textContent = "1,000 means of n = " + n + " draws from a" + ("aeiou".indexOf((d.pop || "exponential")[0]) >= 0 ? "n " : " ") + (d.pop || "exponential") +
        " population. Their sd = " + sd.toFixed(3) + "; σ/√n = " + (pop.sd / Math.sqrt(n)).toFixed(3) + ". Mean of the means = " + mu.toFixed(3) + " (population mean " + pop.mean + ").";
    }
    slider.addEventListener("input", function () { n = +slider.value; out.textContent = n; draw(); });
    el.appendChild(box); el.appendChild(info); el.appendChild(row); draw();
  }

  function mtSim(el) {
    var d = el.dataset, k = parseInt(d.k || "20", 10), alpha = parseFloat(d.alpha || "0.05"), r = rng(seedCounter++), runs = 0, any = 0, bonf = false;
    var info = h("p", "sim-info"), grid = h("div", "sim-grid"), row = h("div", "sim-controls");
    var go = h("button", null, "Run one experiment (" + k + " tests)"), many = h("button", null, "Run 100"), cb = h("input"), lab = h("label");
    cb.type = "checkbox"; lab.appendChild(cb); lab.appendChild(document.createTextNode(" Bonferroni (use α/" + k + ")"));
    row.appendChild(go); row.appendChild(many); row.appendChild(lab);
    function one(show) {
      var a = bonf ? alpha / k : alpha, ps = [], hit = false;
      for (var i = 0; i < k; i++) { var p = r(); ps.push(p); if (p < a) hit = true; }    // every null true: p ~ Uniform(0,1)
      runs++; if (hit) any++;
      if (show) { grid.textContent = ""; ps.forEach(function (p) { var c = h("span", "sim-p" + (p < a ? " sig" : ""), p.toFixed(3)); grid.appendChild(c); }); }
    }
    function report() {
      info.textContent = runs ? "Experiments with at least one \"significant\" result: " + any + " of " + runs + " (" + pct(any / runs) + "). Theory: 1 − (1 − " +
        (bonf ? "α/" + k : "α") + ")^" + k + " = " + pct(familywise(k, alpha, bonf)) + ". Every null hypothesis here is true." : "Each experiment runs " + k + " tests where nothing is going on.";
    }
    go.addEventListener("click", function () { one(true); report(); });
    many.addEventListener("click", function () { for (var i = 0; i < 99; i++) one(false); one(true); report(); });
    cb.addEventListener("change", function () { bonf = cb.checked; runs = any = 0; grid.textContent = ""; report(); });
    el.appendChild(grid); el.appendChild(info); el.appendChild(row); report();
  }

  var SIMS = { "ci-coverage": ciSim, "sampling-mean": meanSim, "multiple-testing": mtSim };
  function init(el) {
    var f = SIMS[el.dataset.sim];
    if (!f) throw new Error("lp-sim: data-sim must be one of " + Object.keys(SIMS).join(", "));
    el.textContent = ""; f(el);
    if (el.dataset.caption) el.appendChild(h("div", "sim-caption", el.dataset.caption));
  }
  if (window.LP && LP.register) LP.register({ type: "sim", selector: ".lp-sim", scored: false, init: init });
  else document.addEventListener("DOMContentLoaded", function () { document.querySelectorAll(".lp-sim").forEach(init); });
})();
