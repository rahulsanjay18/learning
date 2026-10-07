#!/usr/bin/env python3
"""Check a Vim drill by replaying the learner's keystrokes in real Vim (no config), like VimGolf.

    python3 scripts/vimcheck.py START_FILE TARGET_FILE "KEYS"
    python3 scripts/vimcheck.py --drill topics/eng/vim-drills.json <id> "KEYS"

KEYS uses Vim notation: <Esc> <CR> <Tab> <BS> <C-x> (any Ctrl key) and <lt> for a literal '<'. ':wq' is appended if missing.
Prints PASS/FAIL, the keystroke count (fewer is better) and a diff on failure. Exit 0 on pass.
"""
import difflib, json, re, subprocess, sys, tempfile
from pathlib import Path

SPECIAL = {"esc": "\x1b", "cr": "\r", "enter": "\r", "tab": "\t", "bs": "\x08", "lt": "<", "space": " "}


def decode(keys):
    out, n = [], 0
    for tok in re.split(r"(<[^<>\s]+>)", keys):
        if tok.startswith("<") and tok.endswith(">") and len(tok) > 2:
            name = tok[1:-1].lower()
            if name in SPECIAL:
                out.append(SPECIAL[name]); n += 1; continue
            m = re.fullmatch(r"c-(.)", name)
            if m:
                out.append(chr(ord(m.group(1).upper()) - 64)); n += 1; continue
        out.append(tok); n += len(tok)
    return "".join(out), n


def run(start, target, keys):
    keys = re.sub(r"(<Esc>)?(:wq|:x)<CR>\s*$|ZZ\s*$", "", keys.strip(), flags=re.I)  # saving/quitting doesn't count
    raw, count = decode(keys)
    if not raw.rstrip().endswith(":wq\r") and not raw.rstrip().endswith(":x\r"):
        raw += "\x1b:wq\r"
    with tempfile.TemporaryDirectory() as d:
        f, k = Path(d) / "drill.txt", Path(d) / "keys"
        f.write_text(start)
        k.write_bytes(raw.encode())
        subprocess.run(["vim", "-N", "-u", "NONE", "-i", "NONE", "-n", "-s", str(k), str(f)],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        got = f.read_text()
    ok = got.rstrip("\n") == target.rstrip("\n")
    print(f"{'PASS' if ok else 'FAIL'}  {count} keystrokes")
    if not ok:
        print("".join(difflib.unified_diff(target.splitlines(True), got.splitlines(True), "target", "yours")))
    return ok


def main():
    a = sys.argv[1:]
    if a and a[0] == "--drill":
        drills = {x["id"]: x for x in json.loads(Path(a[1]).read_text())["drills"]}
        dr = drills[a[2]]
        ok = run(dr["start"], dr["target"], a[3])
        if ok and "par" in dr:
            print(f"par {dr['par']}")
    else:
        ok = run(Path(a[0]).read_text(), Path(a[1]).read_text(), a[2])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
