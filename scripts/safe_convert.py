#!/usr/bin/env python3
"""Crash-safe book converter. Replaces reconvert.py for anything risky.

Three layers of protection:
  1. TRIAGE before touching a book (cheap, no ML):
     - skips encrypted / unreadable files, files over --max-mb (EPUBs: --max-mb-epub), PDFs over --max-pages
     - skips scanned PDFs and djvu (they need OCR = heavy ML) unless --allow-ocr
  2. LIGHT ENGINES by default, no GPU, no ML models:
     - text PDFs  -> pymupdf4llm (low memory)
     - epub/azw3/mobi/html/docx/txt -> pandoc / calibre / copy
     - GPU is hidden from every child process (CUDA_VISIBLE_DEVICES="")
  3. WATCHDOG while each book converts (polls every 0.5 s):
     - kills the converter if system free RAM drops below --min-free-gb,
       the converter's own RAM passes --max-rss-gb, or it runs longer than --timeout
     - a killed book goes on library/DANGEROUS.csv and is never retried
       (unless --retry-dangerous); the run pauses --cooldown seconds afterwards
     - the run stops entirely after --max-kills watchdog kills
  4. HEAT is the machine's state, not the book's (all 120 temperature kills up to 2026-10-08 came 0-9 s into a book):
     - before each book, wait until the CPU is below --max-temp-c
     - a converter is stopped only after --hot-seconds above it; that book is logged "hot",
       NOT put on DANGEROUS.csv and not counted as a kill, and is tried again next run
     - AMD: reads Tdie/Tccd when present, not Tctl (k10temp's Tctl is a fan-control scale, not a temperature)

Usage:
  pip install pymupdf4llm psutil
  python3 scripts/safe_convert.py --books-root ~/Books --md-root ~/BooksMD                 # triage report only
  python3 scripts/safe_convert.py --books-root ~/Books --md-root ~/BooksMD --run --limit 5 # small batch
  python3 scripts/safe_convert.py --books-root ~/Books --md-root ~/BooksMD --run           # everything
Then re-run scripts/grade_library.py. Everything is logged to library/SAFE-CONVERT-LOG.csv.
"""
import argparse, csv, os, shutil, signal, subprocess, sys, tempfile, threading, time
from pathlib import Path

import psutil

LIB = Path(__file__).resolve().parent.parent / "library"
GB = 1024 ** 3


# ---------- 1. triage ----------
def triage_pdf_inproc(path, max_pages):
    import pymupdf
    pymupdf.TOOLS.mupdf_display_errors(False)
    try:
        doc = pymupdf.open(path)
    except Exception as e:
        return "skip", f"unreadable: {str(e)[:60]}", 0
    with doc:
        if doc.needs_pass:
            return "skip", "encrypted", 0
        n = doc.page_count
        if n == 0:
            return "skip", "no pages", 0
        if n > max_pages:
            return "skip", f"{n} pages > --max-pages", n
        chars, ok = 0, 0
        for i in sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1}):
            try:
                chars += len(doc[i].get_text("text").strip()); ok += 1
            except Exception:
                pass
        if ok == 0:
            return "skip", "damaged PDF (pages won't load)", n
        chars /= ok
    if ok < 3 and n >= 5:
        return "skip", "damaged PDF (most sampled pages won't load)", n
    if chars < 40:
        return "ocr", f"scanned (~{chars:.0f} chars/page)", n
    return "light", f"text PDF, {n} pages", n


def triage_pdf(path, max_pages, a, env):
    code = ("import sys,json;sys.path.insert(0,sys.argv[3]);import safe_convert as s;"
            "print(json.dumps(s.triage_pdf_inproc(sys.argv[1],int(sys.argv[2]))))")
    status, out = run_watched([sys.executable, "-c", code, str(path), str(max_pages), str(Path(__file__).parent)],
                              a, env, timeout=a.triage_timeout, capture=True)
    if status != "ok":
        return "skip", f"triage {status}: {out}", 0
    import json
    try:
        kind, why, n = json.loads(out.strip().splitlines()[-1])
        return kind, why, n
    except Exception:
        return "skip", "triage gave no result", 0


