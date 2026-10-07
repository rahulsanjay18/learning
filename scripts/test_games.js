// Tests for assets/plugins/games.js (tic-tac-toe, Nim, Hex solver) and every game widget in the repo.
//   node scripts/test_games.js
const fs = require("fs"), path = require("path");
const G = require("../assets/plugins/games.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + extra)); if (!cond) fails++; };

// ---------- tic-tac-toe ----------
let s = G.parse("ttt", "");
let v = G.solve("ttt", s);
check("ttt: empty board is a draw with best play, game lasts 9 plies", v.v === 0 && v.d === 9, JSON.stringify(v));
s = G.parse("ttt", "XX./OO./...");
v = G.solve("ttt", s);
check("ttt: X completes the top row: win in 1", v.v === 1 && v.d === 1, JSON.stringify(v));
check("ttt: the winning move is c1 (index 2)", G.solverMove("ttt", s, 0) === 2);
check("ttt: describe", G.describeMove("ttt", s, 2) === "X on c1");
s = G.parse("ttt", "X../.O./..X");      // X corners, O centre, O to move: O must take an edge, a corner loses
const best = G.bestMoves("ttt", s).map(x => x.move).sort();
check("ttt: after X-corner, O-centre, X-opposite-corner, only edges hold the draw for O", JSON.stringify(best) === JSON.stringify([1, 3, 5, 7]), JSON.stringify(best));
check("ttt: rejects bad counts", (() => { try { G.parse("ttt", "XXX/.../..."); return false; } catch { return true; } })());

// ---------- Nim: Bouton's theorem (nim-sum 0 <=> the side to move loses) ----------
let bad = [];
for (let a = 0; a <= 5; a++) for (let b = 0; b <= 5; b++) for (let c = 0; c <= 5; c++) {
  const st = G.parse("nim", `${a} ${b} ${c}`), val = G.solve("nim", st).v, xor = a ^ b ^ c;
  if ((xor !== 0) !== (val === 1)) bad.push(`${a} ${b} ${c}`);
  if (xor !== 0) {   // every best move leaves nim-sum 0
    for (const m of G.bestMoves("nim", st)) { const t = G.play("nim", st, m.move); if (t.heaps.reduce((x, y) => x ^ y, 0) !== 0) bad.push(`move ${m.move} in ${a} ${b} ${c}`); }
  }
}
check("nim: solver agrees with nim-sum on all 216 positions up to 5 5 5", bad.length === 0, bad.slice(0, 5).join("; "));
check("nim: describe", G.describeMove("nim", G.parse("nim", "3 4 5"), 102) === "take 2 from heap 2");
check("nim: rejects huge positions", (() => { try { G.parse("nim", "15 15 15 15"); return false; } catch { return true; } })());

// ---------- Hex ----------
check("hex: Black column wins", G.hexWinner(G.parse("hex", "B../B../BWW")) === "B");
check("hex: White row wins", G.hexWinner(G.parse("hex", "WWW/BB./B..")) === "W");
check("hex: (r,c)-(r+1,c-1) is adjacent: b1, a2, a3 connect top to bottom", G.hexWinner({ n: 3, b: (1 << 1) | (1 << 3) | (1 << 6), w: 0 }) === "B");
check("hex: (r,c)-(r+1,c+1) is NOT adjacent: a1, b2, c3 don't connect", G.hexWinner({ n: 3, b: (1 << 0) | (1 << 4) | (1 << 8), w: 0 }) === null);
// No draws: every full 3×3 board (5 Black, 4 White) has exactly one winner.
let draws = 0, both = 0;
for (let mask = 0; mask < 512; mask++) {
  let k = 0; for (let i = 0; i < 9; i++) if (mask & (1 << i)) k++;
  if (k !== 5) continue;
  const st = { n: 3, b: mask, w: 511 & ~mask };
  const e = G.hexWinner(st), eW = G.hexWinner({ n: 3, b: 0, w: st.w });
  if (!e) draws++;
  if (e === "B" && eW === "W") both++;
}
check("hex: every full 3×3 board has exactly one winner (no draws)", draws === 0 && both === 0, `draws ${draws}, both ${both}`);
check("hex: rejects an empty position string", (() => { try { G.parse("hex", ""); return false; } catch { return true; } })());
s = G.parse("hex", ".../.../...");
v = G.solve("hex", s);
check("hex: 3×3 is a first-player win", v.v === 1, JSON.stringify(v));
check("hex: the centre b2 is a winning first move", G.bestMoves("hex", s).some(x => x.move === 4));
let t0 = Date.now();
s = G.parse("hex", "B.../.W../..B./...W");
v = G.solve("hex", s);
const ms = Date.now() - t0;
check(`hex: a 4×4 position with 4 stones solves fast (${ms} ms)`, ms < 3000);
check("hex: 4×4 needs 4 stones", (() => { try { G.parse("hex", "B.../..../..../...."); return false; } catch { return true; } })());

// ---------- every widget in the repo ----------
const files = [];
(function walk(d) {
  for (const f of fs.readdirSync(d)) {
    if (f === ".git" || f === "node_modules" || f === "library") continue;
    const p = path.join(d, f);
    if (fs.statSync(p).isDirectory()) walk(p); else if (f.endsWith(".html")) files.push(p);
  }
})(path.join(__dirname, ".."));
let widgets = 0;
const attr = (tag, a) => { const m = new RegExp(`\\s${a}="([^"]*)"`).exec(tag); return m ? m[1] : null; };
for (const f of files) {
  const html = fs.readFileSync(f, "utf8");
  for (const m of html.matchAll(/<div\b[^>]*(class="lp-game"|data-type="game-move")[^>]*>/g)) {
    widgets++;
    const tag = m[0], name = attr(tag, "data-game"), pos = attr(tag, "data-position") || "", where = `${path.relative(path.join(__dirname, ".."), f)} ${attr(tag, "data-id") || name}`;
    try {
      const st = G.parse(name, pos);
      if (/game-move/.test(tag)) {
        if (G.over(name, st)) throw new Error("game already over");
        const all = G.moveValues(name, st), bestM = G.bestMoves(name, st);
        if (bestM[0].v < 0) throw new Error("side to move is lost");
        if (bestM.length === all.length) throw new Error("every move is equally good");
        if (attr(tag, "data-answer")) throw new Error("game-move takes no data-answer (the solver decides)");
      }
    } catch (e) { check(`widget ${where}`, false, e.message); continue; }
  }
}
check(`all ${widgets} game widgets in the repo are valid`, true);
console.log(fails ? `games: ${fails} failed` : "games: all passed");
process.exit(fails ? 1 : 0);
