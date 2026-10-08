import os
import curl_cffi
import tqdm
from pathlib import Path
import re
import html
import csv
import sys
import requests
from libgen_api_enhanced import LibgenSearch, SearchType, SearchRequest
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from urllib.parse import urljoin
import pickle

PATTERN = re.compile(
    r'href\s*=\s*["\']'
    r'(?P<link>[^"\']*get\.php\?md5=(?P<md5>[0-9a-fA-F]{32})&(?:amp;)?key=(?P<key>[^"\'&]+))'
    r'["\']'
)

MIRRORS = ['li']#['li', 'vg', 'la', 'bz', 'gl']


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
        with open("search_strings.txt", mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                line = " ".join(line.split(' ')[:-1])
                searches = []
                for mirror in MIRRORS:
                    try:
                        req = SearchRequest(query=line, search_type=SearchType.DEFAULT, mirror=f"https://libgen.{mirror}")
                        searches.append(req)
                    except:
                        continue
                queries.append(searches)
                
        return queries

    print("Error: Neither 'search_strings.tsv' nor 'search_strings.txt' was found.")
    sys.exit(1)

def find_epubs_all_domains(queries):
    results = []
    for q in queries:
        results.append(find_best_epub(q))
    return results

def find_best_epub(query_info):
    """
    Queries LibGen using ISBN first (if available), then title strings.
    Filters and returns the best English EPUB book object.
    """
    results = []
#    tqdm.write(repr(query_info))
    results = query_info.aggregate_request_data_libgen()
 #   tqdm.write(repr(results))
    if not results:
        tqdm.write(f'No results found for link: {query_info.query}')
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
        tqdm.write(f'No book found for link: {query_info.query}')
        return None

    # Sorting Logic: Pick the most recent book edition
    def sorting_key(book_obj):
        try:
            return int(getattr(book_obj, "year", 0))
        except ValueError:
            return 0

    valid_books.sort(key=sorting_key, reverse=True)
    return valid_books[0]

def find_link(page, mirror):
    link = ""
    for m in PATTERN.finditer(page):
        link = html.unescape(m["link"])
        link = urljoin("https://libgen.{mirror}", link)
    return link

def find_one_file(books):
    for book in books:
        try:
            if not book:
                continue
            download_file(book)
        except:
            continue
        else:
            break

def download_file(book):
    """Resolves the download mirror link and streams the EPUB file to disk."""
    # Attempt to resolve using the built-in property wrapper
    download_url = getattr(book, "resolved_download_link", None)
    
    if not download_url:
        tqdm.write("  [-] Could not resolve a download URL for this entry.")
        raise Exception()
    filename = clean_filename(f"{book.title}.epub")
    if Path(f"{book.title}.epub").is_file():
        tqdm.write(f'{book.title}.epub downloaded, skipping...')
        return
    response = curl_cffi.get(download_url, impersonate='firefox', stream=True)
    response.raise_for_status()
    site_data = "" 
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            site_data += chunk.decode("utf-8")
    domain_start = download_url.find('libgen.')
    dl = find_link(site_data, download_url[domain_start:domain_start+2])
    tqdm.write(f"  [+] Downloading to target: {filename}...")
    response = curl_cffi.get(dl, impersonate='firefox', stream=True)
    response.raise_for_status()
    length = 0
    tqdm.write(dl)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                length += len(chunk)
    tqdm.write(f'download succeeded: {length} bytes')

def main():
    # Initialize the enhanced wrapper (defaults to .li mirror structure)
    
    queries = parse_input_files()
    print(f"Loaded {len(queries)} book queries to process.\n" + "="*40)
    books_list = []
    MAX_THREADS = 16
    PICKLE_FILE = 'book_lists.pkl'
    if not Path(PICKLE_FILE).is_file():
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            future_to_query = {executor.submit(find_epubs_all_domains, q): q for q in queries}
            for future in tqdm(as_completed(future_to_query), total=len(future_to_query)):
                q = future_to_query[future]
                try:
                    best_books = future.result()
                except Exception as e:
                    tqdm.write(repr(e))
                    tqdm.write(f"{q} failed.")
                    continue
                if best_books:
                    books_list.append(best_books)
                    find_one_file(best_books)
                import random
                import time

                # Sleep for a random float between 1.5 and 4.5 seconds
                delay = random.uniform(10, 60)
                time.sleep(delay)
        with open(PICKLE_FILE, "wb") as file:
            pickle.dump(books_list, file)
    else:
        with open(PICKLE_FILE, "rb") as file:
            books_list = pickle.load(file)
    #print(books_list)
    #exit()
    #for books in tqdm(books_list):
        #find_one_file(books)

if __name__ == "__main__":
    main()
