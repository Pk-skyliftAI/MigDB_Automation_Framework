# Architecture

## Design Pattern: Page Object Model (POM)

Every screen in the application has a matching **page object** class in
[`pages/`](../pages/) and a matching **locators** class in
[`locators/`](../locators/). Test files import fixtures (not page classes
directly) and call methods on them — no raw Playwright locators appear in
`tests/`.

```
locators/vault_locators.py   ->  role/name tuples and text constants
        │
        ▼
pages/vault_page.py          ->  actions (add_database_alias, etc.)
        │                         and assertions (verify_screen_structure)
        ▼
conftest.py fixture "vault"  ->  VaultPage(logged_in_page)
        │
        ▼
tests/vault/test_*.py        ->  def test_x(navigation, setup, vault): ...
```

Every page object inherits from [`pages/base_page.py`](../pages/base_page.py),
which centralizes the recurring Oracle JET UI quirks this app's frontend has
(documented inline where discovered):

- `click_tree_item` / `expand_tree_item` / `click_by_id` — the left nav is a
  JET tree whose items sometimes need substring matching, sometimes an
  expand-before-click, and one item (`Monitor`) needs an id-based click
  because its accessible name collides with three other tree items.
- `select_lazy_combobox` — many comboboxes populate their option list
  asynchronously with no visible loading indicator; this waits for the real
  option text instead of a fixed delay.
- `select_stable_tab` — some toolbar tabs silently revert to their default
  selection while a background fetch is still in flight; this re-clicks and
  re-checks until the selection holds.
- `wait_for_dialog_to_close`, `right_click_diagram_node`,
  `select_cdb_combobox` — dialog and Designer-diagram-specific helpers.

## Folder Structure

```
conftest.py             Fixtures (browser/context/page, one fixture per
                         page object) and the screenshot-on-failure hook
pytest.ini               Test discovery, default CLI options, markers

config/
  config.yaml            All environment/test data: URLs, credentials,
                          per-screen vault aliases, schema/PDB names, etc.
  settings.py             Loads config.yaml once into a module-level
                          `config` object other modules import

locators/                One *_locators.py per screen — role/name tuples
                          and text constants only, no behavior

pages/
  base_page.py            Shared helpers every page object inherits
  <screen>_page.py         One class per screen/module (login, dashboard,
                            navigation, vault, setup, supplemental_logging,
                            parameter_file, config_tables, connections,
                            purge_cdc_files, assessment, designer,
                            initial_load, manage, monitor, dataflow,
                            conflict_resolution, analyze_objects,
                            analyze_trails, troubleshoot, logfile)

tests/                   One subfolder per screen/module, mirroring pages/
  <module>/test_*.py

utils/
  browser_manager.py      Launches/closes the Playwright browser per
                           config.yaml + --browser CLI override
  logger.py                Central logger, writes to reports/logs/
  screenshot_manager.py    Failure-screenshot capture (used by conftest.py)
  test_data.py              Timestamp-based unique test data generators
  wait_utils.py             Standalone wait helpers (wraps config's
                             browser.timeout as a default)
  assertions.py             Standalone assertion helpers with logging

key/                     SSH private key(s) used ad hoc for direct
                          infra access (not read by the test suite itself)

reports/                 Generated output (git-ignored) — see README.md
```

## How Fixtures Compose

`conftest.py` builds a fixture chain per test, all `scope="function"`
(fresh browser per test):

```
browser  ->  context  ->  page  ->  logged_in_page  ->  <page-object fixture>
```

- `browser` launches Playwright via `BrowserManager`, honoring `--browser`
  or `config.browser["engine"]`.
- `context` creates a `BrowserContext`, optionally recording video/trace per
  `config.reporting`.
- `page` creates the `Page`, exposes it on `request.node.page` so the
  failure-screenshot hook can reach it, and finalizes the video recording
  (Playwright only names the file once the page closes).
- `logged_in_page` drives `LoginPage.open_login_page()` /
  `LoginPage.login()` once and hands back the same `page`.
- Every other fixture (`navigation`, `vault`, `setup`, `designer`, `manage`,
  `monitor`, `dataflow`, `analyze_objects`, …) just wraps `logged_in_page`
  in its matching page-object class — see the full list in `conftest.py`.

A typical test only ever asks for the fixtures it needs by name:

```python
def test_vault_screen_structure(navigation, setup, vault):
    navigation.open_navigation_menu()
    setup.open_setup()
    vault.verify_secure_vault_page()
```

## Configuration-Driven, Not Hard-Coded

Nothing environment-specific is hard-coded in a test or page object.
`config/config.yaml` holds the base URL, login credentials, and every
screen's test data (vault domain/aliases, source/target PDB names,
extract/pump/replicat names, checkpoint table names, schema names, etc.),
grouped by section (`secure_vault`, `supplemental_logging`, `designer`,
`config_tables`, `initial_load`, …) and loaded once into the `config`
object in `config/settings.py`. Tests import `from config.settings import
config` and read the section they need. Switching environments means
editing `config.yaml`, not code.

## Test Tiers

Two tiers of coverage exist across `tests/`, matching what's safe to
exercise repeatedly against a real, shared, live environment:

1. **Screen-structure tests** — navigate to a screen and assert its key
   controls (headings, tabs, buttons, comboboxes) render. Used for screens
   where a full data-changing flow isn't safe to run on every regression
   pass (e.g. `tests/connections/`, `tests/dataflow/`,
   `tests/troubleshoot/`).
2. **Real-flow tests** — actually submit forms, create real vault aliases,
   checkpoint tables, GoldenGate extracts/replicats, etc. Several of these
   are written as **idempotent build-once** flows: they check whether the
   target object already exists (`is_replicat_listed`, `is_load_listed`,
   `is_extract_listed`) before creating it, since the objects they create
   are real, persistent, and have no confirmed delete flow (e.g.
   `tests/designer/test_classic_replicat_apply.py`,
   `tests/initial_load/test_homogeneous_initial_load.py`).
