"""Read-only book server for /teach. Serves only A/B-grade text, in small slices.

Env: BOOKS_TOKEN (required), BOOKS_DB (default books.db), BOOKS_MD_ROOT (default /books_md)
Endpoints (all need 'Authorization: Bearer <BOOKS_TOKEN>'):
  GET /search?q=policy gradient&limit=10   -> matching passages: book id, title, grade, line range, snippet
        [&book=<id>] search one book only;  [&compact=true] -> {"books": {id: meta}, "hits": [{id, start_line, snippet}]}
  GET /grep/{id}?q=Definition 8.3&limit=20 -> lines containing the text (case-insensitive), with line numbers
  GET /read/{id}?start=120&n=80            -> lines start..start+n (max 200)
  GET /toc/{id}                            -> headings with line numbers
  GET /book/{id}                           -> metadata incl. grade + flags
  GET /books?q=sutton barto                -> title lookup: is this book on the server?
  GET /catalog                             -> every book in one call: [[id, grade, title], ...] (diff it against MANIFEST.csv)
"""
import hmac, os, re, sqlite3
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException, Query

TOKEN = os.environ.get("BOOKS_TOKEN", "")
DB = os.environ.get("BOOKS_DB", "books.db")
MD_ROOT = Path(os.environ.get("BOOKS_MD_ROOT", "/books_md"))
MAX_LINES = 200
B_WARNING = "Grade B: use prose only. Do NOT take equations, figures, tables or code from this text; point the learner to the section in the original."

app = FastAPI(title="book-server", docs_url=None, redoc_url=None, openapi_url=None)

def auth(authorization: str = Header(default="")):
    if not TOKEN or not hmac.compare_digest(authorization, f"Bearer {TOKEN}"):
        raise HTTPException(401, "unauthorized")

def db():
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c

def book_or_404(c, bid):
    b = c.execute("SELECT * FROM books WHERE id=?", (bid,)).fetchone()
    if not b:
        raise HTTPException(404, "unknown book, or not grade A/B")
    return b

def meta(b):
    d = {"id": b["id"], "title": b["title"], "grade": b["grade"], "flags": b["flags"], "lines": b["n_lines"]}
    if b["grade"] == "B":
        d["warning"] = B_WARNING
    return d

@app.get("/search", dependencies=[Depends(auth)])
def search(q: str = Query(min_length=2, max_length=200), limit: int = Query(10, ge=1, le=30),
           book: str = Query("", max_length=40), compact: bool = False):
    terms = re.findall(r"\w+", q)
    if not terms:
        raise HTTPException(400, "empty query")
    fts = " ".join(f'"{t}"' for t in terms)  # quoted terms: no FTS syntax injection
    where, args = "chunks MATCH ?", [fts]
    if book:
        where += " AND ch.book_id = ?"
        args.append(book)
    with db() as c:
        if book:
            book_or_404(c, book)
        rows = c.execute(
            f"""SELECT b.*, ch.start_line, snippet(chunks, 2, '[', ']', ' … ', 24) AS snip
               FROM chunks ch JOIN books b ON b.id = ch.book_id
               WHERE {where} ORDER BY bm25(chunks), b.grade LIMIT ?""", args + [limit]).fetchall()
    if compact:   # each book's metadata once, then short hits: far fewer tokens for the reader
        return {"books": {r["id"]: meta(r) for r in rows},
                "hits": [{"id": r["id"], "start_line": r["start_line"], "snippet": r["snip"]} for r in rows]}
    return [{**meta(r), "start_line": r["start_line"], "snippet": r["snip"]} for r in rows]

@app.get("/grep/{bid}", dependencies=[Depends(auth)])
def grep(bid: str, q: str = Query(min_length=2, max_length=200), limit: int = Query(20, ge=1, le=100)):
    """Lines of one book containing q (case-insensitive substring), e.g. "Definition 8.3.5" or "Theorem 6.2.10"."""
    with db() as c:
        b = book_or_404(c, bid)
    needle, out = q.lower(), []
    for i, line in enumerate((MD_ROOT / b["md_path"]).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if needle in line.lower():
            out.append({"line": i, "text": line.strip()[:240]})
            if len(out) >= limit:
                break
    return {**meta(b), "matches": out}

@app.get("/read/{bid}", dependencies=[Depends(auth)])
def read(bid: str, start: int = Query(1, ge=1), n: int = Query(80, ge=1, le=MAX_LINES)):
    with db() as c:
        b = book_or_404(c, bid)
    lines = (MD_ROOT / b["md_path"]).read_text(encoding="utf-8", errors="replace").splitlines()
    return {**meta(b), "start": start, "end": min(start + n - 1, len(lines)), "text": "\n".join(lines[start - 1:start - 1 + n])}

@app.get("/toc/{bid}", dependencies=[Depends(auth)])
def toc(bid: str):
    with db() as c:
        b = book_or_404(c, bid)
    lines = (MD_ROOT / b["md_path"]).read_text(encoding="utf-8", errors="replace").splitlines()
    heads = [{"line": i, "heading": l.strip()} for i, l in enumerate(lines, 1) if re.match(r"#{1,3}\s+\S", l)]
    return {**meta(b), "toc": heads[:500]}

@app.get("/book/{bid}", dependencies=[Depends(auth)])
def book(bid: str):
    with db() as c:
        return meta(book_or_404(c, bid))

@app.get("/books", dependencies=[Depends(auth)])
def books(q: str = Query(min_length=2, max_length=200), limit: int = Query(10, ge=1, le=30)):
    terms = [t.lower() for t in re.findall(r"\w+", q)]
    if not terms:
        raise HTTPException(400, "empty query")
    where = " AND ".join("lower(title) LIKE ?" for _ in terms)
    with db() as c:
        rows = c.execute(f"SELECT * FROM books WHERE {where} ORDER BY grade LIMIT ?",
                         [f"%{t}%" for t in terms] + [limit]).fetchall()
    return [meta(r) for r in rows]

@app.get("/catalog", dependencies=[Depends(auth)])
def catalog():
    with db() as c:
        return [[r["id"], r["grade"], r["title"]] for r in c.execute("SELECT id, grade, title FROM books ORDER BY title")]
