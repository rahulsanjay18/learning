#!/usr/bin/env python3
"""Check programs.json and every curriculum.json for consistency. Exit 1 on errors; warnings don't fail.
Run after editing a curriculum (the /program skill asks for it)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"done", "active", "next", "later"}
COURSE_KEYS = {"id", "title", "status", "requires", "topic", "est_lessons", "lessons", "completed", "plan",
               "pretest", "source", "note"}
errors, warnings = [], []


def err(m): errors.append(m)
def warn(m): warnings.append(m)


cfg = json.loads((ROOT / "programs.json").read_text())
slugs = {m["slug"] for m in cfg["majors"]}
for day, blocks in cfg["week"].items():
    for b in blocks:
        if b not in slugs:
            err(f"programs.json week.{day}: unknown major {b!r}")
for m in cfg["majors"]:
    if m.get("weight") not in ("full", "half"):
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
        if c["status"] not in STATUSES:
            err(f"{where}: bad status {c['status']!r}")
        for r in c.get("requires", []):
            if r not in by_id:
                err(f"{where}: requires unknown course {r}")
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
        if c["status"] == "active" and not c.get("plan") and not c.get("est_lessons"):
            warn(f"{where}: active with no plan and no estimate")
    actives = [c for c in cur["courses"] if c["status"] == "active"]
    if not actives:
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
