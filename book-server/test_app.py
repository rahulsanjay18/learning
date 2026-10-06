"""Tests for the book server with a tiny index.   cd book-server && python3 test_app.py"""
import os, sqlite3, sys, tempfile, pathlib
d = pathlib.Path(tempfile.mkdtemp())
(d / "md").mkdir()
(d / "md" / "a.md").write_text("# Ch 8\nDefinition 8.3.1 The power function\nmore text about power\n")
(d / "md" / "b.md").write_text("# Other\nPower in physics is energy per time\n")
db = sqlite3.connect(d / "books.db")
db.executescript("""CREATE TABLE books(id TEXT PRIMARY KEY, title TEXT, grade TEXT, flags TEXT, category TEXT, md_path TEXT, n_lines INT);
CREATE VIRTUAL TABLE chunks USING fts5(book_id UNINDEXED, start_line UNINDEXED, body, tokenize='porter unicode61');""")
db.executemany("INSERT INTO books VALUES (?,?,?,?,?,?,?)", [("aaa", "Stats book", "A", "", "Math", "a.md", 3), ("bbb", "Physics book", "B", "x", "Sci", "b.md", 2)])
db.executemany("INSERT INTO chunks VALUES (?,?,?)", [("aaa", 1, "Definition 8.3.1 The power function more text about power"), ("bbb", 1, "Power in physics is energy per time")])
db.commit(); db.close()
os.environ.update(BOOKS_TOKEN="t", BOOKS_DB=str(d / "books.db"), BOOKS_MD_ROOT=str(d / "md"))
sys.path.insert(0, os.path.dirname(__file__))
from fastapi.testclient import TestClient
import app as server
c, H = TestClient(server.app), {"Authorization": "Bearer t"}

def test_search_all_and_one_book():
    assert {r["id"] for r in c.get("/search", params={"q": "power"}, headers=H).json()} == {"aaa", "bbb"}
    assert [r["id"] for r in c.get("/search", params={"q": "power", "book": "bbb"}, headers=H).json()] == ["bbb"]
    assert c.get("/search", params={"q": "power", "book": "zzz"}, headers=H).status_code == 404

def test_compact():
    j = c.get("/search", params={"q": "power", "compact": "true"}, headers=H).json()
    assert set(j["books"]) == {"aaa", "bbb"} and "warning" in j["books"]["bbb"] and all(set(h) == {"id", "start_line", "snippet"} for h in j["hits"])

def test_grep():
    j = c.get("/grep/aaa", params={"q": "definition 8.3"}, headers=H).json()
    assert j["matches"] == [{"line": 2, "text": "Definition 8.3.1 The power function"}]
    assert c.get("/grep/aaa", params={"q": "x"}, headers=H).status_code == 422
    assert c.get("/grep/aaa", params={"q": "power"}).status_code == 401

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("ok  ", n)
    print("all passed")
