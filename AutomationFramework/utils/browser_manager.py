from playwright.sync_api import sync_playwright
from config.settings import config


class BrowserManager:
    """
    Browser Manager

    Responsibilities:
    - Start the configured Playwright browser.
    - Support browser override from command-line (--browser).
    - Close browser and Playwright gracefully.
    """

    def __init__(self, browser_name=None):
        self.playwright = None
        self.browser = None
        self.browser_name = browser_name

    def start_browser(self):
        """Launch the configured browser."""

        self.playwright = sync_playwright().start()

        # Command-line browser takes precedence over config.yaml
        browser_name = (
            self.browser_name or config.browser["engine"]
        ).lower()

        headless = config.browser["headless"]
        slow_mo = config.browser["slow_mo"]

        if browser_name == "chromium":
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                slow_mo=slow_mo
            )

        elif browser_name == "firefox":
            self.browser = self.playwright.firefox.launch(
                headless=headless,
                slow_mo=slow_mo
            )

        elif browser_name == "webkit":
            self.browser = self.playwright.webkit.launch(
                headless=headless,
                slow_mo=slow_mo
            )

        else:
            raise ValueError(
                f"Unsupported browser: {browser_name}"
            )

        return self.browser

    def stop_browser(self):
        """Close browser and stop Playwright."""

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()