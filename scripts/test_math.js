// Unit tests for the math engine in assets/plugins/math.js, and a check that every math quiz's data-answer parses.
//   node scripts/test_math.js
const fs = require("fs"), path = require("path");
const M = require("../assets/plugins/math.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const eq = (a, b, o) => M.equivalent(a, b, o).ok;
const ev = (s, env) => M.evaluate(M.parse(s), env);

// precedence and parsing
check("2+3*4 = 14", ev("2+3*4") === 14);
check("-x^2 = -(x^2)", ev("-x^2", { x: 3 }) === -9);
check("2^3^2 right-assoc = 512", ev("2^3^2") === 512);
check("implicit 2x(x+1)", ev("2x(x+1)", { x: 3 }) === 24);
check("xy = x*y", ev("xy", { x: 2, y: 5 }) === 10);
check("2pi r", Math.abs(ev("2pi r", { r: 1 }) - 2 * Math.PI) < 1e-12);
check("sin x without parens", Math.abs(ev("sin x", { x: 1 }) - Math.sin(1)) < 1e-12);
check("sin^2(x)", Math.abs(ev("sin^2(x)", { x: 1 }) - Math.sin(1) ** 2) < 1e-12);
check("e^-x", Math.abs(ev("e^-x", { x: 2 }) - Math.exp(-2)) < 1e-12);
check("1/(1+e^-x) at 0 = 0.5", ev("1/(1+e^-x)", { x: 0 }) === 0.5);
check("unicode × · − π √", Math.abs(ev("2×3·π − √(4)") - (6 * Math.PI - 2)) < 1e-12);
check("1e3 scientific", ev("1e3") === 1000);
check("exp is a function, e x is e*x", Math.abs(ev("exp(1)") - Math.E) < 1e-12 && Math.abs(ev("ex", { x: 2 }) - 2 * Math.E) < 1e-12);
check("greek theta", Math.abs(ev("cos(theta)", { theta: 0 }) - 1) < 1e-12);
for (const bad of ["2+", "(x+1", "x$", ""]) {
  let threw = false; try { M.parse(bad); } catch { threw = true; }
  check(`rejects ${JSON.stringify(bad)}`, threw);
}

// equivalence
check("2x(x+1) ≡ 2x^2+2x", eq("2x(x+1)", "2*x^2+2*x"));
check("(x+1)^2 ≢ x^2+1", !eq("(x+1)^2", "x^2+1"));
check("sin^2+cos^2 ≡ 1", eq("sin(x)^2+cos(x)^2", "1"));
check("sqrt(2)/2 ≡ 1/sqrt(2)", eq("sqrt(2)/2", "1/sqrt(2)"));
check("0.333 not exact 1/3", !eq("0.333", "1/3"));
check("0.333 ≈ 1/3 with tolerance", eq("0.333", "1/3", { tolerance: 0.001 }));
check("ln(xy) ≡ ln x + ln y (on its domain)", eq("ln(x)+ln(y)", "ln(x*y)"));
check("sqrt(x^2) ≢ x (negative samples)", !eq("x", "sqrt(x^2)"));
check("extra variable reported", /depend on y/.test(M.equivalent("x+y", "x").reason || ""));
check("nowhere-defined answer is wrong", !eq("sqrt(-1-x^2)", "x"));
check("sample mean formula (n-1) ≢ n", !eq("s/(n-1)", "s/n"));
check("economics: P*Q ≡ Q*P", eq("Q*P", "P Q"));

// TeX output
const tex = s => M.toTeX(M.parse(s));
check("tex fraction", tex("1/(1+e^-x)") === "\\frac{1}{1 + e^{-x}}", tex("1/(1+e^-x)"));
check("tex sqrt + power", tex("sqrt(x^2+1)") === "\\sqrt{x^{2} + 1}", tex("sqrt(x^2+1)"));
check("tex implicit product", tex("2x(x+1)") === "2 x \\left(x + 1\\right)", tex("2x(x+1)"));
check("tex greek + sin", tex("sin(theta)") === "\\sin\\left(\\theta\\right)", tex("sin(theta)"));

// every math quiz in the repo has a parseable answer
const files = [path.join(__dirname, "../assets/gallery.html")];
for (const t of fs.readdirSync(path.join(__dirname, "../topics")))
  for (const d of ["lessons", "reference"]) {
    const dir = path.join(__dirname, "../topics", t, d);
    if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) if (f.endsWith(".html")) files.push(path.join(dir, f));
  }
for (const f of files)
  for (const tag of fs.readFileSync(f, "utf8").match(/<div[^>]*data-type="math"[^>]*>/g) || []) {
    const ans = (tag.match(/data-answer="([^"]*)"/) || [])[1], id = (tag.match(/data-id="([^"]*)"/) || [])[1];
    let ok = true; try { M.parse(ans); } catch { ok = false; }
    check(`${path.relative(path.join(__dirname, ".."), f)} ${id}: answer "${ans}" parses`, ok);
  }
console.log(fails ? `\n${fails} failure(s)` : "\nall passed");
process.exit(fails ? 1 : 0);
