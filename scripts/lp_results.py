#!/usr/bin/env python3
"""Record pasted results lines (for lessons done on a device without sync).

    python3 scripts/lp_results.py "<the whole pasted block>"        (several lessons OK; or pipe it on stdin)
    python3 scripts/lp_results.py --no-post "<block>"                only update the curriculum

A block is the "Copy my results" text: one `lp-results <topic>/<stem> | ...` line, then `miss <id>: <answer>` and
`free <id>: <answer>` lines. For each lesson this script
  1. posts the answers it can see to the progress server as events (misses, skips, free responses, the note), so they feed spaced
     review, show up for grading (`scripts/grade.py`), and fill in the page on synced devices. Event ids are derived from the
     content, so pasting the same block twice stores nothing new. Right-first-try answers aren't named in the paste, so they
     can't be posted.
  2. marks the lesson completed in its course (curriculum.json "completed"), unless the line says some questions are
     unanswered: then it's reported as partial and left open.
Then it runs scripts/test_programs.py. Learning records stay a judgment call.
"""
import hashlib, json, pathlib, re, subprocess, sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOOKS_URL = "https://books.tail59e10.ts.net"     # CLAUDE.md BOOKS_URL; the cloud proxy injects auth


def blocks(text):
    """[(topic, stem, header_rest, [detail lines])] for every lp-results block in the paste."""
    out, cur = [], None
    for line in text.splitlines():
        m = re.match(r"\s*lp-results\s+([\w-]+)/([\w-]+)\s*\|(.*)$", line)
        if m:
            cur = (m.group(1), m.group(2), m.group(3), []); out.append(cur)
        elif cur and line.strip():
            cur[3].append(line.strip())
    fixed = []
    for topic, stem, rest, details in out:     # newlines lost (pasted through a shell): split detail lines out of the header
        parts = re.split(r"\s(?=(?:miss|free)\s+[\w-]+:)", rest)
        fixed.append((topic, stem, parts[0], [p.strip() for p in parts[1:]] + details))
    out = fixed
    return out


def field(rest, name):
    m = re.search(r"\|\s*" + name + r":\s*([^|]*)", "|" + rest)
    return m.group(1).strip() if m else ""


def events(topic, stem, rest, details):
    page, ts = f"{topic}/{stem}", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    def eid(*parts):
        return "paste-" + hashlib.sha256("|".join((page,) + parts).encode()).hexdigest()[:20]
    evs, seen = [], set()
    for d in details:
        m = re.match(r"(miss|free)\s+([\w-]+):\s*(.*)$", d, re.S)
        if not m: continue
        kind, qid, ans = m.groups()
        seen.add(qid)
        evs.append(dict(v=1, eid=eid(kind, qid, ans), type="attempt", page=page, item=f"{page}#{qid}", ts=ts, answer=ans,
                        kind="deferred" if kind == "free" else "auto", correct=None if kind == "free" else False))
    for qid in filter(None, (x.strip() for x in field(rest, "missed").split(","))):
        if qid not in seen:     # a miss with no recorded answer
            evs.append(dict(v=1, eid=eid("miss", qid), type="attempt", page=page, item=f"{page}#{qid}", ts=ts, kind="auto", correct=False))
    for qid in filter(None, (x.strip() for x in field(rest, "skipped").split(","))):
        evs.append(dict(v=1, eid=eid("skip", qid), type="attempt", page=page, item=f"{page}#{qid}", ts=ts, kind="skip", correct=False))
    for qid in filter(None, (x.strip() for x in field(rest, "guessed").split(","))):
        evs.append(dict(v=1, eid=eid("right", qid), type="attempt", page=page, item=f"{page}#{qid}", ts=ts, kind="auto", correct=True))
        evs.append(dict(v=1, eid=eid("guess", qid), type="confidence", page=page, item=f"{page}#{qid}", ts=ts, value="guessed"))
    for name, typ in (("note", "note"), ("rating", "rating")):
        v = field(rest, name)
        if v:
            evs.append(dict(v=1, eid=eid(name, v), type=typ, page=page, ts=ts, **({"text": v} if typ == "note" else {"value": v})))
    if re.search(r"pretest|placement", stem):
        for e in evs: e["pretest"] = True
    return evs


def post(evs):
    r = subprocess.run(["curl", "-s", "-m", "15", "-X", "POST", BOOKS_URL + "/progress/events", "-H", "Content-Type: application/json",
                        "-d", json.dumps({"events": evs})], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except ValueError:
        return {"error": (r.stdout or r.stderr)[:200]}


def main(text, do_post=True):
    progs = json.loads((ROOT / "programs.json").read_text())
    for topic, stem, rest, details in blocks(text):
        if do_post:
            evs = events(topic, stem, rest, details)
            res = post(evs) if evs else {"stored": 0}
            print(f"{topic}/{stem}: posted {len(evs)} events -> {res}")
        m = re.search(r"(\d+)\s+unanswered", rest)
        if m and int(m.group(1)) > 0:
            print(f"{topic}/{stem}: partial ({m.group(1)} unanswered), left open")
            continue
        done = False
        for maj in progs["majors"]:
            if not maj.get("curriculum"): continue
            p = ROOT / maj["curriculum"]; cur = json.loads(p.read_text())
            for c in cur["courses"]:
                if c.get("topic", maj["slug"]) == topic and stem in c.get("lessons", []):
                    if stem not in c.setdefault("completed", []): c["completed"].append(stem)
                    p.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n"); done = True
                    print(f"{topic}/{stem} -> completed in {maj['curriculum']} {c['id']}:{rest.strip()[:160]}")
        if not done: print(f"{topic}/{stem}: not in any course's lessons (outside the majors, or add it to a curriculum)")
    subprocess.run([sys.executable, str(ROOT / "scripts/test_programs.py")])


if __name__ == "__main__":
    args = sys.argv[1:]
    do_post = "--no-post" not in args
    args = [a for a in args if a != "--no-post"]
    main("\n".join(args) or sys.stdin.read(), do_post)
