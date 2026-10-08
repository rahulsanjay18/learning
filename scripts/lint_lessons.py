#!/usr/bin/env python3
"""Lint lessons and reference pages for the shared widget library.

    python3 scripts/lint_lessons.py [files...]     (default: every topics/*/lessons|reference/*.html + assets/gallery.html)

ERROR (exit 1): broken local links/scripts, choice answer not among its options, categorize item in an unknown bucket,
                duplicate data-id, cloze with no [[blanks]], order with < 2 items, chess-move/go-move missing their position or answer,
                plot-set without data-fns/data-target or targeting a parameter that has no slider,
                timeline-place without data-range/data-answer, map-locate without data-answer/data-view,
                py quiz without a <pre class="code"> (starter code) and a <script class="check"> (the hidden test),
                lp-py snippet without a <pre class="code">.
WARN:           choice options with different word counts (SKILL.md: answers must not give away the answer by length),
                a justification word (because/since/so that/which means) only in the answer (teach/PRINCIPLES.md),
                lesson without a sources list,
                lesson without an "Extra practice" heading (TEACHING-LOG rule 32; lessons listed in
                scripts/fixtures/pre-extra-practice.txt predate the rule and are exempt).
"""
import sys, re, pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
_gf = ROOT / "scripts" / "fixtures" / "pre-extra-practice.txt"
GRANDFATHERED = set(_gf.read_text().split()) if _gf.exists() else set()


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.quizzes, self.links, self.has_sources = [], [], False
        self._stack = []  # open quiz elements, to collect their text (for cloze)
        self.py_snippets = []  # .lp-py blocks: {"line", "pre"}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if "lp-py" in classes:
            self.py_snippets.append({"line": self.getpos()[0], "pre": False})
        elif tag == "pre" and "code" in classes and self.py_snippets and not self._stack:
            self.py_snippets[-1]["pre"] = True
        if self._stack:
            self._stack[-1]["children"].update(f"{tag}.{c}" for c in classes)
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if "sources" in (a.get("class") or "").split():
            self.has_sources = True
        if "quiz" in (a.get("class") or "").split() and a.get("data-type"):
            q = {"attrs": a, "text": "", "line": self.getpos()[0], "depth": 0, "children": set()}
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
            why = re.compile(r"\b(because|since|so that|which means|due to)\b", re.I)
            if why.search(a.get("data-answer") or "") and not any(why.search(o) for o in opts if o != a.get("data-answer")):
                warns.append(f"{where}: only the answer gives a reason (move it to the explanation)")
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
        elif t == "timeline-place" and not (a.get("data-range") and a.get("data-answer")):
            errors.append(f"{where}: needs data-range and data-answer")
        elif t == "estimate" and not re.fullmatch(r"-?[\d.]+", (a.get("data-answer") or "").strip()):
            errors.append(f"{where}: estimate needs a numeric data-answer")
        elif t == "find-error" and not ("ol.steps" in q["children"] or a.get("data-steps")) or (t == "find-error" and not (a.get("data-answer") or "").isdigit()):
            errors.append(f"{where}: find-error needs <ol class=\"steps\"> (or data-steps) and a step number in data-answer")
        elif t == "highlight" and ("div.passage" not in q["children"] or "[[" not in q["text"]):
            errors.append(f"{where}: highlight needs <div class=\"passage\"> with [[marked]] evidence")
        elif t == "map-locate" and not (a.get("data-answer") and a.get("data-view")):
            errors.append(f"{where}: needs data-answer (lat,lon) and data-view")
        elif t == "py":
            if "pre.code" not in q["children"]:
                errors.append(f'{where}: needs a <pre class="code"> with the starter code')
            if "script.check" not in q["children"]:
                errors.append(f'{where}: needs a <script type="text/python" class="check"> with the test')
    for sn in page.py_snippets:
        if not sn["pre"]:
            errors.append(f'line {sn["line"]} (lp-py): needs a <pre class="code"> with the code')

    html = path.read_text(encoding="utf-8")
    body = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    if re.search(r"\\\(|\$\$|\\\[", body) and "plugins/math.js" not in html:
        errors.append("uses \\( \\) or $$ math but doesn't load plugins/math.js (it would show raw TeX)")
    if "/lessons/" in str(rel) and not page.has_sources:
        warns.append("no <ol class=\"sources\"> list")
    if "/lessons/" in str(rel) and str(rel) not in GRANDFATHERED and not re.search(r"<h2[^>]*>\s*Extra practice", body, re.I):
        warns.append("no 'Extra practice' section (optional problems from the course's books + one extra article; rule 32)")
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
