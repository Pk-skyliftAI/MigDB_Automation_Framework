from pages.base_page import BasePage
from locators.logfile_locators import LogFileLocators


class LogFilePage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_logfile(self):

        self.click_tree_item("LogFile")
        self.wait()

    def verify_screen_structure(self):

        self.expect_visible_by_role(
            *LogFileLocators.CDC_ERROR_LOG_TAB,
            timeout=15000
        )

        for role, name in (
            LogFileLocators.REPORT_FILES_TAB,
            LogFileLocators.DISCARD_FILES_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *LogFileLocators.REPORT_FILES_HEADING
        )

        self.expect_visible_by_role(
            *LogFileLocators.SEARCH_TEXTBOX
        )

        self.expect_visible_by_role(
            *LogFileLocators.FILES_GRID
        )
