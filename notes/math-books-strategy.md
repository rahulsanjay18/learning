# Math & physics books when PDFs won't convert

*Written 2026-10-05. Problem: equation-heavy PDFs come out broken, even through `marker`, so those books grade B/C and lessons can't take equations from them.*

## TL;DR
1. **Stop fighting conversion for equations: let me read the page itself.** I can read page *images* directly. If the book server can return one rendered page of the original PDF, the workflow becomes: search the text to find the page, look at the page image, transcribe the equation, then check it with sympy. Text conversion is then only for *finding* things, which already works.
2. **When getting new books, prefer formats that carry the math:** EPUB3 (equations as MathML), HTML textbooks (equations as LaTeX in the page), or LaTeX source.
3. **Use open sources that come with LaTeX:** arXiv lecture notes (source downloadable) and LibreTexts.

---

## 1. Page-image endpoint (recommended)

**Why it works:** the `marker` reconversion step already tries to turn equations into LaTeX [1]. Where it fails, the *original page* is still correct. Reading the original avoids the error-prone conversion altogether.

**Server change (small):**
- Mount the original PDFs read-only next to the converted Markdown. Today the server only mounts the Markdown folder (`BOOKS_MD_ROOT`) [2].
- Add `GET /page/{id}/{n}.png`: render page *n* with PyMuPDF or `pdftoppm`, cap the resolution, cache it. Same token auth as the other endpoints.
- Keep the page-number markers in the text so a search hit maps to a page.

**Cost:** one page image is roughly a thousand or so tokens. It's only used for the specific equation or figure a lesson needs, never for reading whole chapters.

**Rule change needed (your call), in `library/README.md`:**
> B-grade: equations, figures and tables may be taken **from the page image** (never from the converted text). Every equation reused in a lesson is re-typed in LaTeX and checked with sympy or a cited source.

This keeps your safety rule ("a bad conversion can never silently become something I learn" [3]) because nothing comes from the bad conversion any more.

## 2. Getting new books: format checklist
| Format | Equations survive? | Notes |
|---|---|---|
| LaTeX source | perfect | arXiv papers/notes; some authors publish source |
| HTML textbook (LibreTexts, OpenStax web) | very good | equations are LaTeX/MathML in the page |
| EPUB3 with MathML | good | check a sample page; some EPUBs embed equations as images |
| Born-digital PDF | poor via conversion | fine with the page-image route |
| Scanned PDF / DjVu | poor | page-image route only |

## 3. Open sources with clean math
- **Sean Carroll, *Lecture Notes on General Relativity*** (arXiv gr-qc/9712019) [4]. arXiv offers the source files, so equations come straight from LaTeX.
- **LibreTexts** (phys.libretexts.org, math.libretexts.org) [5]: open HTML textbooks across physics, math and statistics.
- **OpenStax** *University Physics* and *Calculus* [6]. You have *Calculus 1–3* as B-grade conversions; the web versions have clean math.

---

## Sources
1. `scripts/reconvert.py` (this repo): "pdf -> marker_single (does its own OCR on scanned pages; LaTeX for equations)".
2. `book-server/app.py` and `book-server/compose.snippet.yml` (this repo): `BOOKS_MD_ROOT`, Markdown-only mount.
3. `library/README.md` (this repo): grade rules and purpose.
4. arXiv gr-qc/9712019: https://arxiv.org/abs/gr-qc/9712019 ("Lecture Notes on General Relativity").
5. LibreTexts Physics: https://phys.libretexts.org/
6. OpenStax: https://openstax.org/details/books/university-physics-volume-1
