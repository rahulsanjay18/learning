"""Where the learner's books live (one place for every library script). Override with LIB_BOOKS_ROOT / LIB_MD_ROOT."""
import os
from pathlib import Path

BOOKS_ROOT = Path(os.environ.get("LIB_BOOKS_ROOT", "/media/rahul/Drive 2/Library/Library"))
MD_ROOT = Path(os.environ.get("LIB_MD_ROOT", "/media/rahul/Drive 2/Library/Markdown_Library"))
