"""Tests for the progress server.   cd progress-server && python3 -m pytest -q   (or: python3 test_app.py)"""
import os, sys, tempfile
os.environ["PROGRESS_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["PROGRESS_TEACHER_TOKEN"] = "teach"
os.environ["PROGRESS_ORIGINS"] = "https://rahulsanjay18.github.io"
sys.path.insert(0, os.path.dirname(__file__))
from fastapi.testclient import TestClient
import app as server

c = TestClient(server.app)
T = {"Authorization": "Bearer teach"}


def ev(eid, item, correct, kind="auto", page="chess/0003-forks", **kw):
    return dict(v=1, eid=eid, type="attempt", page=page, item=f"{page}#{item}", widget="choice", kind=kind,
                correct=correct, answer="x", ts="2026-10-05T10:00:0%dZ" % (len(eid) % 10), **kw)


def test_auth_and_health():
    assert c.get("/health").json() == {"ok": True}
    assert c.get("/status").status_code == 401
    assert c.get("/status", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert c.get("/progress/status", headers=T).status_code == 200      # prefixed route works too


def test_devices_events_dedup_and_permissions():
    tok = c.post("/devices", json={"name": "phone"}, headers=T).json()["token"]
    D = {"Authorization": "Bearer " + tok}
    batch = {"events": [ev("a1", "fork-1", True), ev("a2", "fork-2", False),
                        {"v": 1, "eid": "r1", "type": "rating", "page": "chess/0003-forks", "value": "too-hard", "ts": "2026-10-05T10:01:00Z"},
                        {"v": 1, "eid": "n1", "type": "note", "page": "chess/0003-forks", "text": "pins vs forks?", "ts": "2026-10-05T10:02:00Z"}]}
    assert c.post("/events", json=batch, headers=D).json() == {"stored": 4, "duplicates": 0}
    assert c.post("/events", json=batch, headers=D).json() == {"stored": 0, "duplicates": 4}   # resend is harmless
    assert c.get("/status", headers=D).status_code == 403                # devices can't read teacher digests
    assert c.post("/devices", json={}, headers=D).status_code == 403
    s = c.get("/summary", params={"topic": "chess"}, headers=T).text
    assert "chess/0003-forks: 1/2 right first try" in s and "missed: fork-2" in s and "rating: too-hard" in s and "pins vs forks?" in s
    st = c.get("/status", headers=T).text
    assert "chess: 2 attempts in 14d (50% right)" in st and "note: pins vs forks?" in st
    # revoked device is locked out
    did = c.get("/devices", headers=T).json()[-1]["id"]
    c.delete(f"/devices/{did}", headers=T)
    assert c.post("/events", json=batch, headers=D).status_code == 401


def test_schedule_and_due():
    # a wrong answer goes to box 0 (due in 1 day); make it due now and check /due
    with server.db() as db:
        db.execute("UPDATE review SET due='2000-01-01T00:00:00Z' WHERE item LIKE '%fork-2'")
        row = db.execute("SELECT box FROM review WHERE item LIKE '%fork-1'").fetchone()
    assert row["box"] == 1                                               # a right answer is never box 0 (that means "not yet")
    due = c.get("/due", params={"topic": "chess"}, headers=T).json()
    assert [d["item"] for d in due] == ["chess/0003-forks#fork-2"]
    c.post("/events", json={"events": [ev("a3", "fork-1", True)]}, headers=T)
    with server.db() as db:
        assert db.execute("SELECT box FROM review WHERE item LIKE '%fork-1'").fetchone()["box"] == 2   # 30 days


def test_free_response_grading():
    c.post("/events", json={"events": [ev("f1", "essay", None, kind="deferred", page="econ/0001-scarcity")]}, headers=T)
    ung = c.get("/ungraded", params={"limit": 500}, headers=T).json()
    assert [u["eid"] for u in ung] == ["f1"]
    assert c.post("/grades", json={"grades": [{"event": "f1", "score": 0.8, "feedback": "Good; name the opportunity cost."}]}, headers=T).json() == {"graded": 1}
    assert c.get("/ungraded", params={"limit": 500}, headers=T).json() == []
    fb = c.get("/feedback", params={"page": "econ/0001-scarcity"}, headers=T).json()
    assert fb[0]["score"] == 0.8 and "opportunity cost" in fb[0]["feedback"]
    assert "graded: essay=0.8" in c.get("/summary", params={"topic": "econ"}, headers=T).text


def test_cors_preflight_needs_no_token():
    r = c.options("/events", headers={"Origin": "https://rahulsanjay18.github.io", "Access-Control-Request-Method": "POST",
                                      "Access-Control-Request-Headers": "authorization,content-type"})
    assert r.status_code == 200 and r.headers["access-control-allow-origin"] == "https://rahulsanjay18.github.io"
    r = c.options("/events", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in r.headers


def test_limits():
    assert c.post("/events", json={"events": [ev(f"x{i}", "q", True) for i in range(501)]}, headers=T).status_code == 400
    assert c.post("/events", json={"nope": 1}, headers=T).status_code == 400


def test_guessed_counts_as_not_known():
    page = "stats/0009-guess"
    c.post("/events", json={"events": [ev("g1", "q1", True, page=page), ev("g2", "q2", True, page=page),
        {"v": 1, "eid": "g3", "type": "confidence", "page": page, "item": page + "#q2", "value": "guessed", "ts": "2026-10-05T10:05:00Z"},
        {"v": 1, "eid": "g4", "type": "confidence", "page": page, "item": page + "#q1", "value": "knew", "ts": "2026-10-05T10:05:01Z"}]}, headers=T)
    with server.db() as db:
        r = {x["item"].split("#")[1]: x for x in db.execute("SELECT * FROM review WHERE page=?", (page,))}
    assert r["q2"]["box"] == 0 and r["q2"]["lapses"] == 1      # lucky guess: reset like a miss
    assert r["q1"]["lapses"] == 0                                # "knew" changes nothing
    s = c.get("/summary", params={"topic": "stats"}, headers=T).text
    assert "stats/0009-guess: 1/2 right first try" in s and "guessed: q2" in s, s


def test_reading_notes_never_scheduled():
    page = "stats/0011-notes"
    c.post("/events", json={"events": [ev("note1", "read-surprise", None, kind="deferred", page=page), ev("note2", "q3", False, page=page)]}, headers=T)
    eid = c.get("/ungraded", params={"limit": 500}, headers=T).json()
    eid = [x["eid"] for x in eid if x["item"] == page + "#read-surprise"]
    assert eid, "the note should be waiting for grading"
    c.post("/grades", json={"grades": [{"event": eid[0], "score": 1}]}, headers=T)
    with server.db() as db:
        items = [x["item"] for x in db.execute("SELECT item FROM review WHERE page=?", (page,))]
    assert items == [page + "#q3"], items


def test_pretest_answers_never_scheduled():
    page = "stats/0010-pretest"
    e1 = ev("p1", "q1", False, page=page); e1["pretest"] = True
    c.post("/events", json={"events": [e1, ev("p2", "q2", False, page=page)]}, headers=T)
    with server.db() as db:
        items = [x["item"] for x in db.execute("SELECT item FROM review WHERE page=?", (page,))]
    assert items == [page + "#q2"], items                          # the flagged miss isn't scheduled
    assert c.post("/review/drop", json={"pages": [page]}, headers=T).json() == {"dropped": 1}
    with server.db() as db:
        assert not db.execute("SELECT 1 FROM review WHERE page=?", (page,)).fetchall()
    assert c.post("/review/drop", json={"pages": "x"}, headers=T).status_code == 400


def test_pages_lists_answered_lessons():
    got = c.get("/pages", params={"topic": "chess"}, headers=T).json()["pages"]
    assert "chess/0003-forks" in got and all(p.startswith("chess/") for p in got)
    assert c.get("/pages", params={"topic": "nope"}, headers=T).json() == {"pages": [], "answered": {}, "rated": []}
    j = c.get("/pages", params={"topic": "chess"}, headers=T).json()
    assert j["answered"]["chess/0003-forks"] >= 2 and "chess/0003-forks" in j["rated"]   # fork-1, fork-2; rated "too-hard"
    assert c.get("/pages").status_code == 401



def test_rebuild_replays_under_current_rules():
    page = "chess/0042-rebuild"
    c.post("/events", json={"events": [ev("rb1", "a", True, page=page), ev("rb2", "b", False, page=page),
                                       ev("rb3", "c", True, page="chess/0043-placement")]}, headers=T)
    with server.db() as db:
        db.execute("UPDATE review SET box=0 WHERE page=?", (page,))            # pretend an old rule put a right answer in box 0
    r = c.post("/review/rebuild", json={"skip_pages": ["chess/0043-placement"]}, headers=T).json()
    assert r["items"] >= 2
    with server.db() as db:
        got = {x["item"].split("#")[1]: x["box"] for x in db.execute("SELECT * FROM review WHERE page=?", (page,))}
        assert db.execute("SELECT COUNT(*) FROM review WHERE page='chess/0043-placement'").fetchone()[0] == 0
    assert got == {"a": 1, "b": 0}
    assert c.post("/review/rebuild", json={}, headers={"Authorization": "Bearer nope"}).status_code in (401, 403)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok  ", name)
    print("all passed")
