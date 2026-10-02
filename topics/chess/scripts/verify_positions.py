"""Verify lesson positions: legality, and the material result of an exchange on one square.

Static exchange evaluation (SEE): after the first capture, each side recaptures with its
least valuable piece, and either side may stop whenever continuing would cost it material.
Usage: PYTHONPATH=<path to python-chess> python3 verify_positions.py
"""
import chess

VAL = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}


def least_valuable_capture(board, sq):
    caps = [m for m in board.legal_moves if m.to_square == sq]
    return min(caps, key=lambda m: VAL[board.piece_type_at(m.from_square)], default=None)


def see_after(board, sq):
    """Best gain for the side to move from continuing captures on sq (it may stop: >= 0)."""
    m = least_valuable_capture(board, sq)
    if m is None:
        return 0, []
    gain = VAL[board.piece_type_at(sq)]
    board.push(m)
    reply, line = see_after(board, sq)
    board.pop()
    if gain - reply > 0:
        return gain - reply, [m] + line
    return 0, []


def exchange(fen, san):
    b = chess.Board(fen)
    assert b.is_valid(), (fen, b.status())
    m = b.parse_san(san)
    sq = m.to_square
    gain = VAL[b.piece_type_at(sq)]
    first = b.san(m)
    b.push(m)
    reply, line = see_after(b, sq)
    sans, bb = [first], chess.Board(fen)
    bb.push(m)
    for mv in line:
        sans.append(bb.san(mv)); bb.push(mv)
    return gain - reply, " ".join(sans)


if __name__ == "__main__":
    import json, sys
    positions = json.load(open(sys.argv[1]))
    for p in positions:
        net, line = exchange(p["fen"], p["move"])
        side = chess.Board(p["fen"]).turn
        mover = "White" if side else "Black"
        other = "Black" if side else "White"
        result = f"{mover} gains" if net > 0 else (f"{other} gains" if net < 0 else "Nobody wins")
        ok = "OK " if result == p["answer"] else "BAD"
        print(f"{ok} {p['id']}: {p['move']} -> net {net:+d} for {mover}; line: {line}; expect {p['answer']}, got {result}")
