from playwright.sync_api import expect

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

    # ---------------------------------------------------------
    # Capture setup - Source Deployment
    # ---------------------------------------------------------

    def add_source_deployment(self, deployment_name):

        self.right_click_diagram_node(DesignerLocators.SOURCE_DEPLOYMENT)

        self.click_by_role("menuitem", "Add")

        combo = self.page.get_by_role(
            DesignerLocators.DEPLOYMENT_NAME_COMBOBOX[0],
            name=DesignerLocators.DEPLOYMENT_NAME_COMBOBOX[1]
        )

        combo.click(force=True)

        self.page.get_by_text(deployment_name, exact=True).click()

        self.click_by_role("button", "OK")

        # Triggers an async "Fetching from Source Vault" progress
        # dialog that can take 10-30s+.
        self.wait_for_dialog_to_close(timeout=45000)

    # ---------------------------------------------------------
    # Capture setup - Source Vault (deployment-level Secure Vault)
    # ---------------------------------------------------------

    def add_source_vault(self, domain, alias, pdb_name, schema):

        self.right_click_diagram_node(
            DesignerLocators.SOURCE_CREDENTIAL_STORE
        )

        self.click_by_role("menuitem", "Add")

        domain_input = self.page.locator(
            DesignerLocators.SRC_SECRET_DOMAIN_INPUT
        )
        domain_input.click()
        self.page.get_by_role("option", name=domain).click()

        alias_input = self.page.locator(
            DesignerLocators.SRC_SECRET_ALIAS_INPUT
        )
        # A floating hint label overlaps this input once the domain is
        # selected and intercepts plain clicks - force is required.
        alias_input.click(force=True)
        self.page.get_by_role(
            "option",
            name=alias,
            exact=True
        ).click()

        # Only rendered once a CDB-root alias with a properly registered
        # PDB is selected above - if this hangs, the vault/CDB isn't set
        # up correctly (see CDC-08223 in migdb-framework-state memory).
        pdb_input = self.page.locator(DesignerLocators.SRC_PDB_NAME_INPUT)
        pdb_dropdown = self.page.locator(DesignerLocators.SRC_PDB_NAME_DROPDOWN)

        # This dropdown's option list loads asynchronously after the
        # click with no visible loading indicator (same class of race
        # documented elsewhere in this app, e.g. Config Tables' View tab
        # and Supplemental Logging's schema dropdown) - found live
        # 2026-08-05 on a fresh environment: a single click+wait isn't
        # reliable (the popup can open before the async fetch lands and
        # never pick up the rows once they arrive), so retry the click
        # itself, not just the wait - same retry-the-open pattern
        # already proven in SupplementalLoggingPage.select_trandata_schema.
        rows_ready = False
        for attempt in range(3):
            pdb_input.click(force=True)
            try:
                expect(pdb_dropdown.first).to_be_visible(timeout=8000)
                rows_ready = True
                break
            except AssertionError:
                # Neutral click elsewhere to close the stuck/empty popup
                # before retrying (Escape has been observed to collapse
                # the whole form on this widget family).
                self.page.get_by_text("Select Source SecretStore").click()
                self.page.wait_for_timeout(1000)

        if not rows_ready:
            expect(pdb_dropdown.first).to_be_visible(timeout=8000)

        pdb_dropdown.filter(has_text=pdb_name).first.click()

        # Schema multi-select chip combobox - the last combobox to
        # appear in this form once alias+PDB are both selected. Same
        # async-populate-after-click race as the PDB dropdown above -
        # retry the open rather than a single wait.
        schema_combo = self.page.get_by_role("combobox").last
        schema_option = self.page.get_by_role(
            "option",
            name=schema,
            exact=True
        )

        option_ready = False
        for attempt in range(3):
            schema_combo.click(force=True)
            try:
                expect(schema_option).to_be_visible(timeout=8000)
                option_ready = True
                break
            except AssertionError:
                self.page.get_by_text("Select Source SecretStore").click()
                self.page.wait_for_timeout(1000)

        if not option_ready:
            expect(schema_option).to_be_visible(timeout=8000)

        schema_option.click()

    def analyze_and_confirm_source_vault(self):

        self.click_by_role(*DesignerLocators.ANALYZE_SELECTED_SCHEMAS_BUTTON)

        # Opens a second, stacked "Tables to Exclude" dialog listing the
        # discovered tables - close it without excluding anything (its
        # own Close button, not the outer dialog's).
        self.page.get_by_role(
            DesignerLocators.TABLES_TO_EXCLUDE_HEADING[0],
            name=DesignerLocators.TABLES_TO_EXCLUDE_HEADING[1]
        ).locator(
            "xpath=ancestor::*[@role='dialog']"
        ).get_by_label("Close").click()

        self.click_by_role("button", "OK")

        self.wait_for_dialog_to_close(timeout=45000)

    # ---------------------------------------------------------
    # Capture setup - Integrated Extract
    # ---------------------------------------------------------

    def add_integrated_extract(
        self,
        extract_name,
        trail_name,
        pdb_name
    ):

        self.right_click_diagram_node(DesignerLocators.INTEGRATED_EXTRACT)

        self.click_by_role("menuitem", "Add")

        self.page.get_by_label(
            DesignerLocators.EXTRACT_NAME_LABEL
        ).fill(extract_name)

        self.page.get_by_label(
            DesignerLocators.TRAIL_NAME_LABEL
        ).fill(trail_name)

        # A second, independent required PDB field on this step (distinct
        # widget from Source Vault's PDB field) - must be filled before
        # submission succeeds, per CDC-08223.
        choose_pdb = self.page.get_by_role(
            DesignerLocators.CHOOSE_PDB_COMBOBOX[0],
            name=DesignerLocators.CHOOSE_PDB_COMBOBOX[1]
        )
        choose_pdb.click(force=True)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=pdb_name).first.click()

        self.click_by_role("button", "Next")

        self.click_by_role(*DesignerLocators.ADD_INTEGRATED_EXTRACT_BUTTON)

        # Submission goes through a transient "Creating Integrated
        # Extract" progress dialog, then a final success confirmation
        # ("Integrated Extract <name> - Integrated Extract added.
        # EXTTRAIL added.") that does NOT auto-dismiss - found live
        # 2026-08-05: this previously just waited for any dialog to
        # clear on its own, which left the real success dialog stuck
        # open (and the extract WAS created successfully - confirmed via
        # screenshot - this was purely a missed OK click, not a failure).
        ok_button = self.page.locator(
            "[role='dialog']:visible"
        ).get_by_role("button", name="OK")
        expect(ok_button).to_be_visible(timeout=45000)
        ok_button.click()

        self.wait_for_dialog_to_close()

    # ---------------------------------------------------------
    # Apply setup - Target Deployment / Target CredentialStore
    # ---------------------------------------------------------

    def add_target_deployment(self, deployment_name):

        self.right_click_diagram_node(DesignerLocators.TARGET_DEPLOYMENT)

        self.click_by_role("menuitem", "Add")

        combo = self.page.get_by_role(
            DesignerLocators.DEPLOYMENT_NAME_COMBOBOX[0],
            name=DesignerLocators.DEPLOYMENT_NAME_COMBOBOX[1]
        )

        combo.click(force=True)

        self.page.get_by_text(deployment_name, exact=True).click()

        self.click_by_role("button", "OK")

        self.wait_for_dialog_to_close(timeout=45000)

    def add_target_credential_store(self, domain, alias, db_name, pdb_name):

        self.right_click_diagram_node(
            DesignerLocators.TARGET_CREDENTIAL_STORE
        )

        self.click_by_role("menuitem", "Add")

        domain_input = self.page.locator(
            DesignerLocators.TGT_SECRET_DOMAIN_INPUT
        )
        domain_input.click()
        self.page.get_by_role("option", name=domain).click()

        alias_combo = self.page.get_by_role(
            DesignerLocators.TGT_SECRET_ALIAS_COMBOBOX[0],
            name=DesignerLocators.TGT_SECRET_ALIAS_COMBOBOX[1]
        )
        alias_combo.click(force=True)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=alias).first.click()

        # Populates the Target Database Details grid - select that row
        # before OK (same required-click pattern as Initial Load's grids).
        row = self.page.get_by_role(
            "row",
            name=f"{db_name} {pdb_name}",
            exact=False
        ).first
        row.click()

        self.click_by_role("button", "OK")

        self.wait_for_dialog_to_close(timeout=45000)

    # ---------------------------------------------------------
    # Apply setup - Extract Pump / Classic Replicat
    # ---------------------------------------------------------
    #
    # NOTE: these two methods are built from a confirmed-live dialog
    # structure (field labels, wizard steps, submit button text) but the
    # full submission has NOT been exercised end-to-end - Pump Name/
    # Remote Trail Name/Replicat Name are new short GoldenGate-style
    # names (same character-limit family as Integrated Extract's 8-char
    # Extract Name) that need real values confirmed with the user before
    # ever running for real, exactly like SAMPAPP1/st needed confirming.
    # RLP1 already provides a complete, working real pipeline, so the
    # test built around these methods only calls them if RLP1 (or the
    # configured replicat name) is missing from Monitor - don't create a
    # second, disposable real Extract Pump/Replicat without a confirmed
    # need and confirmed names (no delete flow exists for either).
    #
    # CONFIRMED REAL BUG (2026-08-05, fresh on-prem environment where no
    # pipeline existed yet, forcing this branch to actually run for the
    # first time): Add Extract Pump's submit reliably fails with a
    # captured network response of
    #   405 http://<host>:8080/undefined/api/v2/pump/add
    #   {"detail":"Method Not Allowed"}
    # - the request URL has a literal "undefined" path segment, a
    # frontend JS bug (some deployment/base-URL variable isn't set
    # before being interpolated into the request path), not a locator/
    # timing issue - confirmed via direct network capture, reproduced
    # consistently across multiple attempts including with force=True
    # clicks and generous waits. Same category as the impParallel type
    # bug (Homogeneous Initial Load) and the check_parameters NameError
    # (Assessment) - a real product bug to report to the MigDB dev team,
    # not fixable from the test side. This blocks Classic Replicat too
    # (Extract Pump is a prerequisite node in the diagram).
    #
    # Reproduced again manually 2026-08-11 (same 405/undefined URL) with
    # two additional Chrome DevTools console warnings on this same
    # dialog worth including in the same bug report (non-fatal, doesn't
    # affect automation - this app doesn't rely on ARIA focus semantics
    # here): "Blocked aria-hidden on an element because its descendant
    # retained focus" fired twice - once for the wizard's own
    # `AddExtract_layer` dialog (focus was on the `.oj-train-label`
    # step indicator) and once for the underlying page body (focus was
    # on the capture diagram, `oj-diagram#diagram2`) while it sat behind
    # an aria-hidden ancestor. Root cause pattern: the dialog/overlay is
    # marking its background `aria-hidden="true"` without first moving
    # focus out of it - a real accessibility bug in the same dialog as
    # the 405, not a new/separate issue.

    def add_extract_pump(self, pump_name, remote_trail_name):

        self.right_click_diagram_node(DesignerLocators.EXTRACT_PUMP)

        self.click_by_role("menuitem", "Add")

        self.page.get_by_label(
            DesignerLocators.PUMP_NAME_LABEL
        ).fill(pump_name)

        self.page.get_by_label(
            DesignerLocators.REMOTE_TRAIL_NAME_LABEL
        ).fill(remote_trail_name)

        self.click_by_role("button", "Next")

        self.page.wait_for_timeout(1000)

        self.page.get_by_role(
            DesignerLocators.ADD_EXTRACT_PUMP_BUTTON[0],
            name=DesignerLocators.ADD_EXTRACT_PUMP_BUTTON[1]
        ).click(force=True)

        # Same pattern as Integrated Extract: goes through a transient
        # "Creating Network Pump" progress dialog, then a final success
        # confirmation that does NOT auto-dismiss and needs an explicit
        # OK click - found live 2026-08-05.
        ok_button = self.page.locator(
            "[role='dialog']:visible"
        ).get_by_role("button", name="OK")
        expect(ok_button).to_be_visible(timeout=60000)
        ok_button.click()

        self.wait_for_dialog_to_close()

    def add_classic_replicat(
        self,
        replicat_name,
        source_extract,
        checkpoint_table
    ):

        self.right_click_diagram_node(DesignerLocators.CLASSIC_REPLICAT)

        self.click_by_role("menuitem", "Add")

        self.page.get_by_label(
            DesignerLocators.REPLICAT_NAME_LABEL
        ).fill(replicat_name)

        source_extract_field = self.page.get_by_label(
            DesignerLocators.SOURCE_EXTRACT_LABEL
        )
        source_extract_field.click(force=True)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=source_extract).first.click()

        checkpoint_field = self.page.get_by_label(
            DesignerLocators.CHECKPOINT_TABLE_LABEL
        )
        checkpoint_field.click(force=True)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=checkpoint_table).first.click()

        self.click_by_role("button", "Next")

        self.click_by_role(*DesignerLocators.ADD_CLASSIC_REPLICAT_BUTTON)

        # Same pattern as Integrated Extract/Extract Pump - a final
        # success confirmation that needs an explicit OK click.
        ok_button = self.page.locator(
            "[role='dialog']:visible"
        ).get_by_role("button", name="OK")
        expect(ok_button).to_be_visible(timeout=60000)
        ok_button.click()

        self.wait_for_dialog_to_close()

    # ---------------------------------------------------------
    # Verification
    # ---------------------------------------------------------

    def is_replicat_listed(self, replicat_name, timeout=15000):
        """Widened from a 5000ms default (2026-08-11): Monitor is a
        live-data screen subject to the same "Fetching..." transient-
        dialog lag confirmed on several other screens this session. A
        false "not listed" here is worse than on a plain structure
        check - it sends the caller into the real, no-delete-flow
        creation branch for infrastructure that already exists, hitting
        the confirmed real backend bugs on that path (see
        docs/TROUBLESHOOTING.md) for no reason. Don't shrink this back
        down without re-confirming Monitor loads reliably within 5s.
        """

        try:
            expect(
                self.page.get_by_text(replicat_name, exact=True)
            ).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def verify_replicat_running(self, replicat_name, timeout=30000):

        expect(
            self.page.get_by_text(replicat_name, exact=True)
        ).to_be_visible(timeout=timeout)

    def open_monitor(self):

        # Manage's "WatchDog Processes" grid does NOT list named
        # Extract/Replicat processes (only the MANAGER component) -
        # Monitor's "Extracts" section is the correct place to verify.
        # "Monitor" is not a normal treeitem (its accessible role/name
        # don't resolve via click_tree_item) - it needs id-based lookup,
        # same as NavigationPage.verify_navigation_menu() already does.
        self.click_by_id("monitor")
        self.wait()

    def is_extract_listed(self, extract_name, timeout=15000):

        try:
            expect(
                self.page.get_by_text(extract_name, exact=True)
            ).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def verify_extract_running(self, extract_name, timeout=30000):

        expect(
            self.page.get_by_text(extract_name, exact=True)
        ).to_be_visible(timeout=timeout)