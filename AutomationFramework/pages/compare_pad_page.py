from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.compare_pad_locators import ComparePadLocators


class ComparePadPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def _open_compare_pad_group(self):
        # Same toggle-not-just-expand behavior as Assessment's parent
        # tree item (see AssessmentPage._open_assessment_group) - only
        # click if not already expanded, or a second call in the same
        # test collapses it instead of leaving it open.
        compare_pad = self.page.get_by_role(
            "treeitem",
            name="Compare Pad",
            exact=False
        )

        if compare_pad.get_attribute("aria-expanded") != "true":
            compare_pad.click()
            self.wait()

    def open_compare_pad_configure(self):

        self._open_compare_pad_group()

        self.click_tree_item(ComparePadLocators.CONFIGURE_ITEM)
        self.wait()

    def open_compare_pad_monitor(self):

        self._open_compare_pad_group()

        self.click_by_id(ComparePadLocators.MONITOR_ITEM_ID)
        self.wait()

    def verify_navigated(self, item_name):

        # ComparePad's own screen content depends on an external
        # backend service this environment can't reach (see
        # ComparePadLocators docstring) - only confirm navigation
        # actually landed on the right sub-item, not screen content.
        expect(
            self.page.locator(
                "[role='treeitem'][aria-selected='true']"
            )
        ).to_have_text(item_name)
