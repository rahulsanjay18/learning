# Book access I have (by SOURCE, not by title)

> This file is guidance, not a restriction. What Claude can technically reach is set by the
> cloud environment's network access level. General web research is unaffected by this file.

My catalog of accessible books is too large to list. So this file lists the *places* I can get books
and how to check each one. Claude never needs a title list.

## How to use this file (for any skill)
1. Pick books on merit first (web research, RESOURCES-FORMAT.md rules). Don't pick a worse book just because I can get it.
2. For each book, check sources in the order below. Stop at the first hit.
3. In RESOURCES.md, mark the book `(in collection)`, `(via <source>)`, or `(check: <link>)`.
4. If a source needs a login you can't do, don't guess. Give me the ready-made search link,
   marked `(check: …)`, and I'll tap it.
5. You have no text from any of these sources. Recommend chapters only from a public table of contents
   (publisher page, Open Library), never from memory.

## Sources, in priority order
| # | Source | How to check | Login? |
|---|--------|--------------|--------|
| 1 | My collection | grep `library/MANIFEST.csv` and `library/LIBRARY.md` | no |
| 2 | <e.g. library app> | <search URL with {q}, e.g. https://example.org/search?q={q}> | yes, give me the link |
| 3 | <e.g. subscription through work/school> | <search URL with {q}> | yes, give me the link |
| 3b | **Pages behind a login, fetched by the learner** (Blind, paywalled articles, course portals) | Ask: add a `todo.json` item with the URL and what you need; the learner saves it to `inbox/` (`inbox/README.md`). Claude never gets the account | the learner logs in |
| 4 | Open Library (metadata, ISBNs, borrowable e-books) | `https://openlibrary.org/search.json?q={q}&fields=key,title,author_name,isbn,ebook_access&limit=5` | no |

Notes:
- `{q}` = URL-encoded "title author".
- Open Library needs `openlibrary.org` in the cloud environment's allowed domains (Custom network access).
