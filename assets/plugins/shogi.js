// Shogi plugin: diagrams, a legal-move sandbox, and "find the move" quizzes. Load after assets/lp.js; style: assets/plugins/shogi.css.
// Own rules engine, checked against published perft counts (node scripts/test_xiangqi_shogi.js).
//
// Position: SFEN "board side hands [move]". Start (the default):
//   "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
//   Rows from rank a (top, Gote's back rank) to rank i (Sente's). Uppercase = Sente ("b", moves first, plays up the board),
//   lowercase = Gote ("w"). K king, R rook, B bishop, G gold, S silver, N knight, L lance, P pawn; "+" = promoted (+R dragon,
//   +B horse, +S/+N/+L/+P move like gold). Hands: "-" or counts like "2Pb" (Sente 2 pawns, Gote a bishop).
// Squares and moves (USI): file 9…1 left to right from Sente's side, rank a…i top to bottom. "7g7f", promotion "8h2b+",
// drop "P*5e". Several answers: "7g7f|2g2f".
// Rules: promotion is optional on a move into, out of or within the last three ranks, and forced when the piece could never move
// again (pawn/lance on the last rank, knight on the last two); no two unpromoted pawns of one side on a file (nifu); a pawn drop
// may not give checkmate (uchifuzume); you may not leave your king in check; no legal move = loss. Repetition (sennichite) is not enforced.
//
// Diagram:  <div class="shogi-board" data-sfen="…" [data-hl="7f 2b"] [data-arrows="8h-2b"] [data-flip="true"] [data-play="true"]
//                [data-labels="latin"] [data-caption="…"]></div>
//   data-play="true": a sandbox. Click a piece (or a piece in hand) for its legal moves, then a square; asks "promote?" when it's optional.
//   data-labels="latin": letters instead of kanji (王玉 飛 角 金 銀 桂 香 歩; promoted 龍 馬 全 圭 杏 と).
// Quiz:     <div class="quiz" data-type="shogi-move" data-id="…" data-sfen="…" data-answer="P*5e|7g7f" [data-flip] [data-labels] [data-hint]>
//   Only legal moves can be played; any listed answer is right. The test checks every answer is legal.
(function () {
  "use strict";
  var START = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1";
  var RANKS = "abcdefghi", HAND_ORDER = ["R", "B", "G", "S", "N", "L", "P"];

  // ---------- engine: board[row * 9 + col], row 0 = rank a, col 0 = file 9 ----------
  function colorOf(p) { var t = p.replace("+", ""); return t === t.toUpperCase() ? "b" : "w"; }
  function base(p) { return p.replace("+", "").toUpperCase(); }
  function promoted(p) { return p[0] === "+"; }
  function emptyHands() { var h = {}; HAND_ORDER.forEach(function (k) { h[k] = 0; }); return h; }
  function parse(sfen) {
    var parts = String(sfen || START).trim().split(/\s+/), rows = parts[0].split("/");
    if (rows.length !== 9) throw new Error("shogi SFEN needs 9 rows");
    var board = new Array(81).fill(null);
    rows.forEach(function (row, r) {
      var c = 0, plus = false;
      for (var k = 0; k < row.length; k++) {
        var ch = row[k];
        if (ch === "+") { plus = true; continue; }
        if (/\d/.test(ch)) { c += +ch; continue; }
        if ("KRBGSNLPkrbgsnlp".indexOf(ch) < 0) throw new Error("shogi SFEN: unknown piece " + ch);
        if (plus && "KGkg".indexOf(ch) >= 0) throw new Error("shogi SFEN: " + ch + " can't be promoted");
        if (c > 8) throw new Error("shogi SFEN: row " + RANKS[r] + " too long");
        board[r * 9 + c] = (plus ? "+" : "") + ch; plus = false; c++;
      }
      if (c !== 9) throw new Error("shogi SFEN: row " + RANKS[r] + " has " + c + " files, not 9");
    });
    var hands = { b: emptyHands(), w: emptyHands() }, hs = parts[2] || "-";
    if (hs !== "-") {
      var m, re = /(\d*)([RBGSNLPrbgsnlp])/g, used = 0;
      while ((m = re.exec(hs))) { hands[m[2] === m[2].toUpperCase() ? "b" : "w"][m[2].toUpperCase()] += m[1] ? +m[1] : 1; used += m[0].length; }
      if (used !== hs.length) throw new Error("shogi SFEN: bad hand " + hs);
    }
    var pos = { board: board, turn: parts[1] === "w" ? "w" : "b", hands: hands };
    if (findKing(board, "b") < 0 || findKing(board, "w") < 0) throw new Error("shogi SFEN: each side needs a king");
    return pos;
  }
  function toSfen(pos) {
    var rows = [];
    for (var r = 0; r < 9; r++) {
      var s = "", e = 0;
      for (var c = 0; c < 9; c++) { var p = pos.board[r * 9 + c]; if (!p) e++; else { if (e) s += e; e = 0; s += p; } }
      rows.push(s + (e ? e : ""));
    }
    var h = "";
    ["b", "w"].forEach(function (side) { HAND_ORDER.forEach(function (k) { var n = pos.hands[side][k]; if (n) h += (n > 1 ? n : "") + (side === "b" ? k : k.toLowerCase()); }); });
    return rows.join("/") + " " + pos.turn + " " + (h || "-");
  }
  function sqName(i) { return (9 - i % 9) + RANKS[Math.floor(i / 9)]; }
  function sqIndex(n) { var f = parseInt(n[0], 10), r = RANKS.indexOf(n[1]); return f >= 1 && f <= 9 && r >= 0 && n.length === 2 ? r * 9 + (9 - f) : -1; }
  function findKing(b, c) { var k = c === "b" ? "K" : "k"; for (var i = 0; i < 81; i++) if (b[i] === k) return i; return -1; }

  // Steps and slides in Sente's orientation (dr -1 = forward); Gote flips dr.
  var GOLD = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, 0]];
  var KING = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];
  var STEPS = { K: KING, G: GOLD, S: [[-1, -1], [-1, 0], [-1, 1], [1, -1], [1, 1]], N: [[-2, -1], [-2, 1]], P: [[-1, 0]],
    "+R": [[-1, -1], [-1, 1], [1, -1], [1, 1]], "+B": [[-1, 0], [1, 0], [0, -1], [0, 1]] };
  var SLIDES = { R: [[-1, 0], [1, 0], [0, -1], [0, 1]], B: [[-1, -1], [-1, 1], [1, -1], [1, 1]], L: [[-1, 0]] };
  function kind(p) { var t = base(p); return promoted(p) ? (t === "R" || t === "B" ? "+" + t : "G") : t; }
  function stepsOf(k) { return STEPS[k] || []; }
  function slidesOf(k) { return k === "+R" ? SLIDES.R : k === "+B" ? SLIDES.B : SLIDES[k] || []; }

  function targets(b, from) {
    var p = b[from], c = colorOf(p), k = kind(p), dir = c === "b" ? 1 : -1, r = Math.floor(from / 9), f = from % 9, out = [];
    stepsOf(k).forEach(function (d) {
      var rr = r + d[0] * dir, ff = f + d[1];
      if (rr < 0 || rr > 8 || ff < 0 || ff > 8) return;
      var q = b[rr * 9 + ff]; if (!q || colorOf(q) !== c) out.push(rr * 9 + ff);
    });
    slidesOf(k).forEach(function (d) {
      var rr = r + d[0] * dir, ff = f + d[1];
      while (rr >= 0 && rr <= 8 && ff >= 0 && ff <= 8) {
        var q = b[rr * 9 + ff];
        if (!q) out.push(rr * 9 + ff); else { if (colorOf(q) !== c) out.push(rr * 9 + ff); break; }
        rr += d[0] * dir; ff += d[1];
      }
    });
    return out;
  }
  // Is sq attacked by side `by`? Looks outward from sq for pieces that could reach it.
  function attacked(b, sq, by) {
    var r = Math.floor(sq / 9), f = sq % 9, dir = by === "b" ? 1 : -1;    // `by`'s forward is -dir in row terms… see below
    for (var i = 0; i < 81; i++) {
      var p = b[i];
      if (!p || colorOf(p) !== by) continue;
      var k = kind(p), pr = Math.floor(i / 9), pf = i % 9, dr = r - pr, df = f - pf;
      var st = stepsOf(k);
      for (var s = 0; s < st.length; s++) if (st[s][0] * dir === dr && st[s][1] === df) return true;
      var sl = slidesOf(k);
      for (var t = 0; t < sl.length; t++) {
        var sr = sl[t][0] * dir, sf = sl[t][1], rr = pr + sr, ff = pf + sf;
        while (rr >= 0 && rr <= 8 && ff >= 0 && ff <= 8) {
          if (rr === r && ff === f) return true;
          if (b[rr * 9 + ff]) break;
          rr += sr; ff += sf;
        }
      }
    }
    return false;
  }
  function other(c) { return c === "b" ? "w" : "b"; }
  function inCheck(pos, c) { return attacked(pos.board, findKing(pos.board, c), other(c)); }
  function inZone(row, c) { return c === "b" ? row <= 2 : row >= 6; }
  function mustPromote(t, row, c) { var rel = c === "b" ? row : 8 - row; return ((t === "P" || t === "L") && rel === 0) || (t === "N" && rel <= 1); }

  // Moves: {from, to, promote, drop: "P"|null, usi}
  function apply(pos, m) {
    var b = pos.board.slice(), hands = { b: Object.assign({}, pos.hands.b), w: Object.assign({}, pos.hands.w) }, c = pos.turn;
    if (m.drop) { hands[c][m.drop]--; b[m.to] = c === "b" ? m.drop : m.drop.toLowerCase(); }
    else {
      var cap = b[m.to];
      if (cap) hands[c][base(cap)]++;
      var p = b[m.from];
      b[m.to] = m.promote ? "+" + p : p; b[m.from] = null;
    }
    return { board: b, turn: other(c), hands: hands };
  }
  function pseudoMoves(pos, from) {
    var b = pos.board, c = pos.turn, out = [];
    for (var s = 0; s < 81; s++) {
      if (from != null && from !== s) continue;
      var p = b[s];
      if (!p || colorOf(p) !== c) continue;
      var t = base(p), canPromote = !promoted(p) && t !== "K" && t !== "G";
      targets(b, s).forEach(function (to) {
        var row = Math.floor(to / 9), u = sqName(s) + sqName(to);
        if (canPromote && (inZone(row, c) || inZone(Math.floor(s / 9), c))) {
          out.push({ from: s, to: to, promote: true, drop: null, usi: u + "+" });
          if (!mustPromote(t, row, c)) out.push({ from: s, to: to, promote: false, drop: null, usi: u });
        } else out.push({ from: s, to: to, promote: false, drop: null, usi: u });
      });
    }
    return out;
  }
  function dropMoves(pos, piece) {
    var b = pos.board, c = pos.turn, out = [], pawnFiles = {};
    for (var i = 0; i < 81; i++) if (b[i] === (c === "b" ? "P" : "p")) pawnFiles[i % 9] = true;
    HAND_ORDER.forEach(function (t) {
      if (piece && piece !== t) return;
      if (!pos.hands[c][t]) return;
      for (var sq = 0; sq < 81; sq++) {
        if (b[sq]) continue;
        var row = Math.floor(sq / 9);
        if (mustPromote(t, row, c)) continue;           // would never move again
        if (t === "P" && pawnFiles[sq % 9]) continue;   // nifu
        out.push({ from: null, to: sq, promote: false, drop: t, usi: t + "*" + sqName(sq) });
      }
    });
    return out;
  }
  function legal(pos, m) {
    var n = apply(pos, m);
    if (attacked(n.board, findKing(n.board, pos.turn), other(pos.turn))) return false;
    if (m.drop === "P" && inCheck(n, n.turn) && !hasLegalMove(n)) return false;   // uchifuzume
    return true;
  }
  function hasLegalMove(pos) {
    var ps = pseudoMoves(pos).concat(dropMoves(pos));
    for (var i = 0; i < ps.length; i++) if (legal(pos, ps[i])) return true;
    return false;
  }
  // from: a square index, or "P" etc. for drops of that piece; omitted = all moves.
  function legalMoves(pos, from) {
    var ps = typeof from === "string" ? dropMoves(pos, from) : from != null ? pseudoMoves(pos, from) : pseudoMoves(pos).concat(dropMoves(pos));
    return ps.filter(function (m) { return legal(pos, m); });
  }
  function perft(pos, depth) {
    if (depth === 0) return 1;
    var ms = legalMoves(pos);
    if (depth === 1) return ms.length;
    var n = 0;
    for (var i = 0; i < ms.length; i++) n += perft(apply(pos, ms[i]), depth - 1);
    return n;
  }
  function status(pos) {
    var side = pos.turn === "b" ? "Sente (▲)" : "Gote (△)", win = pos.turn === "b" ? "Gote" : "Sente", chk = inCheck(pos, pos.turn);
    if (!hasLegalMove(pos)) return { over: true, text: (chk ? "Checkmate" : "No legal move") + ": " + win + " wins." };
    return { over: false, check: chk, text: side + " to move" + (chk ? ": check!" : ".") };
  }
  function findMove(pos, usi) {
    usi = String(usi || "").trim();
    if (/^[rbgsnlp]\*/.test(usi)) usi = usi[0].toUpperCase() + usi.slice(1);
    return legalMoves(pos).filter(function (m) { return m.usi === usi; })[0] || null;
  }

  var api = { START: START, parse: parse, toSfen: toSfen, legalMoves: legalMoves, apply: apply, perft: perft, inCheck: inCheck,
    status: status, findMove: findMove, sqName: sqName, sqIndex: sqIndex };
  if (typeof module !== "undefined" && module.exports) { module.exports = api; return; }

  // ---------- drawing ----------
  var KANJI = { K: "王", R: "飛", B: "角", G: "金", S: "銀", N: "桂", L: "香", P: "歩", "+R": "龍", "+B": "馬", "+S": "全", "+N": "圭", "+L": "杏", "+P": "と" };
  var NAMES = { K: "king", R: "rook", B: "bishop", G: "gold", S: "silver", N: "knight", L: "lance", P: "pawn",
    "+R": "dragon", "+B": "horse", "+S": "promoted silver", "+N": "promoted knight", "+L": "promoted lance", "+P": "tokin" };
  var SVGNS = "http://www.w3.org/2000/svg";
  function svg(tag, a) { var e = document.createElementNS(SVGNS, tag); for (var k in a) e.setAttribute(k, a[k]); return e; }
  var S = 40, M = 24, HAND_H = 44;
  function label(p, labels) {
    var key = promoted(p) ? "+" + base(p) : base(p);
    if (labels === "latin") return key;
    return key === "K" && colorOf(p) === "w" ? "玉" : KANJI[key];
  }
  function pieceShape(g, x, y, p, opts, cls) {
    var w = S * 0.4, h = S * 0.44, up = colorOf(p) === "b" ? !opts.flip : !!opts.flip;
    var pts = [[0, -h], [w * 0.8, -h * 0.55], [w, h], [-w, h], [-w * 0.8, -h * 0.55]];
    var tr = "translate(" + x + " " + y + ")" + (up ? "" : " rotate(180)");
    var grp = svg("g", { transform: tr, "class": "sg-pc " + (cls || "") + (promoted(p) ? " promoted" : "") });
    grp.appendChild(svg("polygon", { points: pts.map(function (q) { return q.join(","); }).join(" ") }));
    var t = svg("text", { x: 0, y: opts.labels === "latin" ? 5 : 7, "text-anchor": "middle", "class": opts.labels === "latin" ? "latin" : "" });
    t.textContent = label(p, opts.labels); grp.appendChild(t);
    g.appendChild(grp);
  }
  // opts: {flip, labels, hl, arrows, sel (sq or "hand:b:P"), targets, last, onSquare(sq), onHand(side, piece)}
  function draw(box, pos, opts) {
    opts = opts || {};
    var flip = !!opts.flip, W = 2 * M + 9 * S, top = HAND_H, Hh = top + 2 * M + 9 * S + HAND_H;
    function xy(sq) { var r = Math.floor(sq / 9), c = sq % 9; if (flip) { r = 8 - r; c = 8 - c; } return [M + c * S + S / 2, top + M + r * S + S / 2]; }
    var root = svg("svg", { viewBox: "0 0 " + W + " " + Hh, "class": "sg-svg", role: "img", "aria-label": "Shogi position " + toSfen(pos) });
    var grid = svg("g", { "class": "sg-grid" });
    grid.appendChild(svg("rect", { x: M, y: top + M, width: 9 * S, height: 9 * S, "class": "sg-boardbg" }));
    for (var i = 0; i <= 9; i++) {
      grid.appendChild(svg("line", { x1: M + i * S, y1: top + M, x2: M + i * S, y2: top + M + 9 * S }));
      grid.appendChild(svg("line", { x1: M, y1: top + M + i * S, x2: M + 9 * S, y2: top + M + i * S }));
    }
    [[3, 3], [3, 6], [6, 3], [6, 6]].forEach(function (d) { grid.appendChild(svg("circle", { cx: M + d[1] * S, cy: top + M + d[0] * S, r: 2.5, "class": "sg-star" })); });
    root.appendChild(grid);
    for (var k = 0; k < 9; k++) {
      var fl = flip ? k + 1 : 9 - k, t = svg("text", { x: M + k * S + S / 2, y: top + M - 7, "class": "sg-coord", "text-anchor": "middle" }); t.textContent = fl; root.appendChild(t);
      var rk = flip ? RANKS[8 - k] : RANKS[k], t2 = svg("text", { x: M + 9 * S + 10, y: top + M + k * S + S / 2 + 4, "class": "sg-coord", "text-anchor": "middle" }); t2.textContent = rk; root.appendChild(t2);
    }
    function cell(sq, cls) { var p = xy(sq); root.appendChild(svg("rect", { x: p[0] - S / 2 + 1, y: p[1] - S / 2 + 1, width: S - 2, height: S - 2, "class": cls })); }
    (opts.hl || []).forEach(function (sq) { cell(sq, "sg-hl"); });
    if (opts.last) { if (opts.last.from != null) cell(opts.last.from, "sg-last"); cell(opts.last.to, "sg-last"); }
    if (typeof opts.sel === "number") cell(opts.sel, "sg-sel");
    pos.board.forEach(function (p, sq) {
      var c = xy(sq), g = svg("g", { "class": "sg-sq" + (opts.onSquare ? " live" : ""), "data-sq": sqName(sq) });
      g.appendChild(svg("rect", { x: c[0] - S / 2, y: c[1] - S / 2, width: S, height: S, "class": "sg-hit" }));
      if (p) {
        pieceShape(g, c[0], c[1], p, opts);
        var ti = svg("title", {}); ti.textContent = (colorOf(p) === "b" ? "Sente " : "Gote ") + NAMES[promoted(p) ? "+" + base(p) : base(p)] + " on " + sqName(sq); g.appendChild(ti);
      }
      if (opts.targets && opts.targets.indexOf(sq) >= 0) g.appendChild(svg("circle", { cx: c[0], cy: c[1], r: p ? S * 0.46 : S * 0.12, "class": p ? "sg-cap" : "sg-dot" }));
      if (opts.onSquare) g.addEventListener("click", function () { opts.onSquare(sq); });
      root.appendChild(g);
    });
    // hands: Gote's at the top, Sente's at the bottom (swapped when flipped)
    ["w", "b"].forEach(function (side) {
      var atTop = (side === "w") !== flip, y = atTop ? HAND_H / 2 + 2 : top + 2 * M + 9 * S + HAND_H / 2 - 2;
      var lab = svg("text", { x: M - 4, y: y + 4, "class": "sg-handlabel" }); lab.textContent = side === "b" ? "▲ hand" : "△ hand"; root.appendChild(lab);
      var x = M + 58;
      HAND_ORDER.forEach(function (t) {
        var n = pos.hands[side][t];
        if (!n) return;
        var p = side === "b" ? t : t.toLowerCase(), g = svg("g", { "class": "sg-hand" + (opts.onHand ? " live" : ""), "data-hand": side + t });
        g.appendChild(svg("rect", { x: x - S / 2, y: y - S / 2, width: S, height: S, "class": "sg-hit" }));
        if (opts.sel === "hand:" + side + ":" + t) g.appendChild(svg("rect", { x: x - S / 2 + 1, y: y - S / 2 + 1, width: S - 2, height: S - 2, "class": "sg-sel" }));
        pieceShape(g, x, y, p, opts, "inhand");
        if (n > 1) { var cn = svg("text", { x: x + S * 0.45, y: y + S * 0.45, "class": "sg-count", "text-anchor": "middle" }); cn.textContent = n; g.appendChild(cn); }
        var ti = svg("title", {}); ti.textContent = (side === "b" ? "Sente" : "Gote") + " has " + n + " " + NAMES[t] + (n > 1 ? "s" : "") + " in hand"; g.appendChild(ti);
        if (opts.onHand) g.addEventListener("click", function () { opts.onHand(side, t); });
        root.appendChild(g);
        x += S + 6;
      });
    });
    (opts.arrows || []).forEach(function (a) {
      var p = xy(a[0]), q = xy(a[1]), dx = q[0] - p[0], dy = q[1] - p[1], L = Math.sqrt(dx * dx + dy * dy) || 1, ex = q[0] - dx / L * 10, ey = q[1] - dy / L * 10, nx = -dy / L, ny = dx / L;
      root.appendChild(svg("line", { x1: p[0], y1: p[1], x2: ex, y2: ey, "class": "sg-arrow" }));
      root.appendChild(svg("polygon", { points: [q[0], q[1], ex + nx * 6, ey + ny * 6, ex - nx * 6, ey - ny * 6].join(" "), "class": "sg-arrowhead" }));
    });
    box.textContent = ""; box.appendChild(root);
  }
  function listSq(s) { return String(s || "").split(/[\s,]+/).filter(Boolean).map(sqIndex).filter(function (i) { return i >= 0; }); }
  function listArrows(s) { return String(s || "").split(/[\s,]+/).filter(Boolean).map(function (a) { var p = a.split("-"); return [sqIndex(p[0]), sqIndex(p[1])]; }).filter(function (a) { return a[0] >= 0 && a[1] >= 0; }); }
  function legend(labels) {
    return (labels === "latin" ? "K king · R rook · B bishop · G gold · S silver · N knight · L lance · P pawn; + = promoted."
      : "王玉 king · 飛 rook · 角 bishop · 金 gold · 銀 silver · 桂 knight · 香 lance · 歩 pawn; promoted: 龍 dragon · 馬 horse · 全圭杏と move like gold.")
      + " ▲ Sente moves first; pieces point at the opponent. Click a piece in hand to drop it.";
  }

  // Click controller: board pieces, hand pieces, and a promote? choice. onMove(move) is called with a legal move.
  function clicker(box, chooser, getPos, opts, onMove) {
    var sel = null;
    function render(extra) {
      var pos = getPos(), locked = opts.locked && opts.locked(), targets = [];
      if (sel != null) targets = legalMoves(pos, typeof sel === "number" ? sel : sel.split(":")[2]).map(function (m) { return m.to; });
      draw(box, pos, Object.assign({}, opts, extra || {}, { sel: sel, targets: targets, onSquare: locked ? null : square, onHand: locked ? null : hand }));
    }
    function hand(side, t) {
      var pos = getPos();
      chooser.textContent = "";
      if (side !== pos.turn) return;
      sel = sel === "hand:" + side + ":" + t ? null : "hand:" + side + ":" + t; render();
    }
    function square(sq) {
      var pos = getPos(), p = pos.board[sq];
      chooser.textContent = "";
      if (sel != null) {
        var ms = legalMoves(pos, typeof sel === "number" ? sel : sel.split(":")[2]).filter(function (m) { return m.to === sq; });
        if (ms.length === 1) { sel = null; onMove(ms[0]); return; }
        if (ms.length === 2) {           // promotion is optional: ask
          var q = document.createElement("span"); q.textContent = "Promote? ";
          chooser.appendChild(q);
          ms.sort(function (a, b) { return a.promote ? -1 : 1; }).forEach(function (m) {
            var bt = document.createElement("button"); bt.type = "button"; bt.textContent = m.promote ? "Promote" : "Don't promote";
            bt.addEventListener("click", function () { chooser.textContent = ""; sel = null; onMove(m); });
            chooser.appendChild(bt);
          });
          return;
        }
      }
      sel = p && colorOf(p) === pos.turn && sel !== sq ? sq : null;
      render();
    }
    return render;
  }

  function initDiagram(el) {
    var d = el.dataset, start = parse(d.sfen || START), opts = { flip: d.flip === "true", labels: d.labels, hl: listSq(d.hl), arrows: listArrows(d.arrows) };
    el.textContent = "";
    var box = document.createElement("div"); box.className = "sg-box"; el.appendChild(box);
    var cap = document.createElement("div"); cap.className = "sg-caption";
    if (d.play !== "true") { draw(box, start, opts); if (d.caption) { cap.textContent = d.caption; el.appendChild(cap); } return; }
    var hist = [start], last = null, st = document.createElement("p"); st.className = "sg-status";
    var chooser = document.createElement("div"); chooser.className = "sg-chooser";
    var row = document.createElement("div"); row.className = "sg-controls";
    var undo = document.createElement("button"); undo.type = "button"; undo.textContent = "Undo";
    var reset = document.createElement("button"); reset.type = "button"; reset.textContent = "Start over";
    row.appendChild(undo); row.appendChild(reset);
    var leg = document.createElement("p"); leg.className = "sg-legend"; leg.textContent = legend(d.labels);
    el.insertBefore(leg, box); el.appendChild(chooser); el.appendChild(st); el.appendChild(row);
    if (d.caption) { cap.textContent = d.caption; el.appendChild(cap); }
    opts.hl = []; opts.arrows = [];
    var cur = function () { return hist[hist.length - 1]; };
    var render = clicker(box, chooser, cur, opts, function (m) { hist.push(apply(cur(), m)); last = m; update(); });
    function update() { st.textContent = status(cur()).text; render({ last: last }); }
    undo.addEventListener("click", function () { if (hist.length > 1) { hist.pop(); last = null; chooser.textContent = ""; update(); } });
    reset.addEventListener("click", function () { hist = [start]; last = null; chooser.textContent = ""; update(); });
    update();
  }

  function initMove(q, ctx) {
    var d = q.dataset, pos = parse(d.sfen || START), U = LP.util;
    var answers = String(d.answer || "").split("|").map(function (s) { return s.trim(); }).filter(Boolean);
    if (!answers.length) throw new Error("shogi-move needs data-answer");
    answers = answers.map(function (a) { var m = findMove(pos, a); if (!m) throw new Error("shogi-move: answer " + a + " is not legal here"); return m.usi; });
    var done = false, played = null;
    var leg = U.el("p", "sg-legend", legend(d.labels)), box = U.el("div", "sg-box"), chooser = U.el("div", "sg-chooser");
    U.beforeExplain(q, leg); U.beforeExplain(q, box); U.beforeExplain(q, chooser);
    var opts = { flip: d.flip === "true", labels: d.labels, hl: listSq(d.hl), locked: function () { return done; } };
    var render = clicker(box, chooser, function () { return played ? apply(pos, played) : pos; }, opts, function (m) {
      var ok = answers.indexOf(m.usi) >= 0;
      ctx.result(ok, m.usi);
      if (ok) { done = true; played = m; render({ last: m }); ctx.feedback(true, null); }
      else { render(); ctx.feedback(false, m.usi + " is legal, but not the move we're after." + (d.hint ? " Hint: " + d.hint : "")); }
    });
    render();
    document.addEventListener("lp:event", function (e) {
      var ev = e.detail;
      if (ev.item === ctx.id && (ev.type === "reveal" || ev.kind === "skip") && !done) {
        done = true; var m = findMove(pos, answers[0]); render(m.from != null ? { arrows: [[m.from, m.to]] } : { hl: [m.to] });
      }
    });
  }

  if (window.LP && LP.register) {
    LP.register({ type: "shogi", selector: ".shogi-board", scored: false, init: initDiagram });
    LP.register({ type: "shogi-move", init: initMove });
  } else {
    var init = function () { document.querySelectorAll(".shogi-board").forEach(initDiagram); };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  }
})();
