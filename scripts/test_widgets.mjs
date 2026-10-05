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

const bar = await page.locator(".scorebar").textContent();
const expected = "12 / 12 answered · 9 right first try"; // choice and go-drive missed first; free is ungraded
if (bar.trim() !== expected) fail(`gallery: scorebar "${bar}" != "${expected}"`); else console.log("ok   gallery: scorebar");

await page.click(".lp-footer button:text-is('Just right')");
const log = await page.evaluate(() => JSON.parse(localStorage.getItem("lp.queue") || "[]"));
const attempts = log.filter(e => e.type === "attempt");
if (attempts.length !== 12) fail(`gallery: expected 12 logged attempts, got ${attempts.length}`);
if (!log.some(e => e.type === "rating" && e.value === "just-right")) fail("gallery: rating not logged");
if (attempts.some(e => !e.item.startsWith("gallery/widgets#"))) fail("gallery: bad item ids");
const summary = await page.evaluate(() => LP.summary());
if (!/missed: choice,go-drive/.test(summary) || !/rating: just-right/.test(summary) || !/free free:/.test(summary)) fail("gallery: summary wrong:\n" + summary);
else console.log("ok   gallery: event log + summary\n" + summary.split("\n").map(l => "     " + l).join("\n"));

await browser.close();
server.kill();
console.log(failures ? `\n${failures} failure(s)` : "\nall passed");
process.exit(failures ? 1 : 0);
