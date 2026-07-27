from pages.base_page import BasePage
from locators.parameter_file_locators import ParameterFileLocators


class ParameterFilePage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator, so the first check needs a generous
        # timeout.
        self.expect_visible_by_role(
            *ParameterFileLocators.SEARCH_TEXTBOX,
            timeout=15000
        )

        self.expect_visible_by_role(
            *ParameterFileLocators.EDIT_BUTTON
        )

        self.expect_visible_by_text(
            ParameterFileLocators.MGR_PRM_ROW_TEXT
        )

        self.expect_visible_by_text(
            ParameterFileLocators.GLOBALS_ROW_TEXT
        )
