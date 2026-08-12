from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.connections_locators import ConnectionsLocators


class ConnectionsPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator. Confirmed live 2026-08-11: a
        # "Fetching credential domains" dialog can block ANY check in
        # this sequence, not just the first one - it was seen stalling
        # a later check even after the first one already passed with a
        # generous timeout. Rather than keep chasing which specific
        # check it lands on next, every check here gets the same
        # generous timeout.
        TIMEOUT = 15000

        self.expect_visible_by_text(
            ConnectionsLocators.ALTER_DATABASE_SECRETS_TEXT,
            timeout=TIMEOUT
        )

        for role, name in (
            ConnectionsLocators.ADD_DB_TAB,
            ConnectionsLocators.EDIT_DB_TAB,
            ConnectionsLocators.DELETE_DB_TAB,
        ):
            self.expect_visible_by_role(role, name, timeout=TIMEOUT)

        # Real app regression, confirmed live 2026-08-10: the
        # "Secretstore Alias" and "Database UserName" fields on the Add
        # DB tab have both lost their accessible names (plain
        # get_by_role("textbox", name=...) can never match them now) -
        # a bigger gap than initially reported (only Secretstore Alias
        # was flagged). Only "Connect String" still has one. Fall back
        # to DOM order (confirmed stable: Secretstore Alias is always
        # the first textbox on this tab, Database UserName the second)
        # rather than accessible name for these two - same
        # positional-lookup pattern already used elsewhere in this
        # codebase for unlabeled oj-c-* fields.
        textboxes = self.page.get_by_role("textbox")

        expect(textboxes.nth(0)).to_be_visible(timeout=TIMEOUT)  # Secretstore Alias
        expect(textboxes.nth(1)).to_be_visible(timeout=TIMEOUT)  # Database UserName

        self.expect_visible_by_role(
            *ConnectionsLocators.CONNECT_STRING_TEXTBOX,
            timeout=TIMEOUT
        )

        self.expect_visible_by_text(
            ConnectionsLocators.ALTER_ONEP_USER_SECRETS_TEXT,
            timeout=TIMEOUT
        )

        for role, name in (
            ConnectionsLocators.ADD_USER_TAB,
            ConnectionsLocators.EDIT_USER_TAB,
            ConnectionsLocators.DELETE_USER_TAB,
        ):
            self.expect_visible_by_role(role, name, timeout=TIMEOUT)

        self.expect_visible_by_role(
            *ConnectionsLocators.LOCAL_DEPLOYMENT_RADIO,
            timeout=TIMEOUT
        )

        self.expect_visible_by_role(
            *ConnectionsLocators.REMOTE_DEPLOYMENT_RADIO,
            timeout=TIMEOUT
        )

        # Role combobox lost its accessible name too (same regression
        # as above) - it's the only combobox on this tab, so position
        # is unambiguous.
        expect(self.page.get_by_role("combobox").first).to_be_visible(
            timeout=TIMEOUT
        )
