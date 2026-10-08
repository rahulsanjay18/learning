#!/usr/bin/env python3
"""
book_search_strings.py

One script: scans an ebook library, filters out non-book files, cleans up the
titles, and turns each book into ready-to-use search strings.

Stage 1 - scan (per file):
  * file type: real ebook extensions kept; odd/truncated ones (.epu, .pd, none)
    identified by header bytes (%PDF, epub zip, MOBI)
  * title: parsed from Anna's Archive / libgen / z-lib / Oxford VSI / Springer /
    OpenStax filename formats; weak names (MARTIN~1.EPU, pg12345, Book.pdf,
    pages0-99.pdf) use EPUB/PDF metadata or the parent folder name
  * non-book filter: book signals (ISBN, md5, publisher, edition, trusted folder,
    metadata) => always kept; hard rules => skip wrong types, empty/tiny files,
    camera names, saved-web-page assets; optional LLM judges what's left and
    may only skip on a confident not_book
  * optional: skip books that already have a Markdown version (--markdown)

Stage 2 - search strings (per book):
  * optional LLM extracts title/subtitle/authors/edition/year/isbn as JSON
    (ISBNs must appear in the filename and pass the checksum; years must
    appear in the filename)
  * optional Open Library verification fills canonical title/author/ISBN/year
  * queries are built by code from those fields

Outputs (next to --out):
  search_strings.txt   one query per line: title + author last name (--isbn: ISBN-13 when known)
  search_strings.tsv   all fields + 4 query variants + provenance, one row per book
  book_list.txt        cleaned "Title - Author<TAB>relative path" for every kept book
  skipped_files.txt    skipped files with reasons (repeats grouped per folder)
  needs_review.txt     kept but uncertain (LLM unsure, weak names, odd extensions)
  search_cache.jsonl   per-book stage-2 results; reruns resume from here

Usage:
    pip install tqdm requests rapidfuzz       # + pypdf (optional, PDF metadata)
    python book_search_strings.py --library ./Library --no-compare
    python book_search_strings.py --library ./Library --markdown ./Markdown_Library \
        --llm qwen2.5:14b --verify --contact you@example.com
"""

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import requests
from rapidfuzz import fuzz
from tqdm import tqdm

logging.getLogger("pypdf").setLevel(logging.CRITICAL)   # silence warnings on broken PDFs

OPENLIB_URL = "https://openlibrary.org/search.json"
OPENLIB_DELAY_S = 0.35          # ~3 req/s, Open Library's guidance for identified clients

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
# Book / non-book LLM judge (scan stage)
# =====================================================================

FILTER_SCHEMA = {
    "type": "object",
    "properties": {          # reason FIRST so the verdict follows from it
        "reason": {"type": "string"},
        "verdict": {"type": "string", "enum": ["book", "not_book", "unsure"]},
        "confidence": {"type": "number"},
    },
    "required": ["reason", "verdict", "confidence"],
}

FILTER_PROMPT = """You are sorting files in a personal ebook library. Decide whether this file is
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
            "prompt": FILTER_PROMPT.format(name=title, folder=folder or "(library root)", ext=ext),
            "format": FILTER_SCHEMA,        # structured output: guarantees these exact keys
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


# =====================================================================
# ISBN helpers (checksum-validated, so random digit runs are ignored)
# =====================================================================

def _isbn10_ok(s: str) -> bool:
    if not re.fullmatch(r"\d{9}[\dX]", s):
        return False
    total = sum((10 - i) * (10 if c == "X" else int(c)) for i, c in enumerate(s))
    return total % 11 == 0


def _isbn13_ok(s: str) -> bool:
    if not re.fullmatch(r"97[89]\d{10}", s):
        return False
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s[:12]))
    return (10 - total % 10) % 10 == int(s[12])


def to_isbn13(s: str) -> str | None:
    s = re.sub(r"[\s-]", "", (s or "")).upper()
    if _isbn13_ok(s):
        return s
    if _isbn10_ok(s):
        core = "978" + s[:9]
        check = (10 - sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(core)) % 10) % 10
        return core + str(check)
    return None


def isbns_in(text: str) -> list[str]:
    found = []
    for m in re.finditer(r"(?<![\dX])(?:97[89][\d-]{10,14}|\d{9}[\dXx])(?![\dXx])", text):
        i13 = to_isbn13(m.group(0))
        if i13 and i13 not in found:
            found.append(i13)
    return found


# =====================================================================
# Evidence gathering
# =====================================================================

def gather(rel_path: str, guess: str, library: Path | None) -> dict:
    name = fix_mojibake(Path(rel_path).name)
    ev = {"path": rel_path, "filename": name, "folder": str(Path(rel_path).parent),
          "guess": guess, "meta_title": None, "meta_author": None,
          "isbns": isbns_in(name)}
    if library:
        p = library / rel_path
        if p.is_file():
            kind = book_kind(p)
            if kind == "epub":
                ev["meta_title"], ev["meta_author"] = epub_meta(p)
            elif kind == "pdf":
                ev["meta_title"], ev["meta_author"] = pdf_meta(p)
    return ev


_PERSON = re.compile(r"^(?:[A-Z][\w.'’-]*\.?(?:\s+|$)){2,5}$")   # 'Robert C. Martin'


def split_authors(s: str) -> list[str] | None:
    """'Mike Israetel, Jared Feather' -> [...]; None if it doesn't look like names."""
    parts = [a.strip() for a in re.split(r"\s*(?:&|;|,|\band\b)\s*", s) if a.strip()]
    return parts if parts and all(_PERSON.match(p) for p in parts) else None


