// Unit tests for the pure logic in assets/plugins/timeline.js and assets/plugins/map.js, plus a check that every timeline,
// timeline-place, map and map-locate in the repo parses.
//   node scripts/test_timeline_map.js
const fs = require("fs"), path = require("path"), vm = require("vm");
const T = require("../assets/plugins/timeline.js");
const M = require("../assets/plugins/map.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const near = (a, b, tol) => Math.abs(a - b) <= tol;

// ---------- timeline: years ----------
check("formatYear BCE", T.formatYear(-322, true) === "322 BCE" && T.formatYear(-322, false) === "322 BCE");
check("formatYear CE only when both eras", T.formatYear(1526, true) === "1526 CE" && T.formatYear(1526, false) === "1526");
check("formatYear approx", T.formatYear(-268, true, true) === "c. 268 BCE");
check("formatRange BCE", T.formatRange(-321, -185, true, true) === "c. 321–185 BCE", T.formatRange(-321, -185, true, true));
check("formatRange CE", T.formatRange(1526, 1857, true) === "1526–1857 CE" && T.formatRange(1526, 1857, false) === "1526–1857");
check("formatRange across eras", T.formatRange(-200, 100, true) === "200 BCE – 100 CE", T.formatRange(-200, 100, true));
check("parseYear", same(T.parseYear("c-321"), { year: -321, approx: true }) && same(T.parseYear("1947"), { year: 1947, approx: false }));
check("parseYear rejects year 0 and junk", T.parseYear("0") === null && T.parseYear("abc") === null && T.parseYear("") === null);
check("parseYearInput forms", T.parseYearInput("1757") === 1757 && T.parseYearInput("AD 1757") === 1757 && T.parseYearInput("1757 CE") === 1757 &&
  T.parseYearInput("320 BCE") === -320 && T.parseYearInput("320 bc") === -320 && T.parseYearInput("c. 268 B.C.E.") === -268 && T.parseYearInput("-320") === -320);
check("parseYearInput rejects 0 and nonsense", T.parseYearInput("0") === null && T.parseYearInput("year") === null && T.parseYearInput("-5 BCE") === null);
check("no year 0: 1 BCE to 1 CE is one year", T.yearsBetween(-1, 1) === 1 && T.yearsBetween(1, -1) === 1);
check("yearsBetween same era", T.yearsBetween(1757, 1747) === 10 && T.yearsBetween(-322, -185) === 137);
check("yearsBetween 44 BCE to 14 CE = 57", T.yearsBetween(-44, 14) === 57);

// ---------- timeline: ticks ----------
let t = T.niceYearTicks(-600, 1950, 5);
check("ticks -600..1950 by 500, 0 shown as 1 CE", t.step === 500 && same(t.ticks, [-500, 1, 500, 1000, 1500]), JSON.stringify(t));
t = T.niceYearTicks(1500, 1950, 6);
check("ticks 1500..1950 by 100", t.step === 100 && same(t.ticks, [1500, 1600, 1700, 1800, 1900]), JSON.stringify(t));
t = T.niceYearTicks(1500, 1950, 12);
check("ticks 1500..1950 by 50 when room", t.step === 50 && t.ticks.length === 10, JSON.stringify(t));
t = T.niceYearTicks(1940, 1950, 3);
check("ticks are whole years (no 2.5)", t.ticks.every(Number.isInteger) && t.ticks.length <= 3, JSON.stringify(t));
check("ticks never contain 0", [[-10, 10, 5], [-1000, 1000, 3], [-3, 3, 7]].every(a => !T.niceYearTicks(...a).ticks.includes(0)));

// ---------- timeline: lanes + hit-testing ----------
let L = T.assignLanes([{ start: 0, end: 10 }, { start: 5, end: 15 }, { start: 20, end: 30 }, { start: 12, end: 18 }]);
check("lanes: overlaps stack, gaps reuse", same(L.lanes, [0, 1, 0, 0]) && L.count === 2, JSON.stringify(L));
L = T.assignLanes([{ start: 0, end: 10 }, { start: 10, end: 20 }]);
check("lanes: touching items stack", same(L.lanes, [0, 1]), JSON.stringify(L));
L = T.assignLanes([{ start: 0, end: 10 }, { start: 14, end: 20 }], 8);
check("lanes: gap keeps labels apart", L.count === 2, JSON.stringify(L));
L = T.assignLanes([{ start: 30, end: 40 }, { start: 0, end: 10 }, { start: 5, end: 35 }]);
check("lanes: input order kept in output", same(L.lanes, [0, 0, 1]), JSON.stringify(L));
// event rows: labels (width w) around the dot x; no label overlap, and no leader crosses a label in a row above it
const clean = (items, E) => items.every((a, i) => items.every((b, j) => i === j ||
  (E.rows[i] === E.rows[j] ? (E.starts[i] + a.w < E.starts[j] || E.starts[j] + b.w < E.starts[i]) :
   !(E.rows[j] < E.rows[i] && a.x >= E.starts[j] && a.x <= E.starts[j] + b.w))));
let items = [{ x: 100, w: 80 }, { x: 300, w: 80 }], E = T.placeEventRows(items, 0, 400, 10);
check("event rows: far apart share row 0, centred", same(E.rows, [0, 0]) && same(E.starts, [60, 260]), JSON.stringify(E));
// the gallery's crowded right edge at 360px: Panipat, Revolt, Independence within 50px, labels ~100-165px wide
items = [{ x: 51.6, w: 151 }, { x: 265.5, w: 166 }, { x: 304.9, w: 158 }, { x: 315.6, w: 86 }];
E = T.placeEventRows(items, 8, 320, 10);
check("event rows: crowded edge stays clean", clean(items, E) && E.count <= 4 && E.starts.every((s, i) => s >= 8 && s + items[i].w <= 320.001), JSON.stringify(E));
items = [{ x: 100, w: 80 }, { x: 100, w: 80 }]; E = T.placeEventRows(items, 0, 400, 10);
check("event rows: same year still terminates", E.count === 2, JSON.stringify(E));
const sc = T.scale(-600, 1950, 0, 510);
check("scale ends", sc.x(-600) === 0 && sc.x(1950) === 510);
check("yearAt inverts scale", T.yearAt(sc, sc.x(1526)) === 1526 && T.yearAt(sc, sc.x(-268)) === -268);
check("yearAt clamps to range", T.yearAt(sc, -50) === -600 && T.yearAt(sc, 9999) === 1950);
check("yearAt never returns 0", T.yearAt(sc, sc.x(0)) !== 0 && T.yearAt(sc, sc.x(0) - 0.05) === -1);
check("parseSpans/Events", T.parseSpans("c-321:-185:Maurya Empire")[0].approxStart && T.parseEvents("1947:Independence: a new state")[0].label === "Independence: a new state");
for (const bad of ["1857:1526:backwards", "x:1:a", "1:2"]) { let threw = false; try { T.parseSpans(bad); } catch { threw = true; } check(`parseSpans rejects ${bad}`, threw); }
for (const bad of ["1950:1500", "0:100", "abc"]) { let threw = false; try { T.parseRange(bad); } catch { threw = true; } check(`parseRange rejects ${bad}`, threw); }

// ---------- map: distance ----------
// Reference: airmilescalculator.com gives DEL–BOM (airports 28.5665,77.1031 / 19.0887,72.8679) as 1,135 km (ellipsoidal);
// a spherical haversine is within ~0.5% of that. City centres (Wikipedia infoboxes) are ~1,150 km apart.
const air = M.haversine(28.5665, 77.1031, 19.0887, 72.8679);
check("haversine DEL–BOM airports ≈ 1135 km (±0.5%)", near(air, 1134.7, 6), air.toFixed(1));
const city = M.haversine(28.6139, 77.2089, 19.0761, 72.8775);
check("haversine New Delhi–Mumbai centres ≈ 1150 km", near(city, 1150, 10), city.toFixed(1));
check("haversine symmetric, zero on itself", near(M.haversine(19.08, 72.88, 28.61, 77.21), M.haversine(28.61, 77.21, 19.08, 72.88), 1e-9) && M.haversine(10, 20, 10, 20) === 0);
check("haversine quarter meridian = πR/2", near(M.haversine(0, 0, 90, 0), Math.PI * M.R_EARTH / 2, 1e-6));
check("haversine antipodes", near(M.haversine(0, 0, 0, 180), Math.PI * M.R_EARTH, 1e-6));
check("bearing Delhi->Kolkata is south-east", M.compass(M.bearing(28.61, 77.21, 22.57, 88.37)) === "south-east");
check("bearing north / west", M.compass(M.bearing(0, 0, 10, 0)) === "north" && M.compass(M.bearing(0, 0, 0, -10)) === "west");

// ---------- map: projection ----------
const view = [60, 5, 100, 38], P = M.projection(view, 400);
let worst = 0;
for (const [lat, lon] of [[28.61, 77.21], [5, 60], [38, 100], [13.08, 80.28], [-10, 120]]) {
  const p = P.project(lat, lon), b = P.invert(p.x, p.y);
  worst = Math.max(worst, Math.abs(b.lat - lat), Math.abs(b.lon - lon));
}
check("projection round-trip", worst < 1e-9, worst);
const nw = P.project(38, 60), se = P.project(5, 100);
check("projection corners map to the frame", near(nw.x, 0, 1e-9) && near(nw.y, 0, 1e-9) && near(se.x, 400, 1e-9) && near(se.y, P.H, 1e-9));
check("projection aspect uses cos(centre lat)", near(P.H / P.W, 33 / (40 * Math.cos(21.5 * Math.PI / 180)), 1e-9), P.H / P.W);
check("parseView", same(M.parseView("60,5,100,38"), view) && M.parseView("").length === 4);
for (const bad of ["60,5,100", "100,5,60,38", "a,b,c,d"]) { let threw = false; try { M.parseView(bad); } catch { threw = true; } check(`parseView rejects ${bad}`, threw); }
check("parsePoints", same(M.parsePoints("28.61,77.21:Delhi|19.08,72.88:Mumbai").map(p => p.label), ["Delhi", "Mumbai"]));
for (const bad of ["91,0:x", "28.61:Delhi", "a,b:c"]) { let threw = false; try { M.parsePoints(bad); } catch { threw = true; } check(`parsePoints rejects ${bad}`, threw); }

// ---------- map: TopoJSON decoding ----------
// A hand-built quantized topology: two squares sharing an edge (arc 1), the second uses it reversed.
const tiny = { type: "Topology", transform: { scale: [0.5, 0.5], translate: [10, 20] },
  arcs: [[[0, 0], [0, 2], [2, 0]], [[2, 2], [0, -2]], [[2, 0], [-2, 0]], [[2, 2], [2, 0], [0, -2], [-2, 0]]],
  objects: { countries: { type: "GeometryCollection", geometries: [
    { type: "Polygon", arcs: [[0, 1, 2]], id: "004", properties: { name: "Left" } },
    { type: "MultiPolygon", arcs: [[[3, ~1]]], id: "356", properties: { name: "Right" } }] } } };
const arcs = M.decodeArcs(tiny);
check("decodeArcs undoes deltas + transform", same(arcs[0], [[10, 20], [10, 21], [11, 21]]) && same(arcs[1], [[11, 21], [11, 20]]), JSON.stringify(arcs[0]));
const tf = M.features(tiny, "countries");
check("tiny features: closed rings", tf.every(f => f.polygons.every(p => p.every(r => same(r[0], r[r.length - 1])))), JSON.stringify(tf.map(f => f.polygons)));
check("tiny features: shared arc not duplicated", tf[0].polygons[0][0].length === 5 && tf[1].polygons[0][0].length === 5, JSON.stringify(tf.map(f => f.polygons[0][0].length)));
check("tiny features: bbox", same(tf[1].bbox, [11, 20, 12, 21]), JSON.stringify(tf[1].bbox));
check("highlight by name or ISO numeric (any padding)", M.matches(tf[0], "4") && M.matches(tf[0], "004") && M.matches(tf[1], "right") && !M.matches(tf[1], "IND"));

// the vendored basemap: loads like the browser does, every ring closed, India present as 356
const src = fs.readFileSync(path.join(__dirname, "../assets/vendor/world-atlas/countries-50m.js"), "utf8");
const sandbox = { window: {} }; vm.runInNewContext(src, sandbox);
const topo = sandbox.window.LPWorldAtlas["countries-50m"];
const world = M.features(topo, "countries");
let rings = 0, open = 0;
world.forEach(f => f.polygons.forEach(p => p.forEach(r => { rings++; const a = r[0], b = r[r.length - 1]; if (Math.abs(a[0] - b[0]) > 1e-9 || Math.abs(a[1] - b[1]) > 1e-9 || r.length < 4) open++; })));
check(`world-atlas 50m: ${world.length} countries, ${rings} rings, all closed`, world.length > 200 && open === 0, `${open} open`);
const india = world.find(f => M.matches(f, "India"));
check("India is id 356, bbox around 68–97 E, 6–36 N", india && india.id === "356" && india.bbox[0] > 67 && india.bbox[0] < 70 && india.bbox[2] > 96 && india.bbox[2] < 98 && india.bbox[1] > 6 && india.bbox[1] < 8 && india.bbox[3] > 35 && india.bbox[3] < 37.5,
  india && JSON.stringify(india.bbox));
check("every world coordinate is a valid lon/lat", world.every(f => f.bbox[0] >= -180 && f.bbox[2] <= 180 && f.bbox[1] >= -90 && f.bbox[3] <= 90));

// ---------- every timeline / map in the repo parses ----------
const files = [path.join(__dirname, "../assets/gallery.html")];
for (const tp of fs.readdirSync(path.join(__dirname, "../topics")))
  for (const dir of ["lessons", "reference"]) {
    const full = path.join(__dirname, "../topics", tp, dir);
    if (fs.existsSync(full)) for (const f of fs.readdirSync(full)) if (f.endsWith(".html")) files.push(path.join(full, f));
  }
const unesc = s => s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
const attr = (tag, n) => { const m = tag.match(new RegExp(`data-${n}="([^"]*)"`)); return m ? unesc(m[1]) : null; };
for (const f of files) {
  const html = fs.readFileSync(f, "utf8").replace(/\s+/g, " ");
  for (const tag of html.match(/<div[^>]*(class="lp-timeline"|data-type="timeline-place"|class="lp-map"|data-type="map-locate")[^>]*>/g) || []) {
    const name = `${path.relative(path.join(__dirname, ".."), f)} ${attr(tag, "id") || (tag.match(/ id="([^"]*)"/) || [])[1] || "?"}`;
    let err = "";
    try {
      if (/timeline/.test(tag)) {
        const r = T.parseRange(attr(tag, "range")); T.parseSpans(attr(tag, "spans")); T.parseEvents(attr(tag, "events"));
        if (/timeline-place/.test(tag)) {
          const a = T.parseYearInput(attr(tag, "answer"));
          if (a == null || a < r[0] || a > r[1]) throw new Error("answer missing or outside range");
          if (T.parseEvents(attr(tag, "events")).some(e => e.year === a)) throw new Error("an event gives the answer away");
        }
      } else {
        const v = M.parseView(attr(tag, "view")); M.parsePoints(attr(tag, "points")); M.parsePoints(attr(tag, "choices"));
        if (/map-locate/.test(tag)) {
          const a = M.parseLatLon(attr(tag, "answer"));
          if (!a) throw new Error("answer is not lat,lon");
          if (a.lon < v[0] || a.lon > v[2] || a.lat < v[1] || a.lat > v[3]) throw new Error("answer is outside data-view");
          const ch = M.parsePoints(attr(tag, "choices")), tol = parseFloat(attr(tag, "tolerance-km") || "250");
          if (ch.length && ch.filter(c => M.haversine(c.lat, c.lon, a.lat, a.lon) <= tol).length !== 1) throw new Error("exactly one choice must be within tolerance");
        }
      }
    } catch (e) { err = e.message; }
    check(`${name}: valid`, !err, err);
  }
}

console.log(fails ? `\n${fails} failure(s)` : "\nall passed");
process.exit(fails ? 1 : 0);
