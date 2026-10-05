// Browser smoke test for the shared widget library.
//   node scripts/test_widgets.mjs        (from the repo root; needs Playwright + Chromium)
// 1. Opens every lesson, reference page and the gallery; fails on page errors or widgets that didn't initialise.
// 2. Drives every widget in assets/gallery.html and checks scoring + the local event log.
//    The Python section needs jsDelivr (via HTTPS_PROXY if set); if unreachable it is reported as skipped, not failed.
import { createRequire } from "node:module";
import { execSync, spawn } from "node:child_process";
import { readdirSync, existsSync, readFileSync } from "node:fs";
import { X509Certificate, createHash } from "node:crypto";
import { join } from "node:path";

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require(join(execSync("npm root -g").toString().trim(), "playwright"))); }

const PORT = 8765, BASE = `http://127.0.0.1:${PORT}`;
const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { stdio: "ignore" });
await new Promise(r => setTimeout(r, 800));

const pages = ["assets/gallery.html"];
for (const t of readdirSync("topics")) for (const d of ["lessons", "reference"]) {
  const dir = join("topics", t, d);
  if (existsSync(dir)) for (const f of readdirSync(dir)) if (f.endsWith(".html")) pages.push(join(dir, f));
}

const exe = existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined;
// The Python plugin loads Pyodide from jsDelivr. Where outbound HTTPS must go through a proxy (HTTPS_PROXY), route the TEST
// browser through it; local pages bypass it ("<-loopback>" first: Playwright appends one, and Chromium lets the last matching
// rule win). The proxy re-signs TLS. If its CA is in NODE_EXTRA_CA_CERTS, the test browser trusts exactly those keys
// (--ignore-certificate-errors-spki-list); otherwise it falls back to ignoreHTTPSErrors, which in Chromium can fail worker
// loads with ERR_TOO_MANY_RETRIES. Test-only: nothing here touches shipped code.
const proxyServer = process.env.HTTPS_PROXY || process.env.https_proxy;
function caPins() {
  const f = process.env.NODE_EXTRA_CA_CERTS;
  if (!proxyServer || !f || !existsSync(f)) return [];
  const pems = readFileSync(f, "utf8").match(/-----BEGIN CERTIFICATE-----[\s\S]+?-----END CERTIFICATE-----/g) || [];
  return pems.map(p => { try { return createHash("sha256").update(new X509Certificate(p).publicKey.export({ type: "spki", format: "der" })).digest("base64"); } catch { return null; } })
    .filter(Boolean);
}
const pins = caPins();
const launchOpts = proxyServer ? { proxy: { server: proxyServer, bypass: "<-loopback>,127.0.0.1,localhost" },
  args: pins.length ? [`--ignore-certificate-errors-spki-list=${pins.join(",")}`] : [] } : {};
let browser;
try { browser = await chromium.launch(exe ? { ...launchOpts, executablePath: exe } : launchOpts); }
catch { browser = await chromium.launch(launchOpts); }
// Only jsDelivr (Pyodide) goes out; other third-party loads (the YouTube embed) are aborted so a slow network can't stall "load".
const newPage = async (opts = {}) => {
  const p = await browser.newPage({ ignoreHTTPSErrors: !!proxyServer && !pins.length, ...opts });
  await p.route(u => !/^(127\.0\.0\.1|localhost|cdn\.jsdelivr\.net)$/.test(u.hostname), r => r.abort());
  return p;
};
let failures = 0;
const fail = (msg) => { failures++; console.log("FAIL " + msg); };

