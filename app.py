# app.py

import gradio as gr
import requests
import os
import httpx
import json
from pathlib import Path
from dotenv import load_dotenv
from pipeline import run_pipeline

load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2:1.5b"

DATA_DIR = Path("data")
VALID_URLS_FILE = DATA_DIR / "valid_urls.json"
ERRORS_FILE = DATA_DIR / "errors.json"
RESULTS_FILE = DATA_DIR / "results.json"

def serpapi_search_urls(industry, state, num_results=10):
    query = f"{industry} companies in {state} site:.com"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results
    }
    response = requests.get("https://serpapi.com/search", params=params)
    organic_results = response.json().get("organic_results", [])
    urls = [r["link"] for r in organic_results if "link" in r]

    print("🔍 Querying SerpAPI with:", query)
    print("🌐 Status code:", response.status_code)
    print("📃 Raw response text:", response.text[:300])




    return urls

def check_url_status(url):
    prompt = f"""
Below is a Google search result:

Link: {url}

Is this the official website of a real company in the correct industry? If yes, return the valid URL in this format:
{{"valid_url": "{url}"}}
If not, return:
{{"valid_url": null}}
"""

    try:
        response = httpx.post(OLLAMA_ENDPOINT, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}"

        content = response.json()
        raw = content.get("response", "").strip()

        if "\"valid_url\": null" in raw.lower():
            return False, "LLM rejected"
        else:
            return True, "LLM accepted"

    except Exception as e:
        return False, str(e)

def search_and_process(industry, state):
    DATA_DIR.mkdir(exist_ok=True)

    urls = serpapi_search_urls(industry, state, num_results=10)
    
    print("🔍 Found URLs:", urls)
    valid_urls = []
    error_details = []

    for url in urls:
        ok, detail = check_url_status(url)
        if ok:
            valid_urls.append(url)
        else:
            error_details.append({"url": url, "error": detail})

    with open(VALID_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_urls, f, indent=2)

    with open(ERRORS_FILE, "w", encoding="utf-8") as f:
        json.dump(error_details, f, indent=2)

    run_pipeline(valid_urls)

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            results = json.load(f)
        return results
    except:
        return [{"error": "No results found or failed to load."}]

with gr.Blocks() as demo:
    gr.Markdown("""# 🏭 Company Info Extractor\nEnter a business category and US state, and get real company links + details.""")

    with gr.Row():
        industry_input = gr.Textbox(label="Industry Category", placeholder="e.g. injection molding")
        state_input = gr.Textbox(label="US State", placeholder="e.g. Florida")

    submit_btn = gr.Button("🔍 Search and Extract")
    output_json = gr.JSON(label="Extracted Company Info")

    submit_btn.click(fn=search_and_process, inputs=[industry_input, state_input], outputs=output_json)

if __name__ == "__main__":
    demo.launch()
