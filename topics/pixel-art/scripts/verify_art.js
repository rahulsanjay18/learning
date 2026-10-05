// Builds every pixel picture used in the lessons from segment lists, runs the same checker the lessons use,
// and asserts each picture gets the verdict the lesson claims. Usage: node scripts/verify_art.js
const PL = require("../../../assets/plugins/pixels.js");

// segs: [["h",3],["v",2],["d",1]...]; a diagonal step joins consecutive segments. extra: [[x,y]] added pixels.
function build(segs, { pad = 1, extra = [] } = {}) {
  const pts = []; let x = 0, y = 0, first = true;
  for (const [dir, n] of segs) {
    if (!first) { x++; y++; } first = false;
    for (let i = 0; i < n; i++) { if (i) dir === "h" ? x++ : y++; pts.push([x, y]); }
  }
  const all = pts.concat(extra);
  const W = Math.max(...all.map(p => p[0])) + 1 + 2 * pad, H = Math.max(...all.map(p => p[1])) + 1 + 2 * pad;
  const set = new Set(all.map(p => `${p[0] + pad},${p[1] + pad}`));
  const rows = [];
  for (let r = 0; r < H; r++) { let s = ""; for (let c = 0; c < W; c++) s += set.has(`${c},${r}`) ? "#" : "."; rows.push(s); }
  return { art: rows.join("|"), a: [pts[0][0] + pad, pts[0][1] + pad], b: [x + pad, y + pad], keys: [...set], W, H };
}
// Re-derive verdict from the art alone (endpoints = pixels with one neighbour, top-left first).
function verdict(pic, mode) {
  const r = PL.check(pic.keys, pic.a, pic.b, mode, 0);
  return r.ok ? "Clean" : (r.kind === "double" ? "Double" : r.kind === "jaggy" ? "Jaggy" : r.kind);
}
function mark(pic, mode) { // art with flagged pixels as "!"
  const r = PL.check(pic.keys, pic.a, pic.b, mode, 0), bad = new Set(r.bad);
  return pic.art.split("|").map((row, y) => row.split("").map((c, x) => bad.has(`${x},${y}`) ? "!" : c).join("")).join("|");
}

const H = n => ["h", n], V = n => ["v", n], S = ["h", 1];
const pics = {
  lineJaggy:  [build([H(3), S, H(2), H(3), S, H(2), H(2)]), "line", "Jaggy"],
  lineClean:  [build([H(2), H(2), H(2), H(2), H(2), H(2), H(2)]), "line", "Clean"],
  lineDouble: [build([H(2), H(2), H(2), H(2), H(2), H(2), H(2)], { extra: [[4, 1]] }), "line", "Double"],
  line11:     [build([S, S, S, S, S, S, S]), "line", "Clean"],
  arcClean:   [build([H(3), H(2), S, S, V(2), V(3)]), "curve", "Clean"],
  arcJaggy:   [build([H(3), S, H(3), S, V(2), V(3)]), "curve", "Jaggy"],
  arcDouble:  [build([H(3), H(2), S, S, V(2), V(3)], { extra: [[5, 1]] }), "curve", "Double"],
  drillArc:   [build([H(4), H(3), H(2), S, S, S, V(2), V(3), V(4)]), "curve", "Clean"],
};
let fail = 0;
for (const [name, [pic, mode, want]] of Object.entries(pics)) {
  const got = verdict(pic, mode);
  console.log(`${got === want ? "ok  " : "FAIL"} ${name.padEnd(11)} ${mode.padEnd(5)} want=${want} got=${got} size=${pic.W}x${pic.H} A=${pic.a} B=${pic.b}`);
  console.log(`     art:    ${pic.art}`);
  if (want !== "Clean") console.log(`     marked: ${mark(pic, mode)}`);
  if (got !== want) fail++;
}
// The 2:1 drill: endpoints and the slope requirement.
const drill = pics.lineClean[0];
const r1 = PL.check(drill.keys, drill.a, drill.b, "line", 2), r2 = PL.check(pics.line11[0].keys, pics.line11[0].a, pics.line11[0].b, "line", 2);
console.log("2:1 drill on clean 2:1 ->", r1.ok, r1.msg); console.log("2:1 drill on 1:1 ->", r2.ok, r2.msg);
// A straight 1:1 diagonal must not pass the curve drill; a gap must fail.
const diag = build([S, S, S, S, S, S, S, S, S, S, S, S, S, S]);
console.log("curve drill on diagonal ->", PL.check(diag.keys, diag.a, diag.b, "curve").msg);
const gap = drill.keys.filter(k => k !== "4,2");
console.log("gap ->", PL.check(gap, drill.a, drill.b, "line", 2).kind, "| empty ->", PL.check([], drill.a, drill.b, "line", 2).kind);
if (r1.ok !== true || r2.ok !== false) fail++;
process.exit(fail ? 1 : 0);