for (const p of pages) {
  const page = await newPage();
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", m => { if (m.type() === "error" && !/youtube|ERR_|net::|Failed to load resource/i.test(m.text())) errors.push(m.text()); });
  await page.goto(`${BASE}/${p}`, { waitUntil: "load" });
  await page.waitForTimeout(150);
  const state = await page.evaluate(() => ({
    quizzes: document.querySelectorAll(".quiz[data-type]").length,
    notReady: [...document.querySelectorAll(".quiz[data-type]:not([data-lp-ready])")].map(q => q.dataset.type),
    broken: [...document.querySelectorAll("[data-lp-error]")].map(q => q.dataset.lpError),
    boards: document.querySelectorAll(".board-wrap[data-fen] .board").length - document.querySelectorAll(".board-wrap[data-fen]").length,
    css: getComputedStyle(document.body).backgroundColor,
  }));
  if (errors.length) fail(`${p}: ${errors.join("; ")}`);
  if (state.notReady.length) fail(`${p}: widgets not initialised: ${state.notReady.join(", ")}`);
  if (state.broken.length) fail(`${p}: widget errors: ${state.broken.join("; ")}`);
  if (state.boards < 0) fail(`${p}: some chess diagrams did not render`);
  if (state.css === "rgba(0, 0, 0, 0)") fail(`${p}: stylesheet not applied`);
  console.log(`ok   ${p} (${state.quizzes} quiz items)`);
  await page.close();
}

// ---- drive the gallery ----
const page = await newPage();
await page.goto(`${BASE}/assets/gallery.html`);
await page.evaluate(() => localStorage.clear());
await page.reload();
const q = (id) => `.quiz[data-id="${id}"]`;
const verdictOk = async (id) => (await page.locator(`${q(id)} > .feedback .verdict`).last().getAttribute("class"))?.includes("ok");
async function expectOk(id) { if (!(await verdictOk(id))) fail(`gallery: ${id} did not accept the right answer`); else console.log(`ok   gallery: ${id}`); }

// choice: wrong first (counts as a miss), then right
await page.click(`${q("choice")} button:text-is("Cramming")`);
await page.click(`${q("choice")} button:text-is("Spacing")`);
await expectOk("choice");

await page.fill(`${q("number")} input`, "64"); await page.click(`${q("number")} button`); await expectOk("number");
await page.fill(`${q("exact")} input`, "  paris "); await page.click(`${q("exact")} button`); await expectOk("exact");

const blanks = page.locator(`${q("cloze")} input.blank`);
await blanks.nth(0).fill("100"); await blanks.nth(1).fill("zero");
await page.click(`${q("cloze")} .actions button`); await expectOk("cloze");

// order: bubble rows into the right sequence with the ↑ buttons
const target = ["Mercury", "Venus", "Earth", "Mars"];
for (let i = 0; i < target.length; i++) {
  for (;;) {
    const labels = await page.locator(`${q("order")} .lp-rows li .label`).allTextContents();
    const at = labels.findIndex(l => l.endsWith(target[i]));
    if (at <= i) break;
    await page.locator(`${q("order")} .lp-rows li`).nth(at).locator("button").first().click();
  }
}
await page.click(`${q("order")} .actions button`); await expectOk("order");

for (const [item, bucket] of [["Bat", "Mammal"], ["Penguin", "Bird"], ["Whale", "Mammal"], ["Ostrich", "Bird"]])
  await page.locator(`${q("categorize")} li`, { hasText: item }).locator(`button:text-is("${bucket}")`).click();
await page.click(`${q("categorize")} .actions button`); await expectOk("categorize");

await page.click(`${q("recall")} button:text-is("Show answer")`);
await page.click(`${q("recall")} button:text-is("I had it")`);

for (const cb of await page.locator(`${q("checklist")} input[type=checkbox]`).all()) await cb.check();
await expectOk("checklist");

await page.fill(`${q("free")} textarea`, "Review right before you forget, at growing intervals.");
await page.click(`${q("free")} button`);
if (!(await page.locator(`${q("free")} .rubric`).isHidden())) fail("gallery: rubric is visible to the learner");

// worked example: steps reveal one at a time
await page.click(".lp-worked button"); await page.click(".lp-worked button");
if (await page.locator(".lp-worked .step[hidden]").count()) fail("gallery: worked example did not reveal all steps");

