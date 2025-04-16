# llm/search_with_agent.py (SerpAPI version)

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load SerpAPI key
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def serpapi_search_urls(industry: str, state: str, num_results: int = 10) -> list:
    """
    Search for company websites using SerpAPI based on industry and state.
    """
    query = f"{industry} companies in {state} USA"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        urls = []

        for result in data.get("organic_results", []):
            link = result.get("link")
            if link and link.startswith("http"):
                urls.append(link)
            if len(urls) >= num_results:
                break

        return urls

    except Exception as e:
        print("[ERROR] SerpAPI query failed:", e)
        return []

def check_url_status(url: str) -> tuple:
    """
    Check if a URL is reachable using HEAD, fallback to GET if needed.
    Returns (status_bool, detailed_status_dict).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        if r.status_code == 405:
            r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            return (r.status_code == 200, {"code": r.status_code, "method": "GET", "suggestion": "HEAD not allowed"})
        return (r.status_code == 200, {"code": r.status_code, "method": "HEAD"})
    except requests.RequestException as e:
        return (False, {"error": str(e), "method": "HEAD"})

if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    industry = "injection molding"
    state = "Florida"
    results = serpapi_search_urls(industry, state, num_results=10)

    valid_urls = []
    error_details = []

    print("\n🔎 SerpAPI Suggested URLs (with status):")
    for url in results:
        ok, detail = check_url_status(url)
        if ok:
            valid_urls.append(url)
            status = f"✅ OK ({detail['code']} via {detail['method']})"
        elif 'code' in detail:
            error_details.append({"url": url, "error": f"{detail['code']} via {detail['method']}"})
            status = f"❌ Unreachable ({detail['code']} via {detail['method']})"
        else:
            error_details.append({"url": url, "error": detail['error']})
            status = f"❌ Unreachable ({detail['error']})"
        print(f"- {url} [{status}]")

    with open(output_dir / "valid_urls.json", "w", encoding="utf-8") as vf:
        json.dump(valid_urls, vf, indent=2)

    with open(output_dir / "errors.json", "w", encoding="utf-8") as ef:
        json.dump(error_details, ef, indent=2)

    print("\n✅ Saved valid URLs to data/valid_urls.json")
    print("✅ Saved error details to data/errors.json")
