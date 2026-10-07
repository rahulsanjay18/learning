#!/usr/bin/env python3
"""Check programs.json and every curriculum.json for consistency. Exit 1 on errors; warnings don't fail.
Run after editing a curriculum (the /program skill asks for it)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"done", "active", "next", "later"}
COURSE_KEYS = {"id", "title", "status", "requires", "topic", "est_lessons", "lessons", "completed", "plan",
               "pretest", "source", "note", "level", "group", "credit", "books"}
BOOK_ROLES = {"primary", "secondary", "tertiary", "skip"}
MANIFEST_IDS = {l.split(",", 1)[0] for l in (ROOT / "library" / "MANIFEST.csv").read_text(encoding="utf-8").splitlines()[1:] if l}
GROUPS = {"core", "breadth", "elective", "practice", "independent", "capstone", "colloquium"}
errors, warnings = [], []


def err(m): errors.append(m)
def warn(m): warnings.append(m)


cfg = json.loads((ROOT / "programs.json").read_text())
slugs = {m["slug"] for m in cfg["majors"]}
for day, blocks in cfg["week"].items():
    for b in blocks:
        if b not in slugs:
            err(f"programs.json week.{day}: unknown major {b!r}")
parked = [p for p in cfg.get("parked", []) if p.get("curriculum")]  # designed but not scheduled
for m in cfg["majors"] + parked:
    if m not in parked and m.get("weight") not in ("full", "half"):
        err(f"{m['slug']}: weight must be full or half")
    if not m.get("curriculum"):
        if not m.get("setup"):
            err(f"{m['slug']}: no curriculum and no setup text")
        continue
    p = ROOT / m["curriculum"]
    if not p.exists():
        err(f"{m['curriculum']}: missing"); continue
    try:
        cur = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        err(f"{m['curriculum']}: bad JSON: {e}"); continue
    ids = [c["id"] for c in cur["courses"]]
    if len(ids) != len(set(ids)):
        err(f"{m['slug']}: duplicate course ids")
    by_id = {c["id"]: c for c in cur["courses"]}
    seen_stems = {}
    for c in cur["courses"]:
        where = f"{m['slug']}/{c['id']}"
        extra = set(c) - COURSE_KEYS
        if extra:
            err(f"{where}: unknown keys {sorted(extra)} (add them to COURSE_KEYS and the skill's Files list)")
        if c.get("group") is not None and c["group"] not in GROUPS:
            err(f"{where}: bad group {c['group']!r}")
        if c.get("level") is not None and c["level"] not in ("I", "II", "III"):
            err(f"{where}: bad level {c['level']!r}")
        if c.get("credit") not in (None, "exam", "lessons"):
            err(f"{where}: credit must be exam (tested out) or lessons")
        if c.get("level") == "II" and "II" not in m.get("enrolled_levels", ["I"]) and c["status"] in ("active", "done"):
            err(f"{where}: Level II course is {c['status']} but the learner hasn't enrolled in Level II (programs.json enrolled_levels)")
        if c["status"] not in STATUSES:
            err(f"{where}: bad status {c['status']!r}")
        for r in c.get("requires", []):
            if r not in by_id:
                err(f"{where}: requires unknown course {r}")
            elif c.get("group", "core") == "core" and by_id[r].get("group", "core") != "core":
                err(f"{where}: a core course may only require core courses ({r} is optional: {by_id[r].get('group')})")
            elif c["status"] in ("active", "done") and by_id[r]["status"] != "done":
                warn(f"{where} is {c['status']} but prerequisite {r} is {by_id[r]['status']}")
        topic = c.get("topic", m["slug"])
        lesson_dir = ROOT / "topics" / topic / "lessons"
        for s in c.get("lessons", []):
            if not (lesson_dir / f"{s}.html").exists():
                err(f"{where}: lesson file topics/{topic}/lessons/{s}.html missing")
            if (topic, s) in seen_stems:
                err(f"{where}: lesson {s} also listed in {seen_stems[(topic, s)]}")
            seen_stems[(topic, s)] = c["id"]
        for s in c.get("completed", []):
            if s not in c.get("lessons", []):
                err(f"{where}: completed {s} is not in lessons")
        b = c.get("books")
        if b is not None:
            if not isinstance(b, dict) or set(b) - BOOK_ROLES or not isinstance(b.get("primary", ""), str):
                err(f"{where}: books must be {{primary: str, secondary/tertiary/skip: [str]}}")
            else:
                for role in ("secondary", "tertiary", "skip"):
                    if not isinstance(b.get(role, []), list):
                        err(f"{where}: books.{role} must be a list")
                for ref in [b.get("primary", "")] + b.get("secondary", []) + b.get("tertiary", []) + b.get("skip", []):
                    bid = ref.split()[0].rstrip(":") if ref else ""
                    if len(bid) == 10 and all(ch in "0123456789abcdef" for ch in bid) and bid not in MANIFEST_IDS:
                        err(f"{where}: book id {bid} not in library/MANIFEST.csv")
        if c["status"] == "active" and c.get("group", "core") == "core" and not (b or {}).get("primary"):
            err(f"{where}: active core course needs books.primary (a major is a DAG of books: notes/major-design.md)")
        if c["status"] == "active" and not c.get("plan") and not c.get("est_lessons"):
            warn(f"{where}: active with no plan and no estimate")
    # prerequisites must form a DAG (no cycles)
    state = {}
    def visit(cid, path):
        if state.get(cid) == 1:
            err(f"{m['slug']}: prerequisite cycle {' -> '.join(path + [cid])}")
            return
        if state.get(cid) == 2 or cid not in by_id:
            return
        state[cid] = 1
        for r in by_id[cid].get("requires", []):
            visit(r, path + [cid])
        state[cid] = 2
    for cid in by_id:
        visit(cid, [])
    actives = [c for c in cur["courses"] if c["status"] == "active"]
    if not actives and m not in parked:
        warn(f"{m['slug']}: no active course")
    # every lesson file in a topic used by this major should belong to a course
    for topic in {c.get("topic", m["slug"]) for c in cur["courses"]}:
        d = ROOT / "topics" / topic / "lessons"
        for f in sorted(d.glob("[0-9][0-9][0-9][0-9]-*.html")) if d.is_dir() else []:
            if (topic, f.stem) not in seen_stems:
                err(f"{m['slug']}: topics/{topic}/lessons/{f.name} is not in any course's lessons")

for w in warnings:
    print("WARN", w)
for e in errors:
    print("ERROR", e)
print(f"programs: {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
