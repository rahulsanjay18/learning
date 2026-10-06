#!/usr/bin/env python3
"""Compact book-server client (plain text, few tokens). Auth is injected by the cloud proxy.

    python3 scripts/books.py find "sutton barto"                    is a book on the server? (id, grade, title)
    python3 scripts/books.py search "power function" [--book ID] [-n 10]
    python3 scripts/books.py grep ID "Definition 8.3.5" [-n 20]      line numbers of a phrase inside one book
    python3 scripts/books.py read ID START [N]                       lines START..START+N-1 (N ≤ 200, default 60)

Grade B books print their warning once: prose only, never equations/figures/tables/code (library/README.md).
"""
import json, subprocess, sys, urllib.parse

BASE = "https://books.tail59e10.ts.net"


def get(path, **params):
    url = BASE + path + ("?" + urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")}) if params else "")
    r = subprocess.run(["curl", "-s", "-m", "30", "-w", "\n%{http_code}", url], capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    if code != "200":
        return None, code, body[:200]
    return json.loads(body), code, None


def opt(args, flag, default=None):
    if flag in args:
        i = args.index(flag); v = args[i + 1]; del args[i:i + 2]; return v
    return default


def warn_once(seen, m):
    if m.get("grade") == "B" and m["id"] not in seen:
        seen.add(m["id"]); print(f"  ! {m['id']} is grade B: prose only, no equations/figures/tables/code")


def main(a):
    if not a: sys.exit(__doc__)
    cmd, n, book = a.pop(0), opt(a, "-n"), opt(a, "--book")
    if cmd == "find":
        j, code, err = get("/books", q=" ".join(a), limit=n or 10)
        if j is None: sys.exit(f"HTTP {code} {err}")
        for b in j: print(f"{b['id']}  {b['grade']}  {b['title'][:110]}")
        if not j: print("not on the server (see library/README.md: ask the learner, or check library/ACCESS.md)")
    elif cmd == "search":
        q = " ".join(a)
        j, code, err = get("/search", q=q, limit=n or 10, book=book, compact="true")
        if isinstance(j, list) and book:                        # old server ignores book/compact: filter client-side
            j, code, err = get("/search", q=q, limit=30)
            if j is not None: j = [r for r in j if r["id"] == book][: int(n or 10)]
        if j is None: sys.exit(f"HTTP {code} {err}")
        if isinstance(j, list):                                 # old server: normalise to compact
            j = {"books": {r["id"]: r for r in j}, "hits": [{"id": r["id"], "start_line": r["start_line"], "snippet": r["snippet"]} for r in j]}
        seen = set()
        for bid, m in j["books"].items(): print(f"[{bid}] {m['grade']} {m['title'][:90]}"); warn_once(seen, m)
        for h in j["hits"]: print(f"{h['id']}:{h['start_line']}  {' '.join(h['snippet'].split())}")
        if not j["hits"]: print("no hits")
    elif cmd == "grep":
        bid, q = a[0], " ".join(a[1:])
        j, code, err = get(f"/grep/{bid}", q=q, limit=n or 20)
        if j is None: sys.exit(f"HTTP {code} {err}" + ("  (grep needs the redeployed book server: notes/HANDOFF.md)" if code == "404" else ""))
        warn_once(set(), j)
        for m in j["matches"]: print(f"{m['line']}: {m['text']}")
        if not j["matches"]: print("no matches")
    elif cmd == "read":
        bid, start, cnt = a[0], int(a[1]), int(a[2]) if len(a) > 2 else 60
        j, code, err = get(f"/read/{bid}", start=start, n=cnt)
        if j is None: sys.exit(f"HTTP {code} {err}")
        warn_once(set(), j)
        print(f"--- {j['title'][:80]} lines {j['start']}-{j['end']} of {j['lines']}")
        for i, l in enumerate(j["text"].splitlines(), j["start"]): print(f"{i}: {l}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
