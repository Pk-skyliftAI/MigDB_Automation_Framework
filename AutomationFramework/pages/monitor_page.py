from pages.base_page import BasePage


class MonitorPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_monitor(self):

        self.click_by_id("monitor")
        self.wait()

    def verify_monitor_page(self):

        buttons = [
            "Extracts",
            "Distribution",
            "Replicats"
        ]

        for button in buttons:
            self.expect_visible_by_role(
                "button",
                button
            )