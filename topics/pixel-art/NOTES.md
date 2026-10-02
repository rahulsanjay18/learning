# Notes (teacher's scratchpad)

## Learner preferences
- Background: BS Math + BS CompE (Penn State), MS CS (Georgia Tech), 5 yrs in AI. Speak at that level; math framings
  (slope sequences, monotonicity, discrete geometry) are welcome and help rules stick.
- Inattentive ADHD: keep lessons ~15 min, one skill each, tight feedback loops.
- Wants citations in text and at the end, and a saved Markdown copy of explanations (see `reference/*.md`).
- No drawing experience. Goal: game sprites and illustrations.
- Tool: LibreSprite (chose the recommended option). OS: Windows/Linux.

## Working notes
- `assets/pixels.js`: static pixel pictures (`.px[data-art]`) and drawing drills (`.px-draw`) with an automatic line
  checker (doubles, broken lines, equal segments, progressive curves). `assets/quiz.js` is copied from chess.
- Never hand-type pixel art into a lesson. Add it to `scripts/verify_art.js` (which asserts the verdict), put a
  `{{name.art}}` / `{{name.marked}}` placeholder in a `scripts/*.template.html`, then run `sh scripts/build_lessons.sh`.
- Slope notation in this workspace: a:b = a across per b down (2:1 = flat segments of length 2). Les Forges writes y:x;
  the set of perfect lines is the same.
- Midpoint-circle output is NOT clean by the progressive-segment rule (R=11 gives 4,2,1,2,…). Possible later lesson:
  "why algorithmic circles need hand cleanup". The learner will like this.
- I couldn't find an authoritative description of exactly what LibreSprite's Pixel Perfect checkbox does, so lesson 1
  makes it an experiment. Ask for the learner's answer next session.
- Plan (tentative, revise after the learner's first PNG): 2) silhouette + outline of a 16×16 object (sword, potion);
  3) limited palette + flat colors (Slynyrd Pixelblog 1, Lospec palettes); 4) light & shadow on a sphere;
  5) a 16×16 or 24×24 character; 6) idle animation (2–4 frames, onion skin F3); 7) walk cycle.
- Spacing: open each lesson with 2 retrieval items from earlier lessons (start lesson 2 with a spot-it pair on lines).
- GLOSSARY.md: not started. Add segment, double, jaggy, perfect line once the learner uses them correctly.
