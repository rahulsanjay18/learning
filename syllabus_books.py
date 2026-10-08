#!/usr/bin/env python3
"""
syllabus_books.py  (v2: many OCW / syllabus sites)

Scrapes public, English-language university syllabi, pulls every book they
cite, merges courses that different universities call by different names, and
writes search strings in the same format as book_search_strings.py plus a
topic -> courses -> books map.

Built-in sources (run `--list-sources` for details):
  mit           MIT OpenCourseWare, via the MIT Learn API (~2,500 courses)
  psu-dutton    Penn State EMS sample syllabi (dutton.psu.edu/courses)
  psu-stat      Penn State STAT ONLINE course pages
  tudelft       TU Delft OpenCourseWare (English courses only; Dutch ones skipped)
  yale          Open Yale Courses
  stanford-see  Stanford Engineering Everywhere
Add more with --sources-file my_sites.json (same fields as the built-ins);
an entry with the same name replaces a built-in.

How a generic source is crawled
  index page(s) -> links matching `course_link` -> each course page
  -> links on it that look like a syllabus / readings / textbook / literature
     page (same site, PDFs included) -> visible text
  Non-English pages are skipped. robots.txt is respected, ~1 req/s per host,
  every page is cached on disk.

Then, as before
  local LLM (Ollama, default qwen2.5:7b) extracts books as JSON; guards drop
  titles not on the page, ISBNs not on the page or failing the checksum, years
  not on the page, and authors whose surname isn't on the page.
  Courses: identical normalized titles merge; similar titles from DIFFERENT
  universities go to the LLM ("same course?") and merge only on a confident yes.
  Books merge across courses by ISBN or title + first-author surname;
  --verify checks them against Open Library.

Outputs (next to --out): search_strings.txt (title + last name per line;
--isbn to prefer ISBN-13), search_strings.tsv, book_list.txt,
topics_to_books.tsv/.json, needs_review.txt, skipped_courses.txt, caches.

Needs book_search_strings.py in the same folder.

Usage
    pip install requests beautifulsoup4 rapidfuzz tqdm pypdf
    ollama pull qwen2.5:7b
    python syllabus_books.py --contact you@example.com --verify
    python syllabus_books.py --contact you@example.com --sources yale,tudelft --max-courses 10
"""

import argparse
import hashlib
import io
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz, process
from tqdm import tqdm

try:
    import book_search_strings as bss
except ImportError:
    sys.exit("syllabus_books.py needs book_search_strings.py in the same folder.")

MIT_API = "https://api.learn.mit.edu/api/v1/courses/?platform=ocw"
PROMPT_VERSION = "v1"          # bump to invalidate extract_cache.jsonl after prompt edits

# =====================================================================
# Source configs. Fields:
#   inst          university name used in outputs and for "different school" checks
#   index         list of pages (HTML or RSS) that link to course pages
#   course_link   regex an absolute course URL must match
#   index_next    optional regex for "next page" links on index pages
#   pages         paths fetched relative to the course URL ("" = the course page itself)
#   follow        follow syllabus/readings-looking links found on those pages
#   follow_scope  "course" = link must be under the course URL, "host" = same site
#   title_from    "anchor" (index link text) or "page" (the course page's <h1>)
#   grad_min      course numbers >= this are graduate level (optional)
#   verified      structure checked by hand when this script was written
# =====================================================================

BUILTIN_SOURCES = {
    "psu-dutton": {
        "inst": "Penn State", "index": ["https://dutton.psu.edu/courses"],
        "course_link": r"_sample_syllabus/?$", "pages": [""], "follow": False,
        "title_from": "anchor", "grad_min": 500, "verified": True},
    "psu-stat": {
        "inst": "Penn State", "index": ["https://online.stat.psu.edu/statprogram/"],
        "course_link": r"/statprogram/stat\d{3}[a-z]?/?$", "pages": [""], "follow": False,
        "title_from": "page", "grad_min": 500, "verified": True},
    "tudelft": {
        "inst": "TU Delft", "index": ["https://ocw.tudelft.nl/courses-rss/"],
        "course_link": r"^https?://ocw\.tudelft\.nl/courses/[a-z0-9_-]+/?$",
        "pages": ["", "subjects/"], "follow": True, "follow_scope": "course",
        "title_from": "page", "verified": True},
    "yale": {
        "inst": "Yale", "index": ["https://oyc.yale.edu/courses"],
        "course_link": r"^https?://oyc\.yale\.edu/(?!courses|about|node|user|search|faq|terms|sites)"
                       r"[a-z0-9-]+/[a-z0-9-]+/?$",
        "pages": [""], "follow": True, "follow_scope": "host",
        "title_from": "page", "verified": True},
    "stanford-see": {
        "inst": "Stanford", "index": ["https://see.stanford.edu/Course"],
        "course_link": r"^https?://see\.stanford\.edu/Course/[A-Za-z]+\d+[A-Za-z]?/?$",
        "pages": [""], "follow": True, "follow_scope": "host",
        "title_from": "page", "grad_min": 200, "verified": False},
}
ALL_SOURCES = ["mit"] + list(BUILTIN_SOURCES)

# =====================================================================
# Small helpers
# =====================================================================

def letters(s: str) -> int:
    return sum(c.isalpha() for c in s)


def html_to_text(s: str) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(s or "", "html.parser").get_text(" ")).strip()


def uf_find(parent: dict, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def uf_union(parent: dict, a, b):
    ra, rb = uf_find(parent, a), uf_find(parent, b)
    if ra != rb:
        parent[rb] = ra


def load_jsonl(path: Path, field: str) -> dict:
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
                out[rec[field]] = rec
            except (json.JSONDecodeError, KeyError):
                pass
    return out


# =====================================================================
# Polite fetcher: robots.txt, per-host delay, retries, disk cache, PDF text
# =====================================================================

MAX_PDF_BYTES = 15_000_000


def pdf_to_text(data: bytes, max_pages: int = 25) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:max_pages])
    except Exception:
        return ""


