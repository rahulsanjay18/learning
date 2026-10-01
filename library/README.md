# Library usage contract (for /teach and any other skill)

Any skill that uses this library MUST follow these rules. They exist so a bad PDF conversion
can never silently become something I learn.

## Files
- `MANIFEST.csv` — every converted book: id, grade, flags, category, title, source format, quality stats.
- `toc/<id>.md` — headings only. Safe to use for every non-F book.
- `text/<id>.md` — full text, only for books copied in (grades A/B).
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
