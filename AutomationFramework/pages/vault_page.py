from playwright.sync_api import expect

from pages.base_page import BasePage
from locators.vault_locators import VaultLocators


class VaultPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ---------------------------------------------------------
    # Screen Verification
    # ---------------------------------------------------------

    def verify_secure_vault_page(self):

        headings = [
            VaultLocators.VIEW_SECURE_VAULT_HEADING,
            VaultLocators.ENCRYPTION_KEY_HEADING,
            VaultLocators.MANAGE_SECURE_VAULT_HEADING,
        ]

        for role, name in headings:
            self.expect_visible_by_role(role, name)

    def verify_action_buttons(self):

        buttons = [
            VaultLocators.ADD_USER_TAB,
            VaultLocators.EDIT_USER_TAB,
            VaultLocators.DELETE_USER_TAB,
            VaultLocators.BULK_ADD_TAB,
        ]

        for role, name in buttons:
            self.expect_visible_by_role(role, name)

    def verify_encryption_key(self):

        self.expect_visible_by_text(
            VaultLocators.MASTER_KEY
        )

    # ---------------------------------------------------------
    # Existing Alias Verification
    # ---------------------------------------------------------

    def expand_secure_vault_domain(self, domain):

        self.expand_tree_item(domain, exact=False)
        self.wait()

    def verify_existing_aliases(self, aliases, domain):

        self.expand_secure_vault_domain(domain)

        for alias in aliases:
            self.expect_visible_by_text(alias)

    # ---------------------------------------------------------
    # Add Alias
    # ---------------------------------------------------------

    def open_add_user_tab(self):

        self.select_stable_tab(VaultLocators.ADD_USER_TAB[1])

    def select_domain(self, domain):

        combo = self.page.get_by_role(
            VaultLocators.DOMAIN_COMBOBOX[0],
            name=VaultLocators.DOMAIN_COMBOBOX[1]
        )

        combo.click()
        combo.fill(domain)

        self.page.get_by_role(
            "option",
            name=domain
        ).click()

    def add_database_alias(
        self,
        alias_name,
        username,
        password,
        domain=None
    ):

        self.click_by_role(
            *VaultLocators.EXISTING_DOMAIN_RADIO,
            force=True
        )

        if domain:
            self.select_domain(domain)

        self.fill_by_role(
            *VaultLocators.ALIAS_TEXTBOX,
            alias_name
        )

        self.fill_by_role(
            *VaultLocators.USERNAME_TEXTBOX,
            username
        )

        self.fill_by_role(
            *VaultLocators.PASSWORD_TEXTBOX,
            password
        )

        self.click_by_role(
            *VaultLocators.ADD_USER_BUTTON
        )

    # ---------------------------------------------------------
    # Success Dialog
    # ---------------------------------------------------------

    def verify_add_user_success(self, alias_name):

        expect(
            self.page.get_by_role(
                "heading",
                name="Add User"
            )
        ).to_be_visible()

        expect(
            self.page.get_by_text(
                f"User alias '{alias_name}' added successfully to MigDB SecureVault."
            )
        ).to_be_visible()

    def close_success_dialog(self):

        self.page.get_by_role(
            "button",
            name="OK"
        ).click()

        self.page.wait_for_load_state("networkidle")

        # Closing this dialog kicks off a background "Refreshing Secure
        # Vault" reload (~8s) that resets the toolbar to the Add User tab
        # once it completes - any tab switch attempted before it settles
        # gets silently reverted.
        self.wait_for_dialog_to_close(
            VaultLocators.REFRESHING_VAULT_DIALOG[1]
        )

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------

    def refresh_secure_vault_tree(self, domain):

        self.expand_secure_vault_domain(domain)

    def verify_alias_listed(self, alias):

        self.expect_visible_by_text(alias)

    # ---------------------------------------------------------
    # Delete Alias
    # ---------------------------------------------------------

    def open_delete_user_tab(self):

        self.select_stable_tab(VaultLocators.DELETE_USER_TAB[1])

    def select_alias_to_delete(self, alias_name):

        combo = self.page.get_by_role(
            VaultLocators.DELETE_ALIAS_COMBOBOX[0],
            name=VaultLocators.DELETE_ALIAS_COMBOBOX[1]
        )

        combo.click(force=True)
        combo.fill(alias_name)

        self.page.get_by_role(
            "option",
            name=alias_name,
            exact=True
        ).click()

    def select_username_to_delete(self, username):

        combo = self.page.get_by_role(
            VaultLocators.DELETE_USERNAME_COMBOBOX[0],
            name=VaultLocators.DELETE_USERNAME_COMBOBOX[1]
        )

        combo.click(force=True)
        combo.fill(username)

        self.page.get_by_role(
            "option",
            name=username,
            exact=True
        ).click()

    def delete_database_alias(
        self,
        alias_name,
        username,
        domain=None
    ):

        self.open_delete_user_tab()

        if domain:
            self.select_domain(domain)

        self.select_alias_to_delete(alias_name)

        self.select_username_to_delete(username)

        self.click_by_role(
            *VaultLocators.DELETE_USER_BUTTON,
            force=True
        )

    def confirm_delete_alias(self):

        expect(
            self.page.get_by_role(
                VaultLocators.DELETE_CONFIRM_DIALOG[0],
                name=VaultLocators.DELETE_CONFIRM_DIALOG[1]
            )
        ).to_be_visible()

        # Force-clicking this button (like the Setup toolbar tabs) does
        # not register reliably - a plain click is what actually works.
        self.click_by_role(*VaultLocators.YES_BUTTON)

        # A "Deleting User" progress dialog appears, followed by a
        # success/error dialog (same OK-dialog pattern as Add User) once
        # the delete completes.
        expect(
            self.page.get_by_role(
                VaultLocators.DELETE_SUCCESS_DIALOG[0],
                name=VaultLocators.DELETE_SUCCESS_DIALOG[1]
            )
        ).to_be_visible(timeout=20000)

        self.click_by_role(*VaultLocators.OK_BUTTON)

        # Wait for every dialog to fully clear - a closing dialog's
        # z-order layer keeps intercepting clicks briefly even after its
        # own text disappears.
        self.wait_for_dialog_to_close()

    def verify_alias_not_listed(self, alias, domain):

        self.expand_secure_vault_domain(domain)

        # Closed dialogs (e.g. the delete success message, which embeds
        # the alias name) stay in the DOM as hidden templates, so a plain
        # get_by_text match would false-positive on them - restrict to
        # elements that are actually visible.
        expect(
            self.page.get_by_text(alias, exact=False).filter(visible=True)
        ).to_have_count(0)