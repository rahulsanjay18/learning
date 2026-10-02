"""Move-by-move Stockfish review of a PGN. Usage: PYTHONPATH=<python-chess src> python3 analyze_game.py game.pgn
Needs Stockfish at /usr/games/stockfish (apt-get install -y stockfish works in the cloud container)."""
import sys, chess, chess.pgn, chess.engine
g = chess.pgn.read_game(open(sys.argv[1]))
eng = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
b = g.board()
lim = chess.engine.Limit(depth=18)
def cp(info, pov=chess.WHITE):
    s = info["score"].pov(pov)
    return s.score(mate_score=10000)
prev = eng.analyse(b, lim)
for node in g.mainline():
    mv = node.move
    side = b.turn
    best = prev.get("pv", [None])[0]
    best_san = b.san(best) if best else "?"
    san = b.san(mv)
    num = f"{b.fullmove_number}{'.' if side else '...'}"
    before = cp(prev)
    b.push(mv)
    prev = eng.analyse(b, lim)
    after = cp(prev)
    swing = (after - before) if side == chess.WHITE else (before - after)
    pv = prev.get("pv", [])[:4]
    tmp = b.copy(); pvs = []
    for m in pv: pvs.append(tmp.san(m)); tmp.push(m)
    flag = "  <<< " + ("BLUNDER" if swing < -250 else "mistake") if swing < -90 else ""
    print(f"{num} {san:7} eval(W) {after/100:+6.2f}  best was {best_san:7} swing {swing/100:+6.2f}{flag}  | reply line: {' '.join(pvs)}")
eng.quit()
