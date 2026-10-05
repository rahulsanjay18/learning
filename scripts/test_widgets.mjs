// Browser smoke test for the shared widget library.
//   node scripts/test_widgets.mjs        (from the repo root; needs Playwright + Chromium)
// 1. Opens every lesson, reference page and the gallery; fails on page errors or widgets that didn't initialise.
// 2. Drives every widget in assets/gallery.html and checks scoring + the local event log.
import { createRequire } from "node:module";
import { execSync, spawn } from "node:child_process";
import { readdirSync, existsSync } from "node:fs";
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
let browser;
try { browser = await chromium.launch(exe ? { executablePath: exe } : {}); }
catch { browser = await chromium.launch(); }
let failures = 0;
const fail = (msg) => { failures++; console.log("FAIL " + msg); };

for (const p of pages) {
  const page = await browser.newPage();
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
const page = await browser.newPage();
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

const bar = await page.locator(".scorebar").textContent();
const expected = "15 / 15 answered · 11 right first try"; // choice, go-drive and plot-mean missed first; free is ungraded
if (bar.trim() !== expected) fail(`gallery: scorebar "${bar}" != "${expected}"`); else console.log("ok   gallery: scorebar");

await page.click(".lp-footer button:text-is('Just right')");
const log = await page.evaluate(() => JSON.parse(localStorage.getItem("lp.queue") || "[]"));
const attempts = log.filter(e => e.type === "attempt");
if (attempts.length !== 15) fail(`gallery: expected 15 logged attempts, got ${attempts.length}`);
if (!log.some(e => e.type === "rating" && e.value === "just-right")) fail("gallery: rating not logged");
if (attempts.some(e => !e.item.startsWith("gallery/widgets#"))) fail("gallery: bad item ids");
const summary = await page.evaluate(() => LP.summary());
if (!/missed: choice,go-drive,plot-mean/.test(summary) || !/rating: just-right/.test(summary) || !/free free:/.test(summary)) fail("gallery: summary wrong:\n" + summary);
else console.log("ok   gallery: event log + summary\n" + summary.split("\n").map(l => "     " + l).join("\n"));

await browser.close();
server.kill();
console.log(failures ? `\n${failures} failure(s)` : "\nall passed");
process.exit(failures ? 1 : 0);
