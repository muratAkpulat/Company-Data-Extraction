# app.py

import gradio as gr
from llm.search_with_agent import serpapi_search_urls, check_url_status
from pipeline import run_pipeline
from pathlib import Path
import json

DATA_DIR = Path("data")
VALID_URLS_FILE = DATA_DIR / "valid_urls.json"
ERRORS_FILE = DATA_DIR / "errors.json"
RESULTS_FILE = DATA_DIR / "results.json"


def search_and_process(industry, state):
    DATA_DIR.mkdir(exist_ok=True)

    # Step 1: Search URLs with SerpAPI
    urls = serpapi_search_urls(industry, state, num_results=10)
    valid_urls = []
    error_details = []

    for url in urls:
        ok, detail = check_url_status(url)
        if ok:
            valid_urls.append(url)
        else:
            error_details.append({"url": url, "error": detail})

    # Step 2: Save valid and error URLs
    with open(VALID_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(valid_urls, f, indent=2)

    with open(ERRORS_FILE, "w", encoding="utf-8") as f:
        json.dump(error_details, f, indent=2)

    # Step 3: Run pipeline to extract company info
    run_pipeline(valid_urls)

    # Step 4: Load results and return them
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
