import os
from pathlib import Path
import re
import csv
import sys
import requests
from libgen_api_enhanced import LibgenSearch, SearchType, SearchRequest

def clean_filename(name):
    """Removes characters that are invalid in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def parse_input_files():
    """
    Parses search_strings.tsv if it exists, otherwise falls back to search_strings.txt.
    Returns a list of dictionaries with search keys.
    """
    queries = []
    
    if os.path.exists("search_strings.txt"):
        print("Found 'search_strings.txt'. Parsing text patterns...")
        with open("search_strings.txt", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = " ".join(line.split(' ')[:-1])
                try:
                    req = SearchRequest(query=line, search_type=SearchType.DEFAULT, mirror="https://libgen.bz")
                    queries.append(req)
                except:
                    continue
        return queries

    print("Error: Neither 'search_strings.tsv' nor 'search_strings.txt' was found.")
    sys.exit(1)

def find_best_epub(search_provider, query_info):
    """
    Queries LibGen using ISBN first (if available), then title strings.
    Filters and returns the best English EPUB book object.
    """
    results = []
    results = query_info.aggregate_request_data_libgen()
    print(len(results))
 
    if not results:
        return None

    # Filtering Logic: Find English EPUBs
    valid_books = []
    for book in results:
        # Check if attributes match criteria (safeguarding missing values)
        lang = getattr(book, "language", "").lower()
        ext = getattr(book, "extension", "").lower()
        if ("english" in lang or lang == "en") and ext == "epub":
            valid_books.append(book)

    if not valid_books:
        return None

    # Sorting Logic: Pick the most recent book edition
    def sorting_key(book_obj):
        try:
            return int(getattr(book_obj, "year", 0))
        except ValueError:
            return 0

    valid_books.sort(key=sorting_key, reverse=True)
    return valid_books[0]

def download_file(book, display_name):
    """Resolves the download mirror link and streams the EPUB file to disk."""
    # Attempt to resolve using the built-in property wrapper
    download_url = getattr(book, "resolved_download_link", None)
    
    # Fallback to evaluating explicitly provided mirror elements if necessary
    if not download_url and getattr(book, "mirrors", None):
        download_url = book.mirrors[0] if isinstance(book.mirrors, list) else book.mirrors
        
    if not download_url:
        print("  [-] Could not resolve a download URL for this entry.")
        return False
    firefox_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
    }
    filename = clean_filename(f"{book.title}.epub")
    print(f"  [+] Downloading to target: {filename}...")
    if Path(f"{book.title}.epub").is_file():
        return True 
    try:
        response = requests.get(download_url, headers=firefox_headers, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("  [✓] Download Complete!")
        return True
    except Exception as e:
        print(f"  [-] Failed downloading file: {e}")
        return False

def main():
    # Initialize the enhanced wrapper (defaults to .li mirror structure)
    s = LibgenSearch(mirror="bz")
    
    queries = parse_input_files()
    print(f"Loaded {len(queries)} book queries to process.\n" + "="*40)
    
    for idx, query_info in enumerate(queries, 1):
        
        best_book = find_best_epub(s, query_info)
        
        if best_book:
            print(f"  Found Match: {getattr(best_book, 'title', 'Unknown')} ({getattr(best_book, 'year', 'Year N/A')})")
            download_file(best_book, query_info)
        else:
            print("  [-] No matching English EPUB versions found on LibGen.")

if __name__ == "__main__":
    main()
