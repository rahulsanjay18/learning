# Adding books to the library (steps on your server)

*Written 2026-10-06. After these steps, run `/new-books` in a Claude session: it ticks off requests and updates the course lists.*

Paths below assume the repo is at `~/Documents/learning`, originals in `~/Books`, converted Markdown in `~/BooksMD`, and the
compose file in `~/Documents`. Adjust if yours differ.

1. **Put the files** (PDF/EPUB/…) in `~/Books`, in a sensible category folder.
2. **Convert to Markdown** into `~/BooksMD` (same folder structure). The tools `scripts/reconvert.py` uses:
   EPUB → `pandoc book.epub -t gfm -o book.md`; PDF → `marker_single book.pdf --output_dir …` (handles OCR and LaTeX).
   Or put them in `library/RECONVERT.csv` and run `python3 scripts/reconvert.py` (dry run), then `--run`.
3. **Grade** (rewrites `library/MANIFEST.csv` and `library/toc/`):
   `cd ~/Documents/learning && python3 scripts/grade_library.py --md-root ~/BooksMD --src-root ~/Books`
4. **Rebuild the search index and restart the book server:**
   `cd ~/Documents/learning/book-server && python3 build_index.py --manifest ../library/MANIFEST.csv --md-root ~/BooksMD --db data/books.db`
   then `cd ~/Documents && docker compose restart book-server` (use the db path your compose file mounts).
5. **Commit and push** the catalog: `cd ~/Documents/learning && git add library && git commit -m "library: new books" && git push`.
6. In a Claude session: `/new-books`.
