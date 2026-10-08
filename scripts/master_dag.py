#!/usr/bin/env python3
"""One graph over every major: all curriculum.json files (scheduled and parked) + cross-links.json.

    python3 scripts/master_dag.py           write notes/MASTER-DAG.md and notes/TIME-ESTIMATES.md
    python3 scripts/master_dag.py --check   exit 1 if either file is stale (run by check_all.sh)

Commonality comes from two places: (1) a course id used in several majors is ONE course (the majors built by
scripts/build_majors.py share ids on purpose); (2) cross-links.json links courses whose ids differ (same / overlap / feeds).

Time estimates simulate the remaining Level I core of each major week by week, two ways (details in the generated page):
  A. platform pace: the lesson estimates as written, at 7, 18 or 36 hours a week;
  B. college workload: 135 hours per semester-sized course (federal credit hour: 45 hours per credit), at 18 or 36 h/week.
  No course starts before its prerequisites finish, and no course gets more than 9 h/week (a 3-credit course's pace).
Generated files: never edit them by hand. Standard library only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSON_MIN = 50          # one lesson = two 25-minute blocks
COURSE_HOURS = 135       # 3 credits x 45 hours (1 h class + 2 h outside, weekly, 15 weeks)
PACES = [("your floor (1 h/day)", 7), ("part-time (6 credits)", 18), ("full-time (12 credits)", 36)]


def load():
    cfg = json.loads((ROOT / "programs.json").read_text(encoding="utf-8"))
    majors = [m for m in cfg["majors"] + cfg.get("parked", []) if m.get("curriculum")]
    cur = {m["slug"]: json.loads((ROOT / m["curriculum"]).read_text(encoding="utf-8")) for m in majors}
    names = {m["slug"]: m.get("name", m["slug"]) for m in majors}
    links = json.loads((ROOT / "cross-links.json").read_text(encoding="utf-8"))["links"]
    courses, owners = {}, {}
    for slug, c in cur.items():
        for x in c["courses"]:
            if x["id"] in courses and courses[x["id"]]["title"] != x["title"]:
                raise SystemExit(f"course id {x['id']} means two different courses ({slug} vs {owners[x['id']][0]})")
            courses.setdefault(x["id"], x)
            owners.setdefault(x["id"], []).append(slug)
    for l in links:
        for end in (l["a"], l["b"]):
            slug, cid = end.split("/")
            if slug not in cur or cid not in {x["id"] for x in cur[slug]["courses"]}:
                raise SystemExit(f"cross-links.json: {end} does not exist")
    return cur, names, courses, owners, links


def remaining(c, with_maybe):
    """Level I core courses still to do in one curriculum, and the set treated as already done."""
    ep = c.get("entry_points", {})
    done = {x["id"] for x in c["courses"] if x["status"] == "done"} | set(ep.get("credited", []))
    if not with_maybe:
        done |= set(ep.get("maybe", []))
    todo = [x for x in c["courses"] if x.get("group", "core") == "core" and x.get("level", "I") == "I" and x["id"] not in done]
    return todo, done


# Minutes per counted lesson, by major (render_syllabi.py RATE notes and each PROGRAM.md): Statistics and Indian History
# lessons are two 25-minute blocks; Games, Engineering-career and Critical Theory count single 25-minute blocks/sittings.
LESSON_MINUTES = {"games": 25, "eng": 25, "critical-theory": 25}
STD_COURSE_H = 20 * 50 / 60   # the platform's standard semester-sized course (20 lessons x 50 min) stands for one 3-credit course
COURSE_CAP = 9                # a 3-credit course is 135 h over 15 weeks = 9 h/week; no course goes faster than that
NEW_MAJORS = {"math", "physics", "mech-eng", "unified-eng", "music", "english"}   # courses designed as one semester each


def hours(slug, x):
    return x.get("est_lessons", 6) * LESSON_MINUTES.get(slug, LESSON_MIN) / 60


def college_hours(slug, x):
    """B: semester-sized courses (the majors built by build_majors.py) are 135 h each; other majors' courses are chapter-
    or unit-sized blocks, so they count as their share of a standard course (platform hours / standard course hours)."""
    return COURSE_HOURS if slug in NEW_MAJORS else COURSE_HOURS * hours(slug, x) / STD_COURSE_H


def simulate(todo, edges, budget):
    """Weeks to finish `todo` = [(id, hours, requires)] spending `budget` h/week, at most COURSE_CAP h/week on any one
    course, never starting a course before its prerequisites are finished. Longest remaining chain first."""
    ids = {i for i, _, _ in todo}
    left = {i: h for i, h, _ in todo}
    req = {i: {r for r in rq if r in ids} for i, _, rq in todo}
    for a, b in edges:
        if a in ids and b in ids:
            req[b].add(a)
    users = {i: [j for j in ids if i in req[j]] for i in ids}
    memo = {}
    def chain(i):
        if i not in memo:
            memo[i] = left[i] + max((chain(j) for j in users[i]), default=0)
        return memo[i]
    weeks, done = 0, set()
    while len(done) < len(ids):
        ready = sorted((i for i in ids if i not in done and req[i] <= done), key=lambda i: (-chain(i), i))
        if not ready:
            raise SystemExit("prerequisite cycle")
        b = budget
        for i in ready:
            spend = min(COURSE_CAP, left[i], b)
            left[i] -= spend
            b -= spend
            if b <= 0:
                break
        done |= {i for i in ready if left[i] <= 1e-9}
        weeks += 1
    return weeks


def time_page(cur, names, links):
    feeds = [(l["a"].split("/")[1], l["b"].split("/")[1]) for l in links if l["kind"] == "feeds"]
    same = {l["b"].split("/")[1]: l["a"].split("/")[1] for l in links if l["kind"] == "same"}
    head = ("| {0} | courses left | A: lesson hours | A: years at 7 / 18 / 36 h/wk | B: college hours | "
            "B: school years part-time (18 h/wk) / full-time (36 h/wk) |")
    out = ["# Time estimates for every major", "",
           "Generated by `scripts/master_dag.py`; don't edit by hand. Counts only the **Level I core** still to do from your entry point",
           "(credited and finished courses removed), with and without the \"maybe\" courses.", "",
           "**A. Platform pace:** the lesson estimates as written (50-minute lessons; 25-minute sittings for Games, Engineering",
           "career and Critical Theory), in calendar years of year-round study at 7 h/week (your current floor of 1 hour a day, which",
           "is shared by every subject), 18 h/week (a part-time student) and 36 h/week (a full-time student). The student loads",
           "come from the federal credit hour: 3 hours of work a week per credit; half-time is 6 credits, full-time 12 [1][2].", "",
           "**B. College workload:** each course costs what a real course costs: 135 hours for a semester-sized course (3 credits x",
           "45 hours), or its share of that for the older majors whose courses are chapter-sized blocks. Shown in school years of",
           "two 15-week terms (30 weeks), at part-time and full-time loads.", "",
           "Both are simulated week by week: no course before its prerequisites, and no more than 9 hours a week on any one course",
           "(a 3-credit course's pace), so a long prerequisite chain sets a floor however many hours you have.", "",
           "**Why A and B differ about 8x:** a standard platform course is ~17 hours (20 lessons); a 3-credit course is 135. The",
           "lessons cover the guided reading and the lesson itself; college adds problem sets, labs, papers and exams. For a",
           "problem-heavy subject, real mastery probably lands between the two, closer to B (my judgment).", "",
           head.format("Major"), "|---|---|---|---|---|---|"]
    def row(label, todo):
        n = len(todo)
        if not n:
            return f"| {label} | 0 | 0 | — | 0 | — |"
        ha = [(cid, hours(slug, x), x.get("requires", [])) for slug, cid, x in todo]
        hb = [(cid, college_hours(slug, x), x.get("requires", [])) for slug, cid, x in todo]
        a = " / ".join(f"{simulate(ha, feeds, h) / 52:.1f}" for _, h in PACES)
        b = " / ".join(f"{simulate(hb, feeds, h) / 30:.1f}" for h in (18, 36))
        return f"| {label} | {n} | {sum(h for _, h, _ in ha):.0f} | {a} | {sum(h for _, h, _ in hb):.0f} | {b} |"
    union = {True: {}, False: {}}
    for slug, c in cur.items():
        for wm in (True, False):
            todo, _ = remaining(c, wm)
            if wm or len(todo) != len(remaining(c, True)[0]):
                out.append(row(f"{names[slug]}{'' if wm else ' (no maybe)'}", [(slug, x["id"], x) for x in todo]))
            for x in todo:
                union[wm].setdefault(same.get(x["id"], x["id"]), (slug, x["id"], x))
    out += ["", "**Everything at once** (every major's Level I core in one graph; shared and \"same\" courses counted once):", "",
            head.format("Scope"), "|---|---|---|---|---|---|",
            row("All majors", list(union[True].values())), row("All majors (no maybe)", list(union[False].values())),
            "", "For scale: a US bachelor's degree is about 120 credits (40 three-credit courses, 5,400 hours of work by the credit-hour",
            "rule), four school years full-time.", "",
            "## Sources", "1. 34 CFR 600.2, credit hour: one hour of class and at least two hours of outside work weekly for about 15 weeks per",
            "   semester hour. ED guidance letter GEN-11-06: https://fsapartners.ed.gov/knowledge-center/library/dear-colleague-letters/2011-03-18/gen-11-06-subject-guidance-institutions-and-accrediting-agencies-regarding-credit-hour-defined-final-regulations-published-october-29-2010",
            "2. Full-time = at least 12 credits a term, half-time = 6 (34 CFR 668.2; schools may set higher bars). Example: Kent State,",
            "   https://catalog.kent.edu/academic-policies/enrollment-definitions/", ""]
    return "\n".join(out)


def nid(s):
    return s.replace("-", "_")


def dag_page(cur, names, courses, owners, links):
    shared = {cid: o for cid, o in owners.items() if len(o) > 1}
    pair = {}
    for cid, o in shared.items():
        for i, a in enumerate(o):
            for b in o[i + 1:]:
                pair.setdefault(tuple(sorted((a, b))), [0, 0])[0] += 1
    for l in links:
        a, b = l["a"].split("/")[0], l["b"].split("/")[0]
        pair.setdefault(tuple(sorted((a, b))), [0, 0])[1] += 1
    n_entries = sum(len(c["courses"]) for c in cur.values())
    out = ["# The master graph: every major, one graph", "",
           "Generated by `scripts/master_dag.py` from every `curriculum.json` and `cross-links.json`; don't edit by hand.", "",
           f"- **{len(cur)} majors, {n_entries} course entries, {len(courses)} distinct courses.** {len(shared)} courses are shared by id",
           f"  (the same course listed in several majors), and `cross-links.json` adds {len(links)} links between courses whose ids differ:",
           "  **same** (finishing either counts as both), **overlap** (shared material: the second goes faster), **feeds** (a real",
           "  prerequisite across majors).",
           "- Each major's own course-by-course graph is its `topics/<major>/DAG.md`. This page shows how the majors connect.", "",
           "## How the majors connect", "", "Edge label: shared courses + links.", "", "```mermaid", "flowchart LR"]
    for slug in cur:
        out.append(f'  {nid(slug)}["{names[slug]}<br/><small>{len(cur[slug]["courses"])} courses</small>"]')
    for (a, b), (s, l) in sorted(pair.items()):
        lab = " + ".join(x for x in (f"{s} shared" if s else "", f"{l} linked" if l else "") if x)
        out.append(f"  {nid(a)} ---|{lab}| {nid(b)}")
    out += ["```", "", "## The bridge courses", "",
            "Only the courses that tie majors together. Courses shared by id sit in the box of the first major that lists them, with",
            "the other majors named; solid arrows are prerequisites inside a major, dotted lines are cross-links.", "",
            "```mermaid", "flowchart TB"]
    bridge = set(shared)
    for l in links:
        bridge |= {l["a"].split("/")[1], l["b"].split("/")[1]}
    for slug in cur:
        mine = [cid for cid in sorted(bridge) if owners[cid][0] == slug]
        if not mine:
            continue
        out.append(f'  subgraph M_{nid(slug)}["{names[slug]}"]')
        for cid in mine:
            also = [names[o] for o in owners[cid][1:]]
            extra = f"<br/><small>also: {', '.join(also)}</small>" if also else ""
            out.append(f'    {cid}["{cid} {courses[cid]["title"][:36]}{extra}"]')
        out.append("  end")
    for cid in sorted(bridge):
        for r in courses[cid].get("requires", []):
            if r in bridge:
                out.append(f"  {r} --> {cid}")
    style = {"same": "-. same .-", "overlap": "-. overlap .-", "feeds": "-. feeds .->"}
    for l in links:
        out.append(f"  {l['a'].split('/')[1]} {style[l['kind']]} {l['b'].split('/')[1]}")
    out += ["```", "", "## Shared courses (one course, several majors)", "", "| Course | Title | Majors |", "|---|---|---|"]
    for cid in sorted(shared):
        out.append(f"| {cid} | {courses[cid]['title']} | {', '.join(names[o] for o in shared[cid])} |")
    out += ["", "## Cross-links (different ids)", "", "| A | B | Kind | Why |", "|---|---|---|---|"]
    for l in links:
        a, b = l["a"].split("/")[1], l["b"].split("/")[1]
        out.append(f"| {a} {courses[a]['title'][:40]} | {b} {courses[b]['title'][:40]} | {l['kind']} | {l['why']} |")
    unconnected = [names[s] for s in cur if not any(s in p for p in pair)]
    out += ["", "## Not yet connected", "",
            ("Majors with no shared course or link yet: " + ", ".join(unconnected) + ".") if unconnected else "Every major has at least one connection.",
            "Add links in `cross-links.json` when two courses share real material; the tests check that both ends exist.", ""]
    return "\n".join(out)


def main():
    cur, names, courses, owners, links = load()
    pages = {ROOT / "notes" / "MASTER-DAG.md": dag_page(cur, names, courses, owners, links),
             ROOT / "notes" / "TIME-ESTIMATES.md": time_page(cur, names, links)}
    if "--check" in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, t in pages.items() if not p.exists() or p.read_text(encoding="utf-8") != t]
        if stale:
            print("stale (run python3 scripts/master_dag.py):", ", ".join(stale))
            sys.exit(1)
        print("master graph: up to date")
        return
    for p, t in pages.items():
        p.write_text(t, encoding="utf-8")
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
