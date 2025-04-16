# scraper/fetch_and_clean.py (Playwright-based version)

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def fetch_html(url: str, timeout: int = 10000) -> str:
    """
    Fetch raw HTML content from the given URL using Playwright (JS-rendered).
    Returns the full HTML string if successful, else None.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000, wait_until="domcontentloaded")

            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"[ERROR] Failed to fetch URL with Playwright: {url}\nReason: {e}")
        return None


def clean_html(html: str) -> str:
    """
    Clean the HTML by removing script/style/nav/footer tags and returning only text.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "noscript", "form"]):
        tag.decompose()

    # Get visible text only
    text = soup.get_text(separator=" ", strip=True)

    return text


def fetch_and_clean(url: str) -> str:
    """
    Fetch a webpage (JS rendered) and return cleaned visible text.
    """
    html = fetch_html(url)
    if not html:
        return None
    return clean_html(html)


# If you want to test this module directly:
if __name__ == "__main__":
    test_url = "https://www.americanplasticmolds.com/"
    cleaned_text = fetch_and_clean(test_url)
    if cleaned_text:
        print(cleaned_text[:1000])  # Print first 1000 characters
    else:
        print("Failed to extract clean content.")
