// Tests for assets/plugins/sim.js: quantiles against standard tables, and coverage behaving as theory says.
//   node scripts/test_sim.js
const S = require("../assets/plugins/sim.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const near = (a, b, t) => Math.abs(a - b) <= t;
check("z 0.975 = 1.95996", near(S.zQuantile(0.975), 1.959964, 1e-5), S.zQuantile(0.975));
check("z 0.95 = 1.64485", near(S.zQuantile(0.95), 1.644854, 1e-5));
// t table: t_{0.975, df}
[[1, 12.706], [2, 4.303], [5, 2.571], [9, 2.262], [29, 2.045], [100, 1.984]].forEach(([df, v]) =>
  check(`t 0.975, df ${df} = ${v}`, near(S.tQuantile(0.975, df), v, 1e-3), S.tQuantile(0.975, df)));
check("tCdf symmetric", near(S.tCdf(0, 7), 0.5, 1e-12) && near(S.tCdf(1.5, 7) + S.tCdf(-1.5, 7), 1, 1e-10));
const cz = S.ciCoverage(1, 20000, 5, 0.95, "z"), ct = S.ciCoverage(2, 20000, 5, 0.95, "t"), cp = S.ciCoverage(3, 20000, 5, 0.95, "z-plugin");
check(`z with σ known covers ~95% (${cz})`, near(cz, 0.95, 0.008));
check(`t covers ~95% at n = 5 (${ct})`, near(ct, 0.95, 0.008));
check(`plug-in s with z under-covers at n = 5 (${cp}; theory ≈ 0.878)`, near(cp, 2 * S.tCdf(1.959964, 4) - 1, 0.01));
check("familywise 20 tests at 0.05 = 64.2%", near(S.familywise(20, 0.05, false), 0.6415, 1e-4));
check("Bonferroni keeps it under 5%", S.familywise(20, 0.05, true) < 0.05);
const r = S.rng(42), xs = Array.from({ length: 50000 }, () => S.normal(r)), m = xs.reduce((a, b) => a + b) / xs.length;
check("normal draws: mean ~0, var ~1", near(m, 0, 0.02) && near(xs.reduce((a, b) => a + (b - m) ** 2, 0) / xs.length, 1, 0.03));
console.log(fails ? `sim: ${fails} failed` : "sim: all passed");
process.exit(fails ? 1 : 0);
