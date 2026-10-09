#!/usr/bin/env python3
"""Quiz in chat (the /quiz-me skill): due review questions as plain text, answers recorded on the progress server.

    python3 scripts/quiz.py due [-n 5] [--topic statistics]      due questions that work as text, with answer keys
    python3 scripts/quiz.py pick --topic statistics [-n 5]       random text-friendly questions from a topic's lessons
    python3 scripts/quiz.py record ITEM right|wrong ["answer"]   log one attempt (feeds the spaced-review schedule)

Questions are read from their lesson pages (topics/<t>/lessons/<stem>.html), so they match what the learner saw.
Visual types (boards, maps, plots, code) are skipped: those stay in the review deck (assets/review.html).
The ANSWER/KEY lines are for Claude: never show them before the learner answers.
"""
import html, json, random, re, subprocess, sys, time, pathlib, datetime
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = __import__("os").environ.get("PROGRESS_URL", "https://books.tail59e10.ts.net/progress")   # override for tests
TEXT_TYPES = {"choice", "number", "exact", "cloze", "order", "categorize", "recall", "card", "math", "estimate",
              "find-error", "highlight", "free", "timeline-place"}


def curl(path, data=None):
    cmd = ["curl", "-s", "-m", "20", "-w", "\n%{http_code}", BASE + path]
    tok = __import__("os").environ.get("PROGRESS_TOKEN")      # tests only; cloud sessions get auth from the proxy
    if tok: cmd[1:1] = ["-H", f"Authorization: Bearer {tok}", "--noproxy", "*"]
    if data is not None:
        cmd[1:1] = ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body, _, code = r.stdout.rpartition("\n")
    if code != "200":
        sys.exit(f"progress server: HTTP {code or 'unreachable'} {body[:200]}")
    return json.loads(body)


class Quizzes(HTMLParser):
    """Every .quiz on a page: attrs + text of prompt / explain / rubric / steps / passage."""
    def __init__(self):
        super().__init__(); self.quizzes, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = (a.get("class") or "").split()
        if "quiz" in cls and a.get("data-type") and not self.stack:
            q = {"attrs": a, "prompt": "", "explain": "", "rubric": "", "steps": [], "passage": ""}
            self.quizzes.append(q); self.stack = [("quiz", None)]
            return
        if not self.stack: return
        part = None
        for c in ("prompt", "explain", "rubric", "passage"):
            if c in cls: part = c
        if tag == "li" and any(p == "steps" for p, _ in self.stack): part = "step"
        if tag == "ol" and "steps" in cls: part = "steps"
        if tag == "p" and not self.quizzes[-1]["prompt"] and not any(p in ("explain", "rubric", "passage") for p, _ in self.stack): part = part or "prompt"
        if tag in ("br", "img", "input", "hr"): return
        self.stack.append((part, tag))
        if part == "step": self.quizzes[-1]["steps"].append("")

    def handle_endtag(self, tag):
        if self.stack and len(self.stack) > 1: self.stack.pop()
        elif self.stack and tag == "div": self.stack = []

    def handle_data(self, d):
        if not self.stack: return
        q = self.quizzes[-1]
        for part, _ in reversed(self.stack):
            if part == "step": q["steps"][-1] += d; return
            if part in ("prompt", "explain", "rubric", "passage"): q[part] += d; return


def clean(s): return re.sub(r"\s+", " ", s).strip()


def page_quizzes(page):
    topic, _, stem = page.partition("/")
    for kind in ("lessons", "reference"):
        f = ROOT / "topics" / topic / kind / f"{stem}.html"
        if f.exists():
            text = f.read_text(encoding="utf-8")
            if 'data-pretest="true"' in text:
                return []        # pretests measure what hasn't been taught; they never come back in review
            p = Quizzes(); p.feed(text); return p.quizzes
    return []