// chess: an illegal move must not count; then the mating move by clicking
await page.click(`${q("chess-move")} .sq[data-sq="d1"]`);
await page.click(`${q("chess-move")} .sq[data-sq="h5"]`);
await page.waitForTimeout(1500);
const illegal = await page.locator(`${q("chess-move")} > .feedback`).textContent().catch(() => "");
const chessJsLoaded = /legal/.test(illegal || "");
console.log(chessJsLoaded ? "ok   gallery: chess.js loaded, illegal move rejected" : "note gallery: chess.js not reachable; UCI fallback in use");
await page.click(`${q("chess-move")} .sq[data-sq="d1"]`);
await page.click(`${q("chess-move")} .sq[data-sq="d8"]`);
await page.waitForTimeout(chessJsLoaded ? 300 : 1500);
await expectOk("chess-move");

// go: illegal (occupied) point refused without scoring; single capture; then a line with a wrong try, start over, solve
const goClick = (id, pt) => page.click(`${q(id)} .go-hit[data-pt="${pt}"]`, { force: true });
await goClick("go-capture", "E5");
if (!/already taken/.test(await page.locator(`${q("go-capture")} > .feedback`).textContent())) fail("gallery: go occupied point not refused");
await goClick("go-capture", "E4"); await expectOk("go-capture");
if (await page.locator(`${q("go-capture")} .go-stone.w`).count()) fail("gallery: go captured stone still on board");
await goClick("go-drive", "E4");
await page.click(`${q("go-drive")} button:text-is("Start over")`);
await goClick("go-drive", "E7");
if (await page.locator(`${q("go-drive")} .go-stone.w`).count() !== 3) fail("gallery: go scripted reply missing");
await goClick("go-drive", "E3"); await expectOk("go-drive");
if (await page.locator(`${q("go-drive")} .go-stone.w`).count() !== 0) fail("gallery: go line did not capture");
if (await page.locator(".go-board[data-size]:not(.quiz) svg").count() !== 2) fail("gallery: go diagrams missing");

// math: KaTeX typesets the page; a forbidden form is refused without scoring; an equivalent form is accepted
await page.waitForSelector(".katex", { timeout: 5000 }).catch(() => {});
if ((await page.locator("main .katex").count()) < 4) fail("gallery: KaTeX did not typeset the page");
if (!(await page.locator("p", { hasText: "a price like $5 stays a price" }).count())) fail("gallery: single $ was treated as math");
await page.fill(`${q("math-expand")} input`, "2x(x+1)");
await page.click(`${q("math-expand")} button`);
if (!/asked-for form/.test(await page.locator(`${q("math-expand")} > .feedback`).textContent())) fail("gallery: math forbid not enforced");
await page.fill(`${q("math-expand")} input`, "2x^2+2x");
if (!(await page.locator(`${q("math-expand")} .math-preview .katex`).count())) fail("gallery: math live preview missing");
await page.click(`${q("math-expand")} button`); await expectOk("math-expand");
await page.fill(`${q("math-bernoulli")} input`, "p - p^2"); await page.click(`${q("math-bernoulli")} button`); await expectOk("math-bernoulli");

// plot: sliders redraw the curve, the shaded area is printed, discrete bars respond; plot-set scores a miss then a hit
const slide = (sel, v) => page.$eval(sel, (el, v) => { el.value = v; el.dispatchEvent(new Event("input", { bubbles: true })); }, String(v));
const dOf = (sel) => page.locator(sel).first().getAttribute("d");
if (await page.locator(".lp-plot svg.plot").count() !== 3) fail("gallery: plot diagrams missing");
const normalArea = () => page.locator("#plot-normal .plot-area").textContent();
if (!/≈ 0\.6827/.test(await normalArea())) fail(`gallery: normal ±1σ area wrong: ${await normalArea()}`);
let before = await dOf("#plot-normal .plot-curve");
await slide('#plot-normal input[data-param="sigma"]', 1.6);
await slide('#plot-normal input[data-param="mu"]', -0.7);
if ((await dOf("#plot-normal .plot-curve")) === before) fail("gallery: normal curve did not redraw");
if (!/from −2\.30 to 0\.90 ≈ 0\.6827/.test(await normalArea())) fail(`gallery: normal area text did not update: ${await normalArea()}`);
if (await page.locator("#plot-normal output").first().textContent() !== "−0.7") fail("gallery: slider value not shown");
before = await dOf("#plot-market .plot-curve.c0");
const vBefore = await page.locator("#plot-market .plot-vline").getAttribute("x1");
await slide('#plot-market input[data-param="d"]', 2);
if ((await dOf("#plot-market .plot-curve.c0")) === before || (await page.locator("#plot-market .plot-vline").getAttribute("x1")) === vBefore)
  fail("gallery: demand shift did not redraw");