class Fetcher:
    def __init__(self, cache_dir: Path, contact: str, delay: float, refetch: bool,
                 ca_bundle: str | None = None, insecure_hosts: tuple = ()):
        self.ua = f"syllabus-books/2.0 (+{contact})" if contact else "syllabus-books/2.0"
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": self.ua,                    # honest crawler UA; robots.txt rules match on it
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf;q=0.8,*/*;q=0.5",
            "Accept-Language": "en-US,en;q=0.8"})
        if ca_bundle:
            self.s.verify = ca_bundle
        self.insecure = {h.lower() for h in insecure_hosts}
        if self.insecure:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.ssl_failed: set[str] = set()
        self.loop_hosts: set[str] = set()
        self.redirect_loops = 0
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.refetch = refetch
        self.robots: dict[str, robotparser.RobotFileParser] = {}
        self.last: dict[str, float] = defaultdict(float)

    def _verify(self, url: str):
        return False if (urlparse(url).hostname or "").lower() in self.insecure else self.s.verify

    def _ssl_hint(self, url: str, e: Exception) -> None:
        host = urlparse(url).hostname or url
        if host not in self.ssl_failed:
            self.ssl_failed.add(host)
            tqdm.write(f"  SSL certificate check failed for {host}: {str(e)[:120]}\n"
                       f"    The server may send an incomplete chain, or your CA list is out of date.\n"
                       f"    Fix with --ca-bundle FILE, or skip checks for this site with --insecure-host {host}")

    def _redirect_fallback(self, url: str, err: Exception):
        """A redirect loop is often caused by session cookies or headers. Retry once with a clean,
        cookie-less request; if that loops too, report the loop (once per host) and give up."""
        try:
            return requests.get(url, timeout=60, verify=self._verify(url),
                                headers={"User-Agent": self.ua, "Accept": "*/*"})
        except requests.exceptions.TooManyRedirects as e2:
            err = e2
        except requests.RequestException:
            return None
        self.redirect_loops += 1
        host = urlparse(url).hostname or url
        if host not in self.loop_hosts:
            self.loop_hosts.add(host)
            resp = getattr(err, "response", None)
            hops, seen = [url], {url}
            for h in (resp.history if resp is not None else []):
                loc = urljoin(h.url, h.headers.get("Location", ""))
                hops.append(loc)
                if loc in seen:
                    break
                seen.add(loc)
            tqdm.write(f"  redirect loop on {host} (skipping such pages; cached so reruns skip them):\n    "
                       + "\n    -> ".join(hops[:6]))
        return None

    def _robots(self, url: str) -> robotparser.RobotFileParser:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            rp = robotparser.RobotFileParser()
            try:
                r = self.s.get(base + "/robots.txt", timeout=20, verify=self._verify(url))
                rp.parse(r.text.splitlines() if r.status_code == 200 else [])
            except requests.exceptions.SSLError as e:
                self._ssl_hint(url, e)
                rp.parse([])
            except requests.RequestException:
                rp.parse([])
            self.robots[base] = rp
        return self.robots[base]

    def allowed(self, url: str) -> bool:
        return self._robots(url).can_fetch(self.ua, url)

    def get(self, url: str, accept: str | None = None) -> tuple[int, str, str, str]:
        """(status, text, final_url, kind) with kind 'html' or 'pdf' (text already extracted).
        404s are cached too so reruns skip them."""
        ck = url if not accept else f"{url}|accept={accept}"   # separate cache entry per Accept
        cp = self.dir / (hashlib.sha1(ck.encode()).hexdigest() + ".json")
        if cp.exists() and not self.refetch:
            d = json.loads(cp.read_text(encoding="utf-8"))
            if d["status"] != 415:                   # older versions wrongly cached JSON as 415: refetch those
                return d["status"], d["text"], d["final"], d.get("kind", "html")
        host = urlparse(url).netloc
        wait = max(self.delay, self._robots(url).crawl_delay(self.ua) or 0)
        status, text, final, kind = 0, "", url, "html"
        if (urlparse(url).hostname or "") in self.ssl_failed and \
                (urlparse(url).hostname or "") in getattr(self, "_ssl_tried", set()):
            return 0, "", url, "html"                 # host already failed SSL twice: don't hammer it
        self._ssl_tried = getattr(self, "_ssl_tried", set()) | (
            {urlparse(url).hostname or ""} & self.ssl_failed)
        for attempt in range(4):
            gap = time.time() - self.last[host]
            if gap < wait:
                time.sleep(wait - gap)
            self.last[host] = time.time()
            try:
                r = self.s.get(url, timeout=60, verify=self._verify(url),
                               headers={"Accept": accept} if accept else None)
            except requests.exceptions.SSLError as e:
                self._ssl_hint(url, e)
                break
            except requests.exceptions.TooManyRedirects as e:
                r = self._redirect_fallback(url, e)
                if r is None:                        # a real loop: remember it, don't retry
                    status = 310                     # set by this script: redirect loop
                    cp.write_text(json.dumps({"status": status, "text": "", "final": url, "kind": "html"}),
                                  encoding="utf-8")
                    break
            except requests.RequestException as e:
                tqdm.write(f"  fetch error {url}: {e}")
                time.sleep(2 ** attempt)
                continue
            status, final = r.status_code, r.url
            if status == 429 or status >= 500:
                time.sleep(int(r.headers.get("Retry-After", 0) or 0) or 2 ** (attempt + 1))
                continue
            if status == 200:
                ctype = r.headers.get("Content-Type", "").lower()
                if "pdf" in ctype or urlparse(final).path.lower().endswith(".pdf"):
                    kind = "pdf"
                    text = pdf_to_text(r.content) if len(r.content) <= MAX_PDF_BYTES else ""
                elif not ctype or any(t in ctype for t in ("html", "xml", "json", "text/")):
                    text = r.text                    # pages, RSS feeds, and the MIT API's JSON
                else:
                    status = 415                     # images, video, zips...: skipped (set by this script, not the server)
            cp.write_text(json.dumps({"status": status, "text": text, "final": final, "kind": kind}),
                          encoding="utf-8")
            break
        return status, text, final, kind


# =====================================================================
# Course discovery
# =====================================================================

CODE_RE = re.compile(r"^([A-Za-z]{2,6})\s*(\d{1,3}[A-Za-z]{0,2})\b[\s:.\-–—]*(.*)$")


def split_code(s: str) -> tuple[str, str]:
    """'EME 801 Energy Markets' / 'STAT 414: Intro...' -> ('EME 801', 'Energy Markets')."""
    s = re.sub(r"(?i)\s*\|.*$|\s*sample syllabus\s*$", "", s).strip()
    m = CODE_RE.match(s)
    if m and letters(m.group(3)) >= 3:
        title = re.sub(r"^\([^)]*\)\s*", "", m.group(3).strip())     # 'EME 589 (EME 597) Title'
        return f"{m.group(1).upper()} {m.group(2).upper()}", title
    return "", s


