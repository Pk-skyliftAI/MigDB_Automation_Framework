from playwright.sync_api import expect

from config.settings import config
from pages.base_page import BasePage


class SetupPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_setup(self):
        self.click_tree_item("Setup")
        self.wait()

        # Setup's first load kicks off a silent background vault-tree
        # fetch (no visible loading dialog) that resets the toolbar back
        # to the default "Secret Vault" tab if another tab is selected
        # before it completes. The Secure Vault Domain tree populating
        # with its domain treeitem is the reliable signal that it's done.
        expect(
            self.page.get_by_role(
                "treeitem",
                name=config.secure_vault["domain"],
                exact=False
            )
        ).to_be_visible(timeout=20000)

    def open_secure_vault(self):
        self.select_stable_tab("Secret Vault")
        self.wait()

    def open_supplemental_logging(self):
        self.select_stable_tab("Supplemental Logging")
        self.wait()

    def open_parameter_file(self):
        self.select_stable_tab("Parameter File")
        self.wait()

    def open_config_tables(self):
        self.select_stable_tab("Config Tables")
        self.wait()

    def open_connections(self):
        self.select_stable_tab("Connections")
        self.wait()

    def open_purge_cdc_files(self):
        self.select_stable_tab("Purge CDC Files")
        self.wait()