if (await page.locator("#plot-market .plot-legend .plot-key").count() !== 2) fail("gallery: legend missing");
const binArea = () => page.locator("#plot-binomial .plot-area").textContent();
if (!/= 0\.6496/.test(await binArea())) fail(`gallery: binomial P(X≤3) wrong: ${await binArea()}`);
before = await dOf("#plot-binomial .plot-bars");
await slide('#plot-binomial input[data-param="p"]', 0.5);
if ((await dOf("#plot-binomial .plot-bars")) === before) fail("gallery: binomial bars did not redraw");
if (!/= 0\.1719/.test(await binArea())) fail(`gallery: binomial area did not update: ${await binArea()}`);
else console.log("ok   gallery: plots redraw, areas update");
await page.click(`${q("plot-mean")} button:text-is("Check")`);
if (await verdictOk("plot-mean")) fail("gallery: plot-set accepted the starting value");
await slide(`${q("plot-mean")} input[data-param="mu"]`, 1.5);
if (!/≈ 0\.8413/.test(await page.locator(`${q("plot-mean")} .plot-area`).textContent())) fail("gallery: plot-set area text did not update");
await page.click(`${q("plot-mean")} button:text-is("Check")`); await expectOk("plot-mean");

// timeline: diagram lanes/rows render; place quiz: a typed wrong year (scored miss, no reveal), then a click on 1757 (right, reveal)
if (await page.locator("#tl-india .tl-bar").count() !== 4 || await page.locator("#tl-india .tl-dot").count() !== 4) fail("gallery: timeline diagram incomplete");
if (!(await page.locator("#tl-india .tl-axis text", { hasText: "BCE" }).count())) fail("gallery: timeline BCE ticks missing");
await page.fill(`${q("tl-plassey")} input`, "1700"); await page.click(`${q("tl-plassey")} button:text-is("Check")`);
if (!/57 years too early/.test(await page.locator(`${q("tl-plassey")} > .feedback`).textContent())) fail("gallery: timeline miss message wrong");
if (await page.locator(`${q("tl-plassey")} .tl-marker.truth`).count()) fail("gallery: timeline revealed the answer after one miss");
{
  await page.locator(`${q("tl-plassey")} svg.tl-svg`).scrollIntoViewIfNeeded();
  const box = await page.locator(`${q("tl-plassey")} svg.tl-svg`).boundingBox();
  const x = await page.evaluate(() => { const v = document.querySelector('.quiz[data-id="tl-plassey"] svg.tl-svg'), W = +v.getAttribute("width");
    return LPTimeline.scale(1500, 1950, 12, W - 12).x(1757) * v.getBoundingClientRect().width / W; });
  await page.mouse.click(box.x + x, box.y + box.height / 2);
  const typed = await page.inputValue(`${q("tl-plassey")} input`);
  if (Math.abs(parseInt(typed, 10) - 1757) > 2) fail(`gallery: timeline click picked ${typed}, wanted ~1757`);
}
await page.click(`${q("tl-plassey")} button:text-is("Check")`); await expectOk("tl-plassey");
if (!(await page.locator(`${q("tl-plassey")} .tl-marker.truth`).count())) fail("gallery: timeline did not show the true position");