def mit_code(slug: str) -> str:
    m = re.match(r"^(res-)?([0-9]+[a-z]?|[a-z]{2,4})-([0-9]+[a-z]*)-", slug)
    return "" if not m else (("RES." if m.group(1) else "") + f"{m.group(2)}.{m.group(3)}").upper()


def level_from_code(code: str, grad_min: int | None) -> str | None:
    m = re.search(r"\d+", code or "")
    if not m or not grad_min:
        return None
    return "Graduate" if int(m.group()) >= grad_min else "Undergraduate"


def discover_mit(f: Fetcher, args) -> list[dict]:
    url, out = MIT_API + "&limit=100", []
    flt = re.compile(args.mit_filter, re.I) if args.mit_filter else None
    with tqdm(desc="mit: course list", unit="course") as bar:
        while url:
            # Django REST Framework answers Accept: text/html with its HTML "browsable API" page,
            # so the API must be asked for JSON explicitly.
            st, txt, _, _ = f.get(url, accept="application/json")
            if st != 200:
                tqdm.write(f"  MIT API returned HTTP {st}; stopping MIT discovery")
                break
            try:
                d = json.loads(txt)
            except json.JSONDecodeError:
                snippet = " ".join(txt.split())[:160]
                tqdm.write(f"  MIT API did not return JSON (got: {snippet!r}); stopping MIT discovery")
                break
            for c in d.get("results") or []:
                r0 = (c.get("runs") or [{}])[0]
                cu = c.get("url") or r0.get("url") or ""
                if "ocw.mit.edu/courses/" not in cu:
                    continue
                cu = cu.rstrip("/") + "/"
                topics = [t.get("name") for t in c.get("topics") or [] if t.get("name")]
                title = c.get("title") or ""
                if flt and not flt.search(title + " " + " ".join(topics)):
                    continue
                levels = {lv.get("name") for lv in r0.get("level") or [] if isinstance(lv, dict)}
                slug = cu.rstrip("/").rsplit("/", 1)[-1]
                out.append({
                    "id": f"mit:{slug}", "source": "mit", "inst": "MIT", "code": mit_code(slug),
                    "title": title,
                    "term": " ".join(str(x) for x in (r0.get("semester"), r0.get("year")) if x),
                    "level": next(iter(levels)) if len(levels) == 1 else None,
                    "topics": topics, "url": cu,
                    "desc": html_to_text(r0.get("description") or c.get("description") or "")[:800],
                    "pages": [cu + "pages/syllabus/", cu + "pages/readings/"],
                    "follow": False, "title_from": "known"})
                bar.update()
            url = d.get("next")
            if args.max_courses and len(out) >= args.max_courses:
                break
    return out[: args.max_courses or None]


def discover_generic(name: str, cfg: dict, f: Fetcher, args) -> list[dict]:
    pat = re.compile(cfg["course_link"], re.I)
    nxt = re.compile(cfg["index_next"], re.I) if cfg.get("index_next") else None
    queue, seen_idx = list(cfg["index"]), set()
    found: dict[str, str] = {}
    while queue and len(seen_idx) < args.max_index_pages:
        idx = queue.pop(0)
        if idx in seen_idx:
            continue
        seen_idx.add(idx)
        if not f.allowed(idx):
            tqdm.write(f"  {name}: robots.txt disallows {idx}")
            continue
        st, html, final, _ = f.get(idx)
        if st != 200:
            tqdm.write(f"  {name}: {idx} returned HTTP {st}")
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(final, a["href"]).split("#")[0].split("?")[0]
            text = a.get_text(" ", strip=True)
            if pat.search(href):
                if text and (href not in found or len(text) > len(found[href])):
                    found[href] = text
                found.setdefault(href, "")
            elif nxt and (nxt.search(href) or nxt.search(text)) and urlparse(href).netloc == urlparse(idx).netloc:
                queue.append(href)
        for u in re.findall(r"https?://[^\s\"'<>]+", html):   # RSS/XML feeds: bare URLs
            u = u.split("#")[0].rstrip(".,);")
            if pat.search(u):
                found.setdefault(u, "")
    out = []
    for href, text in found.items():
        code, title = split_code(text) if cfg.get("title_from") == "anchor" else ("", "")
        if not title:
            title = href.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")
        out.append({
            "id": f"{name}:{hashlib.sha1(href.encode()).hexdigest()[:12]}", "source": name,
            "inst": cfg["inst"], "code": code, "title": title, "term": "",
            "level": level_from_code(code, cfg.get("grad_min")), "topics": [], "url": href,
            "desc": "", "pages": [urljoin(href.rstrip("/") + "/", p) if p else href
                                  for p in cfg.get("pages", [""])],
            "follow": cfg.get("follow", False), "follow_scope": cfg.get("follow_scope", "course"),
            "title_from": "anchor" if cfg.get("title_from") == "anchor" and text else "page",
            "grad_min": cfg.get("grad_min")})
    print(f"  {name}: {len(out)} course(s)")
    return out[: args.max_courses or None]


def extra_urls(urls: list[str], inst: str) -> list[dict]:
    return [{"id": f"url:{hashlib.sha1(u.encode()).hexdigest()[:12]}", "source": "url", "inst": inst,
             "code": "", "title": u, "term": "", "level": None, "topics": [], "url": u, "desc": "",
             "pages": [u], "follow": True, "follow_scope": "host", "title_from": "page"} for u in urls]


# =====================================================================
# Page text, language check, syllabus links
# =====================================================================

CUE = re.compile(r"(?i)\b(?:text ?books?|texts?|readings?|required|recommended|optional|materials?|"
                 r"isbn|edition|ed\.|press|publisher|references?|bibliography|books?|literature)\b")
SYL_LINK = re.compile(r"(?i)syllab|reading|text ?books?|\bbooks?\b|literature|bibliograph|"
                      r"course[ _-]?(?:info|materials|outline|description)|required[ _-]materials|"
                      r"references|resources")
SKIP_EXT = re.compile(r"(?i)\.(?:jpe?g|png|gif|svg|webp|mp[34]|m4a|mov|avi|zip|rar|7z|pptx?|xlsx?|docx?|"
                      r"srt|vtt|ipynb|py|m|tex)$")
EN_WORDS = set("the and of to in is for that with as on are this by be or from an it at which will "
               "students course you can not have".split())
NL_WORDS = set("de het een en van in is voor dat met als op zijn deze door te of uit wordt bij "
               "worden naar niet ook".split())


