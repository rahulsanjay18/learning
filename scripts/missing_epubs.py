#!/usr/bin/env python3
"""
missing_titles.py  (v3)

Builds a clean list of book titles from LIBRARY_DIR, optionally skipping books
that already have a Markdown version in MARKDOWN_DIR.

What it does to each file:
  1. File type: real ebook extensions are kept; odd/truncated ones (.epu, .pd,
     no extension) are identified by their header bytes (%PDF, epub zip, MOBI).
  2. Title: parsed from the filename, understanding common formats:
       Anna's Archive   "Title -- Author -- year -- publisher -- isbn -- md5 -- Anna's Archive"
       libgen           "Author - Title (Year, Publisher) - libgen.li"
       z-lib            "Title (Author) (z-lib.org)" / "Title by Author (z-lib.org)"
       Oxford VSI       "Topic_-_OxfordUP.VSI_-_Last,_First.Mon.YYYY"
       Springer         "2016_Book_TitleInCamelCase"
       OpenStax         "Biology2e-WEB_AbC1234"
     Weak names (8.3 like MARTIN~1.EPU, pg12345, "Book.pdf", "pages0-99.pdf")
     use the EPUB/PDF metadata or the parent folder name instead.
  3. Non-book filter, in layers:
       a. Book signals (ISBN, md5, publisher/series names, source-site tags,
          edition text, --trust-dir folders) => always kept, never sent to the LLM.
       b. Hard rules => wrong file type, empty/tiny files, camera-style names,
          saved-web-page asset folders.
       c. Optional local LLM (--llm) for names the rules can't settle. It sees
          the folder path, returns book / not_book / unsure, and a file is only
          skipped on a confident not_book. Unsure => kept and listed for review.

Outputs:
  missing_titles.txt   the clean list
  skipped_files.txt    what was skipped and why (repeats grouped per folder)
  needs_review.txt     kept, but worth a glance (LLM unsure, weak filenames)

Usage:
    python missing_titles.py --library ./Library --markdown ./Markdown_Library
    python missing_titles.py --library ./Library --no-compare --out all_titles.txt \
        --llm qwen2.5:7b --trust-dir "OpenStax" --trust-dir "Fiction"
    pip install tqdm            # progress bar
    pip install pypdf           # optional: lets it read titles from PDF metadata
"""

import argparse
import json
import logging
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

# pypdf logs a warning for every slightly broken PDF; keep the progress bar clean
logging.getLogger("pypdf").setLevel(logging.CRITICAL)

# =====================================================================
# Config you may want to edit
# =====================================================================

BOOK_EXTS = {"pdf", "epub", "mobi", "azw", "azw3", "kfx", "djvu", "fb2",
             "lit", "pdb", "cbz", "cbr", "rtf", "docx", "odt"}

# Extensions that are never books; not even sniffed (keeps it fast).
NON_BOOK_EXTS = {
    "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tif", "tiff",
    "mp3", "wav", "flac", "m4a", "ogg", "avi", "mp4", "mkv", "flv", "mov", "swf",
    "html", "htm", "css", "js", "json", "xml", "txt", "md", "nfo", "ini", "lst",
    "exe", "dll", "ocx", "msi", "cab", "tlb", "hlp", "ttf", "otf", "iso", "bin", "cue",
    "rar", "7z", "zip", "gz", "tar", "mdb", "pgn", "clv", "doc", "xls", "xlsx", "ppt", "pptx",
}

