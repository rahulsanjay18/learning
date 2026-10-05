// Unit tests for the pure plotting math in assets/plugins/plot.js, and a check that every plot / plot-set in the repo compiles.
//   node scripts/test_plot.js
const fs = require("fs"), path = require("path");
const P = require("../assets/plugins/plot.js");
const M = require("../assets/plugins/math.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const phi = x => Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI);

// nice ticks
let t = P.niceTicks(-4, 4, 6);
check("ticks -4..4", same(t.ticks, [-4, -2, 0, 2, 4]), JSON.stringify(t));
t = P.niceTicks(0, 0.5, 5);
check("ticks 0..0.5 by 0.1, no float noise", same(t.ticks, [0, 0.1, 0.2, 0.3, 0.4, 0.5]) && t.decimals === 1, JSON.stringify(t));
t = P.niceTicks(0, 10, 4);
check("ticks 0..10 by 2.5", same(t.ticks, [0, 2.5, 5, 7.5, 10]) && t.decimals === 1, JSON.stringify(t));
t = P.niceTicks(-0.6, 20.6, 6);
check("ticks -0.6..20.6 start at 0", t.ticks[0] === 0 && t.ticks[t.ticks.length - 1] === 20, JSON.stringify(t));
t = P.niceTicks(0, 1000, 5);
check("ticks 0..1000 by 200", same(t.ticks, [0, 200, 400, 600, 800, 1000]) && t.decimals === 0, JSON.stringify(t));
check("ticks on a zero-width range don't loop", P.niceTicks(3, 3).ticks.length === 1);

// area
const near = (a, b, tol) => Math.abs(a - b) < tol;
check("∫ φ from -1 to 1 ≈ 0.6827", near(P.trapezoid(phi, -1, 1), 0.682689, 1e-5), P.trapezoid(phi, -1, 1));
check("∫ φ from -1.96 to 1.96 ≈ 0.95", near(P.trapezoid(phi, -1.96, 1.96), 0.950004, 1e-5), P.trapezoid(phi, -1.96, 1.96));
check("∫ x^2 from 0 to 3 = 9", near(P.trapezoid(x => x * x, 0, 3), 9, 1e-5));
check("reversed bounds give negative area", near(P.trapezoid(phi, 1, -1), -0.682689, 1e-5));
check("area through a pole is not finite", !isFinite(P.trapezoid(x => 1 / x, -1, 1, 2)));

// sampling + path breaks
const s = P.sample(x => x, 0, 1, 4);
check("sample: n+1 evenly spaced points", s.length === 5 && s[2][0] === 0.5 && s[4][1] === 1);
const nanPts = P.sample(x => (x > 0.4 && x < 0.6 ? NaN : x), 0, 1, 10);
const nanRuns = P.segments(nanPts, 0, 1);
check("NaN splits the curve into two runs", nanRuns.length === 2, JSON.stringify(nanRuns));
const d = P.pathD(nanRuns, x => x * 100, y => 100 - y * 100);
check("path has two M commands and no NaN", (d.match(/M/g) || []).length === 2 && !/NaN/.test(d), d);
const inv = P.segments(P.sample(x => 1 / x, -1, 1, 20), -5, 5);   // x=0 gives ±Infinity, neighbours jump past the view
check("1/x breaks at its asymptote", inv.length === 2 && inv[0].every(p => p[0] < 0) && inv[1].every(p => p[0] > 0), JSON.stringify(inv.map(r => r.length)));
const tan = P.segments(P.sample(Math.tan, 0, 3, 301), -5, 5);
check("tan x breaks at π/2 (no Infinity sample)", tan.length === 2, tan.length);
check("far values are clamped", P.segments([[0, 1e9], [1, 0]], 0, 1)[0][0][1] === 11);
check("steep continuous curve stays one run", P.segments(P.sample(x => 50 * x, -1, 1, 40), -5, 5).length === 1);

// discrete
const binom = P.compile("choose(n,x) p^x (1-p)^(n-x)");
const pmf = k => binom({ x: k, n: 10, p: 0.3 });
const pts = P.sampleDiscrete(pmf, -0.6, 20.6);
check("discrete samples whole x only", pts.length === 21 && pts[0][0] === 0 && pts[20][0] === 20 && pts.every(p => Number.isInteger(p[0])));
check("binomial pmf sums to 1", near(pts.reduce((a, p) => a + p[1], 0), 1, 1e-12));
check("binomial pmf is 0 beyond n", pts[15][1] === 0);
check("P(X ≤ 3), Binomial(10, 0.3) = 0.6496", near(P.discreteSum(pmf, 0, 3), 0.6496107184, 1e-9), P.discreteSum(pmf, 0, 3));
check("discreteSum includes both ends", P.discreteSum(() => 1, 2, 5) === 4 && P.discreteSum(() => 1, 2.5, 5.5) === 3);

// the gallery's plot-set target (mu = 1.5) really puts ~84% of the mass left of 2.5 on the plotted range -3..6
const norm = P.compile("exp(-(x-mu)^2/2)/sqrt(2pi)");
const left = mu => P.trapezoid(x => norm({ x, mu }), -3, 2.5);
check("gallery plot-mean: mu=1.5 gives 0.841", near(left(1.5), 0.8413, 1e-4), left(1.5));
check("gallery plot-mean: tolerance edges stay near 84%", left(1.39) > 0.86 && left(1.61) < 0.82 && left(1.4) < 0.865 && left(1.6) > 0.815);

// attribute parsing
const ps = P.parseParams("mu=0:-2:2:0.1 | s=1:0.3:3:0.1");
check("parseParams", ps.length === 2 && ps[0].name === "mu" && ps[0].min === -2 && ps[1].step === 0.1);
for (const bad of ["mu=0:-2:2", "mu=0:2:-2:0.1", "=1:0:2:1", "mu=a:0:1:0.1"]) {
  let threw = false; try { P.parseParams(bad); } catch { threw = true; }
  check(`parseParams rejects ${JSON.stringify(bad)}`, threw);
}
check("parseTargets", same(P.parseTargets("mu=1.5 | s=-2"), { mu: 1.5, s: -2 }));
check("within tolerance", P.within({ mu: 1.6 }, { mu: 1.5 }, () => 0.11) && !P.within({ mu: 1.7 }, { mu: 1.5 }, () => 0.11));
check("decimals of a step", P.decimals(0.05) === 2 && P.decimals(1) === 0 && P.decimals(0.5) === 1);
check("parseRange", same(P.parseRange("-4:4"), [-4, 4]) && same(P.parseRange("4:-4", [0, 1]), [0, 1]));

// every plot and plot-set in the repo compiles; plot-set targets are sliders inside their range
const files = [path.join(__dirname, "../assets/gallery.html")];
for (const tp of fs.readdirSync(path.join(__dirname, "../topics")))
  for (const dir of ["lessons", "reference"]) {
    const full = path.join(__dirname, "../topics", tp, dir);
    if (fs.existsSync(full)) for (const f of fs.readdirSync(full)) if (f.endsWith(".html")) files.push(path.join(full, f));
  }
const attr = (tag, n) => { const m = tag.match(new RegExp(`data-${n}="([^"]*)"`)); return m ? m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">") : null; };
for (const f of files)
  for (const tag of fs.readFileSync(f, "utf8").match(/<div[^>]*(class="lp-plot"|data-type="plot-set")[^>]*>/g) || []) {
    const name = `${path.relative(path.join(__dirname, ".."), f)} ${attr(tag, "id") || (tag.match(/id="([^"]*)"/) || [])[1] || "plot"}`;
    let err = "";
    try {
      const exprs = (attr(tag, "fns") || "").split(";").concat((attr(tag, "vline") || "").split(";"), (attr(tag, "shade") || "").split(":"))
        .map(x => x.trim()).filter(x => x && !/^-?inf$/i.test(x));
      exprs.forEach(e => M.parse(e));
      const params = P.parseParams(attr(tag, "params"));
      const target = attr(tag, "target");
      if (target) for (const [k, v] of Object.entries(P.parseTargets(target))) {
        const p = params.find(q => q.name === k);
        if (!p) throw new Error(`target ${k} is not a slider`);
        if (v < p.min || v > p.max) throw new Error(`target ${k}=${v} outside ${p.min}..${p.max}`);
      }
    } catch (e) { err = e.message; }
    check(`${name}: formulas, params and target are valid`, !err, err);
  }

console.log(fails ? `\n${fails} failure(s)` : "\nall passed");
process.exit(fails ? 1 : 0);
