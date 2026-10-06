#!/usr/bin/env python3
"""What's new in the library, and which requests it fills (the /new-books skill).

    python3 scripts/new_books.py [--since GIT_REF] [--manifest PATH]

Compares library/MANIFEST.csv with its previous committed version (or GIT_REF), lists new and regraded books, and matches
new titles against what Claude asked for: library/WANTED.md lines, topics/*/curriculum.json "source" fields marked
"(to buy)" / "(free" / "check:", and the "Books needed" paragraphs of topics/*/PROGRAM.md. Matching is by title words,
so check each match before ticking anything off.
"""
import csv, io, json, re, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STOP = {"the", "a", "an", "of", "and", "to", "in", "for", "on", "with", "by", "from", "edition", "ed", "2nd", "3rd", "z", "lib", "org"}


def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 1}


def manifest(text):
    return {r["id"]: r for r in csv.DictReader(io.StringIO(text))}


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT).stdout


def requests():
    """(where, text) for every place a book was asked for."""
    out = []
    w = ROOT / "library/WANTED.md"
    if w.exists():
        for l in w.read_text().splitlines():
            m = re.match(r"^- _(.+?)_ — (.+?) — .*status: (.+)$", l)
            if m and "got" not in m.group(3).lower(): out.append(("library/WANTED.md", f"{m.group(1)} — {m.group(2)}"))
    for p in sorted(ROOT.glob("topics/*/curriculum.json")):
        for c in json.loads(p.read_text())["courses"]:
            for part in re.split(r";\s*", c.get("source", "")):
                if re.search(r"\(to buy|\(free|check:", part):
                    out.append((f"{p.relative_to(ROOT)} {c['id']}", re.sub(r"\s*\((to buy|free|check).*$", "", part).strip()))
    for p in sorted(ROOT.glob("topics/*/PROGRAM.md")):
        s = p.read_text()
        for block in re.findall(r"\*\*Books (?:needed|to ask for)[^\n]*(?:\n(?![#\n]).*)*", s):
            for t in re.findall(r"\*([^*\n]{4,80})\*", block):
                out.append((str(p.relative_to(ROOT)), t))
    return out


def main(a):
    ref = a[a.index("--since") + 1] if "--since" in a else None
    path = pathlib.Path(a[a.index("--manifest") + 1]) if "--manifest" in a else ROOT / "library/MANIFEST.csv"
    if not ref:
        revs = git("log", "-2", "--format=%H", "--", "library/MANIFEST.csv").split()
        ref = revs[1] if path == ROOT / "library/MANIFEST.csv" and len(revs) > 1 and not git("status", "--porcelain", "library/MANIFEST.csv").strip() else (revs[0] if revs else None)
    old = manifest(git("show", f"{ref}:library/MANIFEST.csv")) if ref else {}
    new = manifest(path.read_text(encoding="utf-8"))
    added = [new[i] for i in new if i not in old]
    regraded = [(old[i], new[i]) for i in new if i in old and old[i]["grade"] != new[i]["grade"]]
    print(f"compared with {ref[:10] if ref else '(nothing)'}: {len(added)} new, {len(regraded)} regraded, {len(new)} total")
    for b in added: print(f"  NEW {b['id']} {b['grade']} {b['title'][:100]}" + (f"  [{b['flags']}]" if b.get("flags") else ""))
    for o, n in regraded: print(f"  REGRADED {n['id']} {o['grade']} -> {n['grade']} {n['title'][:90]}")
    reqs, hits = requests(), 0
    for b in added + [n for _, n in regraded]:
        bw = words(b["title"])
        for where, want in reqs:
            ww = words(want.split(" — ")[0])
            if ww and len(ww & bw) / len(ww) >= 0.6:
                hits += 1
                print(f"  MATCH {b['id']} ({b['grade']}) fills: {want[:80]}  <- {where}")
    print(f"{hits} request match(es). Grade C/F books don't fill a request: they need reconversion (library/RECONVERT.csv).")


if __name__ == "__main__":
    main(sys.argv[1:])