# Site / source tags to strip from titles (also count as "this is a book" signals).
SOURCE_TAGS = [
    r"lib\s*gen(?:\s*\.\s*(?:li|rs|is|st|lc|org))?",
    r"z\s*-?\s*lib(?:rary)?(?:\s*\.\s*(?:org|io|is|gs))?",
    r"anna(?:â€™|’|')?s?\s*-?\s*ar(?:c(?:h(?:i(?:v(?:e)?)?)?)?)?(?:\s*\.\s*(?:org|li|se))?",
    r"b\s*-\s*ok(?:\s*\.\s*(?:org|cc|xyz))?",
    r"bookzz(?:\s*\.\s*org)?",
    r"pdf\s*drive(?:\s*\.\s*com)?",
    r"sci\s*-?\s*hub",
    r"ebook\s*3000",
    r"\[?retail\]?",
]
# Publishers / series that strongly imply "published book".
PUBLISHER_SIGNALS = [
    r"oxford\s*up", r"\bvsi\b", r"penguin", r"springer", r"_book_", r"o'?reilly", r"manning",
    r"no starch", r"wiley", r"pearson", r"mcgraw", r"norton", r"hal leonard", r"cambridge",
    r"routledge", r"packt", r"apress", r"taunton", r"skyhorse", r"mometrix", r"alfred",
    r"faber", r"abrsm", r"royal conservatory", r"frommer", r"rough guide", r"teach yourself",
    r"openstax", r"[-_](?:web|op)(?:_[a-z0-9]{7})?$",
]

JUNK_WORDS = re.compile(r"(?i)\b(?:readme|read me|license|changelog|cover|covers|thumbnail|"
                        r"thumbs|desktop|index|untitled|new document|invoice|receipt|"
                        r"statement|screenshot|screen shot|resume|cv|notes|todo|backup|"
                        r"copy of|metadata|opf|order to read)\b")
CAMERA_ID = re.compile(r"(?i)^(?:img|dsc|dscn|pxl|vid|scan|screenshot|photo|image|whatsapp image)"
                       r"[\s_-]*\d+|^[0-9a-f\-]{24,}$")
SUSPECT_WORDS = re.compile(r"(?i)\b(?:lecture|lec|lab|hw|homework|assignment|exam|midterm|quiz|"
                           r"syllabus|slides|week|chapter|ch|draft|report|budget|q[1-4]|minutes|"
                           r"agenda|form|application|answers?|solutions?|v\d+|rev|copy|"
                           r"[a-z]{2,4}\s?\d{3,4})\b")
GENERIC_STEM = re.compile(r"(?i)^(?:book|booklet|e-?book|text|main|full|complete|document|"
                          r"output|file|part|vol(?:ume)?|pages?)[\s_\-]*\d*(?:[\s_\-]+\d+)?$")
EIGHT_DOT_THREE = re.compile(r"^\S{1,8}~\d+$")
GUTENBERG = re.compile(r"(?i)^pg\d+(?:-images)?$")

# Folders whose path contains one of these words are treated as book folders.
DEFAULT_TRUST_WORDS = ["fiction", "novel", "literature", "classics", "textbook",
                       "very short introduction", "openstax", "children's books",
                       "stories", "readers", "poetry", "philosophy", "religious"]

MIN_SIZE_BYTES = 20_000

# =====================================================================
# Small helpers
# =====================================================================

_source_re = re.compile(r"(?i)(?:^|[\s\-_.,;|(\[])(?:" + "|".join(SOURCE_TAGS) + r")(?=$|[\s\-_.,;|)\]])")
_publisher_re = re.compile(r"(?i)" + "|".join(PUBLISHER_SIGNALS))
_site_prefix_re = re.compile(r"(?i)^[\w-]+\.(?:net|tips|com|org|pub|io)[_\-]")


def fix_mojibake(s: str) -> str:
    """'Annaâ€™s' -> 'Anna's' (UTF-8 bytes that were decoded as cp1252)."""
    if "â€" in s or "Ã" in s:
        try:
            return s.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass
    return s


def key(title: str) -> str:
    t = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^\w\s]|_", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def letters(s: str) -> int:
    return sum(c.isalpha() for c in s)


def files_in(folder: Path):
    return (p for p in folder.rglob("*") if p.is_file() and not p.name.startswith("."))


def flip_name(author: str) -> str:
    """'Nobes, Christopher' -> 'Christopher Nobes'; handles 'A, B & C, D'."""
    parts = [a.strip() for a in re.split(r"\s*(?:&|;)\s*", author) if a.strip()]
    out = []
    for a in parts:
        m = re.match(r"^([^,]+),\s*([^,]+)$", a)
        out.append(f"{m.group(2).strip()} {m.group(1).strip()}" if m else a)
    return " & ".join(out)


