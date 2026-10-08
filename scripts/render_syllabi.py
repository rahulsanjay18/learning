#!/usr/bin/env python3
"""Render course syllabi (topics/<major>/syllabi/<COURSE>.md) to printable HTML, one page per course, plus a course catalog
per major (topics/<major>/syllabi/index.html = the program of study: PLAN.md + projected terms + catalog).

    python3 scripts/render_syllabi.py            # render every major
    python3 scripts/render_syllabi.py statistics # one major
    python3 scripts/render_syllabi.py --check    # exit 1 if a course has no syllabus or an HTML page is stale

Why: a syllabus is the college-style handout for one course (description, objectives, texts, weekly schedule, grading,
policies). The author writes only those sections; this script adds the facts that already live elsewhere, so they are never
copied by hand: title, level, group, status and prerequisites (curriculum.json), meeting days (programs.json `week`), lessons
done (curriculum.json `lessons`), and a projected calendar (computed below; it moves whenever pretests skip lessons).
Standard: notes/syllabus-standard.md. Standard library only.
"""
import datetime as dt, html, json, math, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from render_lesson import blocks, inline, front_matter, esc  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = "../../../assets/"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
GROUP_NAME = {"core": "Required", "breadth": "Optional (breadth)", "elective": "Optional (elective)",
              "practice": "Optional (practice)", "independent": "Optional (independent study)",
              "capstone": "Optional (capstone)", "colloquium": "Optional (end-of-level conversation)"}
LEVEL_NAME = {"I": "Level I (undergraduate)", "II": "Level II (graduate, if you sign up for it)"}
# Lessons per week for one course of the major, from the weekly blocks in programs.json and the lesson size in each PROGRAM.md:
# Statistics 4 blocks, 2 blocks a lesson; Indian History 2 blocks, 2 a lesson; Games 2 blocks shared by its 2 active courses,
# 1 a lesson; Engineering one block per lane, 1 a lesson.
RATE = {"statistics": 2.0, "indian-history": 1.0, "games": 1.0, "eng": 1.0}
DEFAULT_LESSONS = 6


def today():
    return dt.date.today()


def load(major):
    progs = json.loads((ROOT / "programs.json").read_text())
    entry = next(m for m in progs["majors"] if m["slug"] == major)
    cur = json.loads((ROOT / entry["curriculum"]).read_text())
    return progs, entry, cur


def meeting(progs, major, course):
    days = [d for d in DAYS if major in progs["week"].get(d, [])]
    lane = course.get("lane")
    if major == "eng" and lane in ("staff", "tech", "interview", "interest"):
        cur = json.loads((ROOT / "topics/eng/curriculum.json").read_text())
        days = [d for d, l in cur.get("lanes", {}).items() if l == lane]
        return f"{', '.join(d.title() for d in days)} ({lane} track): one 25-minute block a week. Mock interviews and pretests run about 45 minutes"
    if lane == "embedded":
        return "No meetings of its own. It runs inside every engineering lesson"
    return f"{', '.join(d.title() for d in days)}. That's {len(days)} 25-minute blocks a week, shared by the major's courses"


def lessons_for(course, meta):
    if meta.get("lessons", "").isdigit():
        return int(meta["lessons"])
    return course.get("est_lessons") or DEFAULT_LESSONS


def project(cur, major, metas):
    """Projected start and end dates for the default path: Level I core courses, in prerequisite order (ties: file order),
    one course at a time per lane (Engineering) or per major. Done courses are skipped; extras and Level II are not projected."""
    courses = cur["courses"]
    by_id = {c["id"]: c for c in courses}
    rate = RATE.get(major, 1.0)
    out, end_of = {}, {}
    start = today()
    for c in courses:                       # done courses end in the past
        if c.get("status") == "done":
            end_of[c["id"]] = start
    lanes = {}
    for c in courses:
        if c.get("group") != "core" or c.get("level", "I") != "I" or c.get("status") == "done" or c.get("lane") == "embedded":
            continue
        # Games runs a game course and the strategy course (lessons in topics/military-strategy) side by side.
        lane = c.get("lane") or ("strategy" if c.get("topic") == "military-strategy" else "_")
        lanes.setdefault(lane, []).append(c)
    for lane, cs in lanes.items():
        cs = sorted(cs, key=lambda c: (c.get("status") != "active", courses.index(c)))
        placed, cursor = [], start
        pending = list(cs)
        while pending:
            for c in pending:
                if all(r in end_of or r not in by_id for r in c.get("requires", [])):
                    break
            else:
                break                        # an unmet prerequisite outside the projected set: stop projecting this lane
            pending.remove(c)
            n = lessons_for(c, metas.get(c["id"], {}))
            if c.get("status") == "active":
                n = max(n - len(c.get("lessons", [])), 1)
            if c.get("lane") == "interest" or c["id"] in ("IV100",):
                out[c["id"]] = (cursor, None)  # continuous courses never end
                continue
            s = max([cursor] + [end_of[r] for r in c.get("requires", []) if r in end_of])
            e = s + dt.timedelta(weeks=math.ceil(n / rate))
            out[c["id"]], end_of[c["id"]], cursor = (s, e), e, e
            placed.append(c["id"])
    return out


