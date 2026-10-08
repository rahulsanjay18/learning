#!/usr/bin/env python3
import os
import sys
import re
import argparse
import requests
from pathlib import Path
from tqdm import tqdm
from libgen_api_enhanced import LibgenSearch

# --- Configuration Lists (from Stage 1 rules) ---
BOOK_EXTS = {"pdf", "epub", "mobi", "azw", "azw3", "kfx", "djvu", "fb2", "docx"}
NON_BOOK_EXTS = {"jpg", "jpeg", "png", "gif", "mp3", "wav", "mp4", "html", "htm", "txt", "zip", "exe"}

SOURCE_TAGS = [
    r"lib\s*gen(?:\s*\.\s*(?:li|rs|is|st|lc|org))?",
    r"z\s*-?\s*lib(?:rary)?(?:\s*\.\s*(?:org|io|is|gs))?",
    r"anna(?:â€™|’|')?s?\s*-?\s*ar(?:c(?:h(?:i(?:v(?:e)?)?)?)?)?(?:\s*\.\s*(?:org|li|se))?",
    r"b\s*-\s*ok(?:\s*\.\s*(?:org|cc|xyz))?",
    r"bookzz(?:\s*\.\s*org)?",
    r"\[?retail\]?",
]

_source_re = re.compile(r"(?i)(?:^|[\s\-_.,;|(\[])(?:" + "|".join(SOURCE_TAGS) + r")(?=$|[\s\-_.,;|)\]])")
_site_prefix_re = re.compile(r"(?i)^[\w-]+\.(?:net|tips|com|org|pub|io)[_\-]")

# --- Filename Parsing & Sanitation (Stage 1 logic) ---
def fix_mojibake(s: str) -> str:
    """Fixes corrupted UTF-8 string encoding representations."""
    if "â€" in s or "Ã" in s:
        try: return s.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError): pass
    return s

def sanitize_filename(name):
    """Ensures names contain safe filename characters for saving files locally."""
    return "".join(c for c in name if c.isalnum() or c in (' ', '_', '-', '.')).strip()

def generic_cleanup(s: str) -> str:
    """Strips out structural tags, hashes, and publishers from target file query strings."""
    s = _site_prefix_re.sub("", s)
    s = s.replace("_", " ")
    if " " not in s and re.search(r"[a-z]-[a-z]", s) and s == s.lower():
        s = s.replace("-", " ")
    
    # Strip text inside parenthesis or brackets
    stripped = re.sub(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}", " ", s)
    s = stripped if sum(c.isalpha() for c in stripped) >= 3 else s

    s = _source_re.sub(" ", s)
    s = re.sub(r"(?i)\b[0-9a-f]{32}\b", " ", s) # removes md5 hashes
    s = re.sub(r"\b97[\d-]{10,14}\b|(?<![\d.])\d{9}[\dXx](?!\d)", " ", s) # removes ISBNs
    s = re.sub(r"(?i),?\s*\b\d+(?:st|nd|rd|th)\s*(?:edition\b|ed\b\.?)", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip(" .")

def parse_name(stem: str) -> str:
    """Extracts structural title metadata matching specific source conventions."""
    s = stem
    if " -- " in s: # Anna's Archive format
        fields = [f.strip() for f in s.split(" -- ")]
        title = fields[0].replace("_ ", ": ").replace("_", " ")
        author = fields[1] if len(fields) > 1 else ""
        author = re.sub(r"(?i)^by\s+", "", author).replace("_", ".").strip()
        return generic_cleanup(f"{title} {author}")

    spaced = s.replace("_", " ")

    if re.search(r"(?i)z-?lib", s): # z-library format
        body = re.sub(r"(?i)\s*\(z-?lib(?:\.org)?\)\s*$", "", spaced)
        return generic_cleanup(body)

    if re.search(r"(?i)lib\s*gen", s) and " - " in spaced: # LibGen format
        a, t = spaced.split(" - ", 1)
        return generic_cleanup(f"{t} {a}")

    return generic_cleanup(s)

# --- Main Automated Pipeline ---
def run_pipeline(library_dir, out_dir):
    lib_path = Path(library_dir)
    if not lib_path.is_dir():
        print(f"❌ Error: '{library_dir}' is not a valid directory.")
        sys.exit(1)

    # Ensure out directory exists
    os.makedirs(out_dir, exist_ok=True)

    # Scan the library recursively for files
    all_files = [p for p in lib_path.rglob("*") if p.is_file() and not p.name.startswith(".")]
    
    # Filter files down to ebook extensions, ignoring explicitly non-book items
    book_files = []
    for p in all_files:
        ext = p.suffix.lower().lstrip(".")
        if ext in BOOK_EXTS:
            book_files.append(p)
            
    if not book_files:
        print("⚠️ No valid ebook files found in the target library folder.")
        return

    print(f"📋 Found {len(book_files)} library items to parse.")
    print(f"📂 Output download directory: '{out_dir}'\n")

    s = LibgenSearch()

    for p in book_files:
        # Get baseline clean names from the filename base stem
        raw_stem = p.stem
        fixed_stem = fix_mojibake(raw_stem)
        cleaned_query = parse_name(fixed_stem)

        print(f"🧹 Scanning File: '{p.name}'")
        print(f"🔎 Generated Search Term: '{cleaned_query}'")

        try:
            # Search LibGen using the enhanced package API
            results = s.search_title(cleaned_query)
            if not results:
                print(f"❌ No results found on LibGen.\n")
                continue

            # Strict EPUB object extraction filter
            epub_results = [
                book for book in results
                if getattr(book, "extension", "").lower() == "epub" or str(book.get("Extension", "")).lower() == "epub"
            ]

            if not epub_results:
                print(f"⚠️ Listings found, but none match the target EPUB format.\n")
                continue

            # Grab first matching instance
            target_book = epub_results[0]
            book_title = getattr(target_book, "title", target_book.get("Title", cleaned_query))
            book_author = getattr(target_book, "author", target_book.get("Author", "Unknown"))
            print(f"✅ Found Match: \"{book_title}\" by {book_author}")

            # Download URL compilation
            print("🔗 Resolving mirror links...")
            download_links = s.resolve_download_links(target_book)
            direct_url = download_links.get("GET") or list(download_links.values())[0]

            if not direct_url:
                print("❌ Could not resolve secure download pathway.\n")
                continue

            # Executing File stream down to local disk
            file_name = sanitize_filename(f"{book_title} - {book_author}") + ".epub"
            full_save_path = os.path.join(out_dir, file_name)

            print(f"📥 Downloading into '{full_save_path}'...")
            response = requests.get(direct_url, stream=True, timeout=45)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            with open(full_save_path, "wb") as f_out, tqdm(
                total=total_size, unit='iB', unit_scale=True, desc="Progress"
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f_out.write(chunk)
                        pbar.update(len(chunk))

            print(f"🎉 Successfully downloaded: {file_name}\n")

        except Exception as e:
            print(f"💥 Error processing file string '{p.name}': {e}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified pipeline to scan messy folder structures, clean search names, and download matching EPUB files.")
    parser.add_argument("--library", type=str, required=True, help="Path to your directory tree of messy ebook files.")
    parser.add_argument("--out", type=str, required=True, help="Target destination directory where matching EPUBs are stored.")
    
    args = parser.parse_args()
    run_pipeline(args.library, args.out)

