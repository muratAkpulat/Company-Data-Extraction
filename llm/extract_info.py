# llm/extract_info.py

import os
import json
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # Options: "gemini" or "ollama"

# Configure Gemini if used
if LLM_PROVIDER == "gemini":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-pro")


def build_prompt(text: str) -> str:
    """
    Prepare the prompt to instruct the LLM for extracting company details.
    """
    return f"""
You are an AI agent that extracts company contact and identification details from website content.

Given the following text from a company website, extract:
- Company Name
- Address (City and State if available)
- Phone Number
- Email Address
- Industry Category

Respond in the following JSON format:
{{
  "company_name": "...",
  "address": "...",
  "phone": "...",
  "email": "...",
  "category": "..."
}}

Here is the website text:
{text}
    """


def query_ollama(prompt: str, model_name: str = "qwen2.5:1.5b") -> str:
    """
    Send prompt to Ollama running locally and return the response text.
    """
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model_name,
            "prompt": prompt,
            "stream": False
        })
        return response.json()["response"]
    except Exception as e:
        print("[ERROR] Failed to connect to Ollama:", e)
        return ""


def extract_json_from_text(text: str) -> dict:
    """
    Attempt to extract the first valid JSON object from the given string.
    """
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        print("[ERROR] Failed to parse JSON:", e)
        return {}


def extract_company_info(text: str) -> dict:
    """
    Use selected LLM provider to extract structured company information.
    """
    prompt = build_prompt(text)

    if LLM_PROVIDER == "gemini":
        try:
            response = model.generate_content(prompt)
            data = extract_json_from_text(response.text)
            data["llm_model"] = "gemini-1.5-pro"
            return data
        except Exception as e:
            print("[ERROR] Gemini LLM extraction failed:", e)
            return {}
        except Exception as e:
            print("[ERROR] Gemini LLM extraction failed:", e)
            return {}

    elif LLM_PROVIDER == "ollama":
        result = query_ollama(prompt)
        data = extract_json_from_text(result)
        data["llm_model"] = "qwen2.5:1.5b"
        return data

    else:
        print(f"[ERROR] Unknown LLM provider: {LLM_PROVIDER}")
        return {}


# Test manually if run as script
if __name__ == "__main__":
    from scraper.fetch_and_clean import fetch_and_clean

    test_url = "https://www.americanplasticmolds.com/"
    cleaned_text = fetch_and_clean(test_url)

    if cleaned_text:
        result = extract_company_info(cleaned_text[:5000])
        print(json.dumps(result, indent=2))
    else:
        print("Failed to fetch or clean text.")
