// Checks assets/today.js planFor() against the real programs.json and curricula.
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const T = require("../assets/today.js");
const root = new URL("../", import.meta.url);
const cfg = JSON.parse(readFileSync(new URL("programs.json", root)));
const cur = {};
for (const m of cfg.majors) if (m.curriculum) cur[m.slug] = JSON.parse(readFileSync(new URL(m.curriculum, root)));
let fails = 0;
const ok = (c, msg) => { if (!c) { fails++; console.log("FAIL", msg); } };

// 2026-10-05 is a Monday in New York (noon UTC): statistics + aws-ml, and aws-ml lends its block to statistics.
const mon = T.planFor(cfg, cur, new Date("2026-10-05T16:00:00Z"));
ok(mon.day === "mon" && mon.date === "2026-10-05", "Monday date " + JSON.stringify([mon.day, mon.date]));
ok(mon.blocks.length === 2, "two blocks on Monday");
ok(mon.blocks[0].major === "Statistics", "block 1 statistics");
ok(mon.blocks[1].covering === "AWS ML certification" && mon.blocks[1].major === "Statistics", "AWS block covered by Statistics");
const st = mon.blocks[0].items[0];
ok(st.lesson && /0004-power\.html$/.test(st.lesson.href), "statistics points at first unfinished lesson: " + JSON.stringify(st.lesson));
// Late Sunday UTC is still Sunday in New York; Sunday is a rest day.
const sun = T.planFor(cfg, cur, new Date("2026-10-12T02:00:00Z"));
ok(sun.day === "sun" && sun.blocks.length === 0, "Sunday 22:00 New York is a rest day: " + sun.day);
// Games on Thursday: two active courses -> two choices; every lesson link exists on disk.
const thu = T.planFor(cfg, cur, new Date("2026-10-08T16:00:00Z"));
const games = thu.blocks.find(b => b.slug === "games");
ok(games && games.items.length === 2, "games offers G101 and G150");
for (const p of [mon, thu, T.planFor(cfg, cur, new Date("2026-10-10T16:00:00Z"))])
  for (const b of p.blocks) for (const it of b.items || []) if (it.lesson)
    try { readFileSync(new URL(it.lesson.href.replace(/^\.\.\//, ""), root)); } catch { ok(false, "missing " + it.lesson.href); }
ok(T.pretty("0004-power") === "0004 power", "pretty");
console.log(fails ? `today: ${fails} failed` : "today: all checks passed");
process.exit(fails ? 1 : 0);
