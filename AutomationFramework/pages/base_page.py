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

    def select_stable_tab_scoped(
        self, scope, name, retries=5, stability_ms=3000, timeout=8000
    ):
        """Same retry-until-it-holds pattern as select_stable_tab, but
        scoped to a container locator instead of the whole page.

        Needed wherever a screen renders more than one buttonset with
        overlapping tab names (e.g. Config Tables' CheckpointTable and
        HeartBeatTable sections both have "Add"/"Delete" radios) -
        select_stable_tab's page-wide get_by_role(name=...) would hit a
        strict-mode violation or silently grab the wrong widget's tab in
        that case. Confirmed live (2026-08-10) that CheckpointTable's
        Upgrade/Delete tabs and HeartBeatTable's Edit/Delete tabs are
        subject to the exact same reverts-to-default-tab race that
        select_stable_tab was written for - a single click(force=True)
        landed on "Upgrade"/"Edit" only to have the toolbar silently
        snap back to "Add" before verify_*_structure() ran.

        Unlike select_stable_tab's toolbar (legacy JET, `label.oj-button-
        label`), this app's Config Tables sub-tab toolbars are the newer
        `oj-c-buttonset-single` Core Pack component - confirmed live via
        DOM dump that its class names are build-hashed
        (`BaseButtonStyles_styles_inputLabel__<hash>`) and NOT
        `oj-button-label`, so this targets a plain `label` element by
        visible text instead. The underlying `input[type=radio]` sits in
        a visually-hidden wrapper span (tabindex="-1"), so the label -
        not the radio - is the real click target here.
        """

        label = scope.locator("label", has_text=name)

        radio = scope.get_by_role("radio", name=name, exact=True)

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

    def select_stable_combobox(
        self,
        combo,
        option_text,
        retries=6,
        open_timeout=3000,
        settle_timeout=15000
    ):
        """Click an Oracle JET searchselect-style combobox and select an
        option, retrying the click itself (not just waiting longer) if
        aria-expanded doesn't flip to true.

        Confirmed live (2026-08-10, post app-binary update) that this
        family of combobox (Choose Deployment Name, Choose CDB(in CDB
        Mode), Choose PDB Name, Choose Schema Name, Choose Target
        Deployment, Directory Name, etc.) intermittently drops a single
        force-click's open event - NOT a fixed rendering lag: the same
        field opened reliably at 5s in one run and still hadn't opened
        by 15s in another run with no code difference. A longer fixed
        wait is therefore not a reliable fix on its own. Same root cause
        class as the toolbar-tab reset handled by select_stable_tab -
        this is the equivalent fix generalized to any combobox using
        this widget family, not just tabs.
        """
        for attempt in range(retries):
            combo.click(force=True)
            try:
                expect(combo).to_have_attribute(
                    "aria-expanded", "true", timeout=open_timeout
                )
                break
            except AssertionError:
                if attempt == retries - 1:
                    raise
                continue

        option = self.page.locator(
            "[role='option']:visible, [role='row']:visible"
        ).filter(has_text=option_text).first

        expect(option).to_be_visible(timeout=settle_timeout)
        option.click()

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

    def right_click_diagram_node(self, node_name):
        """Right-click a node in the Designer capture diagram (an Oracle
        JET "Data Visualization: Diagram" canvas widget).

        The diagram re-lays-out/repositions every node after each step
        is configured (confirmed live across multiple screenshots), so a
        fixed pixel coordinate is not reliable. Nodes DO have a stable
        accessible name via role="img" regardless of position - use
        that instead of coordinates.
        """

        self.page.get_by_role(
            "img",
            name=node_name
        ).click(button="right")

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

        # Retry the click itself, not just the wait - confirmed live
        # 2026-08-10 that a single force-click's open event drops
        # intermittently on this widget family post app-binary-update
        # (see select_stable_combobox's docstring for the full
        # evidence). This field's own selection flow differs enough
        # (fill + regex-exact row match against a specific dropdown
        # container) that it isn't routed through select_stable_combobox
        # itself, but needs the same retry-the-open-click fix.
        for attempt in range(6):
            combo.click(force=True)
            try:
                expect(combo).to_have_attribute(
                    "aria-expanded", "true", timeout=3000
                )
                break
            except AssertionError:
                if attempt == 5:
                    raise
                continue

        combo.fill(cdb_name)

        self.page.locator(
            "#lovDropdown_dbdet [role='row']"
        ).filter(
            has_text=re.compile(rf"^{re.escape(cdb_name)}$")
        ).first.click()

    def select_lazy_combobox(
        self, combo, option_text, settle_timeout=15000, retries=4
    ):
        """Select an option from an Oracle JET "oj-c-*" select/combobox
        widget (a newer component family than the oj-select-single/
        oj-searchselect widgets used elsewhere in this app - e.g. Setup's
        Config Tables CheckpointTable/HeartBeatTable forms). Distinctive
        by its popup rendering as plain text inside a `[id$='-dropdown']`
        container, not role='option'/'row' elements.

        Its option data loads asynchronously with no visible loading
        indicator and can take 5-10s+ to actually populate (confirmed
        live - a fixed short wait reliably shows a stale "No matches
        found." even for a value that exists) - wait for the real option
        text itself rather than a fixed delay.

        Retries the click itself, not just the wait: confirmed live
        2026-08-11 that Config Tables' CheckpointTable "Table Name"
        combobox can silently fail to open on a single force-click even
        though the real data exists and is correct (verified directly
        against the database - the app UI showed it fine on a manual
        pass seconds later). Same root-cause class as the searchselect
        family's dropped-click bug that select_stable_combobox already
        works around - a longer settle_timeout alone doesn't help if
        the dropdown never opened in the first place.
        """

        dropdown = self.page.locator("[id$='-dropdown']").last
        option = dropdown.get_by_text(option_text, exact=True)

        # Only the final attempt uses the full settle_timeout budget
        # (which some call sites raise as high as 30000ms) - earlier
        # attempts use a shorter timeout so a dropped-click retry loop
        # can't balloon into minutes.
        retry_timeout = min(settle_timeout, 8000)

        for attempt in range(retries):
            combo.click(force=True)
            is_last = attempt == retries - 1
            try:
                expect(option).to_be_visible(
                    timeout=settle_timeout if is_last else retry_timeout
                )
                break
            except AssertionError:
                if is_last:
                    raise
                self.page.wait_for_timeout(500)

        option.click()