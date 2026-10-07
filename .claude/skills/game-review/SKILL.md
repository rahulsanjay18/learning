---
name: game-review
description: Review a game the learner played (chess now; xiangqi, shogi or Go later) from a pasted PGN, a chess.com/lichess link or a move list. Runs the engine, writes a short review tied to their lessons, updates the course plan. Use when the learner pastes or mentions a game they played.
argument-hint: "[PGN, link, or 'my last game']"
---

# /game-review

Input: `$ARGUMENTS` (a PGN, a link, or nothing: then ask for the PGN; chess.com: Game → Share → PGN).

## Chess
1. **Save** the PGN as `topics/chess/games/YYYY-MM-DD-vs-<opponent-slug>.pgn` (date from the PGN, else today).
2. **Engine:** `python3 topics/chess/scripts/analyze_game.py <pgn>` (Stockfish + python-chess come from the SessionStart hook;
   if missing: `apt-get install -y stockfish`, and see `.claude/hooks/session-start.sh` for python-chess). Depth 18 by default;
   for a long game lower it in the script call's Limit if it's slow. Read only the lines flagged `mistake`/`BLUNDER` plus a few around them.
3. **Read before writing:** `topics/chess/NOTES.md`, the last two learning records, the previous review in `games/`, and G101's
   `plan` in `topics/games/curriculum.json`, so the review connects to what's being taught (checks first, counting, …).
4. **Write** `…-review.md` in the same shape as the existing reviews:
   `# Game review: <White> vs. <Black>, <date>, <result>` · PGN/engine line · **The short version** (4–5 bullets: opening, the
   turning points, the result) · **Moment N** sections (2–3, only the ones that matter: the position as a lichess analysis link
   `https://lichess.org/analysis/standard/<FEN with spaces as _>`, what happened, the engine's move, **which lesson skill it was**) ·
   **What went well** · **The pattern** (compare with earlier games) · **Sources**. Evaluations in pawns, say from whose side.
   Plain language; no move-by-move dump.
5. **Learning record** if the game shows something new (`topics/chess/learning-records/NNNN-*.md`). **Plan:** if a moment points
   at a skill the next lessons don't cover, adjust G101's `plan` (say so in one line). Run `python3 scripts/test_programs.py`.
6. **Index:** add the review under "Game reviews" in `index.html` (one line: date, opponent, result, the story in a few words).
7. Commit + push (`teach(chess): game review <date>`), then give the learner the review path and the 2–3 takeaways in chat.

## Xiangqi, shogi, Go
No strength engine is installed yet. Use the repo's rules engines (`assets/plugins/xiangqi.js`, `shogi.js`; Go:
`scripts/test_go_rules.js` helpers) only to replay and check legality; judge moves yourself and say the review is unassisted.
If these reviews become regular, suggest Fairy-Stockfish (xiangqi + shogi) or KataGo (Go), installed by the learner.
