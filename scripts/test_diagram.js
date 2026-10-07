// Unit tests for assets/plugins/diagram.js (graph layout, set expressions, sequences), plus a check that every .lp-diagram in
// the repo parses and lays out.   node scripts/test_diagram.js
const fs = require("fs"), path = require("path");
const D = require("../assets/plugins/diagram.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const throws = (f, re) => { try { f(); return false; } catch (e) { return re.test(e.message); } };

// ---------- graph ----------
let g = D.parseGraph("ax:The three axioms", "ax>comp|ax>mono:Thm 1.2.8|comp>bonf");
check("nodes from edges get their id as label", same(g.nodes.map(n => n.label), ["The three axioms", "comp", "mono", "bonf"]));
check("edge label and dashes", g.edges[1].label === "Thm 1.2.8" && !g.edges[0].dashed && D.parseEdge("a~>b").dashed);
check("cycles rejected", throws(() => D.parseGraph("", "a>b|b>c|c>a"), /cycle/));
check("self-loop rejected", throws(() => D.parseGraph("", "a>a"), /self-loop/));
check("bad edge rejected", throws(() => D.parseGraph("", "a-b"), /bad edge/));
let L = D.layoutGraph(g), lab0;
const box = id => L.boxes.find(b => b.id === id);
check("down: every edge points down", g.edges.every(e => box(e.from).y < box(e.to).y));
const overlap = (a, b) => Math.abs(a.x - b.x) < (a.w + b.w) / 2 && Math.abs(a.y - b.y) < (a.h + b.h) / 2;
const noOverlap = L => L.boxes.every((a, i) => L.boxes.every((b, j) => i >= j || !overlap(a, b)));
check("no boxes overlap", noOverlap(L));
check("everything inside the canvas", L.boxes.every(b => b.x - b.w / 2 >= 0 && b.y - b.h / 2 >= 0 && b.x + b.w / 2 <= L.width && b.y + b.h / 2 <= L.height));
check("edges start at the source box and end at the target box", L.edges.every(e => {
  const s = box(e.from), t = box(e.to), p = e.pts[0], q = e.pts[e.pts.length - 1];
  return Math.abs(p.y - (s.y + s.h / 2)) < 0.01 && Math.abs(q.y - (t.y - t.h / 2)) < 0.01; }));
// a crossing-prone input order: K2,2 plus a chain is planar when ordered well
g = D.parseGraph("", "a>d|b>c|a>e|b>f|c>g|d>h");
L = D.layoutGraph(g);
check("ordering removes avoidable crossings", L.crossings === 0, "crossings=" + L.crossings);
g = D.parseGraph("", "a>b|b>c|c>d|a>d");
L = D.layoutGraph(g);
check("long edge routed through dummy points", L.edges[3].pts.length === 4, JSON.stringify(L.edges[3].pts.length));
check("long edge layers: d below c", L.boxes.find(b => b.id === "d").y > L.boxes.find(b => b.id === "c").y);
L = D.layoutGraph(D.parseGraph("", "a>b|a>c"), "right");
check("right: edges point right", L.edges.every(e => e.pts[0].x < e.pts[e.pts.length - 1].x) && noOverlap(L));
check("wrapLabel", same(D.wrapLabel("P of the complement equals one minus P", 20), ["P of the complement", "equals one minus P"]));

// ---------- edge labels ----------
g = D.parseGraph("a:One clue|b:Another clue|c:A third clue|r:Result", "a>r:gods and language already exist|b>r:latest parts no older|c>r:count back through the texts");
({ L, labels: lab0 } = D.layoutWithLabels(g));
const lab = lab0;
const ovl = (a, b) => Math.abs(a.x - b.x) < (a.w + b.w) / 2 && Math.abs(a.y - b.y) < (a.h + b.h) / 2;
check("fan-in: every label found a clean spot", lab.every(r => r.ok), JSON.stringify(lab.map(r => r.ok)));
check("fan-in: labels don't overlap each other", lab.every((a, i) => lab.every((b, j) => i >= j || !ovl(a, b))));
check("fan-in: labels don't overlap nodes", lab.every(a => L.boxes.every(b => !ovl(a, b))));
check("fan-in: no other edge runs through a label", lab.every((a, i) => L.edges.every((e, j) => i === j ||
  Array.from({ length: 41 }, (_, k) => D.pointAt(e.pts, false, k / 40)).every(q => !(Math.abs(q.x - a.x) < a.w / 2 - 2 && Math.abs(q.y - a.y) < a.h / 2 - 2)))));
check("pointAt ends are the edge ends", (() => { const e = L.edges[0], p0 = D.pointAt(e.pts, false, 0), p1 = D.pointAt(e.pts, false, 1);
  return Math.hypot(p0.x - e.pts[0].x, p0.y - e.pts[0].y) < 1e-9 && Math.hypot(p1.x - e.pts.at(-1).x, p1.y - e.pts.at(-1).y) < 1e-9; })());

// ---------- sets ----------
const S2 = ["A", "B"], S3 = ["A", "B", "C"];
const regs = (e, n) => JSON.stringify(D.shadedRegions(e, n));
check("A ∩ B is one region", regs("A ∩ B", S2) === "[[true,true]]");
check("A only", regs("A & !B", S2) === "[[true,false]]" && regs("A \\ B", S2) === regs("A - B", S2) && regs("A−B", S2) === regs("A & not B", S2));
check("De Morgan: (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ", regs("(A ∪ B)ᶜ", S2) === regs("A' ∩ B'", S2) && regs("(A|B)^c", S2) === "[[false,false]]");
check("De Morgan: (A ∩ B)' = A' ∪ B'", regs("(A ∩ B)'", S2) === regs("A' ∪ B'", S2));
check("distributive law", regs("A ∩ (B ∪ C)", S3) === regs("(A ∩ B) ∪ (A ∩ C)", S3));
check("∩ binds tighter than ∪", regs("A ∪ B ∩ C", S3) === regs("A ∪ (B ∩ C)", S3));
check("unknown set rejected", throws(() => D.parseSetExpr("A ∩ D", S3), /unknown set/));
check("unbalanced rejected", throws(() => D.parseSetExpr("(A ∩ B", S3), /missing \)/));
check("multi-letter names", regs("Rain and not Wind", ["Rain", "Wind"]) === "[[true,false]]");

