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
        combo.click(force=True)
        self.page.get_by_text(deployment_name, exact=True).click()

        # Triggers an async source-vault fetch before the CDB/alias
        # combobox is usable, same lag family as Designer's equivalent
        # step.
        self.page.wait_for_timeout(5000)

    def select_source(self, alias, pdb_name, schema, load_name):

        alias_combo = self.page.get_by_role(
            InitialLoadLocators.SOURCE_ALIAS_COMBOBOX[0],
            name=InitialLoadLocators.SOURCE_ALIAS_COMBOBOX[1]
        ).first
        alias_combo.click(force=True)
        self.page.wait_for_timeout(3000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=alias).first.click()

        # Selecting the alias reveals Choose PDB Name/Export Mode/Choose
        # Schema Name asynchronously with no visible loading indicator.
        self.page.wait_for_timeout(6000)

        pdb_combo = self.page.get_by_role(
            InitialLoadLocators.SOURCE_PDB_NAME_COMBOBOX[0],
            name=InitialLoadLocators.SOURCE_PDB_NAME_COMBOBOX[1]
        )
        pdb_combo.click(force=True)
        self.page.wait_for_timeout(2000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=pdb_name).first.click()
        self.page.wait_for_timeout(3000)

        schema_combo = self.page.get_by_role(
            InitialLoadLocators.SCHEMA_NAME_COMBOBOX[0],
            name=InitialLoadLocators.SCHEMA_NAME_COMBOBOX[1]
        )
        schema_combo.click(force=True)
        self.page.wait_for_timeout(3000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=schema).first.click()
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
        target_deploy.click(force=True)
        self.page.wait_for_timeout(2000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=deployment_name).first.click()
        self.page.wait_for_timeout(4000)

        # No accessible name at all - it's the last combobox on the page
        # once Target Deployment is chosen.
        target_alias_combo = self.page.get_by_role("combobox").last
        target_alias_combo.click(force=True)
        self.page.wait_for_timeout(3000)
        self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=alias).first.click()
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
        # one is a REAL failure: confirmed via network capture that
        # POST /api/v2/datapump/export returns HTTP 422 because the
        # app's own frontend sends "impParallel" as a number instead of
        # a string like "expParallel" - a real product bug, not
        # something a retry or different UI path can work around. Fail
        # fast with a clear message instead of a confusing downstream
        # timeout on the next unrelated navigation click.
        technical_issue = self.page.get_by_text(
            "There is a technical issue",
            exact=False
        )
        if technical_issue.is_visible():
            raise AssertionError(
                "Create Job failed: app shows 'There is a technical "
                "issue' - confirmed via network capture this is a real "
                "backend 422 on POST /api/v2/datapump/export "
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
