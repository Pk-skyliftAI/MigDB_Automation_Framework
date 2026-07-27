from playwright.sync_api import expect

from pages.base_page import BasePage


class ManagePage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_manage(self):

        self.click_tree_item("Manage")
        self.wait()

    def verify_manage_page(self):

        # Content lags the tree-item navigation by several seconds with
        # no visible loading indicator (same class of race as Setup's
        # tabs and the other screens built off this same nav pattern),
        # so the first check needs a generous timeout.
        expect(
            self.page.get_by_role(
                "grid",
                name="WatchDog Processes"
            )
        ).to_be_visible(timeout=15000)

        buttons = [
            "Primary Extracts Action",
            "Pump Action",
            "Replicat Action"
        ]

        for button in buttons:
            self.expect_visible_by_role("button", button)

    def open_manager_actions(self):

        self.click_by_role(
            "button",
            "Actions for Manager"
        )

    def verify_manager_actions(self):

        items = [
            "Edit Manager Params",
            "START",
            "Stop",
            "Kill",
            "Refresh",
            "View",
        ]

        for item in items:
            self.expect_visible_by_text(item)

    def verify_view_submenu(self):

        self.page.get_by_text(
            "View",
            exact=True
        ).hover()

        submenu = [
            "View Report",
            "Child Process Status",
            "Port Info Detail",
            "PURGEOLDEXTRACTS",
        ]

        for item in submenu:
            self.expect_visible_by_text(item)