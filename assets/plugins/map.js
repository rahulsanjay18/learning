// Map plugin: offline outline maps (country borders) with labelled points, and a "click where it is" quiz. Load after assets/lp.js;
// style: assets/plugins/map.css. No tiles, no map service, nothing fetched from the web: the basemap is Natural Earth 1:50m
// (public domain) via world-atlas (ISC), vendored in assets/vendor/world-atlas/ and loaded on first use.
//
// Coordinates are decimal degrees, "lat,lon" (north and east positive): Delhi = "28.61,77.21".
// data-view="lon1,lat1,lon2,lat2" crops the map (west, south, east, north), e.g. South Asia "60,5,100,38". Default: the world.
// Projection: equirectangular, x scaled by cos(centre latitude) so shapes look right near the middle of the view.
//
// Diagram (unscored):
//   <div class="lp-map" data-view="60,5,100,38" data-points="28.61,77.21:Delhi|19.08,72.88:Mumbai"
//        [data-highlight="India|586"]       countries to tint, by name ("India", as world-atlas spells it) or ISO 3166-1 numeric code
//                                           ("356", "4" = "004"); world-atlas has no ISO alpha-3 codes ("IND" won't match)
//        [data-caption="…"]></div>
// Quiz (scored):
//   <div class="quiz" data-type="map-locate" data-id="…" data-view="60,5,100,38" data-answer="25.59,85.14" [data-tolerance-km="250"]
//        [data-points="…" context, never the answer] [data-highlight="…"]
//        [data-choices="25.59,85.14:Patna|28.61,77.21:Delhi|…"]>    labelled candidate points as buttons (keyboard users)
//     <p class="prompt">Click where Pataliputra stood.</p><div class="explain" hidden>…</div></div>
//   The learner taps the map (or picks a candidate button) and presses Check. Right = great-circle (haversine) distance from the
//   answer ≤ data-tolerance-km (default 250). A miss says how far off and in which direction; the true point is drawn once right
//   or after a second miss. Without data-choices the quiz needs a mouse or touch screen, and says so.
// Pure helpers are exported for Node (node scripts/test_timeline_map.js): decodeArcs, features, projection, haversine, bearing,
// compass, parsePoints, parseView, matches.
(function () {
  "use strict";

  // ---------- pure logic ----------
  // TopoJSON arcs -> arrays of [lon, lat]. Quantized topologies store delta-encoded integers; transform maps them to degrees.
  function decodeArcs(topo) {
    var t = topo.transform;
    return topo.arcs.map(function (arc) {
      var x = 0, y = 0;
      return arc.map(function (p) {
        if (!t) return [p[0], p[1]];
        x += p[0]; y += p[1];
        return [x * t.scale[0] + t.translate[0], y * t.scale[1] + t.translate[1]];
      });
    });
  }
  // One ring from a list of arc indexes (~i = arc i reversed). Consecutive arcs share an end point, kept once.
  function ring(arcs, idx) {
    var out = [];
    idx.forEach(function (i, n) {
      var a = i >= 0 ? arcs[i] : arcs[~i].slice().reverse();
      for (var k = n ? 1 : 0; k < a.length; k++) out.push(a[k]);
    });
    return out;
  }
  // GeometryCollection -> [{id, name, polygons: [[ring, hole…], …], bbox: [w, s, e, n]}]
  function features(topo, objectName, arcs) {
    arcs = arcs || decodeArcs(topo);
    var obj = topo.objects[objectName || "countries"];
    return obj.geometries.map(function (g) {
      var polys = g.type === "Polygon" ? [g.arcs] : g.type === "MultiPolygon" ? g.arcs : [];
      var polygons = polys.map(function (p) { return p.map(function (r) { return ring(arcs, r); }); });
      var bb = [Infinity, Infinity, -Infinity, -Infinity];
      polygons.forEach(function (p) { p[0].forEach(function (q) {
        if (q[0] < bb[0]) bb[0] = q[0]; if (q[1] < bb[1]) bb[1] = q[1]; if (q[0] > bb[2]) bb[2] = q[0]; if (q[1] > bb[3]) bb[3] = q[1];
      }); });
      return { id: g.id == null ? null : String(g.id), name: (g.properties && g.properties.name) || "", polygons: polygons, bbox: bb };
    });
  }
  // view = [lonW, latS, lonE, latN]; width W px. project(lat, lon) -> {x, y}; invert(x, y) -> {lat, lon}.
  function projection(view, W) {
    var k = Math.cos((view[1] + view[3]) / 2 * Math.PI / 180), s = W / ((view[2] - view[0]) * k);
    return {
      W: W, H: (view[3] - view[1]) * s, k: k, s: s,
      project: function (lat, lon) { return { x: (lon - view[0]) * k * s, y: (view[3] - lat) * s }; },
      invert: function (x, y) { return { lat: view[3] - y / s, lon: view[0] + x / (k * s) }; }
    };
  }
  var R_EARTH = 6371.0088;   // mean Earth radius (IUGG), km
  function rad(d) { return d * Math.PI / 180; }
  // Great-circle distance in km.
  function haversine(lat1, lon1, lat2, lon2) {
    var dLat = rad(lat2 - lat1), dLon = rad(lon2 - lon1);
    var a = Math.pow(Math.sin(dLat / 2), 2) + Math.cos(rad(lat1)) * Math.cos(rad(lat2)) * Math.pow(Math.sin(dLon / 2), 2);
    return 2 * R_EARTH * Math.asin(Math.min(1, Math.sqrt(a)));
  }
  // Initial bearing from point 1 to point 2, degrees clockwise from north.
  function bearing(lat1, lon1, lat2, lon2) {
    var y = Math.sin(rad(lon2 - lon1)) * Math.cos(rad(lat2));
    var x = Math.cos(rad(lat1)) * Math.sin(rad(lat2)) - Math.sin(rad(lat1)) * Math.cos(rad(lat2)) * Math.cos(rad(lon2 - lon1));
    return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
  }
  function compass(deg) { return ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"][Math.round(deg / 45) % 8]; }
  function parseLatLon(s) {
    var p = String(s || "").split(",").map(function (t) { return parseFloat(t); });
    if (p.length !== 2 || !isFinite(p[0]) || !isFinite(p[1]) || Math.abs(p[0]) > 90 || Math.abs(p[1]) > 180) return null;
    return { lat: p[0], lon: p[1] };
  }
  // "28.61,77.21:Delhi|19.08,72.88:Mumbai" -> [{lat, lon, label}]
  function parsePoints(s) {
    return String(s || "").split("|").map(function (t) { return t.trim(); }).filter(Boolean).map(function (t) {
      var i = t.indexOf(":"), ll = parseLatLon(i > 0 ? t.slice(0, i) : t);
      if (!ll) throw new Error("bad point “" + t + "” (want lat,lon:label)");
      ll.label = i > 0 ? t.slice(i + 1).trim() : "";
      return ll;
    });
  }
  function parseView(s) {
    if (!s) return [-180, -58, 180, 84];
    var v = String(s).split(",").map(parseFloat);
    if (v.length !== 4 || v.some(function (x) { return !isFinite(x); }) || !(v[2] > v[0]) || !(v[3] > v[1]))
      throw new Error("data-view must be lonW,latS,lonE,latN, e.g. 60,5,100,38");
    return v;
  }
  // Does feature f match a highlight token (ISO numeric code, any zero padding, or name, case-insensitive)?
  function matches(f, token) {
    token = String(token).trim();
    if (/^\d+$/.test(token)) return f.id != null && parseInt(f.id, 10) === parseInt(token, 10);
    return f.name.toLowerCase() === token.toLowerCase();
  }
  function textWidth(s, px) { return String(s).length * (px || 12) * 0.56; }

  var api = { decodeArcs: decodeArcs, features: features, projection: projection, haversine: haversine, bearing: bearing,
    compass: compass, parseLatLon: parseLatLon, parsePoints: parsePoints, parseView: parseView, matches: matches, R_EARTH: R_EARTH };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }
  window.LPMap = api;

  // ---------- basemap loading (one <script>, shared by every map on the page) ----------
  var DATA_URL = new URL("../vendor/world-atlas/countries-50m.js", document.currentScript ? document.currentScript.src : location.href).href;
  var world = null, waiting = null;
  function withWorld(cb) {
    if (world) return cb(world);
    if (waiting) return waiting.push(cb);
    waiting = [cb];
    var done = function (ok) {
      var topo = window.LPWorldAtlas && window.LPWorldAtlas["countries-50m"];
      world = ok && topo ? features(topo, "countries") : [];
      if (!world.length) world.failed = true;
      var q = waiting; waiting = null; q.forEach(function (f) { f(world); });
    };
    if (window.LPWorldAtlas && window.LPWorldAtlas["countries-50m"]) return done(true);
    var s = document.createElement("script");
    s.src = DATA_URL; s.onload = function () { done(true); }; s.onerror = function () { done(false); };
    document.head.appendChild(s);
  }

  // ---------- drawing ----------
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }
  function r1(v) { return Math.round(v * 10) / 10; }

  function pathFor(f, view, P) {
    var d = "", padLon = (view[2] - view[0]) * 0.05, padLat = (view[3] - view[1]) * 0.05;
    if (f.bbox[2] < view[0] - padLon || f.bbox[0] > view[2] + padLon || f.bbox[3] < view[1] - padLat || f.bbox[1] > view[3] + padLat) return "";
    f.polygons.forEach(function (poly) {
      poly.forEach(function (rg) {
        var lx = null, ly = null, part = "";
        rg.forEach(function (q, i) {
          var p = P.project(q[1], q[0]), x = r1(p.x), y = r1(p.y);
          if (i && i < rg.length - 1 && Math.abs(x - lx) < 0.5 && Math.abs(y - ly) < 0.5) return;   // sub-pixel detail
          part += (i ? "L" : "M") + x + "," + y; lx = x; ly = y;
        });
        d += part + "Z";
      });
    });
    return d;
  }

  // Places point labels right, left, above or below their dot, avoiding earlier labels and staying inside the frame.
  function placeLabels(pts, W, H) {
    var boxes = pts.map(function (p) { return [p.x - 4, p.y - 4, p.x + 4, p.y + 4]; }), out = [];
    pts.forEach(function (p) {
      if (!p.label) { out.push(null); return; }
      var w = textWidth(p.label, 12), h = 13, cands = [
        { x: p.x + 7, y: p.y + 4, a: "start", b: [p.x + 6, p.y - 8, p.x + 8 + w, p.y + 5] },
        { x: p.x - 7, y: p.y + 4, a: "end", b: [p.x - 8 - w, p.y - 8, p.x - 6, p.y + 5] },
        { x: p.x, y: p.y - 8, a: "middle", b: [p.x - w / 2, p.y - 8 - h + 2, p.x + w / 2, p.y - 6] },
        { x: p.x, y: p.y + 17, a: "middle", b: [p.x - w / 2, p.y + 6, p.x + w / 2, p.y + 19] }];
      var hit = function (b) { return boxes.some(function (o) { return b[0] < o[2] && b[2] > o[0] && b[1] < o[3] && b[3] > o[1]; }); };
      var inside = function (b) { return b[0] >= 2 && b[2] <= W - 2 && b[1] >= 2 && b[3] <= H - 2; };
      var c = cands.filter(function (c) { return inside(c.b) && !hit(c.b); })[0] || cands.filter(function (c) { return inside(c.b); })[0] || cands[0];
      boxes.push(c.b); out.push(c);
    });
    return out;
  }

  function draw(frame, cfg, overlay) {
    var W = Math.max(260, Math.round(frame.clientWidth) || 560), P = projection(cfg.view, W), H = Math.round(P.H);
    var svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, "class": "map-svg", role: cfg.interactive ? "group" : "img",
      "aria-label": cfg.aria || ("Map" + (cfg.points.length ? " showing " + cfg.points.map(function (p) { return p.label; }).filter(Boolean).join(", ") : "")) });
    var clipId = "mapclip" + (++draw.n);
    var clip = svgEl("clipPath", { id: clipId }); clip.appendChild(svgEl("rect", { x: 0, y: 0, width: W, height: H })); svg.appendChild(clip);
    svg.appendChild(svgEl("rect", { x: 0, y: 0, width: W, height: H, "class": "map-sea" }));
    var g = svgEl("g", { "clip-path": "url(#" + clipId + ")" });
    if (world && world.failed) {
      svg.appendChild(svgEl("text", { x: W / 2, y: H / 2, "text-anchor": "middle", "class": "map-msg" }, "Map data could not be loaded."));
    } else if (world) {
      var land = "", hl = "";
      world.forEach(function (f) {
        var d = pathFor(f, cfg.view, P);
        if (!d) return;
        if (cfg.highlight.some(function (t) { return matches(f, t); })) hl += d; else land += d;
      });
      g.appendChild(svgEl("path", { d: land || "M0,0", "class": "map-land" }));
      if (hl) g.appendChild(svgEl("path", { d: hl, "class": "map-land hl" }));
    }
    svg.appendChild(g);
    var pts = cfg.points.map(function (p) { var q = P.project(p.lat, p.lon); return { x: q.x, y: q.y, label: p.label }; });
    var labels = placeLabels(pts, W, H), gp = svgEl("g", { "class": "map-points" });
    pts.forEach(function (p, i) {
      var c = svgEl("circle", { cx: r1(p.x), cy: r1(p.y), r: 3.5, "class": "map-dot" });
      if (p.label) c.appendChild(svgEl("title", {}, p.label));
      gp.appendChild(c);
      var L = labels[i];
      if (L) gp.appendChild(svgEl("text", { x: r1(L.x), y: r1(L.y), "text-anchor": L.a, "class": "map-label" }, p.label));
    });
    svg.appendChild(gp);
    svg.appendChild(svgEl("rect", { x: 0.5, y: 0.5, width: W - 1, height: H - 1, "class": "map-frame-line" }));
    if (overlay) overlay(svg, P, W, H);
    frame.innerHTML = "";
    frame.appendChild(svg);
    return { svg: svg, P: P, W: W, H: H };
  }
  draw.n = 0;

  function config(el) {
    return { view: parseView(el.dataset.view), points: parsePoints(el.dataset.points),
      highlight: String(el.dataset.highlight || "").split("|").map(function (t) { return t.trim(); }).filter(Boolean) };
  }
  function redrawOnResize(frame, fn) {
    var lastW = frame.clientWidth;
    if (window.ResizeObserver) new ResizeObserver(function () {
      if (frame.clientWidth && Math.round(frame.clientWidth) !== Math.round(lastW)) { lastW = frame.clientWidth; fn(); }
    }).observe(frame);
  }

  function initMap(el) {
    var cfg = config(el), frame = document.createElement("div");
    frame.className = "map-box";
    el.innerHTML = "";
    el.appendChild(frame);
    if (el.dataset.caption) { var c = document.createElement("div"); c.className = "map-caption"; c.textContent = el.dataset.caption; el.appendChild(c); }
    var go = function () { draw(frame, cfg); };
    go(); withWorld(go); redrawOnResize(frame, go);
  }

  function initLocate(q, ctx) {
    var U = LP.util, cfg = config(q), d = q.dataset;
    var answer = parseLatLon(d.answer);
    if (!answer) throw new Error("data-answer must be lat,lon, e.g. 28.61,77.21");
    var tol = parseFloat(d.toleranceKm || "250") || 250;
    var choices = d.choices ? parsePoints(d.choices) : [];
    cfg.interactive = true;
    cfg.aria = "Map: tap where you think the place is";
    var guess = null, misses = 0, done = false, reveal = false, view = null;

    var frame = U.el("div", "map-box interactive");
    U.beforeExplain(q, frame);
    var buttons = [];
    if (choices.length) {
      var crow = U.el("div", "choices map-choices");
      choices.forEach(function (c) {
        var b = U.el("button", null, c.label);
        b.addEventListener("click", function () { if (done) return; buttons.forEach(function (x) { x.classList.remove("on"); }); b.classList.add("on"); pick(c); });
        buttons.push(b); crow.appendChild(b);
      });
      U.beforeExplain(q, U.el("p", "map-note", "Tap the map, or choose one of these places:"));
      U.beforeExplain(q, crow);
    } else {
      U.beforeExplain(q, U.el("p", "map-note", "This question needs a mouse or touch screen: tap the map, then press Check."));
    }
    var row = U.el("div", "actions"), check = U.el("button", null, "Check");
    row.appendChild(check); U.beforeExplain(q, row);

    function overlay(svg, P) {
      var g = svgEl("g", { "class": "map-marks" });
      if (!done) g.appendChild(svgEl("rect", { x: 0, y: 0, width: P.W, height: P.H, "class": "map-hit" }));
      var a = P.project(answer.lat, answer.lon);
      if (guess) {
        var p = P.project(guess.lat, guess.lon);
        if (reveal) g.appendChild(svgEl("line", { x1: r1(p.x), y1: r1(p.y), x2: r1(a.x), y2: r1(a.y), "class": "map-gap" }));
        g.appendChild(svgEl("path", { d: "M" + r1(p.x - 6) + "," + r1(p.y - 6) + "l12,12m0,-12l-12,12", "class": "map-guess" }));
      }
      if (reveal) {
        g.appendChild(svgEl("circle", { cx: r1(a.x), cy: r1(a.y), r: 7, "class": "map-truth" }));
        g.appendChild(svgEl("circle", { cx: r1(a.x), cy: r1(a.y), r: 2.5, "class": "map-truth dot" }));
      }
      svg.appendChild(g);
    }
    function render() { view = draw(frame, cfg, overlay); }
    function pick(ll) { guess = { lat: ll.lat, lon: ll.lon }; render(); }
    frame.addEventListener("click", function (e) {
      if (done || !view) return;
      var r = view.svg.getBoundingClientRect(), s = view.W / r.width;
      buttons.forEach(function (x) { x.classList.remove("on"); });
      pick(view.P.invert((e.clientX - r.left) * s, (e.clientY - r.top) * s));
    });
    function finish() { done = true; reveal = true; check.disabled = true; buttons.forEach(function (b) { b.disabled = true; }); render(); }
    check.addEventListener("click", function () {
      if (!guess) { ctx.feedback(false, choices.length ? "Tap the map or choose a place first." : "Tap the map first."); return; }
      var km = Math.round(haversine(guess.lat, guess.lon, answer.lat, answer.lon)), ok = km <= tol;
      ctx.result(ok, guess.lat.toFixed(2) + "," + guess.lon.toFixed(2) + " (" + km + " km off)");
      if (ok) {
        finish(); ctx.feedback(true, null);
        var v = q.querySelector(":scope > .feedback .verdict");
        if (v) v.textContent = "Right (off by " + km + " km). ";
        return;
      }
      misses++;
      var msg = "Off by " + km + " km: the place is to the " + compass(bearing(guess.lat, guess.lon, answer.lat, answer.lon)) + " of your pick.";
      if (misses >= 2) { finish(); msg += " The true spot is circled."; } else { render(); msg += " " + (d.hint || "Try again."); }
      ctx.feedback(false, msg);
    });
    document.addEventListener("lp:event", function (e) {
      var ev = e.detail;
      if (ev.item === ctx.id && (ev.type === "reveal" || ev.kind === "skip")) finish();
    });
    render(); withWorld(render); redrawOnResize(frame, render);
  }

  if (window.LP && LP.register) {
    LP.register({ type: "map", selector: ".lp-map", scored: false, init: initMap });
    LP.register({ type: "map-locate", init: initLocate });
  } else {
    var init = function () { document.querySelectorAll(".lp-map").forEach(initMap); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
