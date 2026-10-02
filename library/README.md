# Library usage contract (for /teach and any other skill)

Any skill that uses this library MUST follow these rules. They exist so a bad PDF conversion
can never silently become something I learn.

## Files
- `MANIFEST.csv` — every converted book: id, grade, flags, category, title, source format, quality stats.
- `toc/<id>.md` — headings only. Safe to use for every non-F book.
- Full text is NOT in this repo. It's served by my book server (see "Book server" below), A/B grades only.
- `LIBRARY.md` — books in my collection with no usable text (unconverted, physical, etc.).
- `ACCESS.md` — the SOURCES I can get books from, and how to check each one.
- `RECONVERT.csv` — books whose conversion failed, with the fix to try.

## What each grade allows
| Grade | Teach prose from it | Quote it | Equations / figures / tables / code from it |
|---|---|---|---|
| A | yes | yes, short | yes, but re-check any equation you reuse |
| B | yes | prose only | NEVER. Point me to the section/page in my original copy instead |
| C | no | no | no. Use `toc/` only, to tell me which chapter to read |
| F | no | no | no. Treat as "available, unreadable": recommend the book, not its text |

## Rules
1. Look up a book's grade in MANIFEST.csv before opening its text. If you are unsure, treat it as one grade worse.
2. Never read a whole text file. `grep -n -i` for the concept, read nearby lines only.
3. If text looks wrong (broken symbols, `(cid:..)`, missing figure, an equation split over lines), stop using that
   passage, tell me, and add a line to `QUALITY-NOTES.md` (`<id> | <section> | what was wrong`).
4. Every equation that appears in a lesson must come from an A-grade source, a cited high-trust web source,
   or be derived in the lesson. When possible, sanity-check it with code (e.g. sympy) before showing it.
5. Prefer books from my collection or sources as the "primary source" of a lesson, but always cite the original book, never the conversion.

## Book server (full text, on demand)
Base URL: the `BOOKS_URL` environment variable (set on the cloud environment). If it's empty, load it from
the `BOOKS_URL=` line in /CLAUDE.md first:

    export BOOKS_URL="${BOOKS_URL:-$(grep -m1 '^BOOKS_URL=' "$CLAUDE_PROJECT_DIR/CLAUDE.md" | cut -d= -f2-)}"

Authentication is attached automatically by the environment; never ask for or print a token.

    curl -s "$BOOKS_URL/books?q=sutton+barto"                 # is a specific book on the server?
    curl -s "$BOOKS_URL/search?q=policy+gradient&limit=10"   # passages: id, title, grade, start_line, snippet
    curl -s "$BOOKS_URL/toc/<id>"                             # headings with line numbers
    curl -s "$BOOKS_URL/read/<id>?start=120&n=80"             # max 200 lines per call

- Web research stays the primary way to find resources (as the /teach skill says). Books are an EXTRA resource. Search when a lesson topic might be covered; if nothing relevant comes back, move on.
- Every response carries the book's grade. Grade B responses include a warning: obey it.
- Read the smallest slice that answers the question. Don't page through whole books.
- If a call returns `upstream request failed` (502), retry once after a few seconds. If it fails again, carry on without the server and say so once.

## Asking for a book
When research turns up a book that would clearly help and `/books?q=` doesn't find it on the server
(or it's there but graded C/F), don't stop. Append one line to `library/WANTED.md`:

    - _Title_ — Author — for: <topic/lesson> — why: <one line> — status: missing | needs reconversion (<id>)

Commit it with the lesson, and mention it to me once at the end of the session. Never try to obtain the book yourself.
Keep teaching from other sources in the meantime.
