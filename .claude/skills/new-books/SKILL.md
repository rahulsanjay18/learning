---
name: new-books
description: After the learner adds books to their library, find what's new, which requests it fills, and update the books-needed lists and course sources. Also gives the server-side steps. Use when the learner says they added, downloaded or bought books.
argument-hint: "[optional: which books]"
---

# /new-books

The books live on the learner's server; this session sees only `library/MANIFEST.csv` (and the book server). The server-side
steps are in `library/ADDING-BOOKS.md`. If MANIFEST.csv has no new rows after `git pull`, run `python3 scripts/books.py new`
(one `/catalog` call): books can be indexed on the server before the manifest is committed. If that finds none either, give them
ADDING-BOOKS.md's steps and stop. **Never enumerate the server by looping over `/books?q=`**: it took the server down on 2026-10-06.

1. `git pull`, then `python3 scripts/new_books.py` (compares MANIFEST.csv with its previous version; `--since <ref>` for older).
   It lists new and regraded books and the requests each one appears to fill.
2. **Check each match** (title-word matching can misfire): `python3 scripts/books.py find "<title>"` confirms it's served, and
   the grade decides use (library/README.md: A teach freely; B prose only; C/F not usable, add to `library/RECONVERT.csv`).
3. **Update the lists:**
   - `library/WANTED.md`: change the line's `status:` to `got (<id>, grade X, <date>)`.
   - `topics/*/curriculum.json` `source`: replace "(to buy)" / "(free…)" with "(in collection, <grade>, id <id>)".
   - `topics/*/PROGRAM.md` "Books needed": move the book out of the list (keep the list honest).
   - The topic's `RESOURCES.md` if it lists the book.
4. If a new book is better than a course's current spine, say so in one line and propose the swap (don't just do it).
5. `python3 scripts/test_programs.py`, commit (`library: <n> new books`), push, and tell the learner in 3–5 lines: what's usable
   now, what's still missing (top 3 by how soon a course needs it), anything that needs reconversion.
