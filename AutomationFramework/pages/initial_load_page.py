from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.initial_load_locators import InitialLoadLocators


class InitialLoadPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def open_homogeneous_initial_load(self):
        self.page.get_by_role(
            "treeitem",
            name=InitialLoadLocators.NAV_ITEM,
            exact=False
        ).click()
        self.wait()

    def open_homo_initial_load_monitor(self):
        self.page.get_by_role(
            "treeitem",
            name=InitialLoadLocators.MONITOR_NAV_ITEM,
            exact=False
        ).click()
        self.wait()

    # ---------------------------------------------------------
    # DataSource step - source side
    # ---------------------------------------------------------

    def select_source_deployment(self, deployment_name):

        combo = self.page.get_by_role(
            InitialLoadLocators.DEPLOYMENT_NAME_COMBOBOX[0],
            name=InitialLoadLocators.DEPLOYMENT_NAME_COMBOBOX[1]
        )
        self.select_stable_combobox(combo, deployment_name)

        # Triggers an async source-vault fetch before the CDB/alias
        # combobox is usable, same lag family as Designer's equivalent
        # step.
        self.page.wait_for_timeout(5000)

    def select_source(self, alias, pdb_name, schema, load_name):

        alias_combo = self.page.get_by_role(
            InitialLoadLocators.SOURCE_ALIAS_COMBOBOX[0],
            name=InitialLoadLocators.SOURCE_ALIAS_COMBOBOX[1]
        ).first
        self.select_stable_combobox(alias_combo, alias)

        # Selecting the alias reveals Choose PDB Name/Export Mode/Choose
        # Schema Name asynchronously with no visible loading indicator.
        self.page.wait_for_timeout(6000)

        pdb_combo = self.page.get_by_role(
            InitialLoadLocators.SOURCE_PDB_NAME_COMBOBOX[0],
            name=InitialLoadLocators.SOURCE_PDB_NAME_COMBOBOX[1]
        )
        self.select_stable_combobox(pdb_combo, pdb_name)
        self.page.wait_for_timeout(3000)

        schema_combo = self.page.get_by_role(
            InitialLoadLocators.SCHEMA_NAME_COMBOBOX[0],
            name=InitialLoadLocators.SCHEMA_NAME_COMBOBOX[1]
        )
        self.select_stable_combobox(schema_combo, schema)
        self.page.wait_for_timeout(2000)

        load_name_input = self.page.get_by_role(
            InitialLoadLocators.LOAD_NAME_TEXTBOX[0],
            name=InitialLoadLocators.LOAD_NAME_TEXTBOX[1]
        )
        load_name_input.fill(load_name)
        self.page.wait_for_timeout(1000)

    def select_source_db_row(self, db_name, pdb_name):

        row = self.page.get_by_role(
            "row",
            name=f"{db_name} {pdb_name}",
            exact=False
        ).first
        row.click()
        self.page.wait_for_timeout(1500)

    def analyze_selected_schemas(self):

        self.click_by_role(*InitialLoadLocators.ANALYZE_SCHEMAS_BUTTON)

        # Populates the "Tables to exclude from Initial Load" grid from
        # a real schema-analysis call - can take several seconds.
        self.page.wait_for_timeout(10000)

    # ---------------------------------------------------------
    # DataSource step - target side
    # ---------------------------------------------------------

    def select_target(self, deployment_name, alias):

        target_deploy = self.page.get_by_role(
            InitialLoadLocators.TARGET_DEPLOYMENT_COMBOBOX[0],
            name=InitialLoadLocators.TARGET_DEPLOYMENT_COMBOBOX[1]
        )
        self.select_stable_combobox(target_deploy, deployment_name)

        # Async fetch of target CDB/PDB metadata after this selection -
        # confirmed live this needs a genuinely generous wait (12s), not
        # the 4s this used to have, on the current app build.
        self.page.wait_for_timeout(12000)

        # Real app bug, confirmed live 2026-08-10: this field's visible
        # hint text reads "Choose PDB(in CDB Mode)" but it has NO
        # aria-labelledby at all, and shares its DOM id
        # ("SRCDBDomain|input") with the unrelated SOURCE alias field
        # above - so get_by_role(name=...) can never match it, and the
        # old ".last combobox" positional guess breaks whenever a new
        # element gets inserted after it (also confirmed live - a
        # duplicate hidden template now sits after it in DOM order).
        # Report to the dev team: this needs a real aria-labelledby
        # fix, and the duplicate id needs to be unique. Until then,
        # target the second (visible, non-empty-value) element sharing
        # the source alias field's id rather than accessible name or
        # plain position.
        target_alias_combo = self.page.get_by_role(
            "combobox",
            name="Choose PDB(in CDB Mode)"
        )
        if target_alias_combo.count() == 0:
            target_alias_combo = self.page.locator(
                "[id='SRCDBDomain|input']"
            ).last

        self.select_stable_combobox(target_alias_combo, alias)
        self.page.wait_for_timeout(4000)

    def select_target_db_row(self, db_name, pdb_name):

        row = self.page.get_by_role(
            "row",
            name=f"{db_name} {pdb_name}",
            exact=False
        ).first
        row.click()
        self.page.wait_for_timeout(1500)

    # ---------------------------------------------------------
    # Export/Import Options - both required before Create Job enables
    # ---------------------------------------------------------

    def _configure_directory_options(
        self,
        button_locator,
        dialog_text,
        directory_name
    ):

        self.click_by_role(*button_locator)
        self.page.wait_for_timeout(3000)

        dialog = self.page.locator(
            "[role='dialog']:visible"
        ).filter(has_text=dialog_text)

        dir_combo = dialog.get_by_role(
            InitialLoadLocators.DIRECTORY_NAME_COMBOBOX[0],
            name=InitialLoadLocators.DIRECTORY_NAME_COMBOBOX[1]
        )
        dir_combo.click(force=True)
        self.page.wait_for_timeout(3000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=directory_name).first.click()
        self.page.wait_for_timeout(2000)

        dialog.get_by_role(
            InitialLoadLocators.SAVE_BUTTON[0],
            name=InitialLoadLocators.SAVE_BUTTON[1]
        ).click()
        self.wait_for_dialog_to_close(dialog_text)

    def configure_export_options(self, directory_name):

        self._configure_directory_options(
            InitialLoadLocators.EXPORT_OPTIONS_BUTTON,
            InitialLoadLocators.EXPORT_OPTIONS_DIALOG_TEXT,
            directory_name
        )

    def configure_import_options(self, directory_name):

        self._configure_directory_options(
            InitialLoadLocators.IMPORT_OPTIONS_BUTTON,
            InitialLoadLocators.IMPORT_OPTIONS_DIALOG_TEXT,
            directory_name
        )

    # ---------------------------------------------------------
    # Submission and verification
    # ---------------------------------------------------------

    def create_job(self):

        self.click_by_role(*InitialLoadLocators.CREATE_JOB_BUTTON)
        self.page.wait_for_timeout(5000)

        # Unlike Assessment's identical-looking "technical issue" dialog
        # (a confirmed false negative - the job completes anyway), this
        # one is a REAL failure: confirmed via network capture (still
        # true as of 2026-08-10, after an app-binary update that did NOT
        # fix it) that POST /api/v2/datapump/export returns HTTP 422
        # because the app's own frontend sends "impParallel" as a number
        # instead of a string like "expParallel" - a real product bug,
        # not something a retry or different UI path can work around.
        #
        # The 2026-08-10 binary update changed HOW this specific error
        # surfaces - it's now a dedicated "Error" dialog with the raw
        # backend message ("body.impParallel: Input should be a valid
        # string") instead of the old generic "There is a technical
        # issue" text. Checking only the old text left this dialog open
        # and undetected, which then blocked the next navigation click
        # with a confusing, unrelated-looking 30s timeout instead of
        # this clear assertion. Check both so this keeps working
        # whichever dialog text a given build actually shows, and close
        # whatever's found so the test doesn't leave a dialog open for
        # the next step to trip over.
        technical_issue = self.page.get_by_text(
            "There is a technical issue",
            exact=False
        )
        error_dialog = self.page.locator(
            "[role='dialog']:visible"
        ).filter(has_text="Error")

        if technical_issue.is_visible():
            raise AssertionError(
                "Create Job failed: app shows 'There is a technical "
                "issue' - confirmed via network capture this is a real "
                "backend 422 on POST /api/v2/datapump/export "
                "('impParallel' sent as a number, must be a string). "
                "This is a real product bug, not a test/locator issue."
            )

        if error_dialog.count() > 0:
            error_text = error_dialog.first.inner_text()
            error_dialog.first.get_by_role("button", name="OK").click()
            raise AssertionError(
                f"Create Job failed: app shows an Error dialog "
                f"({error_text!r}) - confirmed via network capture this "
                "is a real backend 422 on POST /api/v2/datapump/export "
                "('impParallel' sent as a number, must be a string). "
                "This is a real product bug, not a test/locator issue."
            )

        self.wait()

    def is_load_listed(self, load_name, timeout=5000):

        try:
            expect(
                self.page.get_by_text(load_name, exact=True)
            ).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def verify_load_completed(self, load_name, timeout=60000):

        expect(
            self.page.get_by_text(load_name, exact=True)
        ).to_be_visible(timeout=timeout)

    # ---------------------------------------------------------
    # Heterogeneous Initial Load - screen structure only, confirmed
    # live 2026-08-06 (not exercised for a real cross-platform load
    # this session - this environment is Oracle-only).
    # ---------------------------------------------------------

    def open_heterogeneous_initial_load(self):

        self.click_tree_item(InitialLoadLocators.HETERO_NAV_ITEM)
        self.wait()

    def verify_heterogeneous_screen_structure(self):

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_MAIN_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.DEPLOYMENT_NAME_COMBOBOX
        )

        # "Required Secret Domain" renders twice (source + target side
        # each have their own) - strict mode violation via the shared
        # single-match helper, same class of issue as Analyze Objects'
        # duplicate "All Table" tables. Confirm both exist instead.
        expect(
            self.page.get_by_role(
                InitialLoadLocators.HETERO_SECRET_DOMAIN_COMBOBOX[0],
                name=InitialLoadLocators.HETERO_SECRET_DOMAIN_COMBOBOX[1]
            )
        ).to_have_count(2)

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_SECRET_ALIAS_COMBOBOX
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_GATHER_METADATA_SWITCH
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_LOAD_OPTIONS_RADIOGROUP
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_TARGET_DEPLOYMENT_COMBOBOX
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_CHECKPOINT_TABLE_COMBOBOX
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_DEFER_START_SWITCH
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_CREATE_JOB_BUTTON
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_EXCLUDE_TABLES_HEADING
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETERO_SEARCH_TABLES_TEXTBOX
        )

    # ---------------------------------------------------------
    # Hetro / Homo Initial Load Monitor - screen structure only,
    # confirmed live 2026-08-06.
    # ---------------------------------------------------------

    def open_hetro_initial_load_monitor(self):

        self.click_tree_item(InitialLoadLocators.HETRO_MONITOR_NAV_ITEM)
        self.wait()

    def verify_hetro_monitor_screen_structure(self):

        self.expect_visible_by_role(
            *InitialLoadLocators.HETRO_MONITOR_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.SELECT_LOAD_GROUP_COMBOBOX
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.HETRO_MONITOR_ACTIONS_BUTTON
        )

    def verify_homo_monitor_screen_structure(self):

        self.expect_visible_by_role(
            *InitialLoadLocators.HOMO_MONITOR_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.SELECT_LOAD_GROUP_COMBOBOX
        )

        self.expect_visible_by_role(
            *InitialLoadLocators.RESUMABLE_TASKS_TABLE
        )