def card(item, q):
    a, t = q["attrs"], q["attrs"]["data-type"]
    split = lambda s: [x.strip() for x in (s or "").split("|") if x.strip()]
    prompt = clean(q["prompt"]) or "(no prompt text)"
    lines, key = [f"[{item}] ({t})", "Q: " + re.sub(r"\[\[(.+?)\]\]", "____", prompt)], []
    if t == "choice":
        opts = split(a.get("data-options")); random.shuffle(opts)
        lines.append("Options: " + " / ".join(f"({chr(97 + i)}) {o}" for i, o in enumerate(opts)))
        key.append(a.get("data-answer"))
    elif t in ("number", "exact", "math", "estimate", "timeline-place"):
        tol = a.get("data-tolerance")
        key.append(a.get("data-answer", "") + (f" (± {tol})" if tol else "") + (f" {a['data-unit']}" if a.get("data-unit") else ""))
        if t == "estimate": lines.append(f"(Ask for a range they're {a.get('data-level', '90')}% sure of; right if it contains the answer.)")
        if t == "timeline-place": lines.append("(Ask for the year.)")
    elif t == "cloze":
        key.append("; ".join(re.findall(r"\[\[(.+?)\]\]", q["prompt"])))
    elif t == "order":
        items = split(a.get("data-items")); sh = items[:]; random.shuffle(sh)
        lines.append("Put in order: " + " / ".join(sh)); key.append(" → ".join(items))
    elif t == "categorize":
        pairs = [x.split(">") for x in split(a.get("data-items"))]
        lines.append("Buckets: " + " / ".join(split(a.get("data-buckets"))) + ". Items: " + " / ".join(p[0] for p in pairs))
        key.append("; ".join(f"{p[0]} → {p[1]}" for p in pairs if len(p) == 2))
    elif t == "find-error":
        steps = [clean(s) for s in q["steps"]] or split(a.get("data-steps"))
        lines += [f"  {i + 1}. {s}" for i, s in enumerate(steps)]; key.append(f"step {a.get('data-answer')}")
    elif t == "highlight":
        lines.append("Passage: " + clean(re.sub(r"\[\[(.+?)\]\]", r"\1", q["passage"])))
        key.append(" | ".join(re.findall(r"\[\[(.+?)\]\]", q["passage"])))
    if t in ("recall", "card", "free") or not key or not key[0]:
        key.append(clean(q["rubric"]) or clean(q["explain"]) or "(no model answer: judge from the lesson)")
    lines.append("KEY: " + " ; ".join(k for k in key if k))
    if clean(q["explain"]) and t not in ("recall", "card"): lines.append("WHY: " + clean(q["explain"])[:400])
    return "\n".join(lines)


def find(item):
    page, _, qid = item.partition("#")
    for q in page_quizzes(page):
        if q["attrs"].get("data-id") == qid: return q
    return None


def show(items, n):
    shown = 0
    for it in items:
        q = find(it)
        if not q or q["attrs"]["data-type"] not in TEXT_TYPES: continue
        print(card(it, q) + "\n"); shown += 1
        if shown >= n: break
    return shown


if __name__ == "__main__":
    a = sys.argv[1:]
    n = int(a[a.index("-n") + 1]) if "-n" in a else 5
    topic = a[a.index("--topic") + 1] if "--topic" in a else ""
    cmd = a[0] if a else "due"
    if cmd == "due":
        rows = curl("/due?limit=200" + (f"&topic={topic}" if topic else ""))
        rows = [r for r in rows if "#read-" not in r["item"]]   # reading-guide notes are never re-asked
        k = show([r["item"] for r in rows], n)
        skipped = len(rows) - k
        print(f"{k} shown; {len(rows)} due in total" + (f" ({skipped} are visual or not shown: use the review deck)" if skipped > 0 else "") +
              ("" if rows else ". Nothing due: try `pick --topic <t>` for early practice."))
    elif cmd == "pick":
        if not topic: sys.exit("pick needs --topic")
        pool = []
        for f in sorted((ROOT / "topics" / topic / "lessons").glob("*.html")):
            for q in page_quizzes(f"{topic}/{f.stem}"):
                if q["attrs"]["data-type"] in TEXT_TYPES and q["attrs"].get("data-id"):
                    pool.append(f"{topic}/{f.stem}#{q['attrs']['data-id']}")
        random.shuffle(pool)
        print(f"{show(pool, n)} picked from {len(pool)} text-friendly questions in {topic}")
    elif cmd == "record":
        item, verdict, answer = a[1], a[2], (a[3] if len(a) > 3 else None)
        if verdict not in ("right", "wrong"): sys.exit("record ITEM right|wrong [answer]")
        ev = {"v": 1, "eid": f"chat-{int(time.time() * 1000):x}-{random.randrange(16 ** 6):06x}", "type": "attempt",
              "page": item.split("#")[0], "item": item, "widget": "chat", "kind": "chat", "correct": verdict == "right",
              "answer": answer, "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        print(curl("/events", {"events": [ev]}))
    else:
        sys.exit(__doc__)
