from pages.base_page import BasePage
from locators.analyze_trails_locators import AnalyzeTrailsLocators


class AnalyzeTrailsPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_analyze_trails(self):

        self.click_tree_item("Analyze Trails")
        self.wait()

    def verify_screen_structure(self):

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.LOGDUMP_TAB,
            timeout=15000
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.LOAD_BALANCE_TAB
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.SELECT_PROCESS_HEADING
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.LOAD_TRAILFILES_BUTTON
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.GET_DETAILS_BUTTON
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.TRAILFILES_GRID
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.TRAILFILE_HEADER_HEADING
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.TRAIL_CONTENT_SUMMARY_HEADING
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.RBA_TEXTBOX
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.FILTER_MATCH_ALL_RADIO
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.FILTER_MATCH_ANY_RADIO
        )

        self.expect_visible_by_role(
            *AnalyzeTrailsLocators.FILTER_LIST_TABLE
        )

        for role, name in (
            AnalyzeTrailsLocators.PREVIOUS_RECORD_BUTTON,
            AnalyzeTrailsLocators.FILTER_BUTTON,
            AnalyzeTrailsLocators.NEXT_RECORD_BUTTON,
        ):
            self.expect_visible_by_role(role, name)
