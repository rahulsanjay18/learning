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
for book-server), rebuilds book-server and progress-server, and commits + pushes `library/`. Your paths are its defaults.

**Conversion is crash-safe by default (2026-10-08): step 2 is `scripts/safe_convert.py`**, not `reconvert.py`.
- Triage first: encrypted, damaged and empty files, files over `--max-mb` (100), and PDFs over `--max-pages` (800) are skipped.
- Only light engines run: text PDFs go through pymupdf4llm; EPUB/AZW3/MOBI/HTML/DOCX/TXT go through pandoc, calibre or a plain copy;
  the GPU is hidden. Scanned PDFs and DjVu are skipped unless you pass `--allow-ocr` (alias `--pdf`).
- A watchdog kills a converter when system free RAM drops below `--min-free-gb` (4), when the converter uses more than
  `--max-rss-gb` (6), when the CPU passes `--max-temp-c` (85 °C), or after `--timeout` seconds (1200).
  A killed book goes on `library/DANGEROUS.csv` and is skipped from then on unless you pass `--retry-dangerous`.
  After 5 kills the run stops (`--max-kills`).

Other options: `--dry-run` (triage report only), `--limit N`, `--only epub`, `--source csv` (the `library/RECONVERT.csv`
retry list instead of new books), `--no-docker`, `--no-commit`, `--no-pull`. Needs `pip install tqdm psutil pymupdf4llm`.
Then run `/new-books` in a Claude session.

**One code path.** `add_books.py` only strings the modules together; each step is also a script you can run alone, with the
same flags and the same defaults (your paths live in `scripts/library_paths.py`; override with `LIB_BOOKS_ROOT` / `LIB_MD_ROOT`):

| Step | Alone | Function `add_books.py` calls |
|---|---|---|
| Convert | `python3 scripts/safe_convert.py` (triage only), `--run` (alone it reads RECONVERT.csv; `--source new` for new books) | `safe_convert.run()` (flags from `safe_convert.add_args()`) |
| Grade | `python3 scripts/grade_library.py` | `grade_library.grade_all()` |
| Index | `python3 book-server/build_index.py --manifest library/MANIFEST.csv --md-root … --db …` | `build_index.build()` |

Change a step in its module and both ways of running it get the change.

Stopping a run with Ctrl-C is safe: every finished book keeps its Markdown and its log line, a half-converted book leaves no
partial file, and the next run picks up where this one stopped. Only the later steps (grade, index, rebuild) need the rerun.

## Server setup notes
- Rebuild servers after code changes: `cd ~/Documents && docker compose up -d --build book-server progress-server`.
  **`--build` is what picks up new code**: the code is copied into the image at build time, so `--force-recreate` alone restarts
  the old image. And compose must build from the repo clone (`build: ./learning/book-server`, `./learning/progress-server`),
  not from a copied folder, or `git pull` never reaches the server; `add_books.py` warns if it doesn't.
- Use the db path your compose file mounts for book-server (`add_books.py` reads it from the compose file).