def move_article(title: str) -> str:
    """'Blues, The' -> 'The Blues'."""
    m = re.match(r"^(.*),\s*(The|A|An)$", title.strip())
    return f"{m.group(2)} {m.group(1)}" if m else title


# =====================================================================
# File type detection
# =====================================================================

def sniff(path: Path) -> str | None:
    """Identify an ebook by its header bytes, for odd or truncated extensions."""
    try:
        with open(path, "rb") as f:
            head = f.read(68)
    except OSError:
        return None
    if head.startswith(b"%PDF"):
        return "pdf"
    if head[60:68] == b"BOOKMOBI":
        return "mobi"
    if head.startswith(b"AT&TFORM"):
        return "djvu"
    if head.startswith(b"PK"):
        try:
            with zipfile.ZipFile(path) as z:
                if z.read("mimetype").strip() == b"application/epub+zip":
                    return "epub"
        except Exception:
            pass
    return None


def book_kind(path: Path) -> str | None:
    ext = path.suffix.lower().lstrip(".")
    if ext in BOOK_EXTS:
        return ext
    if ext in NON_BOOK_EXTS:
        return None
    return sniff(path)          # .epu, .pd, .p, .june, no extension, ...


# =====================================================================
# Metadata (for weak filenames)
# =====================================================================

def _clean_meta(t: str | None) -> str | None:
    if not t:
        return None
    t = re.sub(r"(?i)^microsoft (?:word|powerpoint) - ", "", t.strip())
    t = re.sub(r"(?i)\.(?:docx?|pdf|indd|tex)$", "", t).strip()
    if letters(t) < 3 or re.match(r"(?i)^(?:untitled|unknown|document\d*|title)$", t):
        return None
    return t


def epub_meta(path: Path) -> tuple[str | None, str | None]:
    try:
        with zipfile.ZipFile(path) as z:
            container = ET.fromstring(z.read("META-INF/container.xml"))
            opf_path = container.find(".//{*}rootfile").get("full-path")
            opf = ET.fromstring(z.read(opf_path))
            dc = "{http://purl.org/dc/elements/1.1/}"
            t, a = opf.find(f".//{dc}title"), opf.find(f".//{dc}creator")
            return (_clean_meta(t.text if t is not None else None),
                    _clean_meta(a.text if a is not None else None))
    except Exception:
        return None, None


def pdf_meta(path: Path) -> tuple[str | None, str | None]:
    try:
        from pypdf import PdfReader          # optional dependency
        info = PdfReader(str(path)).metadata or {}
        return _clean_meta(info.get("/Title")), _clean_meta(info.get("/Author"))
    except Exception:
        return None, None


# =====================================================================
# Title parsing
# =====================================================================

def raw_stem(path: Path) -> str:
    name = fix_mojibake(path.name)
    base = name
    while True:                                  # strip 'x.pdf.epub' style extensions
        b, dot, ext = base.rpartition(".")
        if dot and (ext.lower() in BOOK_EXTS or ext.lower() in {"doc", "zip"}):
            base = b
        else:
            break
    if base == name and "." in name:             # unknown/truncated ext: drop it
        base = name.rpartition(".")[0] or name
    return base


