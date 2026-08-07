from pages.base_page import BasePage
from locators.conflict_resolution_locators import ConflictResolutionLocators


class ConflictResolutionPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_conflict_resolution(self):

        self.click_tree_item("Conflict Resolution")
        self.wait()

    def verify_screen_structure(self):

        # Content lags the tree-item selection by several seconds with
        # no visible loading indicator, so the first check needs a
        # generous timeout, same as the other post-navigation screens.
        self.expect_visible_by_role(
            *ConflictResolutionLocators.MAIN_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.DEPLOYMENT_COMBOBOX
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.CDB_COMBOBOX
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.ANALYZE_SCHEMAS_BUTTON
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.DB_DETAIL_TABLE
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.AUTO_CDR_HEADING
        )

        for role, name in (
            ConflictResolutionLocators.ENABLE_TAB,
            ConflictResolutionLocators.INFO_TAB,
            ConflictResolutionLocators.DISABLE_TAB,
            ConflictResolutionLocators.EXCEPTIONS_TAB,
            ConflictResolutionLocators.TOMBSTONE_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *ConflictResolutionLocators.ENABLE_CDR_BUTTON
        )

        self.expect_visible_by_role(
            *ConflictResolutionLocators.CDR_TABLE_LIST
        )
