#!/usr/bin/env python3
"""Add new books to the library in one go (run on the server that holds the books).

  python3 scripts/add_books.py            # pull, convert new books, grade, index, rebuild servers, commit + push
  python3 scripts/add_books.py --dry-run  # just list what would be converted

Steps:
  1. git pull this repo
  2. convert every book in BOOKS_ROOT with no Markdown in MD_ROOT yet, with the crash-safe converter (scripts/safe_convert.py):
     triage first (skips encrypted/damaged files, files over --max-mb, PDFs over --max-pages; EPUBs: no size or page limit),
     light engines only by default (text PDFs, EPUB, AZW3/MOBI, HTML, DOCX, TXT; scanned PDFs and DjVu only with --allow-ocr/--pdf),
     and a watchdog that kills a converter on low system RAM, high converter RAM or timeout (killed books go on
     library/DANGEROUS.csv and are skipped unless --retry-dangerous). Heat only pauses: it waits for the CPU to cool before
     each book, and a book stopped for heat is retried next run, never blacklisted
  3. grade all Markdown -> library/MANIFEST.csv + library/toc/ (scripts/grade_library.py)
  4. rebuild the search index at the db path your compose file mounts for book-server (book-server/build_index.py)
  5. docker compose up -d --build book-server progress-server
  6. commit + push library/
Then run /new-books in a Claude session.
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

try:
    import tqdm, psutil  # noqa: F401  (used by the step modules)
except ImportError as e:
    sys.exit(f"needs {e.name}: pip install tqdm psutil pymupdf4llm   (or: sudo apt install python3-{e.name})")

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "book-server")]
import safe_convert, grade_library, build_index  # noqa: E402

COMPOSE_DIR = Path.home() / "Documents"
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


def compose_builds(compose_file, compose_dir, services=("book-server", "progress-server")):
    """{service: resolved host path of its `build:` context} for the given services (missing ones left out)."""
    out, svc, indent = {}, None, 0
    for line in compose_file.read_text().splitlines():
        m = re.match(r"^(\s*)([\w.-]+):\s*$", line)
        if m and m.group(2) in services:
            svc, indent = m.group(2), len(m.group(1)); continue
        if svc and line.strip() and not line.strip().startswith("#") and len(line) - len(line.lstrip()) <= indent:
            svc = None
        b = re.match(r"^\s*build:\s*[\"']?([^\"'#\s]+)", line) if svc else None
        if b:
            path = Path(b.group(1)).expanduser()
            out[svc] = path if path.is_absolute() else (compose_dir / path).resolve()
    return out


def check_builds(compose_file, compose_dir):
    """Warn when compose builds a server from somewhere other than this repo: then `git pull` never reaches it."""
    bad = 0
    for svc, path in compose_builds(compose_file, compose_dir).items():
        if path.resolve() != (REPO / svc).resolve():
            bad += 1
            print(f"WARNING: {compose_file} builds {svc} from {path}, not {REPO / svc}: pulled code never reaches it. "
                  f"Set `build: {os.path.relpath(REPO / svc, compose_dir)}` there.")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    safe_convert.add_args(ap)  # the conversion flags, same as running safe_convert.py on its own
    ap.set_defaults(source="new")  # new books, not the RECONVERT.csv retry list (--source csv for that)
    ap.add_argument("--compose-dir", type=Path, default=COMPOSE_DIR)
    ap.add_argument("--db", type=Path, help="index path (default: the host path compose mounts at /data, + books.db)")
    ap.add_argument("--dry-run", action="store_true", help="list what would be converted, change nothing")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--no-docker", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args()

    compose_file, data_dir, md_mount = compose_mounts(a.compose_dir)
    db = a.db or (data_dir / "books.db" if data_dir else REPO / "book-server" / "data" / "books.db")
    if compose_file:
        check_builds(compose_file, a.compose_dir)
    if md_mount and md_mount.resolve() != a.md_root.resolve():
        print(f"WARNING: {compose_file} mounts {md_mount} as /books_md, not {a.md_root}: the server won't see new books")

    if not a.no_pull and not a.dry_run:
        step(1, "git pull")
        r = sh(["git", "pull", "--ff-only"])
        print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 and r.stdout.strip() else "pull failed; continuing with local copy")

    step(2, "convert new books")
    log = safe_convert.run(a, dry=a.dry_run)
    if a.dry_run:
        print("\ndry run: nothing changed")
        return
    ok = sum(x[1] == "ok" for x in log)

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