def is_english(text: str) -> bool:
    words = re.findall(r"[a-zA-Z]+", text.lower())[:3000]
    if len(words) < 40:
        return True                                  # too little text to judge; let it through
    en = sum(w in EN_WORDS for w in words) / len(words)
    other = sum(w in NL_WORDS for w in words) / len(words)
    return en >= 0.05 and en > other


def page_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else (soup.title.get_text(strip=True) if soup.title else "")
    for t in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "button"]):
        t.decompose()
    text = ""
    for sel in ("main", "[role=main]", "article", "#main-content", "#content"):
        node = soup.select_one(sel)
        if node:
            text = node.get_text("\n")
            if len(text.strip()) >= 200:
                break
    if len(text.strip()) < 200:
        text = (soup.body or soup).get_text("\n")
    lines = (re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines())
    return title, "\n".join(ln for ln in lines if ln)


def clean_pdf_text(text: str) -> str:
    lines = (re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines())
    return "\n".join(ln for ln in lines if ln)


def syllabus_links(html: str, base: str, course_url: str, scope: str) -> list[str]:
    host = urlparse(course_url).netloc
    prefix = course_url.rstrip("/")
    scored = []
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = urljoin(base, a["href"]).split("#")[0]
        if not href.startswith("http") or urlparse(href).netloc != host or SKIP_EXT.search(urlparse(href).path):
            continue
        if scope == "course" and not href.startswith(prefix):
            continue
        label = a.get_text(" ", strip=True) + " " + urlparse(href).path
        if SYL_LINK.search(label):
            scored.append((0 if re.search(r"(?i)syllab|text ?book|reading", label) else 1, href))
    seen, out = set(), []
    for _, h in sorted(scored):
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out


# =====================================================================
# LLM (Ollama structured outputs)
# =====================================================================

def focus_chunks(text: str, chunk_chars: int, max_chunks: int) -> list[str]:
    """Keep lines around book cues, then cut into LLM-sized chunks."""
    lines = text.split("\n")
    if len(text) > chunk_chars:
        keep: set[int] = set()
        for i, ln in enumerate(lines):
            if CUE.search(ln) or bss.isbns_in(ln):
                keep.update(range(max(0, i - 3), min(len(lines), i + 12)))
        lines = [lines[i] for i in sorted(keep)]
    chunks, cur = [], ""
    for ln in lines:
        if cur and len(cur) + len(ln) + 1 > chunk_chars:
            chunks.append(cur)
            cur = ""
        cur += ln + "\n"
    if cur.strip():
        chunks.append(cur)
    return chunks[:max_chunks]


def ollama_json(prompt: str, schema: dict, args) -> dict:
    r = requests.post(f"{args.ollama_url}/api/generate", timeout=300, json={
        "model": args.llm, "prompt": prompt, "format": schema, "stream": False,
        "options": {"temperature": 0, "num_ctx": args.num_ctx}})
    r.raise_for_status()
    return json.loads(r.json()["response"])


def check_ollama(args) -> None:
    try:
        tags = requests.get(f"{args.ollama_url}/api/tags", timeout=10).json()
    except Exception as e:
        sys.exit(f"Can't reach Ollama at {args.ollama_url} ({e}). Start it with `ollama serve`.")
    names = {m.get("name", "") for m in tags.get("models", [])}
    if args.llm not in names and f"{args.llm}:latest" not in names:
        sys.exit(f"Model {args.llm} isn't pulled. Run: ollama pull {args.llm}")


BOOK_SCHEMA = {
    "type": "object",
    "properties": {"books": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "quote": {"type": "string"},
            "title": {"type": "string"},
            "subtitle": {"type": "string"},
            "authors": {"type": "array", "items": {"type": "string"}},
            "edition": {"type": "string"},
            "year": {"type": "string"},
            "isbn": {"type": "string"},
            "publisher": {"type": "string"},
            "role": {"type": "string", "enum": ["required", "recommended", "reference", "unknown"]},
        },
        "required": ["quote", "title", "subtitle", "authors", "edition", "year", "isbn",
                     "publisher", "role"]}}},
    "required": ["books"],
}

BOOK_PROMPT = """You read part of a university course syllabus and list every BOOK it cites.

Course: {course} ({inst})

Count as a book: textbooks, monographs, novels, plays, anthologies, handbooks, workbooks,
published lab manuals, and edited volumes.
Do NOT include: journal or magazine articles, papers, book chapters cited as separate readings,
the instructor's own lecture notes or course readers, websites, software, videos, or datasets.
If only an abbreviation appears (e.g. "[CLRS] Ch. 3") and the full citation is not in this text,
skip it.

For each book:
- quote: copy the exact words from the text where the book is cited (at most 25 words)
- title: main title only, as written in the text, without subtitle or edition
- subtitle: the subtitle if written, else ""
- authors: people as "First Last" (convert "Last, F."); [] if none given; no publishers
- edition: e.g. "3rd" if stated, else ""
- year, isbn, publisher: only if written in the text, else ""
- role: "required", "recommended", "reference" (optional/further reading), or "unknown"

If the text cites no books, return {{"books": []}}.

Syllabus text:
\"\"\"
{text}
\"\"\"
"""

MERGE_SCHEMA = {
    "type": "object",
    "properties": {
        "reason": {"type": "string"},
        "same_course": {"type": "boolean"},
        "confidence": {"type": "number"},
        "topic": {"type": "string"},
    },
    "required": ["reason", "same_course", "confidence", "topic"],
}

MERGE_PROMPT = """Different universities may give the same course different names. Decide whether
these two courses teach essentially the same subject at the same level, so the same textbook would
fit both. Related-but-different subjects (e.g. "Probability" vs "Statistical Inference", or an
intro course vs a graduate course) are NOT the same.

Course A ({inst_a}, {level_a}): {title_a}
Description A: {desc_a}

Course B ({inst_b}, {level_b}): {title_b}
Description B: {desc_b}

Respond in JSON: reason (one sentence), same_course (true/false), confidence (0 to 1),
topic (a short neutral subject name covering both, e.g. "Probability Theory")."""


# =====================================================================
# Book extraction with grounding guards
# =====================================================================

GENERIC_TITLE = re.compile(r"(?i)^(?:lecture notes?|course notes?|class notes?|notes|readings?|"
                           r"textbooks?|course reader|handouts?|slides|syllabus|none|n/?a|tbd)$")


def grounded(phrase: str, text_key: str, min_score: int = 90) -> bool:
    k = bss.key(phrase)
    return bool(k) and (k in text_key or fuzz.partial_ratio(k, text_key) >= min_score)


def clean_book(b: dict, text: str, text_key: str, page_isbns: list[str]) -> dict | None:
    title = str(b.get("title") or "").strip().strip("\"'“”‘’*_ .,:;")
    if letters(title) < 3 or GENERIC_TITLE.match(title) or not grounded(title, text_key):
        return None                                   # title not on the page: hallucinated
    sub = str(b.get("subtitle") or "").strip()
    if sub and not grounded(sub, text_key, 85):
        sub = ""
    authors = []
    for a in b.get("authors") or []:
        a = str(a).strip()
        ln = bss.last_name(a)
        if a and letters(ln) >= 2 and re.search(rf"(?i)\b{re.escape(ln)}\b", text) \
                and not re.search(r"(?i)\b(?:press|publishing|inc|ltd|various|unknown)\b", a):
            authors.append(a)
    isbn = bss.to_isbn13(str(b.get("isbn") or ""))
    if isbn not in page_isbns:
        isbn = None
    year = str(b.get("year") or "").strip()
    if not (re.fullmatch(r"1[5-9]\d\d|20\d\d", year) and re.search(rf"\b{year}\b", text)):
        year = None
    role = b.get("role") if b.get("role") in {"required", "recommended", "reference"} else "unknown"
    return {"title": title, "subtitle": sub or None, "authors": authors,
            "edition": (str(b.get("edition") or "").strip() or None), "year": year, "isbn": isbn,
            "publisher": (str(b.get("publisher") or "").strip() or None), "role": role,
            "confidence": None, "source": "llm"}


def book_key(b: dict) -> str:
    if b["title"]:
        ln = bss.last_name(b["authors"][0]) if b["authors"] else ""
        return f"t:{bss.key(b['title'])}|{bss.key(ln)}"
    return f"i:{b['isbn']}"


def attach_nearby_isbns(found: dict, text: str, window: int = 300) -> None:
    """Give an unclaimed ISBN to the book whose title appears just before it on the page."""
    claimed = {b["isbn"] for b in found.values() if b["isbn"]}
    low = text.lower()
    spots = []
    for m in re.finditer(r"(?<![\dX])(?:97[89][\d-]{10,14}|\d{9}[\dXx])(?![\dXx])", text):
        i13 = bss.to_isbn13(m.group(0))
        if i13 and i13 not in claimed:
            spots.append((m.start(), i13))
    for b in found.values():
        if b["isbn"] or not b["title"]:
            continue
        starts = [m.start() for m in re.finditer(re.escape(b["title"].lower()), low)]
        best = min(((pos - st, i13) for st in starts for pos, i13 in spots if 0 < pos - st <= window),
                   default=None)
        if best and best[1] not in claimed:
            b["isbn"] = best[1]
            claimed.add(best[1])


def extract_course(c: dict, f: Fetcher, args) -> dict:
    rec = {"key": f"{c['id']}|{args.llm}|{PROMPT_VERSION}", **c, "urls": [], "books": [], "status": "ok"}
    queue = [(u, 0) for u in c["pages"]]
    visited, texts, blocked = set(), [], False
    while queue and len(visited) < len(c["pages"]) + args.max_follow:
        u, depth = queue.pop(0)
        if u in visited:
            continue
        visited.add(u)
        if not f.allowed(u):
            blocked = True
            continue
        st, body, final, kind = f.get(u)
        if st != 200 or not body:
            continue
        if kind == "pdf":
            h1, text = "", clean_pdf_text(body)
        else:
            h1, text = page_text(body)
            if c.get("follow") and depth == 0:
                queue += [(h, 1) for h in syllabus_links(body, final, c["url"], c.get("follow_scope", "course"))
                          if h not in visited]
        if depth == 0 and rec.get("title_from") == "page" and h1:
            code, title = split_code(h1)
            rec["code"] = rec["code"] or code
            if title and letters(title) >= 3:
                rec["title"] = title
            rec["level"] = rec["level"] or level_from_code(rec["code"], c.get("grad_min"))
            rec["title_from"] = "done"
        if text:
            texts.append(text)
            rec["urls"].append(final or u)
    if not texts:
        rec["status"] = "robots.txt disallows" if blocked else "no syllabus page"
        return rec
    full = "\n\n".join(texts)
    if not rec["desc"]:
        rec["desc"] = full[:800]
    if not is_english(full):
        rec["status"] = "not English"
        return rec
    page_isbns = bss.isbns_in(full)
    if not CUE.search(full) and not page_isbns:
        rec["status"] = "no book mentions"
        return rec

    text_key = bss.key(full)
    found: dict[str, dict] = {}
    for chunk in focus_chunks(full, args.chunk_chars, args.max_chunks):
        try:
            raw = ollama_json(BOOK_PROMPT.format(course=rec["title"], inst=rec["inst"], text=chunk),
                              BOOK_SCHEMA, args).get("books") or []
        except Exception as e:
            rec["status"] = f"LLM error: {e}"
            continue
        for b in raw:
            cb = clean_book(b, full, text_key, page_isbns)
            if cb:
                k = book_key(cb)
                if k in found:                       # same book in two chunks: keep the richer one
                    old = found[k]
                    for fld in ("isbn", "year", "edition", "subtitle", "publisher"):
                        old[fld] = old[fld] or cb[fld]
                    if len(cb["authors"]) > len(old["authors"]):
                        old["authors"] = cb["authors"]
                else:
                    found[k] = cb
    attach_nearby_isbns(found, full)
    have = {b["isbn"] for b in found.values() if b["isbn"]}
    for i13 in page_isbns:                           # ISBNs still unclaimed: keep as ISBN-only books
        if i13 not in have:
            found[f"i:{i13}"] = {"title": "", "subtitle": None, "authors": [], "edition": None,
                                 "year": None, "isbn": i13, "publisher": None, "role": "unknown",
                                 "confidence": None, "source": "isbn-on-page"}
    rec["books"] = list(found.values())
    if not rec["books"] and rec["status"] == "ok":
        rec["status"] = "no books found"
    return rec


# =====================================================================
# Course dedupe across universities
# =====================================================================

ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5"}
PREFIX = re.compile(r"^(?:an |the )?(?:introduction to|intro to|introductory|fundamentals of|"
                    r"principles of|foundations of|elements of|topics in|special topics in|"
                    r"survey of|basic|elementary|applied)\s+")
FILLER = re.compile(r"\b(?:and|of|the|for|in|with|to|a|an)\b")


