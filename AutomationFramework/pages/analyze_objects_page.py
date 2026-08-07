from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.analyze_objects_locators import AnalyzeObjectsLocators


class AnalyzeObjectsPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_analyze_objects(self):

        self.click_tree_item("Analyze Objects")
        self.wait()

    def verify_screen_structure(self):

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.TABLE_TAB,
            timeout=15000
        )

        for role, name in (
            AnalyzeObjectsLocators.PROCEDURE_TAB,
            AnalyzeObjectsLocators.TRIGGERS_TAB,
            AnalyzeObjectsLocators.FUNCTION_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.DATABASE_ALIAS_COMBOBOX
        )

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.GET_DETAILS_BUTTON
        )

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.TABLE_DETAILS_HEADING
        )

        # "All Table" (application role) renders twice on this screen -
        # once for Table Details, once for Column Details - so this
        # can't use the shared expect_visible_by_role helper (strict
        # mode). Confirm both are present instead.
        expect(
            self.page.get_by_role(
                AnalyzeObjectsLocators.ALL_TABLE[0],
                name=AnalyzeObjectsLocators.ALL_TABLE[1]
            )
        ).to_have_count(2)

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.SCHEMA_NAME_COMBOBOX
        )

        for role, name in (
            AnalyzeObjectsLocators.ANALYZE_BUTTON,
            AnalyzeObjectsLocators.SUMMARY_BUTTON,
            AnalyzeObjectsLocators.DOWNLOAD_REPORT_BUTTON,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *AnalyzeObjectsLocators.COLUMN_DETAILS_HEADING
        )
