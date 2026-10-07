# Should we crop equations and OCR them to LaTeX?

*Written 2026-10-07. Follow-up to `notes/math-books-strategy.md`.*

## Short answer
Yes, the idea is sound. It's the standard pipeline: find the equation regions, crop them, and run a small image-to-LaTeX model on each crop. **`marker` (our reconverter) already does this** [1][2]. So the question isn't "should we build it". It's why it still fails on our B-grade math books, and what to do about that.

## What the pipeline looks like (and who already does it)
1. **Layout detection.** A detector labels page regions as text, title, formula, table or figure.
2. **Crop.** Each formula box is cut out as a small image.
3. **Formula recognition.** An encoder–decoder model reads the crop and outputs LaTeX.
4. **Reassemble** the LaTeX into Markdown at the right spot.

| Tool | Detector → recognizer | Notes |
|---|---|---|
| `marker` (we use it) | surya layout → texify | `--use_llm` lets an LLM fix inline math and tables; `--redo_inline_math` goes further [2] |
| MinerU | layout model → **UniMERNet** | UniMERNet is reported to be close to Mathpix [3][4] |
| PaddleOCR formula pipeline | layout → formula model | same idea [5] |
| pix2tex / Nougat / Mathpix | recognizer only, or whole page | Mathpix is commercial |

## Why it still goes wrong (where the errors come from)
- **Detection misses.** Inline math like `$\hat\beta$` sits inside a text line. If the detector doesn't box it, it ends up as garbled text. That's most of what makes our books grade B.
- **Crop boundaries.** Multi-line `align` blocks, equation numbers, and matrices that get split across two boxes.
- **Silent, plausible errors.** This is the important one. A recognizer can output valid LaTeX that is *wrong*, for example a dropped subscript, `\le` read as `<`, or a transposed index. The result looks fine, so nothing flags it. That breaks the library rule: "a bad conversion can never silently become something I learn" [6].

## How to catch errors: render it back and compare
Render the LaTeX it produced back into an image, then compare that image with the original crop. That's the idea behind the CDM metric (Character Detection Matching), proposed because string-match scores misjudge formula OCR [7]. A cheap version: render with matplotlib mathtext or KaTeX, normalize both images, and flag crops with low pixel or character overlap for a human or Claude to look at.

## Recommendation for this repo
1. **Don't batch-OCR the whole library up front.** There are 485 B-grade books (from `library/MANIFEST.csv`), and most of their equations will never be used in a lesson.
2. **On demand is cheaper and safer:** build the page-image endpoint from `math-books-strategy.md`. I find the page by text search, read the equation from the image, retype it in LaTeX, and check it with sympy. I'm a strong formula reader, and I see the context around it (what $n$ means, the equation number).
3. **Batch only for the few math books we lean on heavily** (e.g. the Casella & Berger–style stats core): rerun `marker` with `--use_llm --redo_inline_math` [2], or try MinerU [3]. Add the render-and-compare check. Promote a book from B to A only if a spot-check of ~20 equations passes.

## Sources
1. `scripts/reconvert.py` (this repo), line 7: "pdf -> marker_single (does its own OCR on scanned pages; LaTeX for equations)".
2. marker README: https://github.com/jazzido/marker (mirror; flags `--use_llm`, `--redo_inline_math`; texify for equations), also https://fossies.org/linux/marker/README.md
3. Wang et al., *MinerU: An Open-Source Solution for Precise Document Content Extraction*, arXiv:2409.18839: https://arxiv.org/pdf/2409.18839
4. PDF-Extract-Kit, formula recognition docs: https://pdf-extract-kit.readthedocs.io/en/latest/algorithm/formula_recognition.html
5. PaddleOCR formula recognition pipeline: https://www.paddleocr.ai/v3.0.0/en/version3.x/pipeline_usage/formula_recognition.html
6. `library/README.md` (this repo), opening paragraph and grade table.
7. Wang et al., *CDM: A Reliable Metric for Fair and Accurate Formula Recognition Evaluation*, arXiv:2409.03643 (from memory, not re-checked this session).