def plan(src, dest, tmp, a, env):
    ext = src.suffix.lower()
    size_mb = src.stat().st_size / 1e6
    limit, flag = (a.max_mb_epub, "--max-mb-epub") if ext == ".epub" else (a.max_mb, "--max-mb")
    if limit and size_mb > limit:
        return None, f"{size_mb:.0f} MB > {flag}"
    pandoc = lambda s, fmt=None: ["pandoc", "+RTS", f"-M{a.max_rss_gb:g}g", "-RTS", str(s)] + (["-f", fmt] if fmt else []) + [
        "-t", "gfm", "--wrap=none", "-o", str(dest), f"--extract-media={dest.parent / (dest.stem + '_assets')}"]
    if ext == ".pdf":
        kind, why, _ = triage_pdf(src, a.max_pages, a, env)
        if kind == "skip":
            return None, why
        if kind == "ocr" and not a.allow_ocr:
            return None, why + " (needs OCR; rerun with --allow-ocr)"
        if kind == "ocr":
            return [["marker_single", str(src), "--output_dir", str(tmp), "--output_format", "markdown",
                     "--disable_multiprocessing", "--mode", "fast"]], "marker"
        code = ("import pymupdf,pymupdf4llm,sys,pathlib;pymupdf.TOOLS.mupdf_display_errors(False);"
                "pathlib.Path(sys.argv[2]).write_text(pymupdf4llm.to_markdown(sys.argv[1]),encoding='utf-8')")
        return [[sys.executable, "-c", code, str(src), str(dest)]], why
    if ext == ".djvu":
        if not a.allow_ocr:
            return None, "djvu is image-only (needs OCR; rerun with --allow-ocr)"
        pdf = tmp / (src.stem + ".pdf")
        return [["ddjvu", "-format=pdf", str(src), str(pdf)],
                ["marker_single", str(pdf), "--output_dir", str(tmp), "--output_format", "markdown",
                 "--disable_multiprocessing", "--mode", "fast"]], "marker"
    if ext in (".azw3", ".mobi"):
        ep = tmp / (src.stem + ".epub")
        return [["ebook-convert", str(src), str(ep)], pandoc(ep)], "calibre+pandoc"
    if ext == ".epub":
        return [pandoc(src)], "pandoc"
    if ext in (".html", ".htm"):
        return [pandoc(src, "html")], "pandoc"
    if ext == ".docx":
        return [pandoc(src, "docx")], "pandoc"
    if ext == ".txt":
        return [["cp", str(src), str(dest)]], "copy"
    return None, f"unsupported {ext}"


# ---------- 3. watchdog ----------
def cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
    except Exception:
        return None
    vals = []
    for name, ts in temps.items():
        if name not in ("coretemp", "k10temp", "zenpower", "cpu_thermal"):
            continue
        ts = [t for t in ts if t.current]
        if name in ("k10temp", "zenpower"):   # Tctl is a fan-control scale (docs.kernel.org/hwmon/k10temp.html): prefer real die temps
            real = [t for t in ts if t.label.startswith(("Tdie", "Tccd"))]
            ts = real or ts
        elif name == "coretemp":              # package sensor: one steady number instead of the hottest core's spikes
            ts = [t for t in ts if t.label.startswith("Package")] or ts
        vals += [t.current for t in ts]
    return max(vals) if vals else None


def tree_rss(proc):
    try:
        procs = [proc] + proc.children(recursive=True)
    except psutil.Error:
        return 0
    total = 0
    for p in procs:
        try:
            total += p.memory_info().rss
        except psutil.Error:
            pass
    return total


