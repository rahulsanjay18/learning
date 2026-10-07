// Screenshot widgets so a diagram can be LOOKED AT before it ships (render → look → fix; idea from amosblomqvist/learn).
//   node scripts/snap.mjs <page.html> [css selector, default ".lp-diagram"] [--dark] [--out DIR] [--width 420]
// Writes one PNG per matching element to DIR (default: $TMPDIR/snaps) and prints the paths. Read them with the Read tool.
import { createRequire } from "node:module";
import { execSync, spawn } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { join, resolve, relative } from "node:path";
import { tmpdir } from "node:os";
import { createServer } from "node:net";

const args = process.argv.slice(2), flag = (k) => { const i = args.indexOf(k); return i >= 0 ? args.splice(i, 2)[1] : undefined; };
const dark = args.includes("--dark"); if (dark) args.splice(args.indexOf("--dark"), 1);
const out = flag("--out") || join(process.env.TMPDIR || tmpdir(), "snaps"), width = +(flag("--width") || 760);
const [page, selector = ".lp-diagram"] = args;
if (!page) { console.error("usage: node scripts/snap.mjs <page.html> [selector] [--dark] [--out DIR] [--width PX]"); process.exit(2); }
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); } catch { ({ chromium } = require(join(execSync("npm root -g").toString().trim(), "playwright"))); }
const port = await new Promise(r => { const s = createServer(); s.listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => r(p)); }); });
const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], { stdio: "ignore" });
await new Promise(r => setTimeout(r, 700));
const exe = existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined;
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
try {
  const p = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: dark ? "dark" : "light", deviceScaleFactor: 1.5 });
  const errors = []; p.on("pageerror", e => errors.push(e.message));
  await p.goto(`http://127.0.0.1:${port}/${relative(process.cwd(), resolve(page))}`, { waitUntil: "load" });
  await p.addStyleTag({ content: ".scorebar { display: none !important; }" });   // the fixed score bar would cover captions
  await p.waitForTimeout(300);
  mkdirSync(out, { recursive: true });
  const els = await p.locator(selector).all();
  for (const [i, el] of els.entries()) {
    const id = (await el.getAttribute("id")) || `${i}`, err = await el.getAttribute("data-lp-error");
    const f = join(out, `${page.replace(/[\/.]/g, "_")}-${id}${dark ? "-dark" : ""}.png`);
    await el.screenshot({ path: f });
    console.log(f + (err ? "   ERROR: " + err : ""));
  }
  if (!els.length) console.log(`no elements match ${selector}`);
  if (errors.length) console.log("page errors: " + errors.join("; "));
} finally { await browser.close(); server.kill(); }