// map: basemap drawn from the vendored data; locate quiz: click on Delhi (miss, distance + direction), then pick "Patna" (right)
await page.waitForSelector("#map-south-asia .map-land", { timeout: 8000 }).catch(() => fail("gallery: map basemap did not load"));
if ((await page.locator("#map-south-asia .map-land").first().getAttribute("d") || "").length < 2000) fail("gallery: map land path too small");
if (!(await page.locator("#map-south-asia .map-land.hl").count())) fail("gallery: map highlight missing");
if (await page.locator("#map-south-asia .map-label").count() !== 4) fail("gallery: map labels missing");
const mapClick = async (id, lat, lon) => {
  const sel = `${q(id)} svg.map-svg`;
  await page.locator(sel).scrollIntoViewIfNeeded();
  const box = await page.locator(sel).boundingBox();
  const p = await page.evaluate(([sel, lat, lon]) => { const v = document.querySelector(sel), W = +v.getAttribute("viewBox").split(" ")[2];
    const P = LPMap.projection([60, 5, 100, 38], W).project(lat, lon), k = v.getBoundingClientRect().width / W; return { x: P.x * k, y: P.y * k }; }, [sel, lat, lon]);
  await page.mouse.click(box.x + p.x, box.y + p.y);
};
await mapClick("map-patali", 28.61, 77.21);
await page.click(`${q("map-patali")} button:text-is("Check")`);
const mapMiss = await page.locator(`${q("map-patali")} > .feedback`).textContent();
const missKm = parseInt((mapMiss.match(/Off by (\d+) km/) || [])[1], 10);
if (!(missKm > 830 && missKm < 880) || !/to the east of your pick/.test(mapMiss)) fail(`gallery: map miss message wrong: ${mapMiss}`);
if (await page.locator(`${q("map-patali")} .map-truth`).count()) fail("gallery: map revealed the answer after one miss");
await page.click(`${q("map-patali")} button:text-is("Patna")`);
await page.click(`${q("map-patali")} button:text-is("Check")`); await expectOk("map-patali");
if (!/off by 0 km/.test(await page.locator(`${q("map-patali")} > .feedback`).textContent()) || !(await page.locator(`${q("map-patali")} .map-truth`).count()))
  fail("gallery: map did not show the true point and distance");

