from utils.logger import Logger
from utils.screenshot_manager import ScreenshotManager


class Assertions:

    logger = Logger.get_logger()

    @staticmethod
    def verify_title(page, expected_title):

        actual = page.title()

        if actual == expected_title:
            Assertions.logger.info(
                f"Title verification PASSED : {actual}"
            )
            return True

        ScreenshotManager.take_screenshot(
            page,
            "title_verification_failed"
        )

        Assertions.logger.error(
            f"Title verification FAILED | "
            f"Expected: {expected_title} | "
            f"Actual: {actual}"
        )

        raise AssertionError(
            f"Expected '{expected_title}' "
            f"but found '{actual}'"
        )

    @staticmethod
    def verify_url(page, expected_url):

        actual = page.url

        if actual == expected_url:
            Assertions.logger.info(
                "URL verification PASSED"
            )
            return True

        ScreenshotManager.take_screenshot(
            page,
            "url_verification_failed"
        )

        Assertions.logger.error(
            f"URL verification FAILED\n"
            f"Expected : {expected_url}\n"
            f"Actual   : {actual}"
        )

        raise AssertionError(
            "URL verification failed"
        )

    @staticmethod
    def verify_visible(page, locator):

        visible = page.locator(locator).is_visible()

        if visible:

            Assertions.logger.info(
                f"{locator} is visible."
            )
            return True

        ScreenshotManager.take_screenshot(
            page,
            "element_not_visible"
        )

        Assertions.logger.error(
            f"{locator} is not visible."
        )

        raise AssertionError(
            f"{locator} is not visible."
        )

    @staticmethod
    def verify_text(page, locator, expected):

        actual = page.locator(locator).text_content()

        if actual == expected:

            Assertions.logger.info(
                "Text verification PASSED"
            )
            return True

        ScreenshotManager.take_screenshot(
            page,
            "text_verification_failed"
        )

        Assertions.logger.error(
            f"Expected : {expected}\n"
            f"Actual   : {actual}"
        )

        raise AssertionError(
            "Text verification failed."
        )
