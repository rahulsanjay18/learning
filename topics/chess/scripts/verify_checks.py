"""Verify "checks first" positions: after the candidate move, list the opponent's checks, and judge the move with Stockfish.

"Safe" = the move doesn't cost 2+ pawns relative to the position's evaluation and isn't losing to a forced mate.
Usage: PYTHONPATH=<python-chess src> python3 verify_checks.py lesson-0002-checks.json
Needs Stockfish at /usr/games/stockfish.
"""
import json, sys
import chess, chess.engine

eng = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
LIMIT = chess.engine.Limit(depth=14, time=3)


def score(board, pov):
    return eng.analyse(board, LIMIT)["score"].pov(pov).score(mate_score=10000)


for p in json.load(open(sys.argv[1])):
    b = chess.Board(p["fen"])
    assert b.is_valid(), (p["id"], b.status())
    mover = b.turn
    before = score(b, mover)
    b.push_san(p["move"])
    checks = sorted(b.san(m) for m in b.legal_moves if b.gives_check(m))
    after = score(b, mover)
    verdict = "Safe" if after > -9000 and after >= min(before, 300) - 200 else "Lost"
    errs = []
    if "checks" in p and sorted(p["checks"]) != checks:
        errs.append(f"checks expected {sorted(p['checks'])}")
    if "answer" in p and p["answer"] != verdict:
        errs.append(f"answer expected {p['answer']}")
    print(("BAD " if errs else "OK  ") + f"{p['id']}: {p['move']} -> checks {checks}; eval {before:+} -> {after:+} ({verdict}) {'; '.join(errs)}")
eng.quit()
