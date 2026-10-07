"""Progress server for the shared lesson library (assets/lp.js). Stores quiz attempts, ratings and notes,
schedules spaced review, and gives the teacher short plain-text digests.

Env:
  PROGRESS_TEACHER_TOKEN  (required) full access. Set it to the book server's token so cloud sessions, whose proxy
                          already injects that token for this hostname, need no extra setup.
  PROGRESS_DB             SQLite file (default progress.db)
  PROGRESS_ORIGINS        comma-separated CORS origins (default https://rahulsanjay18.github.io)

Auth: 'Authorization: Bearer <token>'. Device tokens (made by the teacher) may only POST /events and GET /due, /feedback.
Every route is served both at / and under /progress, so it works whether or not the reverse proxy strips the prefix.

Teacher:  GET /status                      plain text, ~15 lines: per topic activity, due reviews, ungraded work, recent notes
          GET /pages[?topic=chess]          lesson pages with answered questions (device token)
          GET /summary?topic=chess         plain text: per page right-first-try, missed items, ratings, notes, grades
          GET /ungraded                    JSON: free-response answers waiting for a grade
          POST /grades                     {"grades":[{"event":"<eid>","score":0..1,"feedback":"..."}]}
          POST /devices {"name":"phone"}   -> {"id","token"} (token shown once);  GET /devices;  DELETE /devices/{id}
Device:   POST /events                     {"events":[...]} exactly as lp.js sends them (deduplicated by eid)
          GET /due?limit=20&topic=chess    JSON: review items due now
          GET /feedback?page=chess/0003-x  JSON: grades + feedback on your free-response answers
Open:     GET /health
"""
import hashlib, hmac, json, os, secrets, sqlite3, time
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

TEACHER = os.environ.get("PROGRESS_TEACHER_TOKEN", "")
DB = os.environ.get("PROGRESS_DB", "progress.db")
ORIGINS = [o.strip() for o in os.environ.get("PROGRESS_ORIGINS", "https://rahulsanjay18.github.io").split(",") if o.strip()]
INTERVALS = [1, 3, 7, 16, 35, 80, 180]   # days; box n -> next review after INTERVALS[n]
MAX_EVENTS, MAX_TEXT = 500, 4000

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  eid TEXT PRIMARY KEY, received TEXT NOT NULL, device TEXT, ts TEXT, type TEXT, page TEXT, item TEXT,
  widget TEXT, kind TEXT, correct INTEGER, answer TEXT, value TEXT, text TEXT);
CREATE INDEX IF NOT EXISTS events_page ON events(page);
CREATE INDEX IF NOT EXISTS events_item ON events(item);
CREATE TABLE IF NOT EXISTS grades (eid TEXT PRIMARY KEY, score REAL NOT NULL, feedback TEXT, graded TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review (
  item TEXT PRIMARY KEY, page TEXT, box INTEGER NOT NULL, due TEXT NOT NULL, last TEXT, reps INTEGER NOT NULL, lapses INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS devices (id INTEGER PRIMARY KEY, name TEXT, token_hash TEXT UNIQUE, created TEXT, revoked INTEGER DEFAULT 0);
"""


def now():
    return datetime.now(timezone.utc)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def db():
    c = sqlite3.connect(DB, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


with db() as _c:
    _c.executescript(SCHEMA)


def h(token):
    return hashlib.sha256(token.encode()).hexdigest()


def caller(authorization: str = Header(default="")):
    """Returns 'teacher' or 'device:<id>'."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "unauthorized")
    tok = authorization[7:]
    if TEACHER and hmac.compare_digest(tok, TEACHER):
        return "teacher"
    with db() as c:
        r = c.execute("SELECT id FROM devices WHERE token_hash=? AND revoked=0", (h(tok),)).fetchone()
    if r:
        return f"device:{r['id']}"
    raise HTTPException(401, "unauthorized")


def teacher(who: str = Depends(caller)):
    if who != "teacher":
        raise HTTPException(403, "teacher token required")
    return who


# ---------- spaced review (Leitner boxes) ----------
def schedule(c, item, page, correct, when):
    r = c.execute("SELECT * FROM review WHERE item=?", (item,)).fetchone()
    box, reps, lapses = (r["box"], r["reps"], r["lapses"]) if r else (-1, 0, 0)
    if correct:
        box = min(box + 1, len(INTERVALS) - 1)
    else:
        box, lapses = 0, lapses + (1 if r else 0)
    due = when + timedelta(days=INTERVALS[max(box, 0)])
    c.execute("INSERT OR REPLACE INTO review(item,page,box,due,last,reps,lapses) VALUES(?,?,?,?,?,?,?)",
              (item, page, box, iso(due), iso(when), reps + 1, lapses))


def clip(v):
    return None if v is None else str(v)[:MAX_TEXT]


router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True}


@router.post("/events")
def post_events(payload: dict = Body(...), who: str = Depends(caller)):
    events = payload.get("events")
    if not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise HTTPException(400, f"events must be a list of at most {MAX_EVENTS}")
    stored = dup = 0
    t = now()
    with db() as c:
        for e in events:
            if not isinstance(e, dict) or not e.get("type"):
                continue
            eid = clip(e.get("eid")) or hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()[:32]
            correct = e.get("correct")
            cur = c.execute(
                "INSERT OR IGNORE INTO events(eid,received,device,ts,type,page,item,widget,kind,correct,answer,value,text)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (eid, iso(t), who, clip(e.get("ts")), clip(e.get("type")), clip(e.get("page")), clip(e.get("item")),
                 clip(e.get("widget")), clip(e.get("kind")), None if correct is None else int(bool(correct)),
                 clip(e.get("answer")), clip(e.get("value")), clip(e.get("text"))))
            if cur.rowcount == 0:
                dup += 1
                continue
            stored += 1
            if e.get("type") == "attempt" and e.get("item") and correct is not None:
                schedule(c, e["item"], e.get("page"), bool(correct), t)
            elif e.get("type") == "confidence" and e.get("value") == "guessed" and e.get("item"):
                schedule(c, e["item"], e.get("page"), False, t)     # right by luck = not known yet
    return {"stored": stored, "duplicates": dup}


