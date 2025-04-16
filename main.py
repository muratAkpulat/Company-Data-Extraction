# main.py

import json
from pathlib import Path
from pipeline import run_pipeline

DATA_DIR = Path("data")
URLS_FILE = DATA_DIR / "valid_urls.json"


def load_urls(filepath):
    """Load a list of company URLs from a JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read URL list: {e}")
        return []


def run():
    urls = load_urls(URLS_FILE)
    run_pipeline(urls)


if __name__ == "__main__":
    run()