def generic_cleanup(s: str) -> str:
    s = _site_prefix_re.sub("", s)               # kupdf.net_, epdf.tips_, book.mixu.net-
    s = s.replace("_", " ")
    if " " not in s and re.search(r"[a-z]-[a-z]", s) and s == s.lower():
        s = s.replace("-", " ")                  # attack-with-mikhail-tal
    if " " not in s and s.count(".") >= 2:       # The.Great.Gatsby
        s = s.replace(".", " ")
    s = re.sub(r"^\d{4}\s*Book\s*", "", s)       # Springer '2016_Book_'
    s = re.sub(r"(?i)[-\s](?:WEB|OP|HR)(?:\s[A-Za-z0-9]{7})?$", "", s)   # OpenStax suffixes
    s = re.sub(r"^\d{1,2}[.\-](?=[A-Za-z])", "", s)                       # '01.Momotaro'

    inner = re.findall(r"\[([^\]]*)\]", s)       # keep bracket text if it's all there is
    stripped = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", s)
    if letters(stripped) < 3 and inner:
        stripped = max(inner, key=len)
    s = stripped

    s = _source_re.sub(" ", s)
    s = re.sub(r"(?i)\b[0-9a-f]{32}\b", " ", s)
    s = re.sub(r"(?i)\bisbn(?:13|10)?[\s:-]*[\dx-]{10,17}\b", " ", s)
    s = re.sub(r"\b97[89][\d-]{10,14}\b|(?<![\d.])\d{9}[\dXx](?!\d)", " ", s)
    s = re.sub(r"(?i),?\s*\b\d+(?:st|nd|rd|th)\s*(?:edition\b|ed\b\.?)", " ", s)
    s = re.sub(r"(?i)\b\d+ed\b", " ", s)
    s = re.sub(r"(?i)\b(?:third|second|first|fourth|fifth)\s+edition\b", " ", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s) if " " not in s.strip() else s   # CamelCase
    s = re.sub(r"(?<=[a-z])(?=\d+e\b)", " ", s)                                # Chemistry2e
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(?:\s*[-–—,;:|]\s*)+$", "", s)
    s = re.sub(r"^(?:\s*[-–—,;:|]\s*)+", "", s)
    s = re.sub(r"\s*([-–—])\s*(?:[-–—]\s*)+", r" \1 ", s)
    return s.strip(" .")


def parse_name(stem: str) -> tuple[str, str | None]:
    """Return (title, author or None) from a filename stem."""
    s = stem

    # Anna's Archive: 'Title -- Author -- ... -- Anna's Archive'
    if " -- " in s:
        fields = [f.strip() for f in s.split(" -- ")]
        title = fields[0].replace("_ ", ": ").replace("_", " ")
        author = fields[1] if len(fields) > 1 else None
        if author:
            author = re.sub(r"(?i)^by\s+", "", author).replace("_", ".").strip()
            if (re.match(r"(?i)^(?:unknown|various|various artists|\d.*)$", author)
                    or re.search(r"(?i)\b(?:corporation|publishing|abrsm)\b", author)
                    or _source_re.search(" " + author)):
                author = None
        return generic_cleanup(title), author

    spaced = s.replace("_", " ")

    # Oxford Very Short Introductions
    m = re.match(r"(?i)^(.*?)\s*-\s*OxfordUP\.?\s*VSI\s*-\s*(.*?)(?:[.\s]+[A-Z][a-z]{2}\.?\d{2,4})?$",
                 spaced)
    if m:
        topic = move_article(generic_cleanup(m.group(1)))
        return f"{topic}: A Very Short Introduction", flip_name(m.group(2).strip(" .,")) or None

    # z-lib: 'Title (Author) (z-lib.org)' or 'Title by Author (z-lib.org)'
    if re.search(r"(?i)z-?lib", s):
        body = re.sub(r"(?i)\s*\(z-?lib(?:\.org)?\)\s*$", "", spaced)
        groups = re.findall(r"\(([^)]*)\)", body)
        if groups and re.fullmatch(r"[A-Za-z.,'&\s-]+", groups[-1]) \
                and not re.search(r"(?i)edition|ed\.", groups[-1]):
            return generic_cleanup(body[:body.rfind("(")]), groups[-1].strip()
        if " by " in body:
            t, a = body.rsplit(" by ", 1)
            return generic_cleanup(t), generic_cleanup(a)
        return generic_cleanup(body), None

    # libgen: 'Author - Title (Year, Publisher) - libgen.li'
    if re.search(r"(?i)lib\s*gen", s) and " - " in spaced:
        a, t = spaced.split(" - ", 1)
        if letters(a) >= 3 and len(a.split()) <= 6:
            return generic_cleanup(t), generic_cleanup(a)

    title = generic_cleanup(s)
    if title == title.lower() and letters(title) >= 3:
        title = " ".join(w[:1].upper() + w[1:] for w in title.split())
    m = re.match(r"^(.{3,}?)\s+by\s+((?:[A-Z][\w.'-]*\s?){2,4})$", title)
    if m:
        return m.group(1).strip(" .,-"), m.group(2).strip()
    return title, None


