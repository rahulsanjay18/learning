// Tests for assets/plugins/xiangqi.js and assets/plugins/shogi.js, plus every xiangqi/shogi widget in the repo.
//   node scripts/test_xiangqi_shogi.js            (about 10 s; add --quick to skip the depth-4 perfts)
// Move generators are checked with perft (the number of legal move sequences to a given depth) against published counts:
//   Xiangqi: chessprogramming.org "Chinese Chess Perft Results" (start position + positions 2–6).
//   Shogi:   start position 30 / 900 / 25470 / 719731 (Patrice Duhamel, talkchess "Perft for Xiangqi & Shogi"),
//            and 60 positions with pieces in hand cross-checked against python-shogi (scripts/fixtures/shogi-python-shogi-perft.json).
const fs = require("fs"), path = require("path");
const X = require("../assets/plugins/xiangqi.js"), S = require("../assets/plugins/shogi.js");
const quick = process.argv.includes("--quick");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };
const perfts = (E, pos, exp) => exp.map((_, i) => E.perft(E.parse(pos), i + 1));

// ---------- xiangqi perft ----------
const XQ = [
  [X.START, [44, 1920, 79666, 3290240]],
  ["r1ea1a3/4kh3/2h1e4/pHp1p1p1p/4c4/6P2/P1P2R2P/1CcC5/9/2EAKAE2 w", [38, 1128, 43929, 1339047]],
  ["1ceak4/9/h2a5/2p1p3p/5cp2/2h2H3/6PCP/3AE4/2C6/3A1K1H1 w", [7, 281, 8620, 326201]],
  ["5a3/3k5/3aR4/9/5r3/5h3/9/3A1A3/5K3/2EC2E2 w", [25, 424, 9850, 202884]],
  ["CRH1k1e2/3ca4/4ea3/9/2hr5/9/9/4E4/4A4/4KA3 w", [28, 516, 14808, 395483]],
  ["R1H1k1e2/9/3aea3/9/2hr5/2E6/9/4E4/4A4/4KA3 w", [21, 364, 7626, 162837]],
];
XQ.forEach(([fen, exp], i) => {
  const e = quick ? exp.slice(0, 3) : exp, got = perfts(X, fen, e);
  check(`xiangqi perft position ${i + 1} to depth ${e.length}`, JSON.stringify(got) === JSON.stringify(e), got.join(","));
});
// ---------- xiangqi rules ----------
// (Black's general sits on d9 so the generals never face each other on an open file.)
const xmoves = (fen, from) => X.legalMoves(X.parse(fen), X.sqIndex(from)).map(m => m.uci).sort();
check("xiangqi: flying general (a rook between the generals can't step aside)", !X.findMove(X.parse("4k4/9/9/9/9/9/9/9/4R4/4K4 w"), "e1d1") && !!X.findMove(X.parse("4k4/9/9/9/9/9/9/9/4R4/4K4 w"), "e1e5"));
check("xiangqi: elephants never cross the river", JSON.stringify(xmoves("3k5/9/9/9/9/2E6/9/9/9/4K4 w", "c4")) === JSON.stringify(["c4a2", "c4e2"]), xmoves("3k5/9/9/9/9/2E6/9/9/9/4K4 w", "c4").join(","));
check("xiangqi: a horse is hobbled by a piece at its leg", JSON.stringify(xmoves("3k5/9/9/9/9/9/9/9/1P7/1H2K4 w", "b0")) === JSON.stringify(["b0d1"]), xmoves("3k5/9/9/9/9/9/9/9/1P7/1H2K4 w", "b0").join(","));
const cannon = X.parse("3k5/9/9/9/p8/9/P8/9/9/C3K4 w");
check("xiangqi: cannon captures over exactly one screen, moves freely up to it", !!X.findMove(cannon, "a0a5") && !!X.findMove(cannon, "a0a2") && !X.findMove(cannon, "a0a4"));
check("xiangqi: soldiers move sideways only after crossing the river", JSON.stringify(xmoves("3k5/9/9/9/9/P8/9/9/9/4K4 w", "a4")) === JSON.stringify(["a4a5"]) && JSON.stringify(xmoves("3k5/9/9/9/P8/9/9/9/9/4K4 w", "a5")) === JSON.stringify(["a5a6", "a5b5"]));
const stale = X.parse("3k5/4R4/9/9/9/9/9/9/9/5K3 b");      // Black general d9: d8 and e9 both covered by the chariot on e8
check("xiangqi: no legal move loses, even without check (stalemate)", X.status(stale).over && !X.inCheck(stale, "b") && /Red wins/.test(X.status(stale).text));

