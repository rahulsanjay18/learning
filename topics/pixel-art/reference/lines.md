# Pixel art lines: the three rules (Markdown copy of lesson 1)

Saved copy of [lesson 1](../lessons/0001-clean-lines.html) and the [lines reference](lines.html).

## Terms
- **Segment**: one straight run of pixels in a line (flat, upright, or a single pixel). Segments meet diagonally.
- **Double**: an unneeded pixel that makes a right-angle (L) corner in a 1px line [1][4].
- **Jaggy**: a bump from uneven segment lengths in a line that should look straight or smoothly curved [4].
- **Perfect line**: slope 1:0, 2:1, 1:1, 1:2 or 0:1 [2]. Here *a:b* = a across per b down.

## The rules
1. **Diagonal joins only**: no L corners. Break it only to make a deliberate sharp corner [1].
2. **Straight = equal segments.** Prefer perfect lines [1][2].
3. **Curve = segments change progressively.** Longest where the curve is flat or upright, shortest at the diagonal;
   "avoid right angles" [1][2].

**Math version:** give each segment a slope (flat run of n → n, upright run of n → 1/n, single → 1).
A straight line's sequence is constant. A clean convex curve's sequence is monotonic (e.g. 3, 2, 1, 1, ½, ⅓).
Jaggies are where it breaks that pattern. (This is exactly what `assets/pixels.js` checks.)

## LibreSprite [3]
New `Ctrl+N` · Pencil `B` · Eraser `E` · Line `L` · Fill `G` · Eyedropper `I` · Zoom `Z` · Select `M` · Move `V` ·
Save `.ase` `Ctrl+S` · Scaled PNG: File → Save Copy As → resize · Shortcuts `Ctrl+Alt+Shift+K` · "Pixel Perfect" checkbox in the brush options bar.
Scale only by whole numbers, with no smoothing [5].

## Sources
1. Skeddles, "Pixel Art Outlines", Lospec, 2016. https://lospec.com/articles/pixel-art-outlines/
2. Fil Razorback (Les Forges), "Chapter 2: Lines and Curves", OpenGameArt. https://opengameart.org/content/chapter-2-lines-and-curves
3. LibreSprite wiki, "Know your workspace". https://github.com/LibreSprite/libresprite.github.io/wiki/Know-your-workspace
4. FrostDrive, "Pixel Art Practices Explained Simply", Clip Studio Tips. https://tips.clip-studio.com/en-us/articles/5360
5. Raymond Schlitter, "Pixelblog 5: Back to the Basics", 2018. https://www.slynyrd.com/blog/2018/5/16/pixelblog-5-back-to-basics
