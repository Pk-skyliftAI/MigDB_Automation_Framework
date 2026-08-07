from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.config_tables_locators import ConfigTablesLocators


class ConfigTablesPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ---------------------------------------------------------
    # CheckpointTable - View
    # ---------------------------------------------------------

    def _checkpoint_toolbar(self):
        # Scoped to the CheckpointTable section specifically - its
        # sub-tab toolbar ("Add"/"View"/"Upgrade"/"Delete") shares radio
        # names with HeartBeatTable's own toolbar just below it.
        return self.page.locator(
            "xpath=//h6[normalize-space(text())='CheckpointTable']"
            "/parent::div/following-sibling::oj-c-buttonset-single[1]"
        )

    def add_checkpoint_table(self, domain, alias, table_name):
        """Add tab is Config Tables' default landing tab - no explicit
        sub-tab click needed if arriving fresh, but callers that may be
        on another sub-tab should click "Add" via _checkpoint_toolbar()
        first.

        table_name is the 2-part "SCHEMA.TABLENAME" the Add form's own
        tooltip specifies - NOT the 3-part "PDB.SCHEMA.TABLENAME" the
        View tab's dropdown displays once the table exists.
        """

        domain_combo = self.page.get_by_role("combobox").nth(0)
        self.select_lazy_combobox(domain_combo, domain)

        alias_combo = self.page.get_by_role(
            ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
            name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
        ).first
        self.select_lazy_combobox(alias_combo, alias)

        # Unlabeled textbox - the CheckpointTable form's own "Checkpoint
        # TableName" field is the first textbox on the page in DOM
        # order (CheckpointTable's section renders above HeartBeatTable's,
        # whose Frequency/Retention/Purge Fields are also plain textboxes
        # but come later and default to non-empty numeric values).
        self.page.get_by_role("textbox").first.fill(table_name)

        # "Add" (exact) vs. HeartBeatTable's "Add HeartbeatTable" button,
        # both present simultaneously since HeartBeatTable also defaults
        # to its own Add tab - plain click_by_role's substring match
        # hits both.
        self.page.get_by_role(
            ConfigTablesLocators.ADD_CHECKPOINT_BUTTON[0],
            name=ConfigTablesLocators.ADD_CHECKPOINT_BUTTON[1],
            exact=True
        ).click()

    def verify_add_checkpoint_result(self, table_name, timeout=30000):

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_RESULT_DIALOG[0],
                name=ConfigTablesLocators.CHECKPOINT_RESULT_DIALOG[1]
            )
        ).to_be_visible(timeout=timeout)

        self.expect_visible_by_text(table_name)

        self.click_by_role("button", "OK")

        self.wait_for_dialog_to_close()

    def open_checkpoint_view_tab(self):

        self._checkpoint_toolbar().get_by_role(
            "radio",
            name=ConfigTablesLocators.CHECKPOINT_VIEW_TAB,
            exact=True
        ).click(force=True)

        # This form's Vault Domain option list loads asynchronously and
        # can take upwards of 5-10s to populate with no visible loading
        # indicator - opening the combobox before that resolves shows a
        # stale "No matches found." even for a domain that exists.
        self.page.wait_for_timeout(10000)

    def view_checkpoint_table(self, domain, alias, table_name):

        # These three fields are unlabeled/shared-label "oj-c-*"
        # comboboxes - positional lookup is the only reliable way to
        # address them (Vault Domain has no accessible name at all,
        # and re-querying after each selection avoids stale handles
        # since selecting the alias can shift what "third combobox"
        # refers to).
        domain_combo = self.page.get_by_role("combobox").nth(0)
        self.select_lazy_combobox(domain_combo, domain)

        alias_combo = self.page.get_by_role(
            ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
            name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
        ).first
        self.select_lazy_combobox(alias_combo, alias)

        table_combo = self.page.get_by_role("combobox").nth(2)
        self.select_lazy_combobox(
            table_combo,
            table_name,
            settle_timeout=30000
        )

        self.click_by_role(*ConfigTablesLocators.VIEW_BUTTON)

    def verify_checkpoint_table_result(self, table_name, timeout=20000):

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_RESULT_DIALOG[0],
                name=ConfigTablesLocators.CHECKPOINT_RESULT_DIALOG[1]
            )
        ).to_be_visible(timeout=timeout)

        self.expect_visible_by_text(
            f"Checkpoint table {table_name} has been created"
        )

        self.click_by_role("button", "OK")

        self.wait_for_dialog_to_close()

    # ---------------------------------------------------------
    # CheckpointTable - Upgrade / Delete (structure only, no submit -
    # both act on the real checkpoint table backing the live RLP2
    # replicat, so these deliberately stop short of clicking
    # Upgrade/Delete for real).
    # ---------------------------------------------------------

    def open_checkpoint_upgrade_tab(self):

        # The Config Tables screen's content can lag several seconds
        # behind the outer Setup tab switch with no visible loading
        # indicator (same class of race as Setup's other tabs) - wait
        # for the CheckpointTable heading itself before touching its
        # toolbar, or the toolbar locator can time out entirely while
        # the page is still showing the previous tab's content.
        self.expect_visible_by_role(
            *ConfigTablesLocators.CHECKPOINT_TABLE_HEADING,
            timeout=30000
        )

        self._checkpoint_toolbar().get_by_role(
            "radio",
            name=ConfigTablesLocators.CHECKPOINT_UPGRADE_TAB,
            exact=True
        ).click(force=True)

        # Same async-populate quirk as the View sub-tab (no visible
        # loading indicator) - see open_checkpoint_view_tab.
        self.page.wait_for_timeout(10000)

    def open_checkpoint_delete_tab(self):

        self.expect_visible_by_role(
            *ConfigTablesLocators.CHECKPOINT_TABLE_HEADING,
            timeout=30000
        )

        self._checkpoint_toolbar().get_by_role(
            "radio",
            name=ConfigTablesLocators.CHECKPOINT_DELETE_TAB,
            exact=True
        ).click(force=True)

        self.page.wait_for_timeout(10000)

    def verify_checkpoint_upgrade_structure(self):

        # "Choose Vault Alias" renders twice on this page (Checkpoint
        # and HeartBeat sections each have their own, both always in
        # the DOM regardless of active sub-tab) - CheckpointTable's is
        # first, same disambiguation as view_checkpoint_table() above.
        self.expect_visible_by_text(
            ConfigTablesLocators.CHECKPOINT_TABLE_NAME_TEXT,
            timeout=15000
        )

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
                name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
            ).first
        ).to_be_visible()

        self.expect_visible_by_role(
            *ConfigTablesLocators.UPGRADE_BUTTON
        )

    def verify_checkpoint_delete_structure(self):

        self.expect_visible_by_text(
            ConfigTablesLocators.CHECKPOINT_TABLE_NAME_TEXT,
            timeout=15000
        )

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
                name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
            ).first
        ).to_be_visible()

        self.expect_visible_by_role(
            *ConfigTablesLocators.CHECKPOINT_DELETE_BUTTON
        )

    # ---------------------------------------------------------
    # HeartBeatTable - Add / Edit / Delete (structure only, no submit -
    # Add would create a real HeartBeat table/process, Delete would
    # remove one; no confirmed-safe values to submit for real yet).
    # ---------------------------------------------------------

    def _heartbeat_toolbar(self):
        # Scoped to the HeartBeatTable section specifically - its
        # "Add"/"Edit"/"Delete" toolbar shares radio names with
        # CheckpointTable's own "Add"/"Delete" tabs just above it.
        return self.page.locator(
            "xpath=//h6[normalize-space(text())='HeartBeatTable']"
            "/parent::div/following-sibling::oj-c-buttonset-single[1]"
        )

    def open_heartbeat_edit_tab(self):

        # Same content-lag race as the Checkpoint tabs above - wait for
        # the HeartBeatTable heading before touching its toolbar.
        self.expect_visible_by_role(
            *ConfigTablesLocators.HEARTBEAT_TABLE_HEADING,
            timeout=30000
        )

        self._heartbeat_toolbar().get_by_role(
            "radio",
            name=ConfigTablesLocators.HEARTBEAT_EDIT_TAB,
            exact=True
        ).click(force=True)

        self.page.wait_for_timeout(10000)

    def open_heartbeat_delete_tab(self):

        self.expect_visible_by_role(
            *ConfigTablesLocators.HEARTBEAT_TABLE_HEADING,
            timeout=30000
        )

        self._heartbeat_toolbar().get_by_role(
            "radio",
            name=ConfigTablesLocators.HEARTBEAT_DELETE_TAB,
            exact=True
        ).click(force=True)

        self.page.wait_for_timeout(10000)

    def verify_heartbeat_edit_structure(self):

        # Same "Choose Vault Alias" duplicate as Checkpoint's - only
        # HeartBeat's copy is relevant here, and it's always the
        # second/last one in DOM order (HeartBeatTable section sits
        # below CheckpointTable's on this page).
        self.expect_visible_by_text(
            ConfigTablesLocators.FREQUENCY_TEXT,
            timeout=15000
        )

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
                name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
            ).last
        ).to_be_visible()

        self.expect_visible_by_text(
            ConfigTablesLocators.RETENTION_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.PURGE_FREQUENCY_TEXT
        )

        self.expect_visible_by_role(
            *ConfigTablesLocators.SAVE_HEARTBEAT_BUTTON
        )

    def verify_heartbeat_delete_structure(self):

        expect(
            self.page.get_by_role(
                ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[0],
                name=ConfigTablesLocators.CHECKPOINT_VAULT_ALIAS_COMBOBOX[1]
            ).last
        ).to_be_visible(timeout=15000)

        self.expect_visible_by_role(
            *ConfigTablesLocators.DELETE_HEARTBEAT_BUTTON
        )

    def verify_screen_structure(self):

        # Content lags the tab selection by several seconds with no
        # visible loading indicator, so the first check needs a generous
        # timeout.
        self.expect_visible_by_role(
            *ConfigTablesLocators.CHECKPOINT_TABLE_HEADING,
            timeout=15000
        )

        self.expect_visible_by_role(
            *ConfigTablesLocators.HEARTBEAT_TABLE_HEADING
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.CHECKPOINT_TABLENAME_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.DIRECTION_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.PARTITIONED_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.FREQUENCY_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.RETENTION_TEXT
        )

        self.expect_visible_by_text(
            ConfigTablesLocators.PURGE_FREQUENCY_TEXT
        )

        self.expect_visible_by_role(
            *ConfigTablesLocators.ADD_HEARTBEAT_TABLE_BUTTON
        )
