# scrape_with_serpapi_qwen.py

import os
import requests
from dotenv import load_dotenv
import json
import httpx

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:1.5b"

def search_google(industry: str, state: str, num: int = 10):
    query = f"{industry} companies in {state} site:.com"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num
    }
    res = requests.get("https://serpapi.com/search", params=params)
    print("🌐 Raw SerpAPI response:", res.status_code, res.text[:200])
    results = res.json().get("organic_results", [])
    return results

def filter_with_qwen(result):
    prompt = f"""
Below is a Google search result:

Title: {result['title']}
Link: {result['link']}
Snippet: {result.get('snippet', '')}

Is this the official website of a real company in the correct industry? If yes, return the valid URL in this format:
{{"valid_url": "https://example.com"}}
If not, return:
{{"valid_url": null}}
"""
    try:
        response = httpx.post(OLLAMA_ENDPOINT, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        print("\n📝 PROMPT:\n", prompt)

        if response.status_code != 200:
            print("❌ HTTP error:", response.status_code, response.text)
            return None

        content = response.json()
        print("🧠 RAW LLM RESPONSE:", content)
        raw = content["response"].strip()
        return raw

    except Exception as e:
        print("❌ Qwen error:", e)
        return None

if __name__ == "__main__":
    results = search_google("injection molding", "Florida")
    for r in results:
        filtered = filter_with_qwen(r)
        print("🔎", filtered)
