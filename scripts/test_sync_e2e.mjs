// End-to-end: browser lesson page -> progress server.   node scripts/test_sync_e2e.mjs   (repo root; needs fastapi+uvicorn, Playwright)
// Starts the progress server with a temp DB, pairs a device through assets/sync.html, answers gallery quizzes,
// and checks the teacher digest and dedup.
import { createRequire } from "node:module";
import { execSync, spawn } from "node:child_process";
import { mkdtempSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require(join(execSync("npm root -g").toString().trim(), "playwright"))); }

const WEB = "http://127.0.0.1:8775", API = "http://127.0.0.1:8776/progress", TEACH = { Authorization: "Bearer teach" };
const web = spawn("python3", ["-m", "http.server", "8775", "--bind", "127.0.0.1"], { stdio: "ignore" });
const api = spawn("python3", ["-m", "uvicorn", "app:app", "--port", "8776", "--host", "127.0.0.1"], {
  cwd: "progress-server", stdio: "ignore",
  env: { ...process.env, PROGRESS_TEACHER_TOKEN: "teach", PROGRESS_DB: join(mkdtempSync(join(tmpdir(), "lp-")), "p.db"), PROGRESS_ORIGINS: WEB },
});
let fails = 0;
const check = (name, ok, extra = "") => { console.log((ok ? "ok   " : "FAIL ") + name + (ok ? "" : " " + extra)); if (!ok) fails++; };
try {
  for (let i = 0; i < 50; i++) { try { if ((await fetch(API + "/health")).ok) break; } catch {} await new Promise(r => setTimeout(r, 200)); }
  const { token } = await (await fetch(API + "/devices", { method: "POST", headers: { ...TEACH, "Content-Type": "application/json" }, body: '{"name":"test"}' })).json();
  check("device created", !!token);

  const exe = existsSync("/opt/pw-browsers/chromium") ? { executablePath: "/opt/pw-browsers/chromium" } : {};
  const browser = await chromium.launch(exe);
  const page = await browser.newPage();
  await page.goto(`${WEB}/assets/sync.html#endpoint=${encodeURIComponent(API)}&token=${token}`);
  check("pairing link removed from address bar", !page.url().includes("token="), page.url());
  await page.click("#test");
  await page.waitForFunction(() => /Connected/.test(document.getElementById("msg").textContent), null, { timeout: 5000 }).catch(() => {});
  check("sync page connects", /Connected/.test(await page.textContent("#msg")), await page.textContent("#msg"));

  await page.goto(`${WEB}/assets/gallery.html`);
  await page.click('.quiz[data-id="choice"] button:text-is("Cramming")');        // miss
  await page.fill('.quiz[data-id="number"] input', "64"); await page.click('.quiz[data-id="number"] button');
  await page.fill('.quiz[data-id="free"] textarea', "Review just before forgetting."); await page.click('.quiz[data-id="free"] button');
  await page.click(".lp-footer button:text-is('Too hard')");
  await page.waitForTimeout(2500);                                              // lp.js flushes 1.5 s after the last event
  check("local queue emptied after sync", (await page.evaluate(() => JSON.parse(localStorage.getItem("lp.queue") || "[]").length)) === 0);

  const summary = await (await fetch(API + "/summary?topic=gallery", { headers: TEACH })).text();
  check("teacher summary", /gallery\/widgets: 1\/2 right first try \| missed: choice \| rating: too-hard \| 1 ungraded/.test(summary), "\n" + summary);
  const status = await (await fetch(API + "/status", { headers: TEACH })).text();
  check("teacher status", /gallery: 2 attempts in 14d \(50% right\)/.test(status) && /ungraded free responses: 1/.test(status), "\n" + status);

  // re-sending the same events (e.g. a lost response) must not double count
  const evs = [{ v: 1, eid: "dup-1", type: "attempt", page: "gallery/widgets", item: "gallery/widgets#exact", kind: "auto", correct: true, ts: new Date().toISOString() }];
  for (let i = 0; i < 2; i++) await fetch(API + "/events", { method: "POST", headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" }, body: JSON.stringify({ events: evs }) });
  const s2 = await (await fetch(API + "/summary?topic=gallery", { headers: TEACH })).text();
  check("dedup by eid", /2\/3 right first try/.test(s2), s2);
  console.log("\n" + status + "\n" + s2);
  await browser.close();
} finally { web.kill(); api.kill(); }
console.log(fails ? `${fails} failure(s)` : "all passed");
process.exit(fails ? 1 : 0);
