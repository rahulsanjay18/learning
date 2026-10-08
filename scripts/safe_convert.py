#!/usr/bin/env python3
"""Crash-safe book converter. Replaces reconvert.py for anything risky.

Three layers of protection:
  1. TRIAGE before touching a book (cheap, no ML):
     - skips encrypted / unreadable files, files over --max-mb, PDFs over --max-pages
     - skips scanned PDFs and djvu (they need OCR = heavy ML) unless --allow-ocr
  2. LIGHT ENGINES by default, no GPU, no ML models:
     - text PDFs  -> pymupdf4llm (low memory)
     - epub/azw3/mobi/html/docx/txt -> pandoc / calibre / copy
     - GPU is hidden from every child process (CUDA_VISIBLE_DEVICES="")
  3. WATCHDOG while each book converts (polls every 0.5 s):
     - kills the converter if system free RAM drops below --min-free-gb,
       the converter's own RAM passes --max-rss-gb, CPU temp passes --max-temp-c,
       or it runs longer than --timeout
     - a killed book goes on library/DANGEROUS.csv and is never retried
       (unless --retry-dangerous); the run pauses --cooldown seconds afterwards
     - the run stops entirely after --max-kills watchdog kills

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
    if size_mb > a.max_mb:
        return None, f"{size_mb:.0f} MB > --max-mb"
    pandoc = lambda s, fmt=None: ["pandoc", str(s)] + (["-f", fmt] if fmt else []) + [
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
    vals = [t.current for name, ts in temps.items() if name in ("coretemp", "k10temp", "zenpower", "cpu_thermal")
            for t in ts if t.current]
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
    err_buf, out_buf = [], []
    t = threading.Thread(target=lambda: err_buf.append(p.stderr.read()), daemon=True)
    t.start()
    if capture:
        t2 = threading.Thread(target=lambda: out_buf.append(p.stdout.read()), daemon=True)
        t2.start()
    while p.poll() is None:
        avail = psutil.virtual_memory().available / GB
        rss = tree_rss(ps) / GB
        temp = cpu_temp()
        if avail < a.min_free_gb:
            reason = f"system free RAM {avail:.1f} GB < {a.min_free_gb}"
        elif rss > a.max_rss_gb:
            reason = f"converter RAM {rss:.1f} GB > {a.max_rss_gb}"
        elif temp and temp > a.max_temp_c:
            reason = f"CPU {temp:.0f}C > {a.max_temp_c}"
        elif time.time() - start > timeout:
            reason = f"timeout {timeout}s"
        if reason:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            p.wait()
            return "killed", reason
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--books-root", required=True, type=Path)
    ap.add_argument("--md-root", required=True, type=Path)
    ap.add_argument("--run", action="store_true", help="actually convert (default: triage report only)")
    ap.add_argument("--only", default="", help="extensions, e.g. pdf,epub")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-mb", type=float, default=100)
    ap.add_argument("--max-pages", type=int, default=800)
    ap.add_argument("--allow-ocr", action="store_true", help="convert scanned PDFs/djvu with marker (CPU only, heavy)")
    ap.add_argument("--min-free-gb", type=float, default=4, help="kill if system free RAM drops below this")
    ap.add_argument("--max-rss-gb", type=float, default=6, help="kill if converter uses more RAM than this")
    ap.add_argument("--max-temp-c", type=float, default=85, help="kill if CPU gets hotter than this")
    ap.add_argument("--timeout", type=int, default=1200)
    ap.add_argument("--triage-timeout", type=int, default=60, help="seconds allowed to inspect one PDF")
    ap.add_argument("--cooldown", type=int, default=60, help="pause after a kill")
    ap.add_argument("--max-kills", type=int, default=5, help="stop the whole run after this many kills")
    ap.add_argument("--retry-dangerous", action="store_true")
    a = ap.parse_args()

    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", TORCH_DEVICE="cpu",
               OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
    only = {"." + e.strip(". ").lower() for e in a.only.split(",") if e.strip()}
    rows = list(csv.DictReader(open(LIB / "RECONVERT.csv", encoding="utf-8")))
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
    kills, counts = 0, {}

    for i, r in enumerate(rows, 1):
        rel = Path(r["path"].removeprefix("./"))
        src, dest = a.books_root / rel, (a.md_root / rel).with_suffix(".md")
        status, detail = None, ""
        if dest.exists():
            continue
        if not src.exists():
            status, detail = "skipped", "source missing"
        elif str(rel) in dangerous:
            status, detail = "skipped", "on DANGEROUS.csv (killed before)"
        while status is None and psutil.virtual_memory().available / GB < a.min_free_gb + 2:
            print("   waiting: system RAM is low before starting the next book ...")
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
                elif not a.run:
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
        print(f"[{i}/{len(rows)}] {status:13} {rel}  {detail}")
        counts[status] = counts.get(status, 0) + 1
        if a.run:
            log.writerow([time.strftime("%F %T"), str(rel), status, detail])
            log_f.flush()
        if status == "killed":
            kills += 1
            with open(LIB / "DANGEROUS.csv", "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([str(rel), detail])
            if kills >= a.max_kills:
                print(f"STOPPING: {kills} watchdog kills. Check library/DANGEROUS.csv.")
                break
            print(f"   cooling down {a.cooldown}s ...")
            time.sleep(a.cooldown)
    print("summary:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
