from pathlib import Path
from datetime import datetime
import re


class ScreenshotManager:
    """
    Handles screenshot storage for the framework.
    """

    SCREENSHOT_DIR = Path("reports") / "screenshots"

    @classmethod
    def ensure_directory(cls):
        cls.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def generate_filename(cls, test_name: str) -> Path:
        """
        Generates a unique screenshot filename.

        Example:
        reports/screenshots/
            test_login_20260716_091530.png
        """

        cls.ensure_directory()

        safe_name = re.sub(r"[^A-Za-z0-9_-]", "_", test_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return cls.SCREENSHOT_DIR / f"{safe_name}_{timestamp}.png"

    @classmethod
    def capture(cls, page, test_name: str) -> str:
        """
        Captures a screenshot and returns the file path.
        """

        filepath = cls.generate_filename(test_name)

        page.screenshot(
            path=str(filepath),
            full_page=True
        )

        return str(filepath)