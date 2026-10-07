#!/usr/bin/env python3
"""Add new books to the library in one go (run on the server that holds the books).

  python3 scripts/add_books.py            # pull, convert new books, grade, index, rebuild servers, commit + push
  python3 scripts/add_books.py --dry-run  # just list what would be converted

Steps:
  1. git pull this repo
  2. convert every book in BOOKS_ROOT with no Markdown in MD_ROOT yet (scripts/reconvert.py). By default only formats
     that convert cleanly without OCR (EPUB, AZW3/MOBI, HTML, DOCX, TXT); add --pdf for PDF/DjVu (marker: OCR, slow).
     Books that already FAILED (library/RECONVERT-LOG.csv) are skipped unless --retry-failed
  3. grade all Markdown -> library/MANIFEST.csv + library/toc/ (scripts/grade_library.py)
  4. rebuild the search index at the db path your compose file mounts for book-server (book-server/build_index.py)
  5. docker compose up -d --build book-server progress-server
  6. commit + push library/
Then run /new-books in a Claude session.
"""
import argparse, csv, re, shutil, subprocess, sys
from pathlib import Path

try:
    import tqdm  # noqa: F401  (used by the step modules)
except ImportError:
    sys.exit("needs tqdm: pip install tqdm   (or: sudo apt install python3-tqdm)")

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "book-server")]
import reconvert, grade_library, build_index  # noqa: E402

BOOKS_ROOT = Path("/media/rahul/Drive 2/Library/Library")
MD_ROOT = Path("/media/rahul/Drive 2/Library/Markdown_Library")
COMPOSE_DIR = Path.home() / "Documents"
EASY = {".epub", ".azw3", ".mobi", ".html", ".htm", ".docx", ".txt"}  # no OCR needed
COMPOSE_FILES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")


def step(n, title):
    print(f"\n== {n}. {title}", flush=True)


def sh(cmd, cwd=REPO, check=True):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if check and r.returncode != 0:
        print((r.stderr or r.stdout).strip())
    return r


def compose_mounts(compose_dir):
    """Host paths the book-server service mounts at /data and /books_md (None if not found)."""
    f = next((compose_dir / n for n in COMPOSE_FILES if (compose_dir / n).exists()), None)
    if not f:
        return None, None, None
    lines, inside, indent, mounts = f.read_text().splitlines(), False, 0, {}
    for line in lines:
        m = re.match(r"^(\s*)book-server:\s*$", line)
        if m:
            inside, indent = True, len(m.group(1)); continue
        if inside and line.strip() and not line.strip().startswith("#") and len(line) - len(line.lstrip()) <= indent:
            break
        v = re.match(r"^\s*-\s*[\"']?([^:\"']+):(/data|/books_md)(:ro)?[\"']?\s*(#.*)?$", line) if inside else None
        if v:
            host = Path(v.group(1)).expanduser()
            mounts[v.group(2)] = host if host.is_absolute() else (compose_dir / host).resolve()
    return f, mounts.get("/data"), mounts.get("/books_md")


def failed_before():
    log = REPO / "library" / "RECONVERT-LOG.csv"
    if not log.exists():
        return set()
    last = {}
    for row in csv.reader(open(log, encoding="utf-8")):
        if len(row) >= 2:
            last[row[0]] = row[1]
    return {p for p, s in last.items() if s == "FAILED"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--books-root", type=Path, default=BOOKS_ROOT)
    ap.add_argument("--md-root", type=Path, default=MD_ROOT)
    ap.add_argument("--compose-dir", type=Path, default=COMPOSE_DIR)
    ap.add_argument("--db", type=Path, help="index path (default: the host path compose mounts at /data, + books.db)")
    ap.add_argument("--only", default="", help="only convert these extensions, e.g. epub,pdf")
    ap.add_argument("--limit", type=int, default=0, help="convert at most N books")
    ap.add_argument("--pdf", action="store_true", help="also convert PDF and DjVu (marker: OCR + LaTeX, slow, needs marker_single)")
    ap.add_argument("--mode", choices=["fast", "balanced"], help="marker mode for --pdf")
    ap.add_argument("--retry-failed", action="store_true", help="also retry books that failed to convert before")
    ap.add_argument("--dry-run", action="store_true", help="list what would be converted, change nothing")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--no-docker", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args()

    for root, name in ((a.books_root, "books root"), (a.md_root, "markdown root")):
        if not root.is_dir():
            sys.exit(f"{name} not found: {root} (is the drive mounted?)")
    tools = {t: bool(shutil.which(t)) for t in reconvert.TOOLS if a.pdf or t not in ("marker_single", "ddjvu")}
    print("converters:", ", ".join(f"{t} {'ok' if ok else 'MISSING'}" for t, ok in tools.items()))

    compose_file, data_dir, md_mount = compose_mounts(a.compose_dir)
    db = a.db or (data_dir / "books.db" if data_dir else REPO / "book-server" / "data" / "books.db")
    if md_mount and md_mount.resolve() != a.md_root.resolve():
        print(f"WARNING: {compose_file} mounts {md_mount} as /books_md, not {a.md_root}: the server won't see new books")

    if not a.no_pull and not a.dry_run:
        step(1, "git pull")
        r = sh(["git", "pull", "--ff-only"])
        print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else "pull failed; continuing with local copy")

    step(2, "convert new books")
    rows = reconvert.new_books(a.books_root, a.md_root)
    skip = set() if a.retry_failed else failed_before()
    rows = [r for r in rows if r["path"] not in skip]
    only = {"." + e.strip(". ").lower() for e in a.only.split(",") if e.strip()}
    if only:
        rows = [r for r in rows if r["ext"] in only]
    hard = [r for r in rows if r["ext"] not in EASY]
    if not a.pdf:
        rows = [r for r in rows if r["ext"] in EASY]
    if a.limit:
        rows = rows[: a.limit]
    if hard and not a.pdf:
        print(f"{len(hard)} PDF/DjVu books need OCR: not converted (add --pdf to include them)")
    print(f"{len(rows)} books to convert" + (f" ({len(skip)} earlier failures skipped; --retry-failed to retry)" if skip else ""))
    log = reconvert.convert_all(rows, a.books_root, a.md_root, a.mode, dry=a.dry_run)
    if a.dry_run:
        print("\ndry run: nothing changed")
        return
    ok = sum(x[1] == "ok" for x in log)
    print(f"converted {ok}/{len(log)}")

    step(3, "grade")
    grade_library.grade_all(a.md_root, a.books_root)

    step(4, f"index -> {db}")
    db.parent.mkdir(parents=True, exist_ok=True)
    build_index.build(REPO / "library" / "MANIFEST.csv", a.md_root, db)

    if not a.no_docker:
        step(5, "rebuild servers")
        if not compose_file:
            print(f"no compose file in {a.compose_dir}; skipped (--compose-dir)")
        else:
            r = sh(["docker", "compose", "up", "-d", "--build", "book-server", "progress-server"], cwd=a.compose_dir)
            print("servers up" if r.returncode == 0 else "docker failed (try with sudo, or --no-docker and run it yourself)")

    if not a.no_commit:
        step(6, "commit + push library/")
        sh(["git", "add", "library"])
        if sh(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0:
            print("library unchanged; nothing to commit")
        else:
            sh(["git", "commit", "-qm", f"library: new books ({ok} converted)"])
            r = sh(["git", "push", "-q"])
            print("pushed" if r.returncode == 0 else "push failed; push by hand")

    print("\nDone. Next: run /new-books in a Claude session.")


if __name__ == "__main__":
    main()