def run_watched(cmd, a, env, timeout=None, capture=False):
    timeout = timeout or a.timeout
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE if capture else subprocess.DEVNULL, stderr=subprocess.PIPE,
                         text=True, env=env, start_new_session=True, preexec_fn=lambda: os.nice(19))
    ps, start, reason = psutil.Process(p.pid), time.time(), None
    err_buf, out_buf, hot_since = [], [], None
    t = threading.Thread(target=lambda: err_buf.append(p.stderr.read()), daemon=True)
    t.start()
    if capture:
        t2 = threading.Thread(target=lambda: out_buf.append(p.stdout.read()), daemon=True)
        t2.start()
    while p.poll() is None:
        avail = psutil.virtual_memory().available / GB
        rss = tree_rss(ps) / GB
        temp = cpu_temp()
        hot_since = (hot_since or time.time()) if temp and temp > a.max_temp_c else None
        status = "killed"
        if avail < a.min_free_gb:
            reason = f"system free RAM {avail:.1f} GB < {a.min_free_gb}"
        elif rss > a.max_rss_gb:
            reason = f"converter RAM {rss:.1f} GB > {a.max_rss_gb}"
        elif hot_since and time.time() - hot_since >= a.hot_seconds:
            status, reason = "hot", f"CPU {temp:.0f}C > {a.max_temp_c:g} for {a.hot_seconds}s"
        elif time.time() - start > timeout:
            reason = f"timeout {timeout}s"
        if reason:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            return status, reason
        time.sleep(0.5)
    t.join(timeout=2)
    if capture:
        t2.join(timeout=2)
    if p.returncode != 0:
        last = ((err_buf[0] if err_buf else "") or "").strip().splitlines()[-1:] or ["failed"]
        return "failed", last[0][:200]
    return "ok", (out_buf[0] if out_buf else "")


def collect_marker(tmp, stem, dest):
    out = tmp / stem
    mds = list(out.glob("*.md")) if out.exists() else []
    if not mds:
        return False
    shutil.move(str(mds[0]), dest)
    rest = list(out.iterdir())
    if rest:
        assets = dest.parent / (dest.stem + "_assets")
        assets.mkdir(exist_ok=True)
        for f in rest:
            shutil.move(str(f), assets / f.name)
    return True


def load_dangerous():
    f = LIB / "DANGEROUS.csv"
    return {r[0] for r in csv.reader(open(f, encoding="utf-8"))} if f.exists() else set()