def norm_title(t: str) -> str:
    t = bss.key(re.sub(r"\([^)]*\)", " ", t))
    t = " ".join(ROMAN.get(w, w) for w in t.split())
    prev = None
    while prev != t:
        prev, t = t, PREFIX.sub("", t)
    return " ".join(FILLER.sub(" ", t).split())


def levels_ok(a, b) -> bool:
    return not a or not b or a == b


def group_courses(courses: list[dict], args, cache: dict, cache_f) -> tuple[dict, dict, list]:
    """Returns (course_id -> root_id, root_id -> topic name, review notes).
    Only courses from DIFFERENT universities are sent to the LLM; within one
    university only identical normalized titles merge (e.g. MIT runs of 6.006)."""
    parent = {c["id"]: c["id"] for c in courses}
    by_id = {c["id"]: c for c in courses}
    nt = {c["id"]: norm_title(c["title"]) for c in courses}
    llm_topic: dict[str, list[str]] = defaultdict(list)
    review = []

    by_nt = defaultdict(list)                        # 1) identical normalized titles
    for c in courses:
        if nt[c["id"]]:
            by_nt[nt[c["id"]]].append(c)
    for group in by_nt.values():
        for c in group[1:]:
            if levels_ok(group[0]["level"], c["level"]):
                uf_union(parent, group[0]["id"], c["id"])

    # 2) similar titles across universities. The biggest school is only a target, so
    #    MIT's ~2,500 courses are compared against everyone else's, never against each other.
    named = [c for c in courses if nt[c["id"]]]
    sizes = Counter(c["inst"] for c in named)
    biggest = sizes.most_common(1)[0][0] if sizes else None
    all_nts = [nt[c["id"]] for c in named]
    pairs, seen_pairs = [], set()
    for p in named:
        if p["inst"] == biggest:
            continue
        nums = set(re.findall(r"\b\d+\b", nt[p["id"]]))
        seen_roots = set()
        for _, score, j in process.extract(nt[p["id"]], all_nts, scorer=fuzz.token_set_ratio,
                                           limit=60, score_cutoff=args.cand_min):
            m = named[j]
            if m["inst"] == p["inst"]:
                continue
            r = uf_find(parent, m["id"])
            pk = tuple(sorted((p["id"], m["id"])))
            if pk in seen_pairs or r in seen_roots or r == uf_find(parent, p["id"]) \
                    or not levels_ok(p["level"], m["level"]) \
                    or set(re.findall(r"\b\d+\b", nt[m["id"]])) != nums:
                continue
            seen_pairs.add(pk)
            seen_roots.add(r)
            pairs.append((p, m))
            if len(seen_roots) >= args.cand_k:
                break

    for p, m in tqdm(pairs, desc="Course dedupe", unit="pair", dynamic_ncols=True):
        if uf_find(parent, p["id"]) == uf_find(parent, m["id"]):
            continue
        if fuzz.ratio(nt[p["id"]], nt[m["id"]]) >= 97:
            uf_union(parent, m["id"], p["id"])
            continue
        ck = "|".join(sorted([p["id"], m["id"]])) + f"|{args.llm}|{PROMPT_VERSION}"
        d = cache.get(ck)
        if d is None:
            try:
                d = ollama_json(MERGE_PROMPT.format(
                    inst_a=m["inst"], level_a=m["level"] or "level unknown", title_a=m["title"],
                    desc_a=m["desc"][:700] or "(none)", inst_b=p["inst"],
                    level_b=p["level"] or "level unknown", title_b=p["title"],
                    desc_b=p["desc"][:700] or "(none)"), MERGE_SCHEMA, args)
            except Exception as e:
                tqdm.write(f"  merge LLM error ({p['title']} / {m['title']}): {e}")
                continue
            d = {"key": ck, **d}
            cache[ck] = d
            cache_f.write(json.dumps(d, ensure_ascii=False) + "\n")
            cache_f.flush()
        conf = float(d.get("confidence") or 0)
        conf = conf / 100 if conf > 1 else conf
        if d.get("same_course") and conf >= args.merge_min_conf:
            uf_union(parent, m["id"], p["id"])
            if str(d.get("topic") or "").strip():
                llm_topic[m["id"]].append(d["topic"].strip())
            tqdm.write(f"  merged ({conf:.2f}): {p['inst']} {p['title']}  ==  {m['inst']} {m['title']}")
        elif d.get("same_course") and conf >= 0.5:
            review.append(f"possible duplicate course ({conf:.2f}): {d.get('reason', '')}\t"
                          f"{p['inst']} {p['title']} == {m['inst']} {m['title']}\t{p['url']} | {m['url']}")

    roots = {cid: uf_find(parent, cid) for cid in parent}
    members = defaultdict(list)
    for cid, r in roots.items():
        members[r].append(cid)
    topics = {}
    for r, ids in members.items():
        names = [t for cid in ids for t in llm_topic.get(cid, [])]
        if names:
            topics[r] = Counter(names).most_common(1)[0][0]
        else:
            titles = Counter(by_id[cid]["title"] for cid in ids)
            topics[r] = min(titles, key=lambda t: (-titles[t], len(t)))
    return roots, topics, review


ROLE_RANK = {"required": 0, "recommended": 1, "reference": 2, "unknown": 3}


def verify_book(b: dict, session: requests.Session, args) -> dict:
    """Open Library check; if an ISBN points at a different title, drop the ISBN and retry by title."""
    v = bss.openlib_verify(dict(b), session, args.min_score)
    if b["title"] and b["isbn"] and v.get("verify_score") is not None and v["verify_score"] < args.min_score:
        retry = bss.openlib_verify(dict(b, isbn=None), session, args.min_score)
        retry["verify_note"] = ((retry.get("verify_note") or "") + f" ISBN {b['isbn']} matched a different "
                                f"title ({v['title']}); dropped").strip()
        return retry
    return v


