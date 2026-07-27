import re

from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.supplemental_logging_locators import SupplementalLoggingLocators


class SupplementalLoggingPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def verify_page_loaded(self):
        self.expect_visible_by_text(
            SupplementalLoggingLocators.CHOOSE_CDB
        )

        self.expect_visible_by_text(
            SupplementalLoggingLocators.DATABASE_CHECKS
        )

    def select_cdb(self, cdb_name):

        self.select_cdb_combobox(cdb_name)

        expect(
            self.page.get_by_role(
                SupplementalLoggingLocators.ENABLE_DISABLE_TRANDATA_HEADING[0],
                name=SupplementalLoggingLocators.ENABLE_DISABLE_TRANDATA_HEADING[1]
            )
        ).to_be_visible(timeout=15000)

    def verify_action_buttons(self):

        for role, name in (

            SupplementalLoggingLocators.ADD_TRANDATA,
            SupplementalLoggingLocators.VIEW_TRANDATA,
            SupplementalLoggingLocators.DELETE_TRANDATA,

        ):
            self.expect_visible_by_role(role, name)

    # ---------------------------------------------------------
    # Trandata tab navigation
    # ---------------------------------------------------------

    def open_add_trandata_tab(self):
        self.select_stable_tab(SupplementalLoggingLocators.ADD_TRANDATA[1])

    def open_view_trandata_tab(self):
        self.select_stable_tab(SupplementalLoggingLocators.VIEW_TRANDATA[1])

    def open_delete_trandata_tab(self):
        self.select_stable_tab(SupplementalLoggingLocators.DELETE_TRANDATA[1])

    # ---------------------------------------------------------
    # Trandata target selection (identical fields on all three tabs)
    # ---------------------------------------------------------

    def select_trandata_domain(self, domain):

        combo = self.page.get_by_role(
            SupplementalLoggingLocators.VAULT_DOMAIN_COMBOBOX[0],
            name=SupplementalLoggingLocators.VAULT_DOMAIN_COMBOBOX[1],
            exact=True
        )

        # Its options load asynchronously - the accessible name carries a
        # "Loading domains" suffix until they're ready, so exact=True
        # above only matches once that clears.
        expect(combo).to_be_visible(timeout=20000)

        combo.click()
        combo.fill(domain)

        self.page.get_by_role("option", name=domain).click()

        # The dropdown doesn't auto-close on selection and would
        # otherwise intercept the next field's click.
        self.page.keyboard.press("Escape")

    def select_trandata_alias(self, alias):

        combo = self.page.get_by_role(
            SupplementalLoggingLocators.VAULT_ALIAS_COMBOBOX[0],
            name=SupplementalLoggingLocators.VAULT_ALIAS_COMBOBOX[1]
        )

        combo.click(force=True)

        self.page.get_by_role(
            "option",
            name=alias,
            exact=True
        ).click()

    def _schema_rows_ready(self, timeout):
        try:
            expect(
                self.page.locator(
                    f"#{SupplementalLoggingLocators.SCHEMA_NAME_DROPDOWN_ID} [role='row']"
                ).first
            ).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def select_trandata_schema(self, schema, alias=None, retries=3):

        combo = self.page.locator(
            f"[id='{SupplementalLoggingLocators.SCHEMA_NAME_INPUT_ID}']:visible"
        )
        combo.first.click(force=True)

        # Selecting the PDB (above) re-fetches this field's schema list
        # asynchronously with no visible loading indicator, and it can
        # take a while - opening the dropdown before that fetch resolves
        # and typing a filter races it and reports "No matches found".
        # Waiting for at least one unfiltered row confirms the fetch has
        # actually landed. If it never does, re-selecting the alias (the
        # trigger for that fetch) and reopening tends to unstick it -
        # pressing Escape here instead has been observed to collapse the
        # whole form, so a neutral click closes the dropdown instead.
        for attempt in range(retries):
            if self._schema_rows_ready(timeout=15000):
                break

            if attempt == retries - 1 or not alias:
                break

            self.page.get_by_role(
                SupplementalLoggingLocators.ENABLE_DISABLE_TRANDATA_HEADING[0],
                name=SupplementalLoggingLocators.ENABLE_DISABLE_TRANDATA_HEADING[1]
            ).click()
            self.page.wait_for_timeout(1000)

            self.select_trandata_alias(alias)
            self.page.wait_for_timeout(2000)

            combo.first.click(force=True)

        filter_input = self.page.locator(
            f"input[id='{SupplementalLoggingLocators.SCHEMA_NAME_FILTER_INPUT_ID}']:visible"
        )
        filter_input.fill(schema)

        row = self.page.locator(
            f"#{SupplementalLoggingLocators.SCHEMA_NAME_DROPDOWN_ID} [role='row']"
        ).filter(
            has_text=re.compile(rf"^{re.escape(schema)}$")
        ).first

        # The filtered row animates in (oj-animate-add) and briefly
        # reports as not visible mid-transition; wait it out before
        # clicking rather than racing the animation.
        expect(row).to_be_visible(timeout=10000)
        self.page.wait_for_timeout(500)

        row.click()

    def select_trandata_target(self, domain, alias, schema):
        self.select_trandata_domain(domain)
        self.select_trandata_alias(alias)
        self.select_trandata_schema(schema, alias=alias)

    # ---------------------------------------------------------
    # Add / View / Delete submission
    # ---------------------------------------------------------

    def submit_add_trandata(self):
        self.click_by_role(*SupplementalLoggingLocators.ADD_SCHEMA_TRANDATA_BUTTON)

    def submit_view_trandata(self):
        self.click_by_role(*SupplementalLoggingLocators.VIEW_SCHEMA_TRANDATA_BUTTON)

    def submit_delete_trandata(self):

        self.click_by_role(
            *SupplementalLoggingLocators.DELETE_SCHEMA_TRANDATA_BUTTON
        )

        expect(
            self.page.get_by_role(
                SupplementalLoggingLocators.DELETE_CONFIRM_DIALOG[0],
                name=SupplementalLoggingLocators.DELETE_CONFIRM_DIALOG[1]
            )
        ).to_be_visible()

        # A force click does not register reliably on this button -
        # a plain click is what actually works.
        self.click_by_role(*SupplementalLoggingLocators.YES_BUTTON)

    def verify_trandata_result(self, dialog, schema, expected_status, timeout=30000):
        """Wait for an Add/View/Delete Trandata result dialog to finish
        processing (enabling/disabling supplemental logging takes several
        seconds) and confirm the schema's status, then close it.
        """

        role, name = dialog

        expect(
            self.page.get_by_role(role, name=name)
        ).to_be_visible()

        ok_button = self.page.get_by_role(
            SupplementalLoggingLocators.OK_BUTTON[0],
            name=SupplementalLoggingLocators.OK_BUTTON[1]
        )
        expect(ok_button).to_be_visible(timeout=timeout)

        expect(
            self.page.get_by_text(schema, exact=False).first
        ).to_be_visible()

        expect(
            self.page.get_by_text(expected_status, exact=True).first
        ).to_be_visible()

        ok_button.click()

        self.wait_for_dialog_to_close()