@router.get("/due")
def due(limit: int = Query(20, ge=1, le=200), topic: str = "", who: str = Depends(caller)):
    q, args = "SELECT * FROM review WHERE due<=?", [iso(now())]
    if topic:
        q += " AND page LIKE ?"
        args.append(topic + "/%")
    with db() as c:
        rows = c.execute(q + " ORDER BY due LIMIT ?", args + [limit]).fetchall()
    return [dict(x) for x in rows]


@router.get("/pages")
def pages(topic: str = "", who: str = Depends(caller)):
    """Lesson pages with at least one answered question (any device), for the Today page's "done" check."""
    q, args = "SELECT DISTINCT page FROM events WHERE type='attempt' AND page IS NOT NULL", []
    if topic:
        q += " AND page LIKE ?"
        args.append(topic + "/%")
    with db() as c:
        return {"pages": sorted(x[0] for x in c.execute(q, args))}


@router.get("/feedback")
def feedback(page: str = Query(min_length=1), who: str = Depends(caller)):
    with db() as c:
        rows = c.execute("SELECT e.item, e.answer, g.score, g.feedback, g.graded FROM events e JOIN grades g ON g.eid=e.eid"
                         " WHERE e.page=? ORDER BY g.graded", (page,)).fetchall()
    return [dict(x) for x in rows]


@router.get("/ungraded")
def ungraded(limit: int = Query(50, ge=1, le=500), _=Depends(teacher)):
    with db() as c:
        rows = c.execute("SELECT e.eid, e.page, e.item, e.answer, e.ts FROM events e LEFT JOIN grades g ON g.eid=e.eid"
                         " WHERE e.type='attempt' AND e.kind='deferred' AND g.eid IS NULL ORDER BY e.ts LIMIT ?", (limit,)).fetchall()
    return [dict(x) for x in rows]


@router.post("/grades")
def post_grades(payload: dict = Body(...), _=Depends(teacher)):
    grades = payload.get("grades") or []
    t = now()
    done = 0
    with db() as c:
        for g in grades:
            ev = c.execute("SELECT item, page FROM events WHERE eid=?", (g.get("event"),)).fetchone()
            if not ev:
                continue
            score = max(0.0, min(1.0, float(g.get("score", 0))))
            c.execute("INSERT OR REPLACE INTO grades(eid,score,feedback,graded) VALUES(?,?,?,?)",
                      (g["event"], score, clip(g.get("feedback")), iso(t)))
            schedule(c, ev["item"], ev["page"], score >= 0.7, t)
            done += 1
    return {"graded": done}


@router.post("/devices")
def make_device(payload: dict = Body(default={}), _=Depends(teacher)):
    token = secrets.token_urlsafe(32)
    with db() as c:
        cur = c.execute("INSERT INTO devices(name, token_hash, created) VALUES(?,?,?)",
                        (clip(payload.get("name")) or "device", h(token), iso(now())))
    return {"id": cur.lastrowid, "token": token}


@router.get("/devices")
def list_devices(_=Depends(teacher)):
    with db() as c:
        return [dict(x) for x in c.execute("SELECT id, name, created, revoked FROM devices ORDER BY id")]


@router.delete("/devices/{dev_id}")
def revoke_device(dev_id: int, _=Depends(teacher)):
    with db() as c:
        c.execute("UPDATE devices SET revoked=1 WHERE id=?", (dev_id,))
    return {"revoked": dev_id}


# ---------- plain-text digests for the teacher ----------
def topic_of(page):
    return (page or "?").split("/")[0]


