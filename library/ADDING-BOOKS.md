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

**The individual steps** (what the script does, if you need one by hand):

1. **Put the files** (PDF/EPUB/…) in the originals folder, in a sensible category folder.
2. **Convert to Markdown** into the Markdown folder (same folder structure). The tools `scripts/reconvert.py` uses:
   EPUB → `pandoc book.epub -t gfm -o book.md`; PDF → `marker_single book.pdf --output_dir …` (handles OCR and LaTeX).
   Easiest: `--new` converts every book that has no Markdown yet (point both roots at one subfolder to limit it):
   `python3 scripts/reconvert.py --books-root "…/Library/<folder>" --md-root "…/Markdown_Library/<folder>" --new --run`.
   Or put them in `library/RECONVERT.csv` and run
   `python3 scripts/reconvert.py --books-root "/media/rahul/Drive 2/Library/Library" --md-root "/media/rahul/Drive 2/Library/Markdown_Library"`
   (dry run), then the same with `--run`.
3. **Grade** (rewrites `library/MANIFEST.csv` and `library/toc/`):
   `cd ~/Documents/learning && python3 scripts/grade_library.py --md-root "/media/rahul/Drive 2/Library/Markdown_Library" --src-root "/media/rahul/Drive 2/Library/Library"`
4. **Rebuild the search index and restart the book server:**
   `cd ~/Documents/learning/book-server && python3 build_index.py --manifest ../library/MANIFEST.csv --md-root "/media/rahul/Drive 2/Library/Markdown_Library" --db data/books.db`
   then `cd ~/Documents && docker compose up -d --build book-server` (`--build` also picks up new server code) (use the db path your compose file mounts).
5. **Commit and push** the catalog: `cd ~/Documents/learning && git add library && git commit -m "library: new books" && git push`.
6. In a Claude session: `/new-books`.
