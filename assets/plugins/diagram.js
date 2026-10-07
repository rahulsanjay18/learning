// Diagram plugin: code-drawn diagram templates. You supply the facts (nodes, edges, sets); the code does the layout, so nothing
// is hand-drawn or generated. Load after assets/lp.js; style: assets/plugins/diagram.css. Colours come from the lp.css tokens.
// Idea from github.com/amosblomqvist/learn (skills/visualize: one idea, fewest elements, look at the render before shipping).
//
// Graph (dependency maps, flows, trees, prerequisite chains): layered layout, roots first, no cycles.
//   <div class="lp-diagram" data-kind="graph"
//        data-nodes="ax:The three axioms|comp:P(Aᶜ) = 1 − P(A)"   id:label, "|"-separated (optional: an edge end with no
//                                                                node entry becomes a node labelled by its id)
//        data-edges="ax>comp|ax>mono:Theorem 1.2.8"               from>to[:label]; "~>" draws a dashed edge
//        [data-dir="down|right"] [data-hl="comp"] [data-caption="…"]></div>
// Sequence (who sends what to whom, in order):
//   <div class="lp-diagram" data-kind="sequence" data-actors="Client|Server"
//        data-steps="Client>Server:SYN|Server~>Client:SYN-ACK|Server>Server:check"   "~>" dashed (a reply); A>A is a self-step
//        [data-caption="…"]></div>
// Venn (2 or 3 sets in a universe, one shaded set expression):
//   <div class="lp-diagram" data-kind="venn" data-sets="A|B|C" [data-universe="S"] [data-shade="(A∪B)ᶜ ∩ C"] [data-caption]></div>
//   Expression syntax: ∩ & and · ∪ | + or · complement: prefix ! or not, postfix ' ᶜ or ^c · difference: \ or − · parentheses.
// Pure helpers are exported for Node (node scripts/test_diagram.js): parseGraph, layoutGraph, crossings, wrapLabel,
// parseSetExpr, shadedRegions, parseSequence, layoutSequence.
(function () {
  "use strict";

  var CH = 7.2, LINE = 16, PADX = 10, PADY = 7, MAXCH = 20;   // text metrics (13px system-ui ≈ 7.2px per char)

  // ---------- text ----------
  // Greedy wrap at max characters, then the narrowest width that keeps the same line count (no lone "BC" on the last line).
  function wrapLabel(s, max) {
    var lines = greedyWrap(s, max || MAXCH);
    for (var w = 4; w < (max || MAXCH); w++) { var t = greedyWrap(s, w); if (t.length === lines.length) return t; }
    return lines;
  }
  function greedyWrap(s, max) {
    var words = String(s).trim().split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) {
      if (cur && (cur + " " + w).length > max) { lines.push(cur); cur = w; } else cur = cur ? cur + " " + w : w;
    });
    if (cur) lines.push(cur);
    return lines.length ? lines : [""];
  }
  function textW(lines) { return Math.max.apply(null, lines.map(function (l) { return l.length; })) * CH; }
  function splitList(s) { return String(s || "").split("|").map(function (x) { return x.trim(); }).filter(Boolean); }

  // ---------- graph ----------
  // "a>b:label" / "a~>b" -> {from, to, label, dashed}
  function parseEdge(s) {
    var m = /^(.+?)\s*(~?>)\s*([^:]+?)\s*(?::\s*(.*))?$/.exec(s);
    if (!m) throw new Error("bad edge " + JSON.stringify(s) + " (write from>to or from>to:label)");
    return { from: m[1].trim(), to: m[3].trim(), label: (m[4] || "").trim(), dashed: m[2] === "~>" };
  }
  function parseGraph(nodesStr, edgesStr) {
    var nodes = [], byId = {};
    function add(id, label) {
      if (byId[id]) { if (label != null) byId[id].label = label; return; }
      byId[id] = { id: id, label: label == null ? id : label }; nodes.push(byId[id]);
    }
    splitList(nodesStr).forEach(function (n) {
      var i = n.indexOf(":");
      if (i < 0) add(n, n); else add(n.slice(0, i).trim(), n.slice(i + 1).trim());
    });
    var edges = splitList(edgesStr).map(parseEdge);
    edges.forEach(function (e) { add(e.from); add(e.to); if (e.from === e.to) throw new Error("self-loop on " + e.from); });
    // cycle check (Kahn); also the layering order
    var indeg = {}, out = {};
    nodes.forEach(function (n) { indeg[n.id] = 0; out[n.id] = []; });
    edges.forEach(function (e) { indeg[e.to]++; out[e.from].push(e.to); });
    var q = nodes.filter(function (n) { return !indeg[n.id]; }).map(function (n) { return n.id; }), topo = [];
    while (q.length) { var v = q.shift(); topo.push(v); out[v].forEach(function (w) { if (!--indeg[w]) q.push(w); }); }
    if (topo.length !== nodes.length) throw new Error("the graph has a cycle; graph diagrams must be acyclic (a DAG)");
    return { nodes: nodes, edges: edges, topo: topo };
  }

  // Number of crossing edge segments between consecutive layers (for tests and the ordering heuristic).
  function crossings(L) {
    var c = 0;
    for (var k = 0; k + 1 < L.layers.length; k++) {
      var segs = [];
      L.segs.forEach(function (s) { if (L.layerOf[s[0]] === k) segs.push([L.pos[s[0]], L.pos[s[1]]]); });
      for (var i = 0; i < segs.length; i++) for (var j = i + 1; j < segs.length; j++)
        if ((segs[i][0] - segs[j][0]) * (segs[i][1] - segs[j][1]) < 0) c++;
    }
    return c;
  }

  // Layout: longest-path layers, dummy nodes on long edges, barycentre ordering sweeps, then x by neighbour pull.
  // Returns boxes {id, x, y, w, h, lines} (centre coords) and edge polylines, in a "down" frame; dir=right transposes.
  function layoutGraph(g, dir, lgap) {
    var right = dir === "right", layerOf = {}, preds = {}, succ = {};
    g.nodes.forEach(function (n) { preds[n.id] = []; succ[n.id] = []; });
    g.edges.forEach(function (e) { preds[e.to].push(e.from); succ[e.from].push(e.to); });
    g.topo.forEach(function (v) { layerOf[v] = preds[v].reduce(function (m, p) { return Math.max(m, layerOf[p] + 1); }, 0); });
    // pull sinks-with-one-parent up is not needed; push roots down next to their first child to shorten edges
    g.topo.slice().reverse().forEach(function (v) {
      if (!preds[v].length && succ[v].length) layerOf[v] = Math.min.apply(null, succ[v].map(function (w) { return layerOf[w]; })) - 1;
    });
    var nLayers = 1 + Math.max.apply(null, g.topo.map(function (v) { return layerOf[v]; }));
    var size = {}, layers = [], segs = [], chains = [];
    for (var k = 0; k < nLayers; k++) layers.push([]);
    g.nodes.forEach(function (n) {
      var lines = wrapLabel(n.label), w = textW(lines) + 2 * PADX, h = lines.length * LINE + 2 * PADY;
      size[n.id] = { lines: lines, w: right ? h : w, h: right ? w : h, bw: w, bh: h };   // w = extent across layers' axis
    });
    g.topo.forEach(function (v) { layers[layerOf[v]].push(v); });
    var dummy = 0;
    g.edges.forEach(function (e, i) {
      var chain = [e.from], a = layerOf[e.from], b = layerOf[e.to];
      for (var k = a + 1; k < b; k++) {
        var d = "\u0000d" + (dummy++); layerOf[d] = k; layers[k].push(d); size[d] = { w: 8, h: 0, dummy: true }; chain.push(d);
      }
      chain.push(e.to);
      for (var j = 0; j + 1 < chain.length; j++) segs.push([chain[j], chain[j + 1]]);
      chains[i] = chain;
    });
    var pos = {}, up = {}, down = {};
    function index() { layers.forEach(function (l) { l.forEach(function (v, i) { pos[v] = i; }); }); }
    segs.forEach(function (s) { (down[s[0]] = down[s[0]] || []).push(s[1]); (up[s[1]] = up[s[1]] || []).push(s[0]); });
    index();
    var L = { layers: layers, segs: segs, layerOf: layerOf, pos: pos };
    var best = layers.map(function (l) { return l.slice(); }), bestC = crossings(L);
    for (var it = 0; it < 12 && bestC; it++) {
      var downward = it % 2 === 0;
      for (var kk = 0; kk < nLayers; kk++) {
        var k2 = downward ? kk : nLayers - 1 - kk, nb = downward ? up : down;
        var bc = {};
        layers[k2].forEach(function (v) {
          var ns = nb[v] || [];
          bc[v] = ns.length ? ns.reduce(function (s, u) { return s + pos[u]; }, 0) / ns.length : pos[v];
        });
        layers[k2].sort(function (a, b) { return bc[a] - bc[b] || pos[a] - pos[b]; });
        layers[k2].forEach(function (v, i) { pos[v] = i; });
      }
      var c = crossings(L);
      if (c < bestC) { bestC = c; best = layers.map(function (l) { return l.slice(); }); }
    }
    layers.forEach(function (l, i) { layers[i] = best[i]; }); index();
    // across-axis coordinates: pack, then pull toward neighbour mean while keeping order and gaps
    var GAP = g.edges.some(function (e) { return e.label; }) ? 44 : 28, x = {};
    layers.forEach(function (l) { var c = 0; l.forEach(function (v) { x[v] = c + size[v].w / 2; c += size[v].w + GAP; }); });
    function settle(l) {
      for (var i = 1; i < l.length; i++) { var lo = x[l[i - 1]] + (size[l[i - 1]].w + size[l[i]].w) / 2 + GAP; if (x[l[i]] < lo) x[l[i]] = lo; }
      for (var j = l.length - 2; j >= 0; j--) { var hi = x[l[j + 1]] - (size[l[j + 1]].w + size[l[j]].w) / 2 - GAP; if (x[l[j]] > hi) x[l[j]] = hi; }
    }
    for (var r = 0; r < 20; r++) {
      layers.forEach(function (l) {
        l.forEach(function (v) {
          var ns = (up[v] || []).concat(down[v] || []);
          if (ns.length) x[v] = 0.5 * x[v] + 0.5 * ns.reduce(function (s, u) { return s + x[u]; }, 0) / ns.length;
        });
        settle(l);
      });
    }
    var minX = Infinity, maxX = -Infinity;
    Object.keys(x).forEach(function (v) { minX = Math.min(minX, x[v] - size[v].w / 2); maxX = Math.max(maxX, x[v] + size[v].w / 2); });
    // along-axis coordinates: each layer as deep as its largest node, with room for edge labels
    var hasLabels = g.edges.some(function (e) { return e.label; }), LGAP = lgap || (hasLabels ? 84 : 44), y = [], cy = 0;
    layers.forEach(function (l, k) {
      var h = Math.max.apply(null, [0].concat(l.map(function (v) { return size[v].h; })));
      y[k] = { mid: cy + h / 2, h: h }; cy += h + LGAP;
    });
    var M = 12, W = maxX - minX + 2 * M, H = cy - LGAP + 2 * M;
    function pt(v) { return { a: x[v] - minX + M, b: y[layerOf[v]].mid + M }; }   // a = across, b = along
    var boxes = g.nodes.map(function (n) {
      var p = pt(n.id), s = size[n.id];
      return right ? { id: n.id, x: p.b, y: p.a, w: s.bw, h: s.bh, lines: s.lines } : { id: n.id, x: p.a, y: p.b, w: s.bw, h: s.bh, lines: s.lines };
    });
    var edges = g.edges.map(function (e, i) {
      var pts = chains[i].map(function (v, j) {
        var p = pt(v), half = size[v].dummy ? 0 : size[v].h / 2;
        var along = j === 0 ? p.b + half : j === chains[i].length - 1 ? p.b - half : p.b;
        return right ? { x: along, y: p.a } : { x: p.a, y: along };
      });
      return { from: e.from, to: e.to, label: e.label, dashed: e.dashed, pts: pts };
    });
    return { boxes: boxes, edges: edges, width: right ? H : W, height: right ? W : H, crossings: bestC, right: right };
  }

  // Point at fraction t (0 = source, 1 = target) along an edge drawn by curve(): cubic per segment, tangents along the layer axis.
  function pointAt(pts, right, t) {
    var n = pts.length - 1, k = Math.min(Math.floor(t * n), n - 1), u = t * n - k, p = pts[k], q = pts[k + 1];
    var c1 = right ? { x: (p.x + q.x) / 2, y: p.y } : { x: p.x, y: (p.y + q.y) / 2 };
    var c2 = right ? { x: (p.x + q.x) / 2, y: q.y } : { x: q.x, y: (p.y + q.y) / 2 };
    var a = (1 - u) * (1 - u) * (1 - u), b = 3 * (1 - u) * (1 - u) * u, c = 3 * (1 - u) * u * u, d = u * u * u;
    return { x: a * p.x + b * c1.x + c * c2.x + d * q.x, y: a * p.y + b * c1.y + c * c2.y + d * q.y };
  }
  // Edge labels: try spots along each edge (middle first, then toward either end) and keep the first whose box hits no node and
  // no label already placed. Returns [{x, y, lines, w, h, ok}] per edge (null when unlabelled); ok=false = no clean spot found.
  var LCH = 6.6, LLINE = 14;
  function placeEdgeLabels(L) {
    var placed = L.boxes.map(function (b) { return { x: b.x, y: b.y, w: b.w + 4, h: b.h + 4 }; }), out = [];
    var samples = L.edges.map(function (e) { var a = []; for (var i = 0; i <= 40; i++) a.push(pointAt(e.pts, L.right, i / 40)); return a; });
    var own = -1;
    function hits(r) {
      if (placed.some(function (o) { return Math.abs(r.x - o.x) < (r.w + o.w) / 2 && Math.abs(r.y - o.y) < (r.h + o.h) / 2; })) return true;
      return samples.some(function (pts, j) {    // another edge running through the label's text
        return j !== own && pts.some(function (q) { return Math.abs(q.x - r.x) < r.w / 2 - 2 && Math.abs(q.y - r.y) < r.h / 2 - 2; });
      });
    }
    function inside(r) { return r.x - r.w / 2 >= 0 && r.y - r.h / 2 >= 0 && r.x + r.w / 2 <= L.width && r.y + r.h / 2 <= L.height; }
    L.edges.forEach(function (e, ei) {
      own = ei;
      if (!e.label) { out.push(null); return; }
      var lines = wrapLabel(e.label, 18), w = textW(lines) / CH * LCH + 6, h = lines.length * LLINE + 2, best = null;
      var side = (L.right ? h : w) / 2 + 5;   // beside the edge: offset across the layer axis
      [0.5, 0.35, 0.65, 0.25, 0.75, 0.15, 0.85].some(function (t) {
        var p = pointAt(e.pts, L.right, t);
        return [0, side, -side].some(function (d) {
          var r = L.right ? { x: p.x, y: p.y + d, w: w, h: h } : { x: p.x + d, y: p.y, w: w, h: h };
          if (!best) best = r;
          if (!hits(r) && inside(r)) { best = r; best.ok = true; return true; }
          return false;
        });
      });
      best.lines = lines; best.ok = !!best.ok; placed.push(best); out.push(best);
    });
    return out;
  }

  // Layout plus labels: widen the gap between layers until every edge label has a clean spot (or give up after a few tries).
  function layoutWithLabels(g, dir) {
    var L, labels;
    for (var gap = 84; gap <= 244; gap += 40) {
      L = layoutGraph(g, dir, g.edges.some(function (e) { return e.label; }) ? gap : 0);
      labels = placeEdgeLabels(L);
      if (labels.every(function (r) { return !r || r.ok; })) break;
    }
    return { L: L, labels: labels };
  }

  // ---------- sets ----------
  // Parse a set expression over the given set names into a function(membership) -> bool. membership: {A: true, …}.
  function parseSetExpr(src, names) {
    var s = String(src).replace(/\^c/g, "'").replace(/ᶜ/g, "'"), i = 0;
    var sorted = names.slice().sort(function (a, b) { return b.length - a.length; });
    function ws() { while (i < s.length && /\s/.test(s[i])) i++; }
    function word(w) { ws(); if (s.substr(i, w.length).toLowerCase() === w && !/\w/.test(s[i + w.length] || "")) { i += w.length; return true; } return false; }
    function sym(chars) { ws(); if (chars.indexOf(s[i]) >= 0 && s[i]) { i++; return true; } return false; }
    function primary() {
      ws();
      if (sym("(")) { var e = union(); if (!sym(")")) throw new Error("missing ) in " + src); return post(e); }
      if (sym("!") || word("not")) { var p = primary(); return function (m) { return !p(m); }; }
      for (var k = 0; k < sorted.length; k++) if (s.substr(i, sorted[k].length) === sorted[k]) {
        var name = sorted[k]; i += name.length; return post(function (m) { return !!m[name]; });
      }
      throw new Error("unknown set at " + JSON.stringify(s.slice(i)) + " (sets: " + names.join(", ") + ")");
    }
    function post(f) { while (sym("'")) f = (function (g) { return function (m) { return !g(m); }; })(f); return f; }
    function inter() {
      var f = primary();
      for (;;) {
        if (sym("∩&·") || word("and")) { var g = primary(); f = (function (a, b) { return function (m) { return a(m) && b(m); }; })(f, g); }
        else if (sym("\\−-")) { var h = primary(); f = (function (a, b) { return function (m) { return a(m) && !b(m); }; })(f, h); }
        else return f;
      }
    }
    function union() {
      var f = inter();
      while (sym("∪|+") || word("or")) { var g = inter(); f = (function (a, b) { return function (m) { return a(m) || b(m); }; })(f, g); }
      return f;
    }
    var f = union(); ws();
    if (i < s.length) throw new Error("unexpected " + JSON.stringify(s.slice(i)) + " in set expression");
    return f;
  }
  // Which of the 2^n regions are shaded: list of membership arrays like [true,false] (A only), [false,false] (outside all).
  function shadedRegions(expr, names) {
    var f = parseSetExpr(expr, names), out = [];
    for (var mask = 0; mask < (1 << names.length); mask++) {
      var m = {}, bits = names.map(function (n, k) { return !!(mask & (1 << k)); });
      names.forEach(function (n, k) { m[n] = bits[k]; });
      if (f(m)) out.push(bits);
    }
    return out;
  }

  // ---------- sequence ----------
  function parseSequence(actorsStr, stepsStr) {
    var actors = splitList(actorsStr);
    if (actors.length < 1) throw new Error("sequence needs data-actors");
    var steps = splitList(stepsStr).map(function (s) {
      var e = parseEdge(s);
      [e.from, e.to].forEach(function (a) { if (actors.indexOf(a) < 0) throw new Error("unknown actor " + JSON.stringify(a) + " (actors: " + actors.join(", ") + ")"); });
      return e;
    });
    if (!steps.length) throw new Error("sequence needs data-steps");
    return { actors: actors, steps: steps };
  }
  function layoutSequence(sq) {
    var n = sq.actors.length, minGap = sq.actors.map(function () { return 0; });
    // gap between neighbouring columns must fit every label that spans it
    sq.steps.forEach(function (st) {
      var a = sq.actors.indexOf(st.from), b = sq.actors.indexOf(st.to), w = st.label.length * CH + 24;
      if (a === b) { if (a < n - 1) minGap[a] = Math.max(minGap[a], w + 40); return; }
      var lo = Math.min(a, b), hi = Math.max(a, b), per = w / (hi - lo);
      for (var k = lo; k < hi; k++) minGap[k] = Math.max(minGap[k], per);
    });
    var heads = sq.actors.map(function (a) { return Math.max(70, a.length * CH + 2 * PADX); }), x = [], cx = 12 + heads[0] / 2;
    for (var k = 0; k < n; k++) {
      x.push(cx);
      if (k < n - 1) cx += Math.max(minGap[k], (heads[k] + heads[k + 1]) / 2 + 30);
    }
    var lastSelf = sq.steps.some(function (st) { return st.from === st.to && sq.actors.indexOf(st.from) === n - 1; });
    var top = 12 + LINE + 2 * PADY, ROW = 40, rows = sq.steps.map(function (st, i) { return top + 30 + i * ROW; });
    var width = x[n - 1] + Math.max(heads[n - 1] / 2, lastSelf ? 40 + (sq.steps.filter(function (s) { return s.from === s.to; })
      .reduce(function (m, s) { return Math.max(m, s.label.length * CH); }, 0)) : 0) + 12;
    return { x: x, heads: heads, top: top, rows: rows, width: width, height: rows[rows.length - 1] + 30 };
  }

  var api = { parseGraph: parseGraph, layoutGraph: layoutGraph, placeEdgeLabels: placeEdgeLabels, layoutWithLabels: layoutWithLabels, pointAt: pointAt, crossings: crossings, wrapLabel: wrapLabel, parseEdge: parseEdge,
    parseSetExpr: parseSetExpr, shadedRegions: shadedRegions, parseSequence: parseSequence, layoutSequence: layoutSequence };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---------- drawing ----------
  var NS = "http://www.w3.org/2000/svg", uid = 0;
  function el(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function svgRoot(w, h) {
    var svg = el("svg", { viewBox: "0 0 " + w + " " + h, width: w, height: h, class: "dg-svg", role: "img" });
    return svg;
  }
  function arrowDefs(svg, id) {
    var defs = el("defs", {}, svg);
    var m = el("marker", { id: id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0,0 L10,5 L0,10 z", class: "dg-arrowhead" }, m);
    return defs;
  }
  function textLines(parent, lines, cx, cy, cls) {
    var t = el("text", { x: cx, y: cy - (lines.length - 1) * LINE / 2, class: cls, "text-anchor": "middle", "dominant-baseline": "central" }, parent);
    lines.forEach(function (l, i) { var s = el("tspan", { x: cx, dy: i ? LINE : 0 }, t); s.textContent = l; });
    return t;
  }
  function curve(pts, right) {
    var d = "M" + pts[0].x + "," + pts[0].y;
    for (var i = 1; i < pts.length; i++) {
      var p = pts[i - 1], q = pts[i];
      if (right) { var mx = (p.x + q.x) / 2; d += " C" + mx + "," + p.y + " " + mx + "," + q.y + " " + q.x + "," + q.y; }
      else { var my = (p.y + q.y) / 2; d += " C" + p.x + "," + my + " " + q.x + "," + my + " " + q.x + "," + q.y; }
    }
    return d;
  }

  function drawGraph(d) {
    var g = parseGraph(d.nodes, d.edges), LL = layoutWithLabels(g, d.dir), L = LL.L, svg = svgRoot(L.width, L.height), id = "dga" + (++uid);
    var hl = splitList((d.hl || "").replace(/\s+/g, "|"));
    arrowDefs(svg, id);
    L.edges.forEach(function (e) {
      el("path", { d: curve(e.pts, L.right), class: "dg-edge" + (e.dashed ? " dashed" : ""), "marker-end": "url(#" + id + ")" }, svg);
    });
    L.boxes.forEach(function (b) {
      var grp = el("g", { class: "dg-node" + (hl.indexOf(b.id) >= 0 ? " hl" : "") }, svg);
      el("rect", { x: b.x - b.w / 2, y: b.y - b.h / 2, width: b.w, height: b.h, rx: 4 }, grp);
      textLines(grp, b.lines, b.x, b.y, "dg-label");
    });
    LL.labels.forEach(function (r) {
      if (!r) return;
      el("rect", { x: r.x - r.w / 2, y: r.y - r.h / 2, width: r.w, height: r.h, class: "dg-label-bg" }, svg);   // hides the line behind the gaps
      textLines(svg, r.lines, r.x, r.y, "dg-edge-label");
    });
    return svg;
  }

  function drawSequence(d) {
    var sq = parseSequence(d.actors, d.steps), L = layoutSequence(sq), svg = svgRoot(L.width, L.height), id = "dga" + (++uid);
    arrowDefs(svg, id);
    sq.actors.forEach(function (a, k) {
      el("line", { x1: L.x[k], y1: L.top, x2: L.x[k], y2: L.height - 8, class: "dg-lifeline" }, svg);
      var grp = el("g", { class: "dg-node" }, svg), h = LINE + 2 * PADY;
      el("rect", { x: L.x[k] - L.heads[k] / 2, y: 12, width: L.heads[k], height: h, rx: 4 }, grp);
      textLines(grp, [a], L.x[k], 12 + h / 2, "dg-label");
    });
    sq.steps.forEach(function (st, i) {
      var a = L.x[sq.actors.indexOf(st.from)], b = L.x[sq.actors.indexOf(st.to)], y = L.rows[i], cls = "dg-edge" + (st.dashed ? " dashed" : "");
      if (a === b) {
        el("path", { d: "M" + a + "," + (y - 8) + " h30 v16 h-28", class: cls, "marker-end": "url(#" + id + ")" }, svg);
        var t = el("text", { x: a + 36, y: y, class: "dg-edge-label", "dominant-baseline": "central" }, svg); t.textContent = st.label;
        return;
      }
      el("line", { x1: a, y1: y, x2: b + (b > a ? -2 : 2), y2: y, class: cls, "marker-end": "url(#" + id + ")" }, svg);
      if (st.label) { var u = el("text", { x: (a + b) / 2, y: y - 9, class: "dg-edge-label", "text-anchor": "middle" }, svg); u.textContent = st.label; }
    });
    return svg;
  }

  function drawVenn(d) {
    var names = splitList(d.sets);
    if (names.length < 2 || names.length > 3) throw new Error("venn needs 2 or 3 sets");
    var r = 70, W = names.length === 2 ? 340 : 320, H = names.length === 2 ? 210 : 290, cx = W / 2, cy = names.length === 2 ? H / 2 : 150;
    var C = names.length === 2 ? [{ x: cx - 45, y: cy }, { x: cx + 45, y: cy }]
      : [{ x: cx - 42, y: cy - 28 }, { x: cx + 42, y: cy - 28 }, { x: cx, y: cy + 46 }];
    var svg = svgRoot(W, H), p = "dgv" + (++uid), defs = el("defs", {}, svg);
    names.forEach(function (n, k) {
      var cp = el("clipPath", { id: p + "c" + k }, defs); el("circle", { cx: C[k].x, cy: C[k].y, r: r }, cp);
      var mk = el("mask", { id: p + "m" + k }, defs);
      el("rect", { x: 0, y: 0, width: W, height: H, fill: "white" }, mk); el("circle", { cx: C[k].x, cy: C[k].y, r: r, fill: "black" }, mk);
    });
    if (d.shade) shadedRegions(d.shade, names).forEach(function (bits) {
      var parent = svg;
      bits.forEach(function (inSet, k) { parent = el("g", inSet ? { "clip-path": "url(#" + p + "c" + k + ")" } : { mask: "url(#" + p + "m" + k + ")" }, parent); });
      el("rect", { x: 6, y: 6, width: W - 12, height: H - 12, class: "dg-shade" }, parent);
    });
    el("rect", { x: 6, y: 6, width: W - 12, height: H - 12, class: "dg-universe" }, svg);
    var u = el("text", { x: 14, y: 22, class: "dg-label" }, svg); u.textContent = d.universe || "S";
    var LBL = names.length === 2 ? [{ x: -r - 8, y: -r + 8, a: "end" }, { x: r + 8, y: -r + 8, a: "start" }]
      : [{ x: -r - 6, y: -r + 10, a: "end" }, { x: r + 6, y: -r + 10, a: "start" }, { x: r - 4, y: r - 4, a: "start" }];
    names.forEach(function (n, k) {
      el("circle", { cx: C[k].x, cy: C[k].y, r: r, class: "dg-set" }, svg);
      var t = el("text", { x: C[k].x + LBL[k].x, y: C[k].y + LBL[k].y, class: "dg-set-label", "text-anchor": LBL[k].a }, svg); t.textContent = n;
    });
    return svg;
  }

  function initDiagram(box) {
    var d = box.dataset, kind = d.kind || "graph";
    var draw = { graph: drawGraph, sequence: drawSequence, venn: drawVenn }[kind];
    if (!draw) throw new Error("unknown diagram kind " + JSON.stringify(kind) + " (graph, sequence, venn)");
    var svg = draw(d), frame = document.createElement("div");
    frame.className = "dg-scroll";
    if (d.caption) { var t = el("title", {}); t.textContent = d.caption; svg.insertBefore(t, svg.firstChild); }
    // shrink to fit narrow screens, but never below 75% (text stays readable); past that the frame scrolls
    var W = +svg.getAttribute("width");
    svg.style.width = "100%"; svg.style.maxWidth = W + "px"; svg.style.minWidth = Math.round(W * 0.75) + "px"; svg.style.height = "auto";
    frame.appendChild(svg);
    box.innerHTML = ""; box.appendChild(frame);
    if (d.caption) { var c = document.createElement("div"); c.className = "dg-caption"; c.textContent = d.caption; box.appendChild(c); }
  }

  if (window.LP && LP.register) LP.register({ type: "diagram", selector: ".lp-diagram", scored: false, init: initDiagram });
  else {
    var init = function () { document.querySelectorAll(".lp-diagram").forEach(initDiagram); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
