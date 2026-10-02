// Print a midpoint-circle quarter arc (top -> right) as art rows. Usage: node arc.js R
const R = +process.argv[2], pad = 1, W = R + 1 + 2 * pad, H = R + 1 + 2 * pad;
const cx = pad, cy = pad + R, on = new Set();
let x = 0, y = R, d = 1 - R;
while (x <= y) {
  on.add(`${cx + x},${cy - y}`); on.add(`${cx + y},${cy - x}`);
  if (d < 0) d += 2 * x + 3; else { d += 2 * (x - y) + 5; y--; }
  x++;
}
for (let r = 0; r < H; r++) { let s = ""; for (let c = 0; c < W; c++) s += on.has(`${c},${r}`) ? "#" : "."; console.log(s); }