def add_args(ap):
    """The conversion flags, shared by this script and scripts/add_books.py (paths default to scripts/library_paths.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from library_paths import BOOKS_ROOT, MD_ROOT
    ap.add_argument("--books-root", type=Path, default=BOOKS_ROOT)
    ap.add_argument("--md-root", type=Path, default=MD_ROOT)
    ap.add_argument("--source", choices=["csv", "new"], default="csv",
                    help="csv: library/RECONVERT.csv; new: every book with no Markdown yet. Default: csv run alone, new from add_books.py")
    ap.add_argument("--only", default="", help="extensions, e.g. pdf,epub")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-mb", type=float, default=2048, help="skip files over this many MB (default 2048, above every book in the 2026-10 log; 0 = no limit); EPUBs use --max-mb-epub")
    ap.add_argument("--max-mb-epub", type=float, default=0, help="the same for EPUBs (default 0 = no limit: a slow EPUB ends at "
                    "--timeout; pandoc is still capped at --max-rss-gb and watched, so a big one fails instead of filling RAM)")
    ap.add_argument("--max-pages", type=int, default=1100, help="PDFs only (EPUBs have no page limit)")
    ap.add_argument("--allow-ocr", "--pdf", action="store_true", help="convert scanned PDFs/djvu with marker (CPU only, heavy)")
    ap.add_argument("--min-free-gb", type=float, default=4, help="kill if system free RAM drops below this")
    ap.add_argument("--max-rss-gb", type=float, default=6, help="kill if converter uses more RAM than this")
    ap.add_argument("--max-temp-c", type=float, default=95, help="wait before each book until the CPU is below this")
    ap.add_argument("--hot-seconds", type=int, default=30, help="stop a converter after this long above --max-temp-c (not blacklisted)")
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per converter step")
    ap.add_argument("--triage-timeout", type=int, default=60, help="seconds allowed to inspect one PDF")
    ap.add_argument("--cooldown", type=int, default=60, help="pause after a kill")
    ap.add_argument("--max-kills", type=int, default=5, help="stop the whole run after this many kills")
    ap.add_argument("--retry-dangerous", action="store_true")


def select_rows(a):
    """RECONVERT.csv rows, or (--source new) every book with no Markdown yet, as {"path", "ext"} dicts."""
    if a.source == "new":
        import reconvert
        return reconvert.new_books(a.books_root, a.md_root)
    return list(csv.DictReader(open(LIB / "RECONVERT.csv", encoding="utf-8")))


def run(a, dry=False):
    """Triage and (unless dry) convert. Returns [[path, status, detail], ...] for the books it looked at."""
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", TORCH_DEVICE="cpu",
               OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
    only = {"." + e.strip(". ").lower() for e in a.only.split(",") if e.strip()}
    rows = select_rows(a)
    if only:
        rows = [r for r in rows if r["ext"] in only]
    sz = lambda r: (a.books_root / r["path"].removeprefix("./")).stat().st_size \
        if (a.books_root / r["path"].removeprefix("./")).exists() else 0
    rows.sort(key=sz)
    if a.limit:
        rows = rows[: a.limit]
    dangerous = set() if a.retry_dangerous else load_dangerous()
    log_f = open(LIB / "SAFE-CONVERT-LOG.csv", "a", newline="", encoding="utf-8")
    log = csv.writer(log_f)
    kills, counts, out = 0, {}, []

    from tqdm import tqdm
    bar = tqdm(rows, desc="dry run" if dry else "convert", unit="book")
    for i, r in enumerate(bar, 1):
        rel = Path(r["path"].removeprefix("./"))
        src, dest = a.books_root / rel, (a.md_root / rel).with_suffix(".md")
        bar.set_postfix_str(f"{rel.name[:40]} ({src.stat().st_size / 1e6 if src.exists() else 0:.0f} MB)")
        status, detail = None, ""
        if dest.exists():
            continue
        if not src.exists():
            status, detail = "skipped", "source missing"
        elif str(rel) in dangerous:
            status, detail = "skipped", "on DANGEROUS.csv (killed before)"
        while status is None and psutil.virtual_memory().available / GB < a.min_free_gb + 2:
            bar.write("   waiting: system RAM is low before starting the next book ...")
            time.sleep(30)
        while status is None and (temp := cpu_temp() or 0) > a.max_temp_c:
            bar.write(f"   waiting: CPU {temp:.0f}C > --max-temp-c {a.max_temp_c:g} (if this never ends: check `sensors` at idle)")
            time.sleep(30)
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            if status is None:
                try:
                    cmds, why = plan(src, dest, tmp, a, env)
                except Exception as e:  # one bad book must never stop the run
                    cmds, why = None, f"error during triage: {type(e).__name__}: {str(e)[:80]}"
                if cmds is None:
                    status, detail = "skipped", why
                elif dry:
                    status, detail = "would convert", why
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    for c in cmds:
                        if not shutil.which(c[0]) and c[0] != sys.executable:
                            status, detail = "failed", f"{c[0]} not installed"
                            break
                        status, detail = run_watched(c, a, env)
                        if status == "ok":
                            detail = ""
                        if status != "ok":
                            break
                    if status == "ok" and why == "marker" and not collect_marker(tmp, Path(cmds[-1][1]).stem, dest):
                        status, detail = "failed", "marker produced no markdown"
                    if status != "ok" and dest.exists():
                        dest.unlink()
        if status != "ok":          # finished books just move the bar; everything else gets a line
            bar.write(f"[{i}/{len(rows)}] {status:13} {rel}  {detail}")
        counts[status] = counts.get(status, 0) + 1
        out.append([str(rel), status, detail])
        if not dry:
            log.writerow([time.strftime("%F %T"), str(rel), status, detail])
            log_f.flush()
        if status == "killed":
            kills += 1
            with open(LIB / "DANGEROUS.csv", "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([str(rel), detail])
            if kills >= a.max_kills:
                bar.write(f"STOPPING: {kills} watchdog kills. Check library/DANGEROUS.csv.")
                break
            bar.write(f"   cooling down {a.cooldown}s ...")
            time.sleep(a.cooldown)
        elif status == "hot":
            bar.write(f"   too hot; not blacklisted, tried again next run. cooling down {a.cooldown}s ...")
            time.sleep(a.cooldown)
    log_f.close()
    bar.close()
    print("summary:", dict(sorted(counts.items())))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    add_args(ap)
    ap.add_argument("--run", action="store_true", help="actually convert (default: triage report only)")
    a = ap.parse_args()
    run(a, dry=not a.run)


if __name__ == "__main__":
    main()
