from pages.base_page import BasePage
from locators.troubleshoot_locators import TroubleshootLocators


class TroubleshootPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_troubleshoot(self):

        self.click_tree_item("Troubleshoot")
        self.wait()

    def verify_screen_structure(self):

        self.expect_visible_by_role(
            *TroubleshootLocators.INTEGRATED_EXTRACT_TAB,
            timeout=15000
        )

        for role, name in (
            TroubleshootLocators.INTEGRATED_REPLICAT_TAB,
            TroubleshootLocators.CLASSIC_REPLICAT_TAB,
            TroubleshootLocators.PARALLEL_REPLICAT_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_text(
            TroubleshootLocators.HEALTHCHECK_TEXT
        )

        for role, name in (
            TroubleshootLocators.OVERVIEW_TAB,
            TroubleshootLocators.CAPTURE_PROCESSES_TAB,
            TroubleshootLocators.LOGMINER_DETAILS_TAB,
            TroubleshootLocators.LOGMINER_MEMORY_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *TroubleshootLocators.DATABASE_NAME_COMBOBOX
        )

        self.expect_visible_by_role(
            *TroubleshootLocators.GET_DETAILS_BUTTON
        )

        self.expect_visible_by_role(
            *TroubleshootLocators.DATABASE_DETAILS_TABLE
        )

        self.expect_visible_by_role(
            *TroubleshootLocators.CAPTURE_PROCESSES_TABLE
        )

        self.expect_visible_by_role(
            *TroubleshootLocators.LOGMINER_DETAILS_TABLE
        )
