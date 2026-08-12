from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.dashboard_locators import DashboardLocators


class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_dashboard(self):

        self.click_tree_item("Dashboard")
        self.wait()

    def is_dashboard_loaded(self):

        expect(self.page).to_have_title(DashboardLocators.PAGE_TITLE)

        # Same "Refreshing Secure Vault"/similar transient-dialog race as
        # LoginPage.verify_login_success - confirmed live 2026-08-10/11
        # this regularly outlasts the default 5s timeout even on a
        # navigation that isn't a fresh login.
        self.expect_visible_by_role(
            "button",
            "ORACLE admin",
            timeout=20000
        )

        return True

    def verify_logged_in_user(self):

        expect(
            self.page.get_by_role(
                "button",
                name="ORACLE admin"
            )
        ).to_be_visible(timeout=20000)

    def verify_dashboard_cards(self):

        cards = [
            "Load Average",
            "%Total CPU User",
            "%Total CPU Kernel",
            "Total Memory Usage %",
            "CDC Memory Usage %",
            "Process Lag",
            "Lag at Checkpoint",
            "Process Memory Usage",
            "Process CPU Usage",
        ]

        # The chart cards (Process Lag onward) render behind a
        # "Fetching process lag data" progress placeholder with no
        # fixed duration - confirmed live 2026-08-10 this now regularly
        # exceeds the default 5s timeout. The gauge cards above render
        # immediately, so this generous timeout costs nothing there
        # (expect() returns as soon as the text appears).
        #
        # exact=True is required here, not the shared substring-match
        # expect_visible_by_text helper: confirmed live 2026-08-11 that
        # a permanently-hidden <p class="global-progress-text"> element
        # reading "Fetching process lag data" now sits earlier in DOM
        # order than the real "Process Lag" card heading. Substring
        # matching ("process lag" is a case-insensitive substring of
        # "Fetching process lag data") makes `.first` grab that hidden
        # element every time and time out waiting for it to become
        # visible, never reaching the real, already-visible card title.
        for card in cards:
            expect(
                self.page.get_by_text(card, exact=True).first
            ).to_be_visible(timeout=15000)

    def logout(self):

        self.page.get_by_role(
            "button",
            name="ORACLE admin"
        ).click()

        self.page.get_by_role(
            "menuitem",
            name="Sign Out"
        ).click()

        self.page.wait_for_load_state("networkidle")

        expect(
            self.page.get_by_role(
                "button",
                name="Sign In"
            )
        ).to_be_visible()