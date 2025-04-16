# pipeline.py

import json
from scraper.fetch_and_clean import fetch_and_clean
from llm.extract_info import extract_company_info
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_FILE = DATA_DIR / "results.json"


def run_pipeline(urls: list) -> list:
    """
    Takes a list of URLs, processes each one to extract company info,
    and saves the results to a JSON file.
    Returns the list of results.
    """
    results = []
    for url in urls:
        print(f"\n🌐 Processing: {url}")
        clean_text = fetch_and_clean(url)

        if not clean_text:
            print("[SKIP] No clean text extracted.")
            continue

        result = extract_company_info(clean_text[:5000])

        if not result:
            print("[SKIP] LLM extraction failed.")
            continue

        result["website"] = url
        results.append(result)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"[ERROR] Failed to save results: {e}")

    return results