def resolve_title(path: Path, rel: Path, kind: str):
    """Return (title, author, review_note, came_from_metadata)."""
    stem = raw_stem(path)
    weak = bool(EIGHT_DOT_THREE.match(stem) or GUTENBERG.match(stem))
    generic = bool(GENERIC_STEM.match(stem.replace("_", " ")))

    if (weak or generic) and kind in ("epub", "pdf"):
        t, a = epub_meta(path) if kind == "epub" else pdf_meta(path)
        if t:
            return generic_cleanup(t), a, None, True
    if generic and rel.parent.name:
        title, author = parse_name(rel.parent.name)
        return title, author, None, False
    title, author = parse_name(stem)
    if weak:
        return title, author, "weak filename and no readable metadata", False
    return title, author, None, False


# =====================================================================
# Book / non-book decisions
# =====================================================================

def book_signal(path: Path, rel: Path, trust_dirs: list[str], trust_words: list[str]) -> str | None:
    """A reason this is almost certainly a published book, or None."""
    name = fix_mojibake(path.name).replace("_", " ")      # so '_8ed' reads as ' 8ed'
    stem = raw_stem(path).replace("_", " ")
    if any(t.lower() in str(rel.parent).lower() for t in trust_dirs):
        return "trusted folder (--trust-dir)"
    near = " / ".join({rel.parts[0], rel.parent.name}) if len(rel.parts) > 1 else ""
    if any(w in near.lower() for w in trust_words):
        return "book folder"
    if re.search(r"(?i)isbn|(?<!\d)97[89]\d{10}(?!\d)|(?<![\d.])\d{9}[\dXx](?!\d)", name):
        return "ISBN"
    if re.search(r"(?i)\b[0-9a-f]{32}\b", name):
        return "md5 hash (library download)"
    if _source_re.search(" " + name):
        return "source-site tag"
    if _publisher_re.search(stem) or _publisher_re.search(name) \
            or _publisher_re.search(raw_stem(path)):
        return "publisher/series name"
    if re.search(r"(?i)\b\d+(?:st|nd|rd|th)\s*ed|\b\d+e\b|\b\d+ed\b|edition|\(\d{4},\s*[^)]+\)", name):
        return "edition/year-publisher"
    if GUTENBERG.match(stem.replace(" ", "_")):
        return "Project Gutenberg"
    if _site_prefix_re.search(fix_mojibake(path.name)):
        return "download-site prefix"
    return None


def hard_skip_reason(path: Path, stem: str, title: str, size: int, min_size: int) -> str | None:
    if size == 0:
        return "empty file (0 bytes, broken download?)"
    if size < min_size:
        return f"tiny file ({size} bytes)"
    if CAMERA_ID.search(stem):
        return "camera/ID-style name"
    if JUNK_WORDS.search(title) and len(title.split()) <= 3:
        return "junk-word name"
    if not title.strip():
        return "no usable name"
    return None


def is_ambiguous(title: str) -> bool:
    return (len(title.split()) <= 2 or letters(title) == 0
            or bool(re.search(r"\d{3,}", title))
            or bool(SUSPECT_WORDS.search(title)) or bool(JUNK_WORDS.search(title)))


# =====================================================================
# Optional LLM judge
# =====================================================================

LLM_SCHEMA = {
    "type": "object",
    "properties": {          # reason FIRST so the verdict follows from it
        "reason": {"type": "string"},
        "verdict": {"type": "string", "enum": ["book", "not_book", "unsure"]},
        "confidence": {"type": "number"},
    },
    "required": ["reason", "verdict", "confidence"],
}