def baseline_fields(ev: dict) -> dict:
    """No-LLM fallback. Starts from missing_titles.py's resolved 'Title - Author'
    (which already used metadata / folder names for weak filenames)."""
    title, authors = ev["guess"], []
    if " - " in title:
        left, right = title.rsplit(" - ", 1)
        names = split_authors(right)            # only split if the right side is people
        if names:
            title, authors = left, names
    sub = None
    if ": " in title:
        title, sub = title.split(": ", 1)
    return {"title": title, "subtitle": sub, "authors": authors, "edition": None,
            "year": None, "isbn": ev["isbns"][0] if ev["isbns"] else None,
            "confidence": None, "source": "parser"}


# =====================================================================
# Field-extraction LLM (search stage)
# =====================================================================

EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "authors": {"type": "array", "items": {"type": "string"}},
        "edition": {"type": "string"},
        "year": {"type": "string"},
        "isbn": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["title", "subtitle", "authors", "edition", "year", "isbn", "confidence"],
}

EXTRACT_PROMPT = """You extract bibliographic fields from a messy ebook filename so it can be looked up
in a library catalog.

Evidence:
- Original filename: {filename}
- Folder: {folder}
- Cleaned guess: {guess}
- Embedded metadata title: {meta_title}
- Embedded metadata author: {meta_author}
- ISBNs found in filename (checksum-valid): {isbns}

Rules:
- title: the book's main title only, properly capitalized, without subtitle, edition,
  series name, publisher, year, file info, or download-site names.
- subtitle: the subtitle if clearly present (e.g. "A Very Short Introduction"), else "".
- authors: list of people as "First Last" (convert "Last, First"). Exclude publishers,
  editors-as-companies, and "Various". Use [] if none is identifiable.
- edition: e.g. "3rd" if stated, else "".
- year: only if it appears in the evidence AND is clearly a publication year, else "".
- isbn: only copy one from the evidence list above; NEVER invent one. Else "".
- Fix run-together words (e.g. "IntroductiontoSociology" -> "Introduction to Sociology")
  and obvious typos, but do not replace the book with a different, more famous one.
- If you recognize the book with certainty, you may correct the title/author spelling.
- confidence: 0 to 1, how sure you are the title and authors are right.

Respond in JSON only."""


