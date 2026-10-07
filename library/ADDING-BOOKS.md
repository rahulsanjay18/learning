# Adding books to the library (steps on your server)

*Written 2026-10-06. After these steps, run `/new-books` in a Claude session: it ticks off requests and updates the course lists.*

Your paths (2026-10-07): originals in `"/media/rahul/Drive 2/Library/Library"`, converted Markdown in
`"/media/rahul/Drive 2/Library/Markdown_Library"` (quote them: the drive name has a space). Repo assumed at `~/Documents/learning`,
compose file in `~/Documents`. Note the flag names differ: `reconvert.py` takes `--books-root`, `grade_library.py` takes `--src-root`.

1. **Put the files** (PDF/EPUB/…) in the originals folder, in a sensible category folder.
2. **Convert to Markdown** into the Markdown folder (same folder structure). The tools `scripts/reconvert.py` uses:
   EPUB → `pandoc book.epub -t gfm -o book.md`; PDF → `marker_single book.pdf --output_dir …` (handles OCR and LaTeX).
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
