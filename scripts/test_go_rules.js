// Unit tests for the Go rules in assets/plugins/go.js, and a check of every go-move problem's solution.
//   node scripts/test_go_rules.js
const fs = require("fs"), path = require("path");
const GoRules = require("../assets/plugins/go.js");
let fails = 0;
const check = (name, cond) => { console.log((cond ? "ok   " : "FAIL ") + name); if (!cond) fails++; };
const P = (n, s = 9) => GoRules.parse(n, s);

// coordinates skip I
check("coords: J is column 9 (no I)", P("J1").x === 8 && GoRules.parse("I5", 9) === null);

// single-stone capture
let g = new GoRules(9).load("D5 F5 E6", "E5");
let r = g.play("B", P("E4"));
check("capture one stone", r.ok && r.captured.length === 1 && !g.get(P("E5")));

// suicide refused
g = new GoRules(9).load("D5 F5 E6 E4", "");
r = g.play("W", P("E5"));
check("suicide refused", !r.ok && /Suicide/.test(r.reason) && !g.get(P("E5")));

// a move that captures is not suicide
g = new GoRules(9).load("A2", "B1 B2 A3");
r = g.play("W", P("A1"));
check("capturing move into no-liberty point is legal", r.ok && r.captured.length === 1);

// corner capture of two stones
g = new GoRules(9).load("A1 A2", "B1 B2");
r = g.play("W", P("A3"));
check("capture two stones in the corner", r.ok && r.captured.length === 2);

// simple ko. Before White's move (C..F, rows 6..4):
//   . B W .      row 6
//   B . B W      row 5   White plays D5, capturing E5
//   . B W .      row 4
g = new GoRules(9).load("D6 C5 D4 E5", "E6 F5 E4");
r = g.play("W", P("D5"));          // W captures B E5
check("ko: white captures one stone", r.ok && r.captured.length === 1 && GoRules.label(r.captured[0]) === "E5");
r = g.play("B", P("E5"));          // immediate recapture refused
check("ko: immediate recapture refused", !r.ok && /Ko/.test(r.reason));
g.play("B", P("H8")); g.play("W", P("H2"));
r = g.play("B", P("E5"));
check("ko: recapture allowed after a move elsewhere", r.ok && r.captured.length === 1);

// Every go-move problem in the repo: replay the solution and make sure each move is legal.
const files = [path.join(__dirname, "../assets/gallery.html")];
for (const t of fs.readdirSync(path.join(__dirname, "../topics")))
  for (const d of ["lessons", "reference"]) {
    const dir = path.join(__dirname, "../topics", t, d);
    if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) if (f.endsWith(".html")) files.push(path.join(dir, f));
  }
const attr = (tag, name) => { const m = tag.match(new RegExp(name + '="([^"]*)"')); return m ? m[1] : ""; };
for (const f of files) {
  for (const tag of fs.readFileSync(f, "utf8").match(/<div[^>]*data-type="go-move"[^>]*>/g) || []) {
    const size = parseInt(attr(tag, "data-size"), 10) || 19, id = attr(tag, "data-id");
    const line = (attr(tag, "data-solution") || attr(tag, "data-answer").split("|")[0]).toUpperCase().split(/\s+/).filter(Boolean);
    let color = (attr(tag, "data-to-play") || "B").toUpperCase(), board = new GoRules(size).load(attr(tag, "data-black"), attr(tag, "data-white"));
    const ok = line.every(m => { const res = board.play(color, GoRules.parse(m, size)); color = color === "B" ? "W" : "B"; return res.ok; });
    check(`${path.relative(path.join(__dirname, ".."), f)} ${id}: solution ${line.join(" ")} is legal`, ok);
  }
}
console.log(fails ? `\n${fails} failure(s)` : "\nall passed");
process.exit(fails ? 1 : 0);
