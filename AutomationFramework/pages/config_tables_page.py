from pages.base_page import BasePage
from locators.config_tables_locators import ConfigTablesLocators


class ConfigTablesPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator, so the first check needs a generous
        # timeout.
        self.expect_visible_by_role(
            *ConfigTablesLocators.CHECKPOINT_TABLE_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *ConfigTablesLocators.HEARTBEAT_TABLE_HEADING
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.CHECKPOINT_TABLENAME_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.DIRECTION_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.PARTITIONED_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.FREQUENCY_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.RETENTION_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.PURGE_FREQUENCY_TEXT
        )

        self.expect_visible_by_role(
            *ConfigTablesLocators.ADD_HEARTBEAT_TABLE_BUTTON
        )
