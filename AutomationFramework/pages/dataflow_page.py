from pages.base_page import BasePage
from locators.dataflow_locators import DataflowLocators


class DataflowPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_dataflow(self):

        self.click_tree_item("Dataflow")
        self.wait()

    def verify_screen_structure(self):

        self.expect_visible_by_role(
            *DataflowLocators.REPLICATION_FLOW_HEADING
        )