@router.get("/status", response_class=PlainTextResponse)
def status(_=Depends(teacher)):
    t = now()
    since = iso(t - timedelta(days=14))
    out = [f"progress @ {iso(t)}"]
    with db() as c:
        acts = c.execute("SELECT page, COUNT(*) n, SUM(correct) n_right, MAX(ts) last FROM events"
                         " WHERE type='attempt' AND kind!='deferred' AND received>=? GROUP BY page", (since,)).fetchall()
        dues = c.execute("SELECT page, COUNT(*) n FROM review WHERE due<=? GROUP BY page", (iso(t),)).fetchall()
        ungr = c.execute("SELECT COUNT(*) FROM events e LEFT JOIN grades g ON g.eid=e.eid"
                         " WHERE e.kind='deferred' AND g.eid IS NULL").fetchone()[0]
        notes = c.execute("SELECT page, type, value, text, ts FROM events WHERE type IN ('note','rating')"
                          " ORDER BY ts DESC LIMIT 6").fetchall()
    topics = {}
    for a in acts:
        d = topics.setdefault(topic_of(a["page"]), {"n": 0, "right": 0, "last": "", "due": 0})
        d["n"] += a["n"]; d["right"] += a["n_right"] or 0; d["last"] = max(d["last"], a["last"] or "")
    for x in dues:
        topics.setdefault(topic_of(x["page"]), {"n": 0, "right": 0, "last": "", "due": 0})["due"] += x["n"]
    if not topics:
        out.append("no activity in the last 14 days, nothing due")
    for name, d in sorted(topics.items()):
        acc = f"{round(100 * d['right'] / d['n'])}% right" if d["n"] else "no attempts"
        out.append(f"{name}: {d['n']} attempts in 14d ({acc}), {d['due']} reviews due, last {d['last'][:10] or '-'}")
    out.append(f"ungraded free responses: {ungr}")
    for n in notes:
        what = f"rated {n['value']}" if n["type"] == "rating" else "note: " + (n["text"] or "").replace("\n", " ")[:120]
        out.append(f"  {n['ts'][:10] if n['ts'] else ''} {n['page']}: {what}")
    return "\n".join(out) + "\n"


@router.get("/summary", response_class=PlainTextResponse)
def summary(topic: str = Query(min_length=1), _=Depends(teacher)):
    out = [f"summary: {topic}"]
    with db() as c:
        pages = [x[0] for x in c.execute("SELECT DISTINCT page FROM events WHERE page LIKE ? ORDER BY page", (topic + "/%",))]
        for p in pages:
            # first attempt per item decides "right first try"
            # SQLite takes bare columns from the MIN(ts) row
            firsts = c.execute("SELECT item, correct, MIN(ts) FROM events WHERE page=? AND type='attempt' AND kind!='deferred'"
                               " GROUP BY item", (p,)).fetchall()
            lucky = {x[0] for x in c.execute("SELECT item FROM events WHERE page=? AND type='confidence' AND value='guessed'", (p,))}
            right = sum(1 for f in firsts if f["correct"] and f["item"] not in lucky)
            missed = [f["item"].split("#")[-1] for f in firsts if f["correct"] == 0]
            guessed = [i.split("#")[-1] for i in sorted(lucky)]
            rating = c.execute("SELECT value FROM events WHERE page=? AND type='rating' ORDER BY ts DESC LIMIT 1", (p,)).fetchone()
            notes = c.execute("SELECT text FROM events WHERE page=? AND type='note' ORDER BY ts", (p,)).fetchall()
            grades = c.execute("SELECT e.item, g.score FROM events e JOIN grades g ON g.eid=e.eid WHERE e.page=?", (p,)).fetchall()
            ungraded = c.execute("SELECT COUNT(*) FROM events e LEFT JOIN grades g ON g.eid=e.eid"
                                 " WHERE e.page=? AND e.kind='deferred' AND g.eid IS NULL", (p,)).fetchone()[0]
            line = f"{p}: {right}/{len(firsts)} right first try"
            if missed: line += " | missed: " + ",".join(missed)
            if guessed: line += " | guessed: " + ",".join(guessed)
            if rating: line += f" | rating: {rating['value']}"
            if grades: line += " | graded: " + ",".join(f"{g['item'].split('#')[-1]}={g['score']:.1f}" for g in grades)
            if ungraded: line += f" | {ungraded} ungraded"
            out.append(line)
            for n in notes:
                out.append("    note: " + (n["text"] or "").replace("\n", " ")[:200])
    if len(out) == 1:
        out.append("no activity")
    return "\n".join(out) + "\n"


app = FastAPI(title="progress-server", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS, allow_methods=["GET", "POST"],
                   allow_headers=["Authorization", "Content-Type"], max_age=86400)
app.include_router(router)
app.include_router(router, prefix="/progress")
