import re

from playwright.sync_api import expect


class BasePage:

    def __init__(self, page):
        self.page = page

    def open(self, url):
        self.page.goto(url)

    def wait(self):
        self.page.wait_for_load_state("networkidle")

    def click_by_role(self, role, name, force=False):
        self.page.get_by_role(role, name=name).click(force=force)

    def expand_tree_item(self, name, exact=False):
        """Expand a collapsed tree node via keyboard (ArrowRight), for
        Oracle JET-style trees where clicking the row selects rather than
        expands it."""

        item = self.page.get_by_role(
            "treeitem",
            name=name,
            exact=exact
        )
        item.click()
        item.press("ArrowRight")

    def fill_by_role(self, role, name, value):
        self.page.get_by_role(role, name=name).fill(value)

    def expect_visible_by_role(self, role, name, timeout=None):
        expect(
            self.page.get_by_role(role, name=name)
        ).to_be_visible(timeout=timeout)

    def expect_visible_by_text(self, text, timeout=None):
        expect(
            self.page.get_by_text(text, exact=False).first
        ).to_be_visible(timeout=timeout)

    def expect_visible_by_css(self, selector, timeout=None):
        expect(
            self.page.locator(selector)
        ).to_be_visible(timeout=timeout)

    def click_tree_item(self, name, exact=False):
        self.page.get_by_role(
            "treeitem",
            name=name,
            exact=exact
        ).click()

    def expect_tree_item_visible(self, name, exact=False):
        expect(
            self.page.get_by_role(
                "treeitem",
                name=name,
                exact=exact
            )
        ).to_be_visible()

    def click_by_id(self, element_id):
        self.page.locator(f"#{element_id}[role='treeitem']").click()

    def expect_visible_by_id(self, element_id):
        expect(
            self.page.locator(f"#{element_id}[role='treeitem']")
        ).to_be_visible()

    def select_stable_tab(self, name, retries=5, stability_ms=3000, timeout=8000):
        """Click an Oracle JET buttonset tab and confirm it stays selected.

        Force-clicking the tab's underlying role="radio" input directly
        is unreliable for these toolbar tabs - clicking the visible
        label.oj-button-label text is what the widget actually listens
        to. This app also silently reverts toolbar tab selections back
        to their default for a variable window after certain background
        loads (e.g. Setup's initial vault-tree fetch, or a post-add/
        delete vault refresh) with no visible loading indicator to key
        off, so we re-click and re-check after a short stability window
        to reliably land - and stay - on the intended tab.
        """

        label = self.page.locator(
            "label.oj-button-label",
            has_text=name
        )

        radio = self.page.get_by_role(
            "radio",
            name=name,
            exact=True
        )

        for _ in range(retries):
            label.click()

            try:
                expect(radio).to_be_checked(timeout=timeout)
            except AssertionError:
                continue

            self.page.wait_for_timeout(stability_ms)

            if radio.is_checked():
                return

        raise AssertionError(
            f"'{name}' tab did not remain selected after {retries} "
            "attempts (app resets to a default tab during a background "
            "refresh)."
        )

    def wait_for_dialog_to_close(self, dialog_text=None, timeout=20000):
        """Wait for a transient dialog (e.g. "Refreshing Secure Vault",
        "Deleting User", a Yes/No confirm) to disappear.

        These dialogs are permanent hidden DOM templates - duplicate
        elements share the same role="dialog" accessible name whether
        open or not - so waiting on the role locator's hidden/attached
        state returns immediately instead of waiting for the real one to
        close. Keying off the :visible CSS pseudo-class avoids that.

        A closing dialog's underlying z-order layer can also keep
        intercepting clicks for a moment after its own text disappears,
        so when no specific dialog_text is given this waits for *any*
        visible dialog to clear rather than just one.
        """
        locator = self.page.locator("[role='dialog']:visible")

        if dialog_text:
            locator = locator.filter(has_text=dialog_text)

        expect(locator).to_have_count(0, timeout=timeout)

    def select_cdb_combobox(self, cdb_name):
        """Select a value in the "Choose CDB(in CDB Mode)" oj-select-single
        combobox shared by Supplemental Logging and Assessment (same DOM
        id "dbdet" on both screens).

        Populated with Secure Vault database aliases, not domains -
        options render as role="row" inside a grid, not role="option".
        Callers must wait for their own screen-specific settle signal
        after calling this (its background fetch/refresh differs per
        screen).
        """

        combo = self.page.get_by_role(
            "combobox",
            name="Choose CDB(in CDB Mode)"
        ).first

        combo.click(force=True)

        expect(combo).to_have_attribute("aria-expanded", "true")

        combo.fill(cdb_name)

        self.page.locator(
            "#lovDropdown_dbdet [role='row']"
        ).filter(
            has_text=re.compile(rf"^{re.escape(cdb_name)}$")
        ).first.click()