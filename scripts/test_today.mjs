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

// 2026-10-05 is a Monday in New York (noon UTC): statistics + eng (the engineering career major took the old aws-ml slot).
const mon = T.planFor(cfg, cur, new Date("2026-10-05T16:00:00Z"));
ok(mon.day === "mon" && mon.date === "2026-10-05", "Monday date " + JSON.stringify([mon.day, mon.date]));
ok(mon.blocks.length === 2, "two blocks on Monday");
ok(mon.blocks[0].major === "Statistics", "block 1 statistics");
ok(mon.blocks[1].slug === "eng" && !mon.blocks[1].covering, "block 2 is the engineering career major");
const st = mon.blocks[0].items[0];
// expected = the first written lesson not yet completed (null once all are done: then "next" names the lesson to write)
const s150 = cur.statistics.courses.find(c => c.status === "active");
const want = (s150.lessons || []).find(s => !(s150.completed || []).includes(s)) || null;
ok(want ? st.lesson && st.lesson.href.endsWith(want + ".html") : st.lesson === null && !!st.next,
   "statistics points at first unfinished lesson: " + JSON.stringify(st.lesson));
// eng has lanes: Monday shows only the staff lane's active course(s), Thursday only the interview lane's
const engMon = mon.blocks.find(b => b.slug === "eng");
ok(engMon && engMon.items.length && engMon.items.every(it => it.course.startsWith("SE")), "eng Monday = staff lane: " + JSON.stringify(engMon && engMon.items.map(i => i.course)));
const engThu = T.planFor(cfg, cur, new Date("2026-10-08T16:00:00Z")).blocks.find(b => b.slug === "eng");
ok(engThu && engThu.items.every(it => it.course.startsWith("IV")), "eng Thursday = interview lane");
// the learner's to-do list (todo.json): only open items, oldest first
const todo = JSON.parse(readFileSync(new URL("todo.json", root)));
const open = T.openTodos(todo);
ok(open.length === todo.items.filter(t => !t.done).length && open.every(t => !t.done), "openTodos keeps only open items");
ok(open.every((t, i) => i === 0 || (open[i - 1].added || "") <= (t.added || "")), "openTodos sorted oldest first");
ok(T.openTodos({ items: [{ id: "a", done: true }] }).length === 0, "done items hidden");
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
// a lesson answered on the server (or in this browser) counts as done: the link moves on
// (fixture: IH 0003 as the only unfinished lesson, so the check doesn't break when the learner finishes it)
const cur3 = structuredClone(cur), ih100 = cur3["indian-history"].courses.find(c => c.id === "IH100");
ih100.completed = (ih100.completed || []).filter(s => s !== "0003-the-indus-cities");
ih100.lessons = ih100.lessons.filter(s => s <= "0003-the-indus-cities");
const tue = T.planFor(cfg, cur3, new Date("2026-10-06T16:00:00Z"));
const ih = it => it.course.startsWith("IH100");
const before = tue.blocks.flatMap(b => b.items || []).find(ih);
const after = T.planFor(cfg, cur3, new Date("2026-10-06T16:00:00Z"), ["indian-history/0003-the-indus-cities"])
  .blocks.flatMap(b => b.items || []).find(ih);
ok(before && before.lesson && before.lesson.href.endsWith("0003-the-indus-cities.html"), "IH 0003 is today's lesson");
ok(after && !after.lesson, "answered IH 0003 -> no unfinished IH lesson left");
ok(T.pretty("0004-power") === "0004 power", "pretty");
console.log(fails ? `today: ${fails} failed` : "today: all checks passed");
process.exit(fails ? 1 : 0);
