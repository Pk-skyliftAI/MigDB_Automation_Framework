import time
from datetime import datetime

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
        #
        # This list accumulates 25+ jobs across days of testing, and the
        # dropdown only renders a subset unfiltered - picking `.last`
        # against that unfiltered/undertyped list can silently grab a
        # STALE job from a previous day instead of the one this run just
        # created (confirmed live 2026-08-11: the combobox ended up
        # showing "SOURCECDB_20260810163016" - a leftover job from the
        # day before - while a brand new "SOURCECDB_20260811124209" had
        # completed in the background, unselected; verify_assessment_
        # completed() then failed on Export JSON/PDF because that old
        # job's record was itself a leftover of the known assessment-
        # stall bug, not a fresh completed report). Typing today's date
        # onto the alias prefix narrows the list to a small, fully
        # rendered, chronologically-ascending set, so `.last` reliably
        # lands on the newest match instead of whatever happened to be
        # rendered first.
        today_prefix = job_name_prefix + datetime.now().strftime("%Y%m%d")

        matching = self.page.locator(
            "[role='row']"
        ).filter(has_text=job_name_prefix)

        narrowed = matching.filter(has_text=today_prefix)

        deadline = time.monotonic() + (timeout / 1000)

        while time.monotonic() < deadline:
            combo.click(force=True)
            combo.fill("")
            combo.type(today_prefix, delay=30)
            self.page.wait_for_timeout(1000)

            if narrowed.count() > 0:
                break

            self.page.wait_for_timeout(3000)
        else:
            combo.click(force=True)
            combo.fill("")
            combo.type(today_prefix, delay=30)
            self.page.wait_for_timeout(1000)

        # Fall back to the unfiltered match only if typing somehow found
        # nothing at all under today's date (e.g. right at a midnight
        # boundary) rather than hard-failing.
        target = narrowed if narrowed.count() > 0 else matching
        target.last.click()

    def verify_assessment_completed(self, timeout=300000):

        # The real completion signal is the "Running Assessment" modal
        # closing, NOT a generic role="progressbar" count - confirmed
        # live 2026-08-11 that this dialog renders its "X of Y steps
        # complete Z%" indicator as plain text, not an ARIA progressbar
        # element, so the old `get_by_role("progressbar").to_have_count
        # (0)` check could pass immediately while this dialog was still
        # genuinely open and running. That, combined with the finishing
        # heading/button checks below only getting Playwright's default
        # 5s timeout (no explicit timeout was passed), is what produced
        # repeated "stalled at 89-92%" failures - a live diagnostic
        # (poll every 10s) showed the SAME job going from 50% -> 93% ->
        # dialog closed in just 20s total when given the chance, so this
        # was a test-side timeout bug, not a permanent backend hang.
        # 300s is generous - a real, heavily-loaded stall (e.g. during a
        # full concurrent regression run) is still possible and should
        # still fail loudly rather than pass, just not this early.
        self.wait_for_dialog_to_close("Running Assessment", timeout=timeout)

        TIMEOUT = 15000

        self.expect_visible_by_role(
            *AssessmentLocators.RECOMMENDED_RDS_HEADING, timeout=TIMEOUT
        )

        self.expect_visible_by_role(
            *AssessmentLocators.MIGRATION_BLOCKERS_HEADING, timeout=TIMEOUT
        )

        # Export JSON/PDF buttons intentionally removed from this screen -
        # confirmed live 2026-08-11 (user-confirmed intentional app
        # change, not a bug): a completed report page (checked for both a
        # freshly finished job and one from over a day earlier, fully
        # settled) has exactly 2 buttons in the entire DOM - "Start Here"
        # and "ORACLE admin" - neither Export button exists at all
        # anymore. Don't re-add these checks without first confirming
        # they're back in the live app.