// ---------- shogi perft ----------
const sp = [30, 900, 25470, 719731], se = quick ? sp.slice(0, 3) : sp, got = perfts(S, S.START, se);
check(`shogi perft start to depth ${se.length}`, JSON.stringify(got) === JSON.stringify(se), got.join(","));
const ref = JSON.parse(fs.readFileSync(path.join(__dirname, "fixtures/shogi-python-shogi-perft.json"), "utf8"));
const bad = ref.filter(r => S.legalMoves(S.parse(r.sfen)).length !== r.n1 || S.perft(S.parse(r.sfen), 2) !== r.p2);
check(`shogi: ${ref.length} positions with pieces in hand match python-shogi (moves and perft 2)`, bad.length === 0, bad.slice(0, 3).map(b => b.sfen).join(" ; "));
// ---------- shogi rules ----------
let p = S.parse("7nk/7p1/8G/9/9/9/9/9/K8 b PG 1");
check("shogi: a pawn drop may not give checkmate (uchifuzume); a gold drop may", !S.findMove(p, "P*1b") && S.status(S.apply(p, S.findMove(p, "G*1b"))).over);
p = S.parse("4k4/9/9/9/9/9/4P4/9/4K4 b P 1");
check("shogi: no second unpromoted pawn on a file (nifu)", !S.findMove(p, "P*5e") && !!S.findMove(p, "P*4e"));
p = S.parse("4k4/7P1/9/9/9/9/9/9/4K4 b - 1");
check("shogi: a pawn reaching the last rank must promote", !S.findMove(p, "2b2a") && !!S.findMove(p, "2b2a+"));
p = S.parse("4k4/9/9/7P1/9/9/9/9/4K4 b - 1");
check("shogi: promotion is optional entering the zone", !!S.findMove(p, "2d2c") && !!S.findMove(p, "2d2c+"));
p = S.parse("4k4/9/9/9/9/9/9/9/4K4 b N 1");
check("shogi: a knight can't be dropped where it could never move", !S.findMove(p, "N*5b") && !!S.findMove(p, "N*5c"));
p = S.parse("4k4/9/9/9/4+r4/9/9/4R4/4K4 b - 1");
check("shogi: a captured dragon goes to hand as a plain rook", S.toSfen(S.apply(p, S.findMove(p, "5h5e"))) === "4k4/9/9/9/4R4/9/9/9/4K4 w R");

// ---------- every widget in the repo ----------
const files = [];
(function walk(d) {
  for (const f of fs.readdirSync(d)) {
    if ([".git", "node_modules", "library"].includes(f)) continue;
    const q = path.join(d, f);
    if (fs.statSync(q).isDirectory()) walk(q); else if (f.endsWith(".html")) files.push(q);
  }
})(path.join(__dirname, ".."));
const attr = (tag, a) => { const m = new RegExp(`\\s${a}="([^"]*)"`).exec(tag); return m ? m[1] : null; };
let widgets = 0;
for (const f of files) {
  const html = fs.readFileSync(f, "utf8"), rel = path.relative(path.join(__dirname, ".."), f);
  for (const m of html.matchAll(/<div\b[^>]*(class="xq-board"|data-type="xiangqi-move"|class="shogi-board"|data-type="shogi-move")[^>]*>/g)) {
    widgets++;
    const tag = m[0], xq = /xq-board|xiangqi-move/.test(tag), E = xq ? X : S, where = `${rel} ${attr(tag, "data-id") || (xq ? "xiangqi" : "shogi")}`;
    try {
      const pos = E.parse(attr(tag, xq ? "data-fen" : "data-sfen") || E.START);
      if (/-move"/.test(tag)) {
        const ans = (attr(tag, "data-answer") || "").split("|").filter(Boolean);
        if (!ans.length) throw new Error("no data-answer");
        ans.forEach(a => { if (!E.findMove(pos, a)) throw new Error(`answer ${a} is not legal`); });
      }
    } catch (e) { check(`widget ${where}`, false, e.message); }
  }
}
check(`all ${widgets} xiangqi/shogi widgets in the repo are valid`, true);
console.log(fails ? `xiangqi/shogi: ${fails} failed` : "xiangqi/shogi: all passed");
process.exit(fails ? 1 : 0);