// python: Pyodide from the CDN (through the proxy if one is set). Snippet runs numpy; an error in Run is shown, not scored;
// the exercise misses with the assert message (wrong divisor), then is right. If the CDN can't be reached, say so and skip.
let pythonRan = false;
{
  const t0 = Date.now();
  await page.click(`#py-clt button:text-is("Run")`);
  const loaded = await page.waitForFunction(() => {
    const out = document.querySelector("#py-clt pre.py-out"), st = document.querySelector("#py-clt .py-status");
    return (out && !out.hidden) ? "ran" : /Couldn't load/.test(st && st.textContent) ? st.textContent : false;
  }, null, { timeout: 180000 }).then(h => h.jsonValue()).catch(() => "timed out after 180 s");
  if (loaded !== "ran") {
    console.log(`SKIP gallery: python — skipped: CDN unreachable (${loaded})`);
  } else {
    pythonRan = true;
    const out = await page.locator("#py-clt pre.py-out").textContent();
    if (!/mean of means: 0\.4993  theory 0\.5/.test(out) || !/SD of means:   0\.0527  theory 0\.0527/.test(out) || !/0\.471 #{29}\n/.test(out))
      fail(`gallery: python CLT snippet output wrong:\n${out}`);
    else console.log(`ok   gallery: python loaded via ${proxyServer ? "proxy" : "direct"} in ${((Date.now() - t0) / 1000).toFixed(1)} s; numpy CLT: mean 0.4993, SD 0.0527 (theory 0.0527)`);
    const py = q("py-var"), ta = `${py} textarea.py-code`, starter = await page.inputValue(ta);
    if (await page.locator(`${py} script.check`).isVisible() || /statistics/.test(starter)) fail("gallery: python check code is visible");
    await page.fill(ta, "print(undefined_name)");
    await page.click(`${py} button:text-is("Run")`);
    await page.waitForSelector(`${py} pre.py-out .err`, { timeout: 30000 }).catch(() => {});
    const errOut = await page.locator(`${py} pre.py-out`).textContent();
    if (!/NameError: name 'undefined_name' is not defined/.test(errOut) || /_lp_run/.test(errOut)) fail(`gallery: python traceback wrong:\n${errOut}`);
    if (await page.locator(`${py} > .feedback`).count()) fail("gallery: python Run was scored");
    const feedback = () => page.locator(`${py} > .feedback`).textContent();
    await page.fill(ta, starter + "\n    return sum((x - m) ** 2 for x in xs) / n");
    await page.click(`${py} button:text-is("Check")`);
    await page.waitForSelector(`${py} > .feedback .verdict`, { timeout: 30000 }).catch(() => {});
    const miss = await feedback();
    if (!/Not quite.*sample_var\(\[1, 2, 3, 4\]\) gave 1\.25: that divides by n/.test(miss) || /assert|statistics/.test(miss)) fail(`gallery: python miss message wrong: ${miss}`);
    else console.log(`ok   gallery: py-var miss: ${miss}`);
    await page.fill(ta, starter + "\n    return sum((x - m) ** 2 for x in xs) / (n - 1)");
    await page.click(`${py} button:text-is("Check")`);
    await page.waitForSelector(`${py} > .feedback .verdict.ok`, { timeout: 30000 }).catch(() => {});
    await expectOk("py-var");
    // an endless loop is stopped after data-timeout (default 10 s); Python restarts, with a fresh namespace per run
    const runAndRead = async (code, wait) => {
      await page.fill(ta, code); await page.click(`${py} button:text-is("Run")`);
      await page.waitForFunction((sel) => !document.querySelector(sel).disabled, `${py} .py-bar button`, { timeout: wait });
      return page.locator(`${py} pre.py-out`).textContent();
    };
    const t1 = Date.now(), stopped = await runAndRead("while True:\n    pass", 30000);
    if (!/Stopped after 10 s/.test(stopped)) fail(`gallery: python endless loop not stopped: ${stopped}`);
    const fresh = await runAndRead("print('means' in globals(), 'sample_var' in globals())", 60000);
    if (fresh.trim() !== "False False") fail(`gallery: python namespace leaked or no restart: ${fresh}`);
    else console.log(`ok   gallery: python endless loop stopped and restarted in ${((Date.now() - t1) / 1000).toFixed(1)} s; fresh namespace per run`);
    await page.click(`${py} button:text-is("Reset")`);
    if (await page.inputValue(ta) !== starter) fail("gallery: python Reset did not restore the starter code");
  }
}

const bar = await page.locator(".scorebar").textContent();
// choice, go-drive, plot-mean, tl-plassey, map-patali, py-var missed first; free is ungraded. py-var is unanswered if the CDN was unreachable.
const expected = pythonRan ? "18 / 18 answered · 11 right first try" : "17 / 18 answered · 11 right first try";
if (bar.trim() !== expected) fail(`gallery: scorebar "${bar}" != "${expected}"`); else console.log("ok   gallery: scorebar");

await page.click(".lp-footer button:text-is('Just right')");
const log = await page.evaluate(() => JSON.parse(localStorage.getItem("lp.queue") || "[]"));
const attempts = log.filter(e => e.type === "attempt");
if (attempts.length !== (pythonRan ? 18 : 17)) fail(`gallery: expected ${pythonRan ? 18 : 17} logged attempts, got ${attempts.length}`);
if (!log.some(e => e.type === "rating" && e.value === "just-right")) fail("gallery: rating not logged");
if (attempts.some(e => !e.item.startsWith("gallery/widgets#"))) fail("gallery: bad item ids");
const summary = await page.evaluate(() => LP.summary());
if (!new RegExp("missed: choice,go-drive,plot-mean,tl-plassey,map-patali" + (pythonRan ? ",py-var" : "")).test(summary)|| !/rating: just-right/.test(summary) || !/free free:/.test(summary)) fail("gallery: summary wrong:\n" + summary);
else console.log("ok   gallery: event log + summary\n" + summary.split("\n").map(l => "     " + l).join("\n"));

// "I don't know" (data-skip): skip before answering; after a wrong try it becomes "Show me the answer" (no second score)
{
  const pre = await newPage();
  await pre.goto(`${BASE}/topics/statistics/lessons/0001-placement-pretest.html`);
  const pq = (id) => `.quiz[data-id="${id}"]`;
  await pre.click(`${pq("rv-geom")} button.skip`);
  await pre.click(`${pq("prob-union")} button:text-is("0.80")`);
  const label = await pre.locator(`${pq("prob-union")} button.skip`).textContent().catch(() => "");
  if (label !== "Show me the answer") fail(`skip: after a wrong answer the button reads "${label}"`);
  await pre.click(`${pq("prob-union")} button.skip`);
  if (await pre.locator(`${pq("prob-union")} .explain`).isHidden()) fail("skip: answer not revealed after a wrong try");
  await pre.click(`${pq("dist-2sd")} button:text-is("95%")`);
  if (await pre.locator(`${pq("dist-2sd")} button.skip`).count()) fail("skip: button still shown after a right answer");
  const sum = await pre.evaluate(() => LP.summary());
  if (!/missed: prob-union \| skipped: rv-geom/.test(sum) || !/2\/21|1\/21/.test(sum)) fail("skip: summary wrong: " + sum);
  const revealed = await pre.evaluate(() => JSON.parse(localStorage.getItem("lp.queue") || "[]").filter(e => e.type === "reveal").length);
  if (revealed !== 1) fail(`skip: expected 1 reveal event, got ${revealed}`);
  if (!failures) console.log("ok   skip: skip, wrong→show answer, right→hidden\n     " + sum);
  await pre.close();
}

// Daily review deck: old misses (seeded event log, no schedule yet) come back, pulled from their lessons
{
  const rv = await newPage();
  const errs = []; rv.on("pageerror", e => errs.push(e.message));
  await rv.goto(`${BASE}/assets/review.html`);
  const twoDaysAgo = new Date(Date.now() - 2 * 864e5).toISOString(), soon = new Date(Date.now() - 1 * 3600e3).toISOString();
  const evs = [
    { type: "attempt", item: "statistics/0001-placement-pretest#prob-union", kind: "auto", correct: false, ts: twoDaysAgo },
    { type: "attempt", item: "statistics/0001-placement-pretest#dist-poisson", kind: "skip", correct: false, ts: twoDaysAgo },
    { type: "attempt", item: "chess/0001-is-it-safe#q1", kind: "auto", correct: false, ts: twoDaysAgo },
    { type: "attempt", item: "statistics/0002-what-a-p-value-is#find-196", kind: "auto", correct: false, ts: twoDaysAgo },
    { type: "attempt", item: "statistics/9999-deleted#gone", kind: "auto", correct: false, ts: twoDaysAgo },
    { type: "attempt", item: "statistics/0001-placement-pretest#rv-var", kind: "auto", correct: true, ts: soon },   // due in 1 day: not shown
  ];
  await rv.evaluate((evs) => { localStorage.clear(); localStorage.setItem("lp.queue", JSON.stringify(evs)); }, evs);
  await rv.reload();
  await rv.waitForSelector(".review-card", { timeout: 8000 }).catch(() => {});
  const status = await rv.textContent("#deck-status");
  const cards = await rv.locator(".review-card").count();
  if (cards !== 4) fail(`review: expected 4 cards, got ${cards} (${status})`);
  if (!/4 due now/.test(status) || !/1 couldn't be loaded/.test(status)) fail(`review: status "${status}"`);
  await rv.waitForSelector(".review-card .katex", { state: "attached", timeout: 5000 }).catch(() => fail("review: math not typeset"));
  if (!(await rv.locator('.review-card .lp-plot svg, .review-card .quiz[data-type="plot-set"] svg').count())) fail("review: plot not rendered");
  const rq = (id) => `.quiz[data-id="${id}"]`;
  await rv.click(`${rq("statistics/0001-placement-pretest#prob-union")} button:text-is("0.65")`);
  const entry = await rv.evaluate(() => JSON.parse(localStorage.getItem("lp.review"))["statistics/0001-placement-pretest#prob-union"]);
  const days = (new Date(entry.due) - Date.now()) / 864e5;
  if (entry.box !== 1 || days < 2.9 || days > 3.1) fail(`review: schedule not advanced: ${JSON.stringify(entry)}`);
  if (errs.length) fail("review: page errors: " + errs.join("; "));
  if (!failures) console.log(`ok   review: ${cards} due cards from 3 lessons, math+plot rendered, answer moved next review to +3 days\n     ${status}`);
  await rv.close();
}

await browser.close();
server.kill();
console.log(failures ? `\n${failures} failure(s)` : "\nall passed");
process.exit(failures ? 1 : 0);
