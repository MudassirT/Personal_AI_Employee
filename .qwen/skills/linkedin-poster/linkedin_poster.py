from pathlib import Path
import time
from typing import Optional

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False


class LinkedInPoster:
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

    def create_post(self, content: str, image_path: Optional[str] = None, headless: bool = True) -> bool:
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError('Playwright not installed')

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=headless,
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            try:
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
                time.sleep(2)

                # Click start post
                start_post = page.query_selector('[aria-label="Start a post"]')
                if not start_post:
                    start_post = page.query_selector('button[aria-label*="post"]')

                if start_post:
                    start_post.click()
                    time.sleep(1)
                    text_input = page.query_selector('[role="textbox"]')
                    if text_input:
                        text_input.fill(content)
                        time.sleep(1)
                        if image_path:
                            file_input = page.query_selector('input[type="file"]')
                            if file_input:
                                file_input.set_input_files(image_path)
                                time.sleep(2)
                        post_btn = page.query_selector('button[aria-label*="Post"]')
                        if post_btn:
                            post_btn.click()
                            time.sleep(3)
                            browser.close()
                            return True

                browser.close()
                return False
            except Exception:
                browser.close()
                return False