def llm_extract(ev: dict, model: str, url: str) -> dict | None:
    prompt = EXTRACT_PROMPT.format(
        filename=ev["filename"], folder=ev["folder"] or "(root)", guess=ev["guess"],
        meta_title=ev["meta_title"] or "(none)", meta_author=ev["meta_author"] or "(none)",
        isbns=", ".join(ev["isbns"]) or "(none)")
    try:
        r = requests.post(f"{url}/api/generate", timeout=180, json={
            "model": model, "prompt": prompt, "format": EXTRACT_SCHEMA,
            "stream": False, "options": {"temperature": 0}})
        r.raise_for_status()
        d = json.loads(r.json()["response"])
    except Exception as e:
        tqdm.write(f"  LLM failed on {ev['filename']}: {e}")
        return None

    title = str(d.get("title") or "").strip()
    if len(re.sub(r"\W", "", title)) < 2:
        return None
    isbn = to_isbn13(str(d.get("isbn") or ""))
    if isbn and isbn not in ev["isbns"]:          # model invented one; drop it
        isbn = None
    year = str(d.get("year") or "").strip()
    if not (re.fullmatch(r"1[5-9]\d\d|20\d\d", year) and year in ev["filename"]):
        year = None
    conf = float(d.get("confidence") or 0)
    conf = conf / 100 if conf > 1 else conf
    authors = [a.strip() for a in (d.get("authors") or []) if isinstance(a, str) and a.strip()
               and not re.search(r"(?i)\b(?:various|unknown|corporation|publishing|press)\b", a)]
    return {"title": title, "subtitle": (d.get("subtitle") or "").strip() or None,
            "authors": authors, "edition": (d.get("edition") or "").strip() or None,
            "year": year, "isbn": isbn or (ev["isbns"][0] if ev["isbns"] else None),
            "confidence": round(max(0.0, min(conf, 1.0)), 2), "source": "llm"}


# =====================================================================
# Open Library verification
# =====================================================================

def openlib_verify(f: dict, session: requests.Session, min_score: float) -> dict:
    params = {"fields": "title,subtitle,author_name,first_publish_year,isbn", "limit": 10}
    if f["isbn"]:
        params["q"] = f"isbn:{f['isbn']}"
    else:
        params["title"] = f["title"]
        if f["authors"]:
            params["author"] = f["authors"][0]
    try:
        r = session.get(OPENLIB_URL, params=params, timeout=30)
        r.raise_for_status()
        docs = r.json().get("docs", [])
    except requests.RequestException as e:
        tqdm.write(f"  Open Library error on '{f['title']}': {e}")
        return f
    finally:
        time.sleep(OPENLIB_DELAY_S)
    if not docs:
        return f

    want = f"{f['title']} {f['authors'][0] if f['authors'] else ''}".lower()

    def score(d):
        got = f"{d.get('title', '')} {(d.get('author_name') or [''])[0]}".lower()
        return fuzz.token_set_ratio(want, got) * 0.7 + fuzz.token_sort_ratio(want, got) * 0.3

    best = max(docs, key=score)
    s = score(best)
    if s < min_score and not f["isbn"]:
        f["verify_note"] = f"no confident match (best {s:.0f}: {best.get('title')})"
        return f

    out = dict(f)
    out["title"] = best.get("title") or f["title"]
    out["subtitle"] = best.get("subtitle") or f["subtitle"]
    if best.get("author_name"):
        out["authors"] = best["author_name"][:4]
    out["year"] = f["year"] or (str(best["first_publish_year"]) if best.get("first_publish_year") else None)
    if not out["isbn"]:
        out["isbn"] = next((i for i in (best.get("isbn") or []) if _isbn13_ok(i)), None)
    out["source"] = f["source"] + "+openlibrary"
    out["verify_score"] = round(s)
    return out


# =====================================================================
# Query building
# =====================================================================

def last_name(author: str) -> str:
    parts = [p for p in re.split(r"\s+", author.strip()) if p]
    while len(parts) > 1 and re.fullmatch(r"(?i)jr\.?|sr\.?|ii|iii|iv|phd|md", parts[-1]):
        parts.pop()
    if not parts:
        return ""
    i = len(parts) - 1                 # keep particles: 'du Maurier', 'van Rossum', 'de la Mare'
    while i > 0 and re.fullmatch(r"(?i)du|de|da|di|del|della|la|le|van|von|der|den|ter|bin|ibn|al|el", parts[i - 1]):
        i -= 1
    return " ".join(parts[i:])


def build_queries(f: dict, quote: bool) -> dict:
    t = re.sub(r"\s+", " ", f["title"]).strip(" .:-")
    qt = f'"{t}"' if quote else t
    ln = last_name(f["authors"][0]) if f["authors"] else ""
    if ln and re.search(rf"(?i)\b{re.escape(ln)}\b", t):     # 'Attack with Mikhail Tal' + 'Tal'
        ln = ""
    full_title = f"{t}: {f['subtitle']}" if f.get("subtitle") else t
    return {
        "query": f"{qt} {ln}".strip(),
        "query_title": qt,
        "query_full": " ".join([full_title] + [a for a in f["authors"]
                                                if a.lower() not in full_title.lower()]).strip(),
        "query_isbn": f["isbn"] or "",
    }



# =====================================================================
# Stage 1: scan the library
# =====================================================================

def scan_library(args) -> list[tuple[str, str]]:
    """Returns [(\"Title - Author\", relative_path)] for every kept book."""
    extra = re.compile(args.exclude, re.I) if args.exclude else None
    trust_words = [] if args.no_default_trust else DEFAULT_TRUST_WORDS
    filter_model = args.filter_llm or args.llm

    have_md: set[str] = set()
    if not args.no_compare:
        for p in files_in(args.markdown):
            t, a = parse_name(raw_stem(p))
            have_md |= {key(t), key(f"{t} {a}" if a else t)}

    results: dict[str, tuple[str, str]] = {}
    grouped: dict[tuple[str, str], int] = defaultdict(int)
    singles: list[tuple[str, str]] = []
    review: list[str] = []
    llm_calls = 0

    bar = tqdm(sorted(files_in(args.library)), desc="Stage 1/2 scanning", unit="file", dynamic_ncols=True)
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
                grouped[(f"not an ebook file ({p.suffix.lower() or '(none)'})", str(rel.parent))] += 1
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

        if filter_model and not args.keep_all and not signal \
                and (args.llm_scope == "all" or is_ambiguous(title)):
            llm_calls += 1
            verdict, conf, why = llm_judge(full, str(rel.parent), kind, filter_model, args.ollama_url)
            tqdm.write(f"  filter LLM {verdict:>8} ({conf:.2f})  {rel}")
            if verdict == "not_book" and conf >= args.llm_min_conf:
                singles.append((f"LLM: {why} ({conf:.2f})", str(rel)))
                continue
            if verdict != "book":
                note = (note + "; " if note else "") + f"LLM {verdict} ({conf:.2f}): {why}"

        if note:
            review.append(f"{note}\t{full}\t{rel}")
        results.setdefault(key(full), (full, str(rel)))
    bar.close()

    books = sorted(results.values(), key=lambda x: x[0].lower())
    out_dir = args.out.parent
    (out_dir / "book_list.txt").write_text("".join(f"{t}\t{r}\n" for t, r in books), encoding="utf-8")

    skip_lines = [f"{r} x{n}\t{folder}/" for (r, folder), n in grouped.items()]
    skip_lines += [f"{r}\t{f}" for r, f in singles]
    if skip_lines:
        (out_dir / "skipped_files.txt").write_text(
            "reason\tpath\n" + "\n".join(sorted(skip_lines, key=lambda l: l.split("\t")[-1])) + "\n",
            encoding="utf-8")
    if review:
        (out_dir / "needs_review.txt").write_text(
            "note\ttitle\tpath\n" + "\n".join(review) + "\n", encoding="utf-8")

    print(f"Stage 1: {len(books)} book(s) kept, {sum(grouped.values()) + len(singles)} file(s) skipped, "
          f"{len(review)} flagged for review" + (f", {llm_calls} LLM call(s)" if filter_model else ""))
    return books


# =====================================================================
# Stage 2: search strings
# =====================================================================

