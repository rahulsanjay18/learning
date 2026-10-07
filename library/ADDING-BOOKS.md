# Adding books to the library (steps on your server)

*Written 2026-10-06. After these steps, run `/new-books` in a Claude session: it ticks off requests and updates the course lists.*

Your paths (2026-10-07): originals in `"/media/rahul/Drive 2/Library/Library"`, converted Markdown in
`"/media/rahul/Drive 2/Library/Markdown_Library"` (quote them: the drive name has a space). Repo assumed at `~/Documents/learning`,
compose file in `~/Documents`. Note the flag names differ: `reconvert.py` takes `--books-root`, `grade_library.py` takes `--src-root`.

**One command (2026-10-07):** put the files in the originals folder, then on the server:

```bash
cd ~/Documents/learning && python3 scripts/add_books.py
```

It pulls the repo, converts every book with no Markdown yet, grades, rebuilds the index (at the path your compose file mounts
for book-server), rebuilds book-server and progress-server, and commits + pushes `library/`, with progress bars. Your paths
are its defaults. PDFs are checked first: one whose text layer grades A (clean prose) is converted from that layer
with no OCR; scans and math-heavy PDFs are listed with their grade and left for `--pdf`. Options: `--dry-run` (list only),
`--pdf` (also the hard ones and DjVu, via marker: OCR, slow; off by default),
`--retry-failed`, `--limit N`, `--only epub`, `--no-docker`, `--no-commit`, `--no-pull`. Needs `tqdm`; `pymupdf4llm` is recommended for PDFs (keeps headings; without it, poppler's `pdftotext` is used):
`pip install tqdm pymupdf4llm`.
Then run `/new-books` in a Claude session.

**One code path.** `add_books.py` only strings the modules together; each step is also a script you can run alone, with the
same flags and the same defaults (your paths live in `scripts/library_paths.py`; override with `LIB_BOOKS_ROOT` / `LIB_MD_ROOT`):

| Step | Alone | Function `add_books.py` calls |
|---|---|---|
| Convert | `python3 scripts/reconvert.py` (dry run), `--run` | `reconvert.run()` (flags from `reconvert.add_args()`) |
| Grade | `python3 scripts/grade_library.py` | `grade_library.grade_all()` |
| Index | `python3 book-server/build_index.py --manifest library/MANIFEST.csv --md-root … --db …` | `build_index.build()` |

Change a step in its module and both ways of running it get the change.

## Server setup notes
- Rebuild servers after code changes: `cd ~/Documents && docker compose up -d --build book-server progress-server`.
- Use the db path your compose file mounts for book-server (`add_books.py` reads it from the compose file).