def merge_books(occ: list[dict]) -> list[dict]:
    """occ: one dict per (course, book). Groups by ISBN or title+surname."""
    parent = {i: i for i in range(len(occ))}
    first: dict[str, int] = {}
    title_keys = defaultdict(set)
    for i, b in enumerate(occ):
        keys = [book_key(b)] + ([f"i:{b['isbn']}"] if b["isbn"] else [])
        for k in keys:
            if k in first:
                uf_union(parent, first[k], i)
            else:
                first[k] = i
        if b["title"]:
            title_keys[bss.key(b["title"])].add(book_key(b))
    for i, b in enumerate(occ):                      # no author on this one: attach to the unique authored match
        if b["title"] and not b["authors"]:
            others = [k for k in title_keys[bss.key(b["title"])] if not k.endswith("|")]
            if len(others) == 1:
                uf_union(parent, first[others[0]], i)

    groups = defaultdict(list)
    for i in range(len(occ)):
        groups[uf_find(parent, i)].append(occ[i])
    merged = []
    for g in groups.values():
        rep = max(g, key=lambda b: ("openlibrary" in b["source"], b.get("verify_score") or 0,
                                    bool(b["title"]), len(b["authors"])))
        isbns = Counter(b["isbn"] for b in g if b["isbn"])
        eds = Counter(b["edition"] for b in g if b["edition"])
        notes = sorted({b["verify_note"] for b in g if b.get("verify_note")})
        merged.append({
            "title": rep["title"], "subtitle": rep["subtitle"], "authors": rep["authors"],
            "edition": eds.most_common(1)[0][0] if eds else None,
            "year": rep["year"], "isbn": isbns.most_common(1)[0][0] if isbns else rep["isbn"],
            "confidence": None, "source": rep["source"], "verify_score": rep.get("verify_score"),
            "verify_note": "; ".join(notes) or None,
            "role": min((b["role"] for b in g), key=ROLE_RANK.get),
            "courses": sorted({b["course_id"] for b in g}),
            "urls": sorted({u for b in g for u in b["urls"]}),
        })
    return merged


# =====================================================================
# Main
# =====================================================================