def term_of(d):
    season = "Spring" if d.month <= 5 else "Summer" if d.month <= 8 else "Fall"
    return f"{season} {d.year}"


def term_key(t):
    season, year = t.split()
    return (int(year), ["Spring", "Summer", "Fall"].index(season))


def fmt(d):
    return d.strftime("%b %-d, %Y") if d else "—"


TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")


def tables(lines):
    """Pipe tables -> one-line HTML tables (so render_lesson.blocks passes them through as raw HTML)."""
    out, i = [], 0
    while i < len(lines):
        if TABLE_ROW.match(lines[i]) and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            cells = lambda l: [x.strip() for x in l.strip().strip("|").split("|")]
            head = cells(lines[i]); i += 2
            rows = []
            while i < len(lines) and TABLE_ROW.match(lines[i]):
                rows.append(cells(lines[i])); i += 1
            h = "".join(f"<th>{inline(x)}</th>" for x in head)
            b = "".join("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in r) + "</tr>" for r in rows)
            out += ["", f'<table class="syllabus"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>', ""]
            continue
        out.append(lines[i]); i += 1
    return out


def header_rows(progs, entry, cur, major, c, meta, proj):
    by_id = {x["id"]: x for x in cur["courses"]}
    reqs = c.get("requires", [])
    req = ", ".join(f'<a href="{r}.html">{r} {html.escape(by_id[r]["title"])}</a>' if r in by_id else r for r in reqs) or "none"
    n = lessons_for(c, meta)
    done = len(c.get("completed", []))
    written = len(c.get("lessons", []))
    status = {"done": "Completed", "active": "In progress", "next": "Next up", "later": "Not started"}.get(c.get("status"), c.get("status"))
    if c.get("credit") == "exam":
        status += " (passed by pretest)"
    rows = [("Course", f"{c['id']} · {html.escape(c['title'])}"),
            ("Major", html.escape(entry["name"])),
            ("Level and group", f"{LEVEL_NAME.get(c.get('level', 'I'))} · {GROUP_NAME.get(c.get('group', 'core'), c.get('group'))}"),
            ("Status", f"{status}" + (f" · {done} of {written} written lessons done" if written else "")),
            ("Instructor", "Claude. Office hours: any session"),
            ("Meets", meeting(progs, major, c)),
            ("Length", f"about {n} lessons" + (", plus a pretest at the start" if c.get("pretest") else "")),
            ("Prerequisites", req)]
    if c["id"] in proj:
        s, e = proj[c["id"]]
        rows.append(("Estimated dates", f"{fmt(s)} to {fmt(e) if e else 'ongoing'} <small>(estimate; it moves earlier when the pretest lets you skip lessons)</small>"))
    elif c.get("status") != "done":
        rows.append(("Estimated dates", "not scheduled: " + ("Level II starts only if you sign up for it" if c.get("level") == "II" else
                     "optional; starts when you choose it" if c.get("group") != "core" else "after its prerequisites")))
    return "<table class=\"syllabus meta\"><tbody>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</tbody></table>"


STYLE = """<style>
table.syllabus{border-collapse:collapse;width:100%;margin:1em 0;font-size:.95em}
table.syllabus th,table.syllabus td{border-top:1px solid var(--rule,#ccc);padding:.35em .5em;text-align:left;vertical-align:top}
table.syllabus.meta th{width:11em;font-weight:normal;color:var(--muted,#666)}
@media print{nav.crumbs{display:none}}
</style>
"""


def page(title, crumb, body, src):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{ASSETS}lp.css">
{STYLE}<!-- generated by scripts/render_syllabi.py from {src}; edit the .md and re-render -->
</head>
<body>
<main>
<nav class="crumbs"><a href="../../../index.html">All topics</a> · {crumb}</nav>
{body}
</main>
</body>
</html>
"""


def render_major(major, write=True):
    progs, entry, cur = load(major)
    d = ROOT / "topics" / major / "syllabi"
    metas, bodies, problems = {}, {}, []
    for c in cur["courses"]:
        f = d / f"{c['id']}.md"
        if not f.exists():
            problems.append(f"{major}: no syllabus for {c['id']} ({f.relative_to(ROOT)})")
            continue
        meta, body = front_matter(f.read_text(encoding="utf-8"))
        if meta.get("course") != c["id"]:
            problems.append(f"{f.relative_to(ROOT)}: front matter course: must be {c['id']}")
        for need in ("## Course description", "## Learning objectives", "## Texts", "## Schedule", "## Assessment"):
            if need not in body:
                problems.append(f"{f.relative_to(ROOT)}: missing section '{need}'")
        metas[c["id"]], bodies[c["id"]] = meta, body
    proj = project(cur, major, metas)
    pages = {}
    for c in cur["courses"]:
        if c["id"] not in bodies:
            continue
        meta, body = metas[c["id"]], bodies[c["id"]]
        title = f"{c['id']} {c['title']}: syllabus"
        content = (f"<h1>{inline(c['id'] + ' ' + c['title'])}</h1>\n<p class=\"subtitle\">Syllabus · {html.escape(entry['name'])}"
                   f" · updated {meta.get('updated', '')}</p>\n"
                   + header_rows(progs, entry, cur, major, c, meta, proj) + "\n"
                   + blocks(tables(body.splitlines()))
                   + '\n<h2>Course policies</h2>\n<p>Meetings, missed days, grading, honesty and accommodations work the same way in every course. See the '
                   '<a href="../../../notes/course-policies.md">course policies</a>. Once a course starts, its lesson-by-lesson plan is in '
                   '<a href="../SYLLABUS.md">the major\'s syllabus file</a>. The whole major is on the <a href="index.html">program page</a>.</p>')
        pages[d / f"{c['id']}.html"] = page(title, f'<a href="index.html">{html.escape(entry["name"])} program</a> · {c["id"]}', content, f"{c['id']}.md")
    # catalog
    rows = []
    for grp in ("I", "II"):
        cs = [c for c in cur["courses"] if c.get("level", "I") == grp]
        if not cs:
            continue
        rows.append(f"<h2>{LEVEL_NAME[grp]}</h2>")
        rows.append('<table class="syllabus"><thead><tr><th>Course</th><th>Group</th><th>Status</th><th>Prerequisites</th><th>Estimated dates</th></tr></thead><tbody>')
        for c in cs:
            p = proj.get(c["id"])
            link = f'<a href="{c["id"]}.html">{c["id"]} {html.escape(c["title"])}</a>' if c["id"] in bodies else f'{c["id"]} {html.escape(c["title"])}'
            rows.append(f"<tr><td>{link}</td><td>{c.get('group', 'core')}</td><td>{c.get('status')}</td>"
                        f"<td>{', '.join(c.get('requires', [])) or '—'}</td><td>{fmt(p[0]) + ' to ' + (fmt(p[1]) if p[1] else 'ongoing') if p else '—'}</td></tr>")
        rows.append("</tbody></table>")
    terms = {}
    for cid, (s0, e0) in proj.items():
        terms.setdefault(term_of(s0), []).append(cid)
    term_rows = "".join(f"<tr><td>{t}</td><td>{', '.join(f'<a href=\"{c}.html\">{c}</a>' for c in cs)}</td></tr>"
                        for t, cs in sorted(terms.items(), key=lambda kv: term_key(kv[0])))
    plan_md = d / "PLAN.md"
    plan_html = ""
    if plan_md.exists():
        pm, pb = front_matter(plan_md.read_text(encoding="utf-8"))
        plan_html = blocks(tables(pb.splitlines()))
    else:
        problems.append(f"{major}: no program plan ({plan_md.relative_to(ROOT)})")
    cat = (f"<h1>{html.escape(entry['name'])}: program of study</h1>\n<p class=\"subtitle\">The plan for the whole major, then every course "
           "with a link to its syllabus. Dates are estimates as of "
           f"{fmt(today())}. They move earlier as pretests let you skip lessons.</p>\n" + plan_html
           + "\n<h2>When each required course starts (estimate)</h2>\n<p>Fall is September to December, spring is January to May, summer is June to August.</p>"
           + f'<table class="syllabus"><thead><tr><th>Term</th><th>Courses starting</th></tr></thead><tbody>{term_rows}</tbody></table>'
           + "\n<h2>All courses</h2>\n" + "\n".join(rows))
    pages[d / "index.html"] = page(f"{entry['name']} program of study", f"{html.escape(entry['name'])} program", cat, "PLAN.md + curriculum.json")
    if write:
        for p, text in pages.items():
            p.write_text(text, encoding="utf-8")
    return problems, pages


def main(argv):
    check = "--check" in argv
    majors = [a for a in argv if not a.startswith("--")]
    progs = json.loads((ROOT / "programs.json").read_text())
    majors = majors or [m["slug"] for m in progs["majors"]]
    all_problems = []
    for m in majors:
        problems, pages = render_major(m, write=not check)
        all_problems += problems
        if check:
            for p, text in pages.items():
                old = p.read_text(encoding="utf-8") if p.exists() else ""
                # dates in the projection change daily; compare with dates masked
                mask = lambda s: re.sub(r"[A-Z][a-z]{2} \d{1,2}, \d{4}", "DATE", s)
                if mask(old) != mask(text):
                    all_problems.append(f"stale: {p.relative_to(ROOT)} (run python3 scripts/render_syllabi.py)")
    for p in all_problems:
        print("FAIL", p)
    if not check:
        print(f"rendered syllabi for {', '.join(majors)}; {len(all_problems)} problem(s)")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
