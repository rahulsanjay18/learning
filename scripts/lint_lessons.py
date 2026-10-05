#!/usr/bin/env python3
"""Lint lessons and reference pages for the shared widget library.

    python3 scripts/lint_lessons.py [files...]     (default: every topics/*/lessons|reference/*.html + assets/gallery.html)

ERROR (exit 1): broken local links/scripts, choice answer not among its options, categorize item in an unknown bucket,
                duplicate data-id, cloze with no [[blanks]], order with < 2 items, chess-move/go-move missing their position or answer,
                plot-set without data-fns/data-target or targeting a parameter that has no slider.
WARN:           choice options with different word counts (SKILL.md: answers must not give away the answer by length),
                lesson without a sources list.
"""
import sys, re, pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.quizzes, self.links, self.has_sources = [], [], False
        self._stack = []  # open quiz elements, to collect their text (for cloze)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if "sources" in (a.get("class") or "").split():
            self.has_sources = True
        if "quiz" in (a.get("class") or "").split() and a.get("data-type"):
            q = {"attrs": a, "text": "", "line": self.getpos()[0], "depth": 0}
            self.quizzes.append(q)
            self._stack.append(q)
        elif self._stack:
            self._stack[-1]["depth"] += 1

    def handle_endtag(self, tag):
        if self._stack:
            if self._stack[-1]["depth"] == 0:
                self._stack.pop()
            else:
                self._stack[-1]["depth"] -= 1

    def handle_data(self, data):
        if self._stack:
            self._stack[-1]["text"] += data


def split(s):
    return [x.strip() for x in (s or "").split("|") if x.strip()]


def lint(path):
    errors, warns = [], []
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT)

    for link in page.links:
        if re.match(r"^(https?:|mailto:|#|data:|javascript:)", link):
            continue
        target = (path.parent / link.split("#")[0].split("?")[0]).resolve()
        if link.split("#")[0] and not target.exists():
            errors.append(f"broken link {link}")

    ids = {}
    for q in page.quizzes:
        a, where = q["attrs"], f"line {q['line']} ({q['attrs'].get('data-type')})"
        if a.get("data-id"):
            if a["data-id"] in ids:
                errors.append(f"{where}: duplicate data-id {a['data-id']!r}")
            ids[a["data-id"]] = 1
        t = a["data-type"]
        if t == "choice":
            opts = split(a.get("data-options"))
            if a.get("data-answer") not in opts:
                errors.append(f"{where}: answer {a.get('data-answer')!r} is not one of the options")
            counts = {len(o.split()) for o in opts}
            if len(counts) > 1:
                warns.append(f"{where}: options differ in word count: " + " | ".join(opts))
        elif t == "categorize":
            buckets = split(a.get("data-buckets"))
            for item in split(a.get("data-items")):
                b = item.split(">")[1].strip() if ">" in item else None
                if b not in buckets:
                    errors.append(f"{where}: item {item!r} has no valid bucket (buckets: {', '.join(buckets)})")
        elif t == "order" and len(split(a.get("data-items"))) < 2:
            errors.append(f"{where}: needs at least two data-items")
        elif t == "cloze" and not re.search(r"\[\[.+?\]\]", q["text"]):
            errors.append(f"{where}: no [[blanks]] found")
        elif t == "chess-move" and not (a.get("data-fen") and a.get("data-answer")):
            errors.append(f"{where}: needs data-fen and data-answer")
        elif t == "math" and not a.get("data-answer"):
            errors.append(f"{where}: needs data-answer")
        elif t == "plot-set":
            if not (a.get("data-fns") and a.get("data-target")):
                errors.append(f"{where}: needs data-fns and data-target")
            else:
                sliders = {p.split("=")[0].strip() for p in split(a.get("data-params"))}
                for tgt in split(a.get("data-target")):
                    if tgt.split("=")[0].strip() not in sliders:
                        errors.append(f"{where}: target {tgt!r} is not one of the data-params sliders")
        elif t == "go-move" and not (a.get("data-size") and (a.get("data-answer") or a.get("data-solution"))):
            errors.append(f"{where}: needs data-size and data-answer or data-solution")

    if "/lessons/" in str(rel) and not page.has_sources:
        warns.append("no <ol class=\"sources\"> list")
    return rel, errors, warns


def main(argv):
    files = [pathlib.Path(f).resolve() for f in argv] or sorted(
        list(ROOT.glob("topics/*/lessons/*.html")) + list(ROOT.glob("topics/*/reference/*.html")) + [ROOT / "assets/gallery.html"])
    n_err = 0
    for f in files:
        rel, errors, warns = lint(f)
        for e in errors:
            print(f"ERROR {rel}: {e}")
        for w in warns:
            print(f"WARN  {rel}: {w}")
        n_err += len(errors)
    print(f"{len(files)} files, {n_err} error(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
