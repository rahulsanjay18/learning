#!/usr/bin/env python3
"""Self-updating catalogs: topics/<major>/catalog.json lists certs, skills, languages and tracks with the date each was last
checked on the web. This script says which entries are due for a re-check; /program then re-checks them (official page first),
updates the entry and its `verified` date, and logs what changed in topics/<major>/CHANGES.md.

    python3 scripts/catalog.py                 due entries for every catalog (what /program shows)
    python3 scripts/catalog.py --all           every entry with its age
    python3 scripts/catalog.py --course CR130  entries for one course (re-check before starting it)
    python3 scripts/catalog.py --check         validate every catalog (run by test_programs.py); exit 1 on errors
    add --date YYYY-MM-DD to pretend today is another day
"""
import json, sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"cert", "skill", "framework", "language", "track", "benchmark"}
STATES = {"current", "check", "retiring", "retired", "announced"}
PICKS = {"core", "elective", "watch", "skip"}
SOON = 45  # days before a watch_date when an entry comes due


def catalogs():
    return sorted(ROOT.glob("topics/*/catalog.json"))


def validate(path):
    errs = []
    try:
        cat = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{path}: bad JSON: {e}"]
    ids = set()
    for e in cat.get("entries", []):
        w = f"{path.parent.name}/{e.get('id')}"
        if e.get("id") in ids:
            errs.append(f"{w}: duplicate id")
        ids.add(e.get("id"))
        for k in ("id", "kind", "name", "pick", "why", "verified", "sources"):
            if not e.get(k):
                errs.append(f"{w}: missing {k}")
        if e.get("kind") not in KINDS:
            errs.append(f"{w}: kind must be one of {sorted(KINDS)}")
        if e.get("kind") == "cert" and e.get("state") not in STATES:
            errs.append(f"{w}: cert state must be one of {sorted(STATES)}")
        if e.get("pick") not in PICKS:
            errs.append(f"{w}: pick must be one of {sorted(PICKS)}")
        for k in ("verified", "watch_date"):
            if e.get(k):
                try:
                    date.fromisoformat(e[k])
                except ValueError:
                    errs.append(f"{w}: {k} is not YYYY-MM-DD")
    return errs


def course_status(major):
    p = ROOT / "topics" / major / "curriculum.json"
    try:
        return {c["id"]: c["status"] for c in json.loads(p.read_text(encoding="utf-8"))["courses"]}
    except Exception:
        return {}


def due(cat, today, statuses=None):
    """(entry, reason) for entries needing a web re-check. 'check' entries only nag once their course is next or active."""
    out, every = [], timedelta(days=cat.get("refresh_days", 60))
    statuses = statuses or {}
    for e in cat["entries"]:
        if e.get("pick") == "skip":  # rejected options aren't worth re-checking
            continue
        v = date.fromisoformat(e["verified"])
        wd = date.fromisoformat(e["watch_date"]) if e.get("watch_date") else None
        if today - v >= every:
            out.append((e, f"last checked {v} ({(today - v).days} days ago)"))
        elif e.get("state") == "check" and statuses.get(e.get("course")) in ("next", "active"):
            out.append((e, "state is 'check': confirm before its course starts"))
        elif wd and v < wd and (wd - today).days <= SOON:
            out.append((e, f"watch date {wd}"))
    return out


def main():
    a = sys.argv[1:]
    today = date.fromisoformat(a[a.index("--date") + 1]) if "--date" in a else date.today()
    if "--check" in a:
        errs = [x for p in catalogs() for x in validate(p)]
        print("\n".join(errs) or f"catalogs: {len(catalogs())} ok")
        sys.exit(1 if errs else 0)
    for p in catalogs():
        cat = json.loads(p.read_text(encoding="utf-8"))
        major = p.parent.name
        if "--course" in a:
            cid = a[a.index("--course") + 1]
            rows = [(e, f"verified {e['verified']}") for e in cat["entries"] if e.get("course") == cid]
        elif "--all" in a:
            rows = [(e, f"verified {e['verified']}") for e in cat["entries"]]
        else:
            rows = due(cat, today, course_status(major))
        if not rows:
            continue
        print(f"{major}: {len(rows)} entr{'y' if len(rows) == 1 else 'ies'}" + ("" if "--all" in a or "--course" in a else " due for a re-check"))
        for e, why in rows:
            print(f"  {e['id']:<24} {e.get('pick', ''):<8} {why}  [{e['sources'][0]}]")


if __name__ == "__main__":
    main()
