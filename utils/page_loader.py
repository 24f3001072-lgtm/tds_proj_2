from playwright.sync_api import sync_playwright

def load_page(url: str, wait_ms: int = 2000) -> str:
    """
    Loads a webpage using Playwright and returns rendered HTML.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # wait for JS-rendered content
        page.wait_for_timeout(wait_ms)

        html = page.content()
        browser.close()
        return html
