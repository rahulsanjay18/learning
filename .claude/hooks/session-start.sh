#!/bin/bash
# SessionStart hook (cloud sessions only): installs what the repo's tests and tools need. Idempotent; skips what's present.
#   fastapi/uvicorn/httpx  -> progress-server + book-server tests
#   python-shogi           -> differential tests behind scripts/fixtures/shogi-python-shogi-perft.json
#   python-chess, stockfish -> /game-review (topics/chess/scripts/analyze_game.py)
# Playwright + Chromium are preinstalled in the cloud image (scripts/test_widgets.mjs).
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then exit 0; fi

have_py() { python3 -c "import $1" >/dev/null 2>&1; }

for mod in fastapi:fastapi uvicorn:uvicorn httpx:httpx shogi:python-shogi tqdm:tqdm pymupdf4llm:pymupdf4llm; do
  m="${mod%%:*}"; pkg="${mod##*:}"
  have_py "$m" || pip install -q "$pkg" 2>&1 | grep -v -i warning || true
done

# python-chess is pure Python, but Debian's old setuptools can't build its sdist: unpack the source onto the user site instead.
if ! have_py chess; then
  tmp=$(mktemp -d)
  pip download -q chess --no-deps --no-binary :all: -d "$tmp" 2>&1 | grep -v -i warning || true
  site=$(python3 -m site --user-site); mkdir -p "$site"
  tar -xzf "$tmp"/chess-*.tar.gz -C "$tmp" && cp -r "$tmp"/chess-*/chess "$site"/
  rm -rf "$tmp"
fi

if [ ! -x /usr/games/stockfish ]; then
  (apt-get install -y -q stockfish >/dev/null 2>&1 || (apt-get update -q >/dev/null 2>&1 && apt-get install -y -q stockfish >/dev/null 2>&1)) \
    || echo "session-start: stockfish install failed (only /game-review needs it)" >&2
fi

# Report what's missing, never fail the session over it.
for m in fastapi uvicorn httpx shogi chess; do have_py "$m" || echo "session-start: python module $m missing" >&2; done
exit 0