def build_search_strings(books: list[tuple[str, str]], args) -> None:
    cache_path = args.out.parent / "search_cache.jsonl"
    cache: dict[str, dict] = {}
    if cache_path.exists() and not args.fresh:
        for l in cache_path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(l)
                cache[rec["path"]] = rec
            except (json.JSONDecodeError, KeyError):
                pass

    session = requests.Session()
    session.headers["User-Agent"] = f"book-search-strings/1.0 ({args.contact})" if args.contact \
        else "book-search-strings/1.0"
    mode = "+".join(x for x in ["llm" if args.llm else "parser", "verify" if args.verify else ""] if x)

    results = []
    with open(cache_path, "a", encoding="utf-8") as cache_f:
        bar = tqdm(books, desc="Stage 2/2 search strings", unit="book", dynamic_ncols=True)
        for guess, rel in bar:
            hit = cache.get(rel)
            if hit and hit.get("mode") == mode:
                results.append(hit)
                continue
            ev = gather(rel, guess, args.library)
            f = (llm_extract(ev, args.llm, args.ollama_url) if args.llm else None) or baseline_fields(ev)
            if args.verify:
                f = openlib_verify(f, session, args.min_score)
            rec = {"path": rel, "mode": mode, **f, **build_queries(f, args.quote)}
            results.append(rec)
            cache_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            cache_f.flush()
            bar.set_postfix(isbn=sum(1 for r in results if r.get("isbn")), refresh=False)
        bar.close()

    best, seen = [], set()
    for r in results:
        q = (r["query_isbn"] if args.isbn else "") or r["query"]
        if q.lower() not in seen:
            seen.add(q.lower())
            best.append(q)
    args.out.write_text("\n".join(best) + "\n", encoding="utf-8")

    cols = ["query", "query_title", "query_full", "query_isbn", "title", "subtitle", "authors",
            "edition", "year", "isbn", "confidence", "source", "verify_score", "verify_note", "path"]
    with open(args.out.with_suffix(".tsv"), "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in results:
            vals = [("; ".join(r[c]) if isinstance(r.get(c), list) else str(r.get(c) or "")) for c in cols]
            fh.write("\t".join(v.replace("\t", " ") for v in vals) + "\n")

    low = sum(1 for r in results if (r.get("confidence") is not None and r["confidence"] < 0.6)
              or r.get("verify_note"))
    print(f"Stage 2: {len(best)} search string(s) -> {args.out}  "
          f"({sum(1 for r in results if r.get('isbn'))}/{len(results)} with ISBN"
          + (f", {low} low-confidence/unverified" if low else "") + ")")


# =====================================================================
# Main
# =====================================================================

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_argument_group("input / output")
    g.add_argument("--library", type=Path, default=Path("Library"))
    g.add_argument("--markdown", type=Path, default=Path("Markdown_Library"),
                   help="skip books that already have a Markdown version here")
    g.add_argument("--no-compare", action="store_true", help="ignore --markdown; process every book")
    g.add_argument("--out", type=Path, default=Path("search_strings.txt"),
                   help="main output; all other files are written next to it")
    g = ap.add_argument_group("non-book filter (stage 1)")
    g.add_argument("--min-size", type=int, default=MIN_SIZE_BYTES)
    g.add_argument("--exclude", metavar="REGEX", help="extra filename regex to skip")
    g.add_argument("--trust-dir", action="append", default=[], metavar="TEXT",
                   help="folders whose path contains TEXT are always books (repeatable)")
    g.add_argument("--no-default-trust", action="store_true",
                   help="don't treat Fiction/Literature/Textbook/... folders as book folders")
    g.add_argument("--keep-all", action="store_true", help="disable all non-book filtering")
    g.add_argument("--llm-scope", choices=["ambiguous", "all"], default="ambiguous")
    g.add_argument("--llm-min-conf", type=float, default=0.9,
                   help="filter LLM may skip only on not_book with at least this confidence")
    g = ap.add_argument_group("LLM (both stages)")
    g.add_argument("--llm", metavar="MODEL", help="Ollama model, e.g. qwen2.5:14b (enables both LLM steps)")
    g.add_argument("--filter-llm", metavar="MODEL", help="optional different (smaller) model for stage 1")
    g.add_argument("--ollama-url", default="http://localhost:11434")
    g = ap.add_argument_group("search strings (stage 2)")
    g.add_argument("--verify", action="store_true", help="confirm titles/ISBNs with Open Library")
    g.add_argument("--min-score", type=float, default=80, help="Open Library match threshold (0-100)")
    g.add_argument("--contact", default="", help="email for Open Library's User-Agent")
    g.add_argument("--quote", action="store_true", help='wrap titles in quotes: "Title" Author')
    g.add_argument("--fresh", action="store_true", help="ignore search_cache.jsonl and redo stage 2")
    g.add_argument("--isbn", action="store_true",
                   help="old behavior: write the ISBN-13 instead of the title query when known")
    args = ap.parse_args()

    for d in ((args.library,) if args.no_compare else (args.library, args.markdown)):
        if not d.is_dir():
            print(f"Error: {d} is not a directory (use --no-compare to skip the Markdown check)",
                  file=sys.stderr)
            return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)

    books = scan_library(args)
    if not books:
        print("No books to process.")
        return 0
    build_search_strings(books, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
