#!/usr/bin/env bash
# Library pipeline shortcuts. Run on the machine that holds the books (paths: scripts/library_paths.py).
# Details and every flag: library/ADDING-BOOKS.md, or python3 scripts/add_books.py --help.
#   bash scripts/library.sh new        convert books with no Markdown yet, grade, index, rebuild servers, commit + push
#   bash scripts/library.sh retry      same, but for the retry list (library/RECONVERT.csv), light engines only
#   bash scripts/library.sh retry-ocr  retry list including scanned PDFs and DjVu (slow; OCR)
#   bash scripts/library.sh dry [new|retry]   show what would be converted, change nothing
#   bash scripts/library.sh servers    rebuild book-server and progress-server only
# Extra flags pass through, e.g. bash scripts/library.sh retry --limit 20
set -euo pipefail
cd "$(dirname "$0")/.."
cmd="${1:-help}"; shift || true
case "$cmd" in
  new)       python3 scripts/add_books.py --source new "$@" ;;
  retry)     python3 scripts/add_books.py --source csv "$@" ;;
  retry-ocr) python3 scripts/add_books.py --source csv --allow-ocr "$@" ;;
  dry)       src="${1:-new}"; shift || true
             [ "$src" = retry ] && src=csv
             python3 scripts/add_books.py --dry-run --source "$src" "$@" ;;
  servers)   (cd ~/Documents && docker compose up -d --build book-server progress-server) ;;
  *)         sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//' ;;
esac
