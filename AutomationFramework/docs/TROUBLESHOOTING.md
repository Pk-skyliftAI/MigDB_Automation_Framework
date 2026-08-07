# Troubleshooting

Issues that actually come up with this framework, drawn from the codebase
(config, fixtures, and comments left where they were first diagnosed) —
not a generic Playwright/pytest checklist.

## Setup

### `playwright._impl._errors.Error: Executable doesn't exist`

`pip install -r requirements.txt` installs the `playwright` Python package
but **not** the browser binaries. Run:

```bash
playwright install chromium firefox webkit
```

### Tests hang or time out immediately connecting to the app

`config/config.yaml`'s `urls.base_url` points at a private on-prem address
(`192.168.77.130`). If you're running from a machine that isn't on that
network (including any GitHub-hosted CI runner), every test will fail to
even reach the login page. Confirm you can `curl` the `base_url` before
debugging anything else. See `docs/CI_CD.md` for why CI must use a
self-hosted runner.

### `KeyError` from `config/settings.py` on import

`Config.__init__` unconditionally reads a fixed set of top-level keys out
of `config.yaml` (`application`, `environment`, `browser`, `urls`,
`credentials`, `secure_vault`, `execution`, `reporting`,
`supplemental_logging`, `designer`, `config_tables`, `initial_load`). If
`config.yaml` is edited and one of those sections is removed or renamed,
every test fails at collection time with a `KeyError`, not a normal test
failure. Check `config.yaml` against that list first.

## Running Tests

### A test that used to pass now times out on a specific vault alias / PDB name / table name

This app's environment has drifted mid-project more than once — vault
alias names, source/target PDB names, and checkpoint table names have all
changed on the live application without any corresponding code change.
`config.yaml` has inline comments flagging every value that's been wrong
before (e.g. `designer.target_pdb_name`, `config_tables.checkpoint_alias`,
`initial_load.source_db_name`) — check those comments and re-verify the
value live in the app (Secure Vault screen, or a direct DB query) before
assuming it's a locator/code bug.

### Intermittent `strict mode violation: ... resolved to N elements`

Several screens render two elements with an identical accessible role+name
(e.g. Analyze Objects' two `application "All Table"` tables, Heterogeneous
Initial Load's two `combobox "Required Secret Domain"` fields, or the nav
tree's `Monitor`/`Hetro Initial Load Monitor`/`Homo Initial Load
Monitor`/Compare Pad `Monitor` all matching a plain `"Monitor"` substring
search). This is not random flakiness — check whether the locator needs
`.first`, an exact `id` (see `click_by_id` in `base_page.py`), or a
`to_have_count()` assertion instead of the shared single-match
`expect_visible_by_role` helper.

### `AssertionError: Locator expected to be visible` on a combobox/dropdown, only sometimes

Several Oracle JET comboboxes across this app (Vault Domain, Vault Alias,
Schema Name, Checkpoint Table, …) populate their option list
**asynchronously with no visible loading indicator**. A fixed `wait_for_timeout`
is unreliable; `base_page.py`'s `select_lazy_combobox` waits for the real
option text to appear instead, with a default 15s `settle_timeout` — some
call sites override this higher (e.g. 30000ms) where the lag is worse.
If this still fails intermittently under load, that's the known,
documented pattern behind the `@pytest.mark.flaky(reruns=2,
reruns_delay=10)` marker already used on `test_pre_migration_assessment.py`,
`test_manager_actions_menu.py`, `test_add_checkpoint_table.py`, and the
Config Tables upgrade/delete-structure tests — add it rather than chasing
a longer fixed wait.

### The left navigation drawer suddenly can't find any tree items

`NavigationPage.open_navigation_menu()`'s hamburger button **toggles**
the drawer rather than only opening it, and the drawer stays open across
in-app navigation. Calling it a second time when the drawer is already
open closes it instead, and every subsequent `treeitem` lookup then times
out. The fixture already guards this (`if not tree.is_visible(): click`)
— if you're calling nav-open logic directly instead of through the
existing page-object methods, check for the same collapse-on-second-click
behavior (the `Assessment` and `Compare Pad` parent tree items have the
identical toggle behavior for their own sub-items).

### A "Create Job" / "Add Extract Pump" / similar submit hangs or shows a generic error

Check the test/page-object comments first — several of these are
**confirmed real backend bugs**, not test issues, found via direct network
response capture:

- Homogeneous Initial Load's `create_job()` (`pages/initial_load_page.py`)
  raises a clear `AssertionError` if the app's "There is a technical
  issue" dialog appears — a real `POST /api/v2/datapump/export` 422
  because the app sends `impParallel` as a number instead of a string.
- Designer's Extract Pump submission (`add_extract_pump` in
  `pages/designer_page.py`) can hang on a "Creating Network Pump" progress
  dialog indefinitely — a real `405` on `POST
  .../undefined/api/v2/pump/add` (a literal `undefined` in the URL).

If a submit-related test fails with one of these signatures, it's a
product bug to report, not something to fix from the test side.

### Idempotent tests report "PASSED" without doing anything

Several tests are written as **build-once, verify-forever**: they create a
real, persistent GoldenGate object (extract, replicat, load job) only if
it doesn't already exist, then just verify it's still there on every later
run (`is_replicat_listed`, `is_load_listed`, `is_extract_listed` in the
relevant page object). If you need the creation path to actually re-run
(e.g. to test it after a code change), delete or rename the target object
in the live application first — there's no flag to force it.

## Reports & Screenshots

### No screenshot was captured for a failed test

The failure-screenshot hook (`conftest.py`'s `pytest_runtest_makereport`)
only fires for `report.failed` on the `call` phase, and only if
`item.page` was set — which happens in the `page` fixture. A test that
fails during fixture *setup* (e.g. login itself fails) won't have a page
attached yet and won't get a screenshot; check the console/log output
(`reports/logs/`) instead.

### Video file is missing or has a random name

Video is only enabled if `config.yaml`'s `reporting.video` is `true`.
Playwright doesn't finalize/name the video file until the page closes —
the `page` fixture grabs the video handle before closing and renames it to
match the test name afterward. If a test crashes hard enough to skip
teardown, the video may be left under Playwright's own temp naming instead
of `reports/videos/<test_name>.webm`.

## Configuration Notes Worth Knowing

- `config.yaml`'s `execution` section (`retries`, `workers`) is loaded into
  `config.execution` by `settings.py` but **not currently read anywhere
  else in the codebase** — `pytest-xdist` (parallelization) is installed
  but not wired into `pytest.ini`'s `addopts`, so `pytest -n <workers>`
  must be passed manually if you want parallel execution.
- Login credentials fall back to plaintext in the committed
  `config/config.yaml` (`credentials.username`/`password`), but
  `config/settings.py` overrides them with the `MIGDB_USERNAME` /
  `MIGDB_PASSWORD` environment variables when set — CI injects these from
  GitHub Secrets (see `docs/CI_CD.md`). Locally, if you don't export those
  two variables, you're using whatever is in `config.yaml`, unchanged from
  before. `.env` exists at the repo root but is empty and unused — the
  framework doesn't read it (no `python-dotenv` call anywhere), so setting
  values there does nothing; export real shell environment variables
  instead. Every other screen's test data (vault aliases, schema/PDB
  names, etc.) has no secret-backed override and still lives only in
  `config.yaml` — treat that file as sensitive despite it being tracked in
  git.
