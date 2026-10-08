#!/usr/bin/env python3
"""Check a lesson's question families (lesson .md + its .variants.md bank). Writes nothing that stays.

    python3 .claude/skills/write-questions/check_questions.py topics/<t>/lessons/NNNN-name.md

Renders the lesson and its bank (NNNN-name.variants.md, if present) to throwaway copies in the same folder, runs
scripts/lint_lessons.py on them, deletes the copies, then checks the families across both files (notes/practice-variants.md):
ERROR  a data-id used twice across lesson + bank; a bank item whose id isn't <family>-v<n>; a bank for a pretest page (rule 28).
WARN   a lesson quiz id that isn't a family id; a family with < 3 members; a family with no recall-type member (rule 8);
       a family name already used by another lesson in the same topic.
Also checks that every math answer parses (assets/plugins/math.js, needs node). Lint warnings about sources / Extra practice
are dropped for the bank (no one reads it as a page) and for lessons that predate rule 32.
"""
import json, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import lint_lessons, render_lesson  # noqa: E402

RECOGNITION = {"choice", "categorize", "order", "find-error", "highlight"}
FAMILY = re.compile(r"^(.+)-v(\d+)$")


def lint_copy(md):
    """Render a temporary copy of md next to it, lint it, delete it. Returns (errors, warns, quizzes)."""
    tmp_md = md.with_name(f"_qcheck-{md.stem}.md")
    text = md.read_text(encoding="utf-8")
    if not text.startswith("---"):  # a bank needs no front matter of its own
        text = f"---\ntitle: {md.stem} (check)\n---\n" + text
    tmp_md.write_text(text, encoding="utf-8")
    try:
        out, *_ = render_lesson.render(str(tmp_md))
        try:
            _, errors, warns = lint_lessons.lint(out)
            page = lint_lessons.Page()
            page.feed(out.read_text(encoding="utf-8"))
            return errors, warns, page.quizzes
        finally:
            out.unlink(missing_ok=True)
    finally:
        tmp_md.unlink(missing_ok=True)


def main(lesson):
    lesson = pathlib.Path(lesson).resolve()
    bank = lesson.with_name(lesson.name.replace(".md", ".variants.md"))
    errors, warns, items, maths = [], [], [], []  # items: (id, type, file label)
    for md, label in ((lesson, "lesson"), (bank, "bank")):
        if not md.exists():
            continue
        e, w, quizzes = lint_copy(md)
        errors += [f"{label}: {x}" for x in e]
        old = str(md.with_suffix(".html").relative_to(ROOT)) in lint_lessons.GRANDFATHERED
        if label == "bank" or old:
            w = [x for x in w if "Extra practice" not in x and (label != "bank" or "sources" not in x)]
        warns += [f"{label}: {x}" for x in w]
        items += [(q["attrs"].get("data-id", ""), q["attrs"]["data-type"], label) for q in quizzes]
        maths += [(q["attrs"].get("data-id", ""), q["attrs"].get("data-answer", "")) for q in quizzes
                  if q["attrs"]["data-type"] == "math"]
    if maths and shutil.which("node"):
        js = ("const M=require(process.argv[1]);for(const [i,a] of JSON.parse(process.argv[2]))"
              "{try{M.parse(a)}catch(e){console.log(i+': math answer '+JSON.stringify(a)+' does not parse')}}")
        r = subprocess.run(["node", "-e", js, str(ROOT / "assets/plugins/math.js"), json.dumps(maths)],
                           capture_output=True, text=True)
        errors += [x for x in r.stdout.splitlines() if x] + ([r.stderr.strip()] if r.returncode else [])
    if bank.exists() and re.search(r"^main:.*data-pretest=true", lesson.read_text(), re.M):
        errors.append("bank: pretest pages never feed review, so they get no variants bank (rule 28)")

    seen, families = {}, {}
    for qid, typ, label in items:
        if not qid:
            continue
        if qid in seen:
            errors.append(f"data-id {qid!r} used in {seen[qid]} and {label}")
        seen[qid] = label
        m = FAMILY.match(qid)
        if m:
            families.setdefault(m.group(1), []).append((qid, typ, label))
        elif label == "bank":
            errors.append(f"bank: {qid!r} is not a family id (<family>-v<n>)")
        elif not qid.startswith("read-"):  # reading-guide notes are not practice
            warns.append(f"lesson: {qid!r} is not a family id (fine for reading notes and old lessons)")

    others = [p for p in lesson.parent.glob("*.html") if not p.name.startswith(lesson.stem)]
    for fam, members in sorted(families.items()):
        kinds = ", ".join(f"{q} ({t}, {lab})" for q, t, lab in members)
        print(f"family {fam}: {kinds}")
        if len(members) < 3:
            warns.append(f"family {fam!r}: {len(members)} member(s); aim for 3-5")
        if all(t in RECOGNITION for _, t, _ in members):
            warns.append(f"family {fam!r}: every member is recognition ({'/'.join(sorted(RECOGNITION))}); add a recall one")
        pat = re.compile(rf'data-id="{re.escape(fam)}-v\d+"')
        clash = [p.name for p in others if pat.search(p.read_text(encoding="utf-8"))]
        if clash:
            warns.append(f"family {fam!r} also used in {', '.join(clash)}; pick a new name")

    for x in errors:
        print("ERROR", x)
    for x in warns:
        print("WARN ", x)
    print(f"{len(families)} families, {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".md") or sys.argv[1].endswith(".variants.md"):
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
