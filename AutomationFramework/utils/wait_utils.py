from playwright.sync_api import TimeoutError
from config.settings import config


class WaitUtils:

    DEFAULT_TIMEOUT = config.browser["timeout"]

    @staticmethod
    def wait_for_visible(page, locator, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.locator(locator).wait_for(
            state="visible",
            timeout=timeout
        )

    @staticmethod
    def wait_for_hidden(page, locator, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.locator(locator).wait_for(
            state="hidden",
            timeout=timeout
        )

    @staticmethod
    def wait_for_attached(page, locator, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.locator(locator).wait_for(
            state="attached",
            timeout=timeout
        )

    @staticmethod
    def wait_for_detached(page, locator, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.locator(locator).wait_for(
            state="detached",
            timeout=timeout
        )

    @staticmethod
    def wait_for_url(page, url, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.wait_for_url(url, timeout=timeout)

    @staticmethod
    def wait_for_title(page, title, timeout=None):
        timeout = timeout or WaitUtils.DEFAULT_TIMEOUT
        page.wait_for_function(
            f"document.title === '{title}'",
            timeout=timeout
        )

    @staticmethod
    def wait_for_load(page):
        page.wait_for_load_state("load")

    @staticmethod
    def wait_for_dom(page):
        page.wait_for_load_state("domcontentloaded")

    @staticmethod
    def wait_for_network_idle(page):
        page.wait_for_load_state("networkidle")
