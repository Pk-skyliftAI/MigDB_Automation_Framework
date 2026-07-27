from pages.base_page import BasePage
from locators.purge_cdc_files_locators import PurgeCdcFilesLocators


class PurgeCdcFilesPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator, so the first check needs a generous
        # timeout.
        self.expect_visible_by_role(
            *PurgeCdcFilesLocators.MANAGER_PARAMETERS_HEADING,
            timeout=15000
        )

        self.expect_visible_by_css(
            PurgeCdcFilesLocators.ENABLE_PURGEOLDEXTRACTS_TOGGLE
        )

        self.expect_visible_by_css(
            PurgeCdcFilesLocators.ENABLE_AUTOSTART_TOGGLE
        )

        self.expect_visible_by_css(
            PurgeCdcFilesLocators.ENABLE_AUTORESTART_TOGGLE
        )

        self.expect_visible_by_text(
            PurgeCdcFilesLocators.NO_PARAMETER_ENABLED_TEXT
        )
