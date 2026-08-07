import time

from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError

from pages.base_page import BasePage
from locators.assessment_locators import AssessmentLocators


class AssessmentPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def _open_assessment_group(self):
        # Like the nav drawer's hamburger button, this parent tree item
        # TOGGLES expand/collapse rather than only expanding - clicking
        # it while already expanded (e.g. it was left expanded by an
        # earlier open_create_job() call in the same test) collapses it
        # instead, hiding "Create Job"/"Monitor Job" and breaking
        # whichever click comes next. Confirmed live via a diagnostic
        # script that this parent item's aria-expanded flips true/false
        # on repeated clicks. Only click if not already expanded.
        assessment = self.page.get_by_role(
            "treeitem",
            name=AssessmentLocators.ASSESSMENT_NAV_ITEM,
            exact=False
        )

        if assessment.get_attribute("aria-expanded") != "true":
            assessment.click()
            self.wait()

    def open_create_job(self):
        self._open_assessment_group()

        self.click_tree_item(AssessmentLocators.CREATE_JOB_NAV_ITEM)
        self.wait()

    def open_monitor_job(self):
        self._open_assessment_group()

        self.click_tree_item(AssessmentLocators.MONITOR_JOB_NAV_ITEM)
        self.wait()

    # ---------------------------------------------------------
    # Create Job
    # ---------------------------------------------------------

    def select_cdb(self, cdb_name):

        self.select_cdb_combobox(cdb_name)

        expect(
            self.page.get_by_role(
                AssessmentLocators.RUN_ASSESSMENT_BUTTON[0],
                name=AssessmentLocators.RUN_ASSESSMENT_BUTTON[1]
            )
        ).to_be_enabled(timeout=15000)

    def run_assessment(self):

        self.click_by_role(*AssessmentLocators.RUN_ASSESSMENT_BUTTON)

        # Clicking this button reliably surfaces a "technical issue"
        # dialog immediately, but it's a false negative - the job keeps
        # running in the background and completes successfully seconds
        # later (confirmed via Monitor Job against the live app). Dismiss
        # it if it shows up rather than treating it as a real failure.
        dialog = self.page.get_by_role(
            AssessmentLocators.TECHNICAL_ISSUE_DIALOG[0],
            name=AssessmentLocators.TECHNICAL_ISSUE_DIALOG[1]
        )

        try:
            dialog.wait_for(state="visible", timeout=5000)
            dialog.get_by_label("Close").click()
            self.wait_for_dialog_to_close(
                AssessmentLocators.TECHNICAL_ISSUE_DIALOG[1]
            )
        except PlaywrightTimeoutError:
            pass

    # ---------------------------------------------------------
    # Monitor Job
    # ---------------------------------------------------------

    def open_assessment_job(self, job_name_prefix, timeout=60000):

        combo = self.page.get_by_role(
            AssessmentLocators.SELECT_ASSESSMENT_COMBOBOX[0],
            name=AssessmentLocators.SELECT_ASSESSMENT_COMBOBOX[1]
        )

        # Job names are "<alias>_<timestamp>" - the most recently created
        # matching job is the one this run just kicked off. The job can
        # take well over the previous fixed ~20s retry budget to appear
        # in this list under load (confirmed live: a job created seconds
        # earlier was still missing from a fresh listing), consistent
        # with the same backend flakiness behind Run Assessment's known
        # false-negative "technical issue" dialog - so retry reopening
        # the combobox (it re-fetches on open) against a generous time
        # budget rather than a small fixed retry count.
        matching = self.page.locator(
            "[role='row']"
        ).filter(has_text=job_name_prefix)

        deadline = time.monotonic() + (timeout / 1000)

        while time.monotonic() < deadline:
            combo.click(force=True)

            if matching.count() > 0:
                break

            combo.click(force=True)
            self.page.wait_for_timeout(3000)
        else:
            combo.click(force=True)

        matching.last.click()

    def verify_assessment_completed(self, timeout=45000):

        expect(
            self.page.get_by_role("progressbar")
        ).to_have_count(0, timeout=timeout)

        self.expect_visible_by_role(
            *AssessmentLocators.RECOMMENDED_RDS_HEADING
        )

        self.expect_visible_by_role(
            *AssessmentLocators.MIGRATION_BLOCKERS_HEADING
        )

        self.expect_visible_by_role(
            *AssessmentLocators.EXPORT_JSON_BUTTON
        )

        self.expect_visible_by_role(
            *AssessmentLocators.EXPORT_PDF_BUTTON
        )