LLM_PROMPT = """You are sorting files in a personal ebook library. Decide whether this file is
BOOK-LIKE READING MATERIAL to keep.

Counts as "book" (keep): any published or professionally produced reading material. That includes
novels, nonfiction, textbooks (including open/free textbooks), solutions manuals, workbooks,
study and exam-prep guides, published manuals and handbooks, music method books, songbooks and
sheet-music collections, dictionaries, phrasebooks, travel guides, religious scriptures, academic
monographs, series volumes, children's stories, plays, and single stories or volumes from a
published set.

Counts as "not_book" (skip): personal or work files. Homework, someone's own class notes, lecture
slides, worksheets with answer keys from a class, receipts, forms, reading lists, game records,
software readmes, single scanned page images, and cover images.

Rules:
- An unfamiliar title is NOT evidence. Most real books are not famous. Never answer "not_book"
  just because you don't recognize the title.
- The folder path is strong context. A plain title inside a "Fiction" or textbook folder is a book.
- If you can't tell, answer "unsure".

Examples:
- "Accounting: A Very Short Introduction - Christopher Nobes" in "A Very Short Introduction" -> book
- "Statistics" in "OpenStax" -> book
- "Solutions Manual Hogg Tanis" in "Math/Probability and Statistics" -> book
- "Rebecca" in "Fiction" -> book
- "Owner's Manual" in "Pimsleur Japanese/EXTRAS" -> not_book
- "Fortran95 notes" in "Computer Science/Other" -> not_book
- "order to read" in "Chess/Winning Chess" -> not_book

File name: {name}
Folder: {folder}
File type: {ext}

Respond in JSON with: reason (one short sentence), verdict, confidence (0 to 1)."""


def llm_judge(title: str, folder: str, ext: str, model: str, url: str) -> tuple[str, float, str]:
    """Returns (verdict, confidence, reason). Any failure => ('unsure', 0, error)."""
    import requests
    try:
        r = requests.post(f"{url}/api/generate", timeout=120, json={
            "model": model,
            "prompt": LLM_PROMPT.format(name=title, folder=folder or "(library root)", ext=ext),
            "format": LLM_SCHEMA,        # structured output: guarantees these exact keys
            "stream": False,
            "options": {"temperature": 0},
        })
        r.raise_for_status()
        data = json.loads(r.json()["response"])
        verdict = str(data.get("verdict", "")).strip().lower().replace(" ", "_").replace("-", "_")
        if verdict not in {"book", "not_book", "unsure"}:
            verdict = "unsure"                    # never treat a malformed answer as a skip
        conf = float(data.get("confidence") or 0)
        if conf > 1:                              # some models answer 80 instead of 0.8
            conf /= 100
        return verdict, max(0.0, min(conf, 1.0)), str(data.get("reason", ""))[:200]
    except Exception as e:
        return "unsure", 0.0, f"LLM error: {e}"


# =====================================================================
# Main
# =====================================================================

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--library", type=Path, default=Path("Library"))
    ap.add_argument("--markdown", type=Path, default=Path("Markdown_Library"))
    ap.add_argument("--no-compare", action="store_true", help="ignore the Markdown folder")
    ap.add_argument("--out", type=Path, default=Path("missing_titles.txt"))
    ap.add_argument("--no-author", action="store_true", help="titles only, no ' - Author'")
    ap.add_argument("--with-originals", action="store_true", help="add '<TAB>original path' to each line")
    ap.add_argument("--min-size", type=int, default=MIN_SIZE_BYTES)
    ap.add_argument("--exclude", metavar="REGEX", help="extra filename regex to skip")
    ap.add_argument("--trust-dir", action="append", default=[], metavar="TEXT",
                    help="folders whose path contains TEXT are always books (repeatable)")
    ap.add_argument("--no-default-trust", action="store_true",
                    help="don't treat Fiction/Literature/Textbook/... folders as book folders")
    ap.add_argument("--keep-all", action="store_true", help="disable all non-book filtering")
    ap.add_argument("--llm", metavar="MODEL", help="Ollama model for unclear names, e.g. qwen2.5:7b")
    ap.add_argument("--llm-scope", choices=["ambiguous", "all"], default="ambiguous")
    ap.add_argument("--llm-min-conf", type=float, default=0.9,
                    help="skip only on not_book with at least this confidence (default 0.9)")
    ap.add_argument("--ollama-url", default="http://localhost:11434")
    args = ap.parse_args()
    extra = re.compile(args.exclude, re.I) if args.exclude else None
    trust_words = [] if args.no_default_trust else DEFAULT_TRUST_WORDS

    dirs = (args.library,) if args.no_compare else (args.library, args.markdown)
    for d in dirs:
        if not d.is_dir():
            print(f"Error: {d} is not a directory", file=sys.stderr)
            return 1

    have_md: set[str] = set()
    if not args.no_compare:
        for p in files_in(args.markdown):
            t, a = parse_name(raw_stem(p))
            have_md |= {key(t), key(f"{t} {a}" if a else t)}

    results: dict[str, tuple[str, str]] = {}
    grouped: dict[tuple[str, str], int] = defaultdict(int)   # (reason, folder) -> count
    singles: list[tuple[str, str]] = []
    review: list[str] = []
    llm_calls = 0

    all_files = sorted(files_in(args.library))
    bar = tqdm(all_files, desc="Scanning", unit="file", dynamic_ncols=True)
    for p in bar:
        rel = p.relative_to(args.library)
        bar.set_postfix(kept=len(results), skipped=sum(grouped.values()) + len(singles),
                        llm=llm_calls, refresh=False)

        if not args.keep_all:
            web_dir = next((i for i, part in enumerate(rel.parts[:-1]) if part.endswith("_files")), None)
            if web_dir is not None:
                grouped[("saved web page assets", str(Path(*rel.parts[:web_dir + 1])))] += 1
                continue

        kind = book_kind(p)
        if kind is None:
            if not args.keep_all:
                ext = p.suffix.lower() or "(none)"
                grouped[(f"not an ebook file ({ext})", str(rel.parent))] += 1
                continue
            kind = p.suffix.lower().lstrip(".")

        title, author, note, from_meta = resolve_title(p, rel, kind)
        stem = raw_stem(p)
        signal = book_signal(p, rel, args.trust_dir, trust_words)
        if from_meta and not signal:
            signal = "title read from file metadata"
        if p.suffix.lower().lstrip(".") not in BOOK_EXTS:
            note = (note + "; " if note else "") + f"odd extension, detected as {kind}"

        if not args.keep_all:
            reason = hard_skip_reason(p, stem, title, p.stat().st_size, args.min_size)
            if reason and (not signal or reason.startswith(("empty", "tiny"))):
                singles.append((reason, str(rel)))
                continue
            if extra and extra.search(p.name):
                singles.append(("matched --exclude", str(rel)))
                continue

        full = f"{title} - {author}" if author else title
        if key(title) in have_md or key(full) in have_md:
            continue

        if args.llm and not args.keep_all and not signal \
                and (args.llm_scope == "all" or is_ambiguous(title)):
            llm_calls += 1
            verdict, conf, why = llm_judge(full, str(rel.parent), kind, args.llm, args.ollama_url)
            tqdm.write(f"  LLM {verdict:>8} ({conf:.2f})  {rel}")
            if verdict == "not_book" and conf >= args.llm_min_conf:
                singles.append((f"LLM: {why} ({conf:.2f})", str(rel)))
                continue
            if verdict != "book":
                note = (note + "; " if note else "") + f"LLM {verdict} ({conf:.2f}): {why}"

        out_title = title if args.no_author else full
        if note:
            review.append(f"{note}\t{out_title}\t{rel}")
        results.setdefault(key(out_title), (out_title, str(rel)))

    bar.close()

    # ---- write outputs ----
    lines = [f"{t}\t{o}" if args.with_originals else t
             for t, o in sorted(results.values(), key=lambda x: x[0].lower())]
    args.out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    label = "title(s)" if args.no_compare else "missing title(s)"
    print(f"\n{len(lines)} {label} -> {args.out}")

    skip_lines = [f"{r} x{n}\t{folder}/" for (r, folder), n in grouped.items()]
    skip_lines += [f"{r}\t{f}" for r, f in singles]
    if skip_lines:
        sp = args.out.with_name("skipped_files.txt")
        sp.write_text("reason\tpath\n" + "\n".join(sorted(skip_lines, key=lambda l: l.split("\t")[-1]))
                      + "\n", encoding="utf-8")
        n_files = sum(grouped.values()) + len(singles)
        print(f"{n_files} file(s) skipped ({len(skip_lines)} lines) -> {sp}")
    if review:
        rp = args.out.with_name("needs_review.txt")
        rp.write_text("note\ttitle\tpath\n" + "\n".join(review) + "\n", encoding="utf-8")
        print(f"{len(review)} kept but worth a look -> {rp}")
    if args.llm:
        print(f"LLM was asked about {llm_calls} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
