#!/usr/bin/env python3
"""
fetch_missing_epubs.py

For every book in LIBRARY_DIR that isn't already an EPUB (and has no .epub of
the same name), search Project Gutenberg (public domain) via the Gutendex API
and download the EPUB if there's a confident match. Anything not found is
skipped and listed in not_found.txt.

Usage:
    pip install requests
    python fetch_missing_epubs.py --library ./Library --out ./Downloaded_EPUBs [--dry-run]

Options:
    --markdown DIR     also skip books that already have a .md in DIR
    --max-downloads N  max simultaneous downloads (default 3); searching is not limited
"""

import argparse
import re
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path

import requests

DEFAULT_LIBRARY_PATH = Path("/media/rahul/Drive\ 2/Library/Library/")
DEFAULT_MD_LIBRARY_PATH = Path("/media/rahul/Drive\ 2/Library/Markdown_Library/")
 
GUTENDEX_URL = "https://gutendex.com/books/"
EPUB_MIME = "application/epub+zip"
MIN_MATCH_SCORE = 0.6       # title similarity threshold (0-1)
REQUEST_DELAY_S = 1.0       # be polite to the free API
TIMEOUT_S = 60              # Gutendex can be slow
USER_AGENT = "fetch-missing-epubs/4.0"

BOOK_EXTS = {".pdf", ".mobi", ".azw", ".azw3", ".kfx", ".txt", ".rtf", ".docx",
             ".odt", ".html", ".htm", ".fb2", ".djvu", ".lit", ".pdb", ".cbz", ".cbr"}

_local = threading.local()
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def normalize(name: str) -> str:
    """Lowercase, strip accents/punctuation/extra whitespace for comparison."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[_\-]+", " ", name.lower())
    name = re.sub(r"[^\w\s]", "", name)
    return re.sub(r"\s+", " ", name).strip()


def files_in(folder: Path):
    return (p for p in folder.rglob("*") if p.is_file() and not p.name.startswith("."))


def find_non_epubs(library: Path, out: Path, markdown: Path | None) -> list[Path]:
    """Non-EPUB books in library with no EPUB (in library or out) of the same name."""
    skip = {normalize(p.stem) for d in (library, out) if d.is_dir()
            for p in files_in(d) if p.suffix.lower() == ".epub"}
    if markdown:
        skip |= {normalize(p.stem) for p in files_in(markdown)}

    todo, seen = [], set()
    for p in sorted(files_in(library)):
        key = normalize(p.stem)
        if p.suffix.lower() in BOOK_EXTS and key not in skip and key not in seen:
            seen.add(key)       # if both foo.pdf and foo.mobi exist, handle once
            todo.append(p)
    return todo


def search_libgen(query: str, session: requests.Session) -> dict | None:
    """Return the best-matching Gutendex book that has an EPUB, or None."""
    resp = session.get(GUTENDEX_URL, params={"search": query}, timeout=TIMEOUT_S)
    resp.raise_for_status()
    results = [b for b in resp.json().get("results", []) if EPUB_MIME in b.get("formats", {})]
    if not results:
        return None

    q = normalize(query)

    def score(book: dict) -> float:
        title = normalize(book.get("title", ""))
        authors = " ".join(normalize(a.get("name", "")) for a in book.get("authors", []))
        return max(SequenceMatcher(None, q, title).ratio(),
                   SequenceMatcher(None, q, f"{title} {authors}").ratio(),
                   SequenceMatcher(None, q, f"{authors} {title}").ratio())

    best = max(results, key=score)
    return best if score(best) >= MIN_MATCH_SCORE else None


def thread_session() -> requests.Session:
    """requests.Session isn't guaranteed thread-safe, so one per worker thread."""
    if not hasattr(_local, "session"):
        _local.session = requests.Session()
        _local.session.headers["User-Agent"] = USER_AGENT
    return _local.session


def download(url: str, dest: Path, session: requests.Session) -> None:
    tmp = dest.with_suffix(".part")
    with session.get(url, stream=True, timeout=TIMEOUT_S) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
    tmp.rename(dest)


def download_job(src: Path, dest: Path, url: str) -> bool:
    """Runs in the worker pool (max N at once). Returns True on success."""
    try:
        download(url, dest, thread_session())
        log(f"    [done] {src.name} -> {dest.name}")
        return True
    except requests.RequestException as e:
        log(f"    [fail] {src.name}: download failed ({e})")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--library", type=Path, default=DEFAULT_LIBRARY_PATH)
    ap.add_argument("--out", type=Path, default=DEFAULT_LIBRARY_PATH.parent / Path("Downloaded_EPUBs"))
    ap.add_argument("--markdown", type=Path, default=DEFAULT_MD_LIBRARY_PATH)
    ap.add_argument("--max-downloads", type=int, default=3,
                    help="max simultaneous downloads (default 3)")
    ap.add_argument("--dry-run", action="store_true", help="show matches without downloading")
    args = ap.parse_args()

    if not args.library.is_dir():
        print(f"Error: {args.library} is not a directory", file=sys.stderr)
        return 1

    todo = find_non_epubs(args.library, args.out, args.markdown)
    log(f"{len(todo)} non-EPUB book(s) without an EPUB version.\n")
    if not todo:
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    not_found: list[str] = []
    search_session = requests.Session()
    search_session.headers["User-Agent"] = USER_AGENT

    # Searches run here in the main thread; downloads go to a pool capped at
    # max_downloads workers, so at most that many run at once.
    with ThreadPoolExecutor(max_workers=max(1, args.max_downloads)) as pool:
        futures = {}
        for i, src in enumerate(todo, 1):
            log(f"[{i}/{len(todo)}] {src.name}")
            try:
                book = search_libgen(src.stem, search_session)
            except requests.RequestException as e:
                log(f"    search failed ({e}); skipping")
                book = None
            time.sleep(REQUEST_DELAY_S)

            if not book:
                log("    not found; skipping")
                not_found.append(str(src))
                continue

            authors = ", ".join(a["name"] for a in book.get("authors", [])) or "Unknown"
            log(f"    match: #{book['id']} '{book['title']}' by {authors}")
            if not args.dry_run:
                dest = args.out / f"{src.stem}.epub"
                futures[pool.submit(download_job, src, dest, book["formats"][EPUB_MIME])] = src
                log("    queued")

        for fut in as_completed(futures):
            src = futures[fut]
            try:
                ok = fut.result()
            except Exception as e:  # don't let one bad file kill the run
                log(f"    [fail] {src.name}: {e}")
                ok = False
            if not ok:
                not_found.append(str(src))

    if not_found:
        report = args.out / "not_found.txt"
        report.write_text("\n".join(not_found) + "\n", encoding="utf-8")
        log(f"\n{len(not_found)} book(s) skipped; listed in {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
