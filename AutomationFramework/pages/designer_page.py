from pages.base_page import BasePage
from locators.designer_locators import DesignerLocators


class DesignerPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_designer(self):

        self.click_tree_item("Designer")
        self.wait()

    def verify_designer_loaded(self):

        self.expect_visible_by_text(
            "CDC Components"
        )

    def verify_default_workflow(self):

        components = [
            DesignerLocators.SOURCE_DEPLOYMENT,
            DesignerLocators.SOURCE_CREDENTIAL_STORE,
            DesignerLocators.INTEGRATED_EXTRACT,
            DesignerLocators.TARGET_DEPLOYMENT,
            DesignerLocators.EXTRACT_PUMP,
            DesignerLocators.TARGET_CREDENTIAL_STORE,
            DesignerLocators.CLASSIC_REPLICAT,
        ]

        for component in components:

            self.expect_visible_by_role("img", component)