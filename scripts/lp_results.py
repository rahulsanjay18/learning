#!/usr/bin/env python3
"""Record pasted results lines in the curriculum (for lessons done without sync).

    python3 scripts/lp_results.py "lp-results statistics/0004-power | 9/12 right first try | missed: a,b"   (several lines OK)

Marks each lesson as completed in its course (curriculum.json "completed"), prints a one-line summary per lesson, and runs
scripts/test_programs.py. Learning records stay a judgment call: write one when the results show something new.
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(text):
    progs = json.loads((ROOT / "programs.json").read_text())
    for m in re.finditer(r"lp-results\s+([\w-]+)/([\w-]+)\s*\|([^\n]*)", text):
        topic, stem, rest = m.group(1), m.group(2), m.group(3)
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
    main(" ".join(sys.argv[1:]) or sys.stdin.read())
