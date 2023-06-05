from playwright.sync_api import sync_playwright

class BrowserWrapper:
    def __init__(self):
        self.page = None
        self.client = None
        self.page_element_buffer = None

    def start_browser_and_goto_page(self, url: str) -> str:
        global browser
        
        browser = (
            sync_playwright()
            .start()
            .chromium.launch(
                headless=False,
            )
        )

        self.page = browser.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 1080})

        try:
            self.page.goto(url=url if "://" in url else "http://" + url)
            self.client = self.page.context.new_cdp_session(self.page)
            self.page_element_buffer = {}
        except:
            return "Failed to go to URL, please try again and make sure the URL is correct."

        return f"Browser successfully started and navigated to {url}!"


browser_wrapper = BrowserWrapper()