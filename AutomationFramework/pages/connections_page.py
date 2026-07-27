from pages.base_page import BasePage
from locators.connections_locators import ConnectionsLocators


class ConnectionsPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator, so the first check needs a generous
        # timeout.
        self.expect_visible_by_text(
            ConnectionsLocators.ALTER_DATABASE_SECRETS_TEXT,
            timeout=15000
        )

        for role, name in (
            ConnectionsLocators.ADD_DB_TAB,
            ConnectionsLocators.EDIT_DB_TAB,
            ConnectionsLocators.DELETE_DB_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *ConnectionsLocators.SECRETSTORE_ALIAS_TEXTBOX
        )

        self.expect_visible_by_role(
            *ConnectionsLocators.DATABASE_USERNAME_TEXTBOX
        )

        self.expect_visible_by_role(
            *ConnectionsLocators.CONNECT_STRING_TEXTBOX
        )

        self.expect_visible_by_text(
            ConnectionsLocators.ALTER_ONEP_USER_SECRETS_TEXT
        )

        for role, name in (
            ConnectionsLocators.ADD_USER_TAB,
            ConnectionsLocators.EDIT_USER_TAB,
            ConnectionsLocators.DELETE_USER_TAB,
        ):
            self.expect_visible_by_role(role, name)

        self.expect_visible_by_role(
            *ConnectionsLocators.LOCAL_DEPLOYMENT_RADIO
        )

        self.expect_visible_by_role(
            *ConnectionsLocators.REMOTE_DEPLOYMENT_RADIO
        )

        self.expect_visible_by_role(
            *ConnectionsLocators.ROLE_COMBOBOX
        )