def load_sources(args) -> dict:
    srcs = {k: dict(v) for k, v in BUILTIN_SOURCES.items()}
    if args.sources_file:
        extra = json.loads(Path(args.sources_file).read_text(encoding="utf-8"))
        for e in (extra if isinstance(extra, list) else [extra]):
            missing = {"name", "inst", "index", "course_link"} - set(e)
            if missing:
                sys.exit(f"--sources-file entry {e.get('name', '?')} is missing {sorted(missing)}")
            srcs[e["name"]] = {k: v for k, v in e.items() if k != "name"}
    return srcs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_argument_group("sources")
    g.add_argument("--sources", default="all",
                   help="comma list (default: all). Built-ins: " + ",".join(ALL_SOURCES))
    g.add_argument("--sources-file", metavar="JSON", help="extra/override site configs (see --list-sources)")
    g.add_argument("--list-sources", action="store_true", help="print the source configs and exit")
    g.add_argument("--extra-url", "--psu-url", action="append", default=[], metavar="URL",
                   help="any extra syllabus page (repeatable); use with --extra-inst")
    g.add_argument("--extra-inst", default="Other", help="university name for --extra-url pages")
    g.add_argument("--mit-filter", metavar="REGEX", help="only MIT courses whose title/topics match")
    g.add_argument("--max-courses", type=int, default=0, help="cap per source (for testing)")
    g.add_argument("--max-index-pages", type=int, default=50, help="index pages per source, max")
    g.add_argument("--max-follow", type=int, default=4, help="syllabus-like links followed per course")
    g = ap.add_argument_group("crawling")
    g.add_argument("--contact", default="", help="your email; sent in the User-Agent (please set it)")
    g.add_argument("--delay", type=float, default=1.0, help="seconds between requests per host")
    g.add_argument("--refetch", action="store_true", help="ignore the page cache")
    g.add_argument("--ca-bundle", metavar="PEM", help="CA file to trust (e.g. certifi bundle + a missing intermediate)")
    g.add_argument("--insecure-host", action="append", default=[], metavar="HOST",
                   help="skip TLS certificate checks for this host only (repeatable)")
    g = ap.add_argument_group("LLM")
    g.add_argument("--llm", default="qwen2.5:7b", help="Ollama model")
    g.add_argument("--ollama-url", default="http://localhost:11434")
    g.add_argument("--num-ctx", type=int, default=8192, help="Ollama context window")
    g.add_argument("--chunk-chars", type=int, default=6000)
    g.add_argument("--max-chunks", type=int, default=4, help="LLM calls per course, max")
    g = ap.add_argument_group("course dedupe")
    g.add_argument("--cand-min", type=float, default=75, help="title similarity to ask the LLM about a merge")
    g.add_argument("--cand-k", type=int, default=3, help="candidates per course from other universities")
    g.add_argument("--merge-min-conf", type=float, default=0.8)
    g = ap.add_argument_group("output")
    g.add_argument("--out", type=Path, default=Path("syllabus_books/search_strings.txt"))
    g.add_argument("--verify", action="store_true", help="check books with Open Library")
    g.add_argument("--min-score", type=float, default=80)
    g.add_argument("--isbn", action="store_true", help="search_strings.txt: ISBN-13 instead of title when known")
    g.add_argument("--quote", action="store_true", help='wrap titles in quotes: "Title" Author')
    g.add_argument("--fresh", action="store_true", help="ignore extract/merge/verify caches")
    args = ap.parse_args()

    sources = load_sources(args)
    if args.list_sources:
        print(json.dumps({"mit": {"inst": "MIT", "index": [MIT_API], "verified": True}, **sources}, indent=2))
        return 0
    wanted = list(dict.fromkeys(["mit"] + list(sources))) if args.sources == "all" \
        else [s.strip() for s in args.sources.split(",") if s.strip()]
    unknown = [s for s in wanted if s != "mit" and s not in sources]
    if unknown:
        sys.exit(f"unknown source(s): {unknown}. Known: {['mit'] + list(sources)}")

    out_dir = args.out.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    check_ollama(args)
    f = Fetcher(out_dir / "page_cache", args.contact, args.delay, args.refetch,
                args.ca_bundle, tuple(args.insecure_host))

    # 1. discover
    courses = []
    for s in wanted:
        if s == "mit":
            courses += discover_mit(f, args)
        else:
            if not sources[s].get("verified", True):
                print(f"  note: source '{s}' was not hand-checked; inspect skipped_courses.txt after the run")
            courses += discover_generic(s, sources[s], f, args)
    courses += extra_urls(args.extra_url, args.extra_inst)
    courses = list({c["id"]: c for c in courses}.values())
    print("Courses: " + ", ".join(f"{i} {n}" for i, n in Counter(c["inst"] for c in courses).most_common()))

    # 2. extract books per course
    ex_path = out_dir / "extract_cache.jsonl"
    ex_cache = {} if args.fresh else load_jsonl(ex_path, "key")
    recs = []
    with open(ex_path, "a", encoding="utf-8") as ex_f:
        for c in tqdm(courses, desc="Syllabi", unit="course", dynamic_ncols=True):
            k = f"{c['id']}|{args.llm}|{PROMPT_VERSION}"
            rec = ex_cache.get(k)
            if rec is None:
                rec = extract_course(c, f, args)
                if not rec["status"].startswith("LLM error"):
                    ex_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    ex_f.flush()
            recs.append(rec)
    if f.redirect_loops:
        print(f"  {f.redirect_loops} page(s) skipped due to redirect loops on: {', '.join(sorted(f.loop_hosts))}")
    skipped = [f"{r['status']}\t{' '.join(x for x in (r['inst'], r['code'], r['title']) if x)}\t{r['url']}"
               for r in recs if r["status"] != "ok"]
    recs = [r for r in recs if r["status"] != "not English"]

    # 3. course dedupe
    mg_path = out_dir / "merge_cache.jsonl"
    mg_cache = {} if args.fresh else load_jsonl(mg_path, "key")
    with open(mg_path, "a", encoding="utf-8") as mg_f:
        roots, topics, review = group_courses(recs, args, mg_cache, mg_f)
    by_id = {r["id"]: r for r in recs}

    # 4. books: dedupe, verify, dedupe again
    occ = [{**b, "course_id": r["id"], "urls": r["urls"]} for r in recs for b in r["books"]]
    books = merge_books(occ)
    if args.verify:
        session = requests.Session()
        session.headers["User-Agent"] = f"syllabus-books/2.0 ({args.contact})" if args.contact \
            else "syllabus-books/2.0"
        vcache_path = out_dir / "verify_cache.jsonl"
        vcache = {} if args.fresh else load_jsonl(vcache_path, "vkey")
        with open(vcache_path, "a", encoding="utf-8") as vf:
            for i, b in enumerate(tqdm(books, desc="Open Library", unit="book", dynamic_ncols=True)):
                vk = f"{b['isbn']}|{b['title']}|{';'.join(b['authors'])}"
                v = vcache.get(vk)
                if v is None:
                    v = {"vkey": vk, **verify_book(b, session, args)}
                    vf.write(json.dumps(v, ensure_ascii=False) + "\n")
                    vf.flush()
                books[i] = {**b, **{k: v[k] for k in v if k not in ("vkey", "courses", "urls", "role")}}
        occ = [{**b, "course_id": cid, "urls": b["urls"]} for b in books for cid in b["courses"]]
        books = merge_books(occ)

    # 5. outputs
    for b in books:
        b.update(bss.build_queries(b, args.quote))
        b["topics"] = sorted({topics[roots[cid]] for cid in b["courses"]})
    books.sort(key=lambda b: (b["title"] or "~", b["isbn"] or ""))

    best, seen = [], set()
    for b in books:
        q = (b["query_isbn"] if args.isbn or not b["title"] else "") or b["query"]
        if q and q.lower() not in seen:
            seen.add(q.lower())
            best.append(q)
    args.out.write_text("\n".join(best) + "\n", encoding="utf-8")

    cols = ["query", "query_title", "query_full", "query_isbn", "title", "subtitle", "authors",
            "edition", "year", "isbn", "confidence", "source", "verify_score", "verify_note", "path"]
    with open(args.out.with_suffix(".tsv"), "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for b in books:
            row = {**b, "path": " | ".join(b["urls"])}
            vals = [("; ".join(row[c]) if isinstance(row.get(c), list) else str(row.get(c) or "")) for c in cols]
            fh.write("\t".join(v.replace("\t", " ") for v in vals) + "\n")

    (out_dir / "book_list.txt").write_text("".join(
        f"{b['title'] or b['isbn']}{' - ' + b['authors'][0] if b['authors'] else ''}\t{'; '.join(b['topics'])}\n"
        for b in books), encoding="utf-8")

    def course_label(cid):
        r = by_id[cid]
        return f"{r['inst']} {r['code'] + ' ' if r['code'] else ''}{r['title']}" + (f" ({r['term']})" if r["term"] else "")

    topic_courses = defaultdict(set)
    for cid, root in roots.items():
        topic_courses[topics[root]].add(cid)
    topic_books = defaultdict(list)
    for b in books:
        for t in b["topics"]:
            topic_books[t].append(b)
    with open(out_dir / "topics_to_books.tsv", "w", encoding="utf-8") as fh:
        fh.write("topic\tuniversities\tcourses\tbook_title\tauthors\trole\tquery\n")
        for t in sorted(topic_books, key=str.lower):
            unis = "; ".join(sorted({by_id[c]["inst"] for c in topic_courses[t]}))
            cl = "; ".join(sorted(course_label(c) for c in topic_courses[t]))
            for b in topic_books[t]:
                fh.write("\t".join(x.replace("\t", " ") for x in (
                    t, unis, cl, b["title"] or "(ISBN only)", "; ".join(b["authors"]), b["role"],
                    (b["query_isbn"] if args.isbn or not b["title"] else "") or b["query"])) + "\n")
    (out_dir / "topics_to_books.json").write_text(json.dumps({
        t: {"universities": sorted({by_id[c]["inst"] for c in topic_courses[t]}),
            "courses": [{"label": course_label(c), "university": by_id[c]["inst"], "url": by_id[c]["url"],
                         "mit_topics": by_id[c].get("topics", [])} for c in sorted(topic_courses[t])],
            "books": [{"title": b["title"], "authors": b["authors"], "isbn": b["isbn"], "role": b["role"],
                       "query": b["query"]} for b in topic_books.get(t, [])]}
        for t in sorted(topic_courses, key=str.lower)}, indent=2, ensure_ascii=False), encoding="utf-8")

    for b in books:
        if not b["title"]:
            review.append(f"ISBN on page but no title resolved\t{b['isbn']}\t{' | '.join(b['urls'])}")
        elif b.get("verify_note"):
            review.append(f"{b['verify_note']}\t{b['title']}\t{' | '.join(b['urls'])}")
    if review:
        (out_dir / "needs_review.txt").write_text("note\ttitle\tpath\n" + "\n".join(review) + "\n",
                                                  encoding="utf-8")
    if skipped:
        (out_dir / "skipped_courses.txt").write_text("reason\tcourse\turl\n" + "\n".join(sorted(skipped)) + "\n",
                                                     encoding="utf-8")

    multi = sum(1 for t in topic_courses if len({by_id[c]["inst"] for c in topic_courses[t]}) > 1)
    print(f"{len(books)} book(s), {len(best)} search string(s) -> {args.out}  "
          f"({len(topic_courses)} topic(s), {multi} shared by 2+ universities; "
          f"{len(skipped)} course(s) skipped; {len(review)} for review)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