// ---------- sequence ----------
let sq = D.parseSequence("Client|Server", "Client>Server:SYN|Server~>Client:SYN-ACK|Client>Client:wait");
let Q = D.layoutSequence(sq);
check("sequence: columns in order, rows go down", Q.x[0] < Q.x[1] && Q.rows.every((r, i) => !i || r > Q.rows[i - 1]));
check("sequence: long label widens the gap", D.layoutSequence(D.parseSequence("A|B", "A>B:" + "x".repeat(60))).x[1] - 0 > 60 * 7);
check("sequence: unknown actor rejected", throws(() => D.parseSequence("A|B", "A>C:hi"), /unknown actor/));

// ---------- every diagram in the repo ----------
const files = ["assets/gallery.html"];
for (const t of fs.readdirSync("topics")) for (const d of ["lessons", "reference"]) {
  const dir = path.join("topics", t, d);
  if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) if (f.endsWith(".html")) files.push(path.join(dir, f));
}
const attr = (tag, k) => { const m = new RegExp(`data-${k}="([^"]*)"`).exec(tag); return m ? m[1].replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&amp;/g, "&").replace(/&quot;/g, '"') : undefined; };
let n = 0;
for (const f of files) {
  for (const m of fs.readFileSync(f, "utf8").matchAll(/<div class="lp-diagram"[^>]*>/g)) {
    const tag = m[0], kind = attr(tag, "kind") || "graph", where = `${f}: ${kind} ${attr(tag, "caption") || ""}`.trim();
    n++;
    try {
      if (kind === "graph") {
        const G = D.parseGraph(attr(tag, "nodes"), attr(tag, "edges")), LL = D.layoutGraph(G, attr(tag, "dir"));
        if (G.nodes.length > 12) throw new Error(`${G.nodes.length} nodes: split it (one idea, fewest elements)`);
        if (!noOverlap(LL)) throw new Error("boxes overlap");
        const bad = D.layoutWithLabels(G, attr(tag, "dir")).labels.filter(r => r && !r.ok);
        if (bad.length) throw new Error("edge labels collide: " + bad.map(r => r.lines.join(" ")).join("; ") + " (shorten them or drop some)");
      } else if (kind === "sequence") D.layoutSequence(D.parseSequence(attr(tag, "actors"), attr(tag, "steps")));
      else if (kind === "venn") { const s = (attr(tag, "sets") || "").split("|"); if (attr(tag, "shade")) D.shadedRegions(attr(tag, "shade"), s); }
      else throw new Error("unknown kind");
      check(where, true);
    } catch (e) { check(where, false, e.message); }
  }
}
console.log(`${n} diagram(s) in the repo checked`);
process.exit(fails ? 1 : 0);
