#!/usr/bin/env python3
"""Grade free-response answers without opening lessons.

    python3 scripts/grade.py                      print a grading packet: each ungraded answer with its prompt and rubric
    python3 scripts/grade.py --from FILE.json     same, from a saved /ungraded response (offline, for tests)
    python3 scripts/grade.py post GRADES.json     POST grades: [{"event": "<eid>", "score": 0..1, "feedback": "..."}]

The packet is plain text, one block per answer, with the rubric pulled from the lesson file (topics/<t>/lessons/<stem>.html,
the quiz's <div class="rubric">). Grading 0.7 or more counts as known for spaced review (progress-server/app.py).
"""
import html, json, re, subprocess, sys, pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://books.tail59e10.ts.net/progress"


def curl(path, data=None):
    cmd = ["curl", "-s", "-m", "20", "-w", "\n%{http_code}", BASE + path]
    if data is not None:
        cmd[1:1] = ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    if code != "200":
        sys.exit(f"progress server: HTTP {code or 'unreachable'} {body[:200]}")
    return json.loads(body)


class QuizText(HTMLParser):
    """Collects prompt and rubric text for one data-id."""
    def __init__(self, qid):
        super().__init__(); self.qid, self.depth, self.part, self.prompt, self.rubric = qid, 0, None, [], []
        self.part_depth = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.depth == 0:
            if "quiz" in (a.get("class") or "").split() and a.get("data-id") == self.qid:
                self.depth = 1
            return
        self.depth += 1
        cls = (a.get("class") or "").split()
        if self.part is None and ("rubric" in cls or "prompt" in cls or (tag == "p" and not self.prompt)):
            self.part, self.part_depth = ("rubric" if "rubric" in cls else "prompt"), self.depth

    def handle_endtag(self, tag):
        if self.depth == 0: return
        if self.part and self.depth == self.part_depth: self.part = None
        self.depth -= 1

    def handle_data(self, d):
        if self.depth and self.part == "prompt": self.prompt.append(d)
        elif self.depth and self.part == "rubric": self.rubric.append(d)


def lookup(item):
    page, _, qid = item.partition("#")
    topic, _, stem = page.partition("/")
    f = ROOT / "topics" / topic / "lessons" / f"{stem}.html"
    if not f.exists(): f = ROOT / "topics" / topic / "reference" / f"{stem}.html"
    if not f.exists(): return None, None, f"(lesson file for {page} not found)"
    q = QuizText(qid); q.feed(f.read_text(encoding="utf-8"))
    clean = lambda parts: re.sub(r"\s+", " ", "".join(parts)).strip()
    return clean(q.prompt), clean(q.rubric), str(f.relative_to(ROOT))


def packet(rows):
    if not rows:
        print("nothing to grade"); return
    for r in rows:
        prompt, rubric, where = lookup(r["item"])
        print(f"=== {r['eid']}  {r['item']}  ({(r.get('ts') or '')[:10]}, {where})")
        print(f"Q: {prompt}")
        print(f"RUBRIC: {rubric or '(none: grade from the lesson text)'}")
        print("A: " + (r.get("answer") or "").strip().replace("\n", "\n   "))
    print(f"\n{len(rows)} to grade. Post: python3 scripts/grade.py post grades.json  "
          '([{"event": "<eid>", "score": 0..1, "feedback": "..."}])')


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["post"]:
        grades = json.loads(pathlib.Path(a[1]).read_text())
        print(curl("/grades", {"grades": grades}))
    elif a[:1] == ["--from"]:
        packet(json.loads(pathlib.Path(a[1]).read_text()))
    else:
        packet(curl("/ungraded?limit=100"))
