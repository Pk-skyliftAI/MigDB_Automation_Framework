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

        self.expect_visible_by_role(
            "button",
            "ORACLE admin"
        )

        return True

    def verify_logged_in_user(self):

        expect(
            self.page.get_by_role(
                "button",
                name="ORACLE admin"
            )
        ).to_be_visible()

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

        for card in cards:
            self.expect_visible_by_text(card)

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