from pages.base_page import BasePage
from locators.navigation_locators import NavigationLocators


class NavigationPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_navigation_menu(self):
        # Not page.locator("button").first: hidden dialog templates (e.g.
        # the Assessment "technical issue" dialog once it has ever fired)
        # can insert their own <button> ahead of the real hamburger
        # button in DOM order. Not a bare icon-class selector either: the
        # Designer screen's "Start" (CDC) button reuses the identical
        # hamburger icon glyph. The hamburger button's accessible name is
        # "Start Here" (visually hidden, in the persistent banner) - use
        # that directly, it's unique across the whole app.
        #
        # This button TOGGLES the nav drawer rather than only opening it,
        # and the drawer stays open across in-app navigation. Calling
        # this unconditionally a second time (e.g. before a second
        # tree-item click later in the same test) silently closes the
        # drawer instead, which then makes every subsequent tree-item
        # click fail/timeout since the whole tree is gone - this was
        # root-caused via a live diagnostic script after it looked like a
        # flaky animation race. The `#navlist` tree's own visibility is a
        # reliable open/closed signal (confirmed live), so only click if
        # it isn't already open.
        tree = self.page.get_by_role(
            "tree",
            name="Choose a navigation item"
        )

        if not tree.is_visible():
            self.page.get_by_role("button", name="Start Here").click()

    def verify_navigation_menu(self):

        menu_items = [
            NavigationLocators.DASHBOARD,
            NavigationLocators.DATAFLOW,
            NavigationLocators.MANAGE,
            NavigationLocators.MONITOR,
            NavigationLocators.DESIGNER,
            NavigationLocators.HETEROGENEOUS_INITIAL_LOAD,
            NavigationLocators.HETRO_INITIAL_LOAD_MONITOR,
            NavigationLocators.HOMOGENEOUS_INITIAL_LOAD,
            NavigationLocators.HOMO_INITIAL_LOAD_MONITOR,
            NavigationLocators.CONFLICT_RESOLUTION,
            NavigationLocators.ANALYZE_OBJECTS,
            NavigationLocators.ANALYZE_TRAILS,
            NavigationLocators.SETUP,
            NavigationLocators.TROUBLESHOOT,
            NavigationLocators.LOGFILE,
            NavigationLocators.ASSESSMENT,
            NavigationLocators.COMPARE_PAD,
        ]

        for item in menu_items:

            if item == NavigationLocators.MONITOR:
                self.expect_visible_by_id("monitor")
            else:
                self.expect_tree_item_visible(item, exact=False)