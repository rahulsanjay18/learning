#!/usr/bin/env python3
"""Print the ~20-line 'where you are' block for /program.

Reads programs.json and each major's curriculum.json, checks which lesson files exist, and asks the progress
server which lesson pages the learner has actually done. Never fails: problems become WARN lines.
Usage: status.py [--offline] [--date YYYY-MM-DD]
"""
import json, os, re, subprocess, sys
from datetime import datetime, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BOOKS_URL = "https://books.tail59e10.ts.net"
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def load(p):
    return json.loads((ROOT / p).read_text())


def fetch(path):
    """GET from the progress server via curl (the cloud proxy injects auth). None if unreachable."""
    try:
        r = subprocess.run(["curl", "-s", "-m", "8", "-w", "\n%{http_code}", BOOKS_URL + "/progress" + path],
                           capture_output=True, text=True, timeout=12)
        body, _, code = r.stdout.rpartition("\n")
        return body if code == "200" else None
    except Exception:
        return None


def today(tz, override):
    if override:
        return date.fromisoformat(override)
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(tz)).date()
    except Exception:
        return date.today()


def lesson_files(topic):
    d = ROOT / "topics" / topic / "lessons"
    return sorted(p.stem for p in d.glob("[0-9][0-9][0-9][0-9]-*.html")) if d.is_dir() else []


def main():
    args = sys.argv[1:]
    offline = "--offline" in args
    d_override = args[args.index("--date") + 1] if "--date" in args else None
    cfg = load("programs.json")
    names = {m["slug"]: m["name"] for m in cfg["majors"]}
    d = today(cfg.get("timezone", "UTC"), d_override)
    day = DAYS[d.weekday()]
    blocks = cfg["week"].get(day, [])
    out, warn = [], []

    out.append(f"PROGRAM STATUS {d.isoformat()} ({day.title()})")
    plan = " -> ".join([f"review ({cfg['review']})"] + [names.get(b, b) for b in blocks]) if blocks else "rest day (review optional)"
    out.append(f"Today: {plan}")

    status = None if offline else fetch("/status")
    if status is None:
        out.append("Progress server: unreachable" + (" (--offline)" if offline else "") + "; ask for pasted lp-results lines")
    else:
        lines = [l for l in status.strip().splitlines()[1:] if l.strip()]
        out.append("Progress: " + (lines[0] if lines else "no data"))
        out += ["  " + l for l in lines[1:6]]

    summaries = {}
    for m in cfg["majors"]:
        tag = f"{m['name']} [{m['weight']}]"
        if not m.get("curriculum"):
            out.append(f"{tag}: SETUP NEEDED. {m.get('setup', '')}")
            continue
        try:
            cur = load(m["curriculum"])
        except Exception as e:
            warn.append(f"{m['curriculum']}: {e}")
            continue
        courses = cur["courses"]
        done = sum(1 for c in courses if c["status"] == "done")
        active = [c for c in courses if c["status"] == "active"]
        if not active:
            ready = [c for c in courses if c["status"] in ("next", "later")
                     and all(any(x["id"] == r and x["status"] == "done" for x in courses) for r in c.get("requires", []))]
            out.append(f"{tag}: no active course ({done}/{len(courses)} done). Ready to start: "
                       + (", ".join(f"{c['id']} {c['title']}" for c in ready[:3]) or "none"))
        for c in active:
            topic = c.get("topic", m["slug"])
            files = set(lesson_files(topic))
            missing = [l for l in c.get("lessons", []) if l not in files]
            if missing:
                warn.append(f"{c['id']}: lesson files missing in topics/{topic}/lessons: {', '.join(missing)}")
            if topic not in summaries:
                summaries[topic] = None if offline or status is None else fetch(f"/summary?topic={topic}")
            summ = summaries[topic]
            # done = attempted on the progress server, or recorded by hand in "completed" (pasted lp-results)
            done_l = set(re.findall(rf"^{re.escape(topic)}/(\S+?):", summ or "", re.M)) | set(c.get("completed", []))
            lessons = c.get("lessons", [])
            n, est = len(lessons), c.get("est_lessons", "?")
            line = f"{tag} {c['id']} {c['title']}: {n}/{est} lessons written"
            if lessons:
                last = lessons[-1]
                if last in done_l:
                    line += f"; latest {last} DONE"
                elif summ is None:
                    line += f"; latest {last} (done? unknown)"
                else:
                    line += f"; latest {last} NOT DONE YET (learner's next step)"
            out.append(line)
            nxt = (c.get("plan") or [None])[0]
            if nxt:
                out.append(f"    next to write: {nxt}")
            elif c.get("est_lessons") and n >= c["est_lessons"]:
                out.append("    plan empty and estimate reached: course check, then mark done and activate the next course")
            unmapped = sorted(f for f in files if not any(f in x.get("lessons", []) for x in courses
                                                        if x.get("topic", m["slug"]) == topic))
            if unmapped:
                warn.append(f"topics/{topic}/lessons not in any course: {', '.join(unmapped)}")
        nxt_c = [c for c in courses if c["status"] == "next"]
        if nxt_c:
            out.append(f"    queued: " + ", ".join(f"{c['id']} {c['title']}" for c in nxt_c))

    if cfg.get("parked"):
        out.append("Parked: " + ", ".join(p["slug"] for p in cfg["parked"]))
    out += ["WARN " + w for w in warn]
    print("\n".join(out))


if __name__ == "__main__":
    main()
