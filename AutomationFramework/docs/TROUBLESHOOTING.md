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

This has gone beyond just data values, too: as of a 2026-08-10 app-binary
update, **Compare Pad was removed from the application entirely**
(confirmed live — zero matches for "Compare Pad" anywhere on the page,
across the whole nav tree). All Compare Pad tests, page object, locators,
and fixtures have been removed from this framework to match. If a nav
item you're expecting suddenly isn't there, check whether the app itself
changed before assuming a locator broke.

### A screen throws a raw "Internal error: no such column: ..." dialog

This is a **SQLite** error surfacing directly from the app's own backend
(the phrasing "no such column: X" is SQLite's, not Oracle's — Oracle
would say `ORA-00904`). The app keeps its own deployment/connection
metadata in `/u01/app/skyliftai/home/conn.db` on the app host — a schema
migration that should have added a column wasn't applied alongside a
binary update (confirmed live 2026-08-10: `ONEPCONN` was missing
`dep_priv_url`, likely tied to the new "Enable Zero DownTime" feature).
Not fixable from the test side — check that table's schema
(`sqlite3 conn.db '.schema ONEPCONN'`) against what the current binary
expects, and get the missing column added.

### Intermittent `strict mode violation: ... resolved to N elements`

Several screens render two elements with an identical accessible role+name
(e.g. Analyze Objects' two `application "All Table"` tables, Heterogeneous
Initial Load's two `combobox "Required Secret Domain"` fields, or the nav
tree's `Monitor`/`Hetro Initial Load Monitor`/`Homo Initial Load Monitor`
all matching a plain `"Monitor"` substring search). This is not random
flakiness — check whether the locator needs
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

### A combobox's `aria-expanded` stays `false` even right after clicking it, intermittently

Confirmed live (2026-08-10, after an app-binary update) that a single
`force=True` click on the Oracle JET searchselect widget family (Choose
Deployment Name, Choose CDB(in CDB Mode), Choose PDB Name, Choose Schema
Name, Choose Target Deployment, Directory Name, …) can silently drop its
open event. This is **not** a rendering-lag problem — the same field
opened correctly after a 5s wait in one run and still hadn't opened after
a 15s `expect()` wait in another run with no code difference — so a
longer fixed wait is not a reliable fix on its own. Use
`BasePage.select_stable_combobox(combo, option_text)`, which retries the
click itself (not just the wait), the same approach `select_stable_tab`
already uses for toolbar tabs. `select_cdb_combobox` has the equivalent
retry built in directly. Reach for this on any *new* combobox interaction
in this widget family before writing a single click + fixed wait.

### Homogeneous Initial Load's Target Alias field can't be found by role/name

Real, confirmed app bug (2026-08-10): the field whose visible hint text
reads "Choose PDB(in CDB Mode)" (target side) has **no `aria-labelledby`
at all**, and shares its DOM id (`SRCDBDomain|input`) with the unrelated
*source*-side alias field. `get_by_role("combobox", name=...)` can never
match it as a result. `InitialLoadPage.select_target()` already works
around this (falls back to `[id='SRCDBDomain|input']).last` when the
named lookup returns zero matches) — worth reporting to the dev team
since it also breaks screen-reader accessibility for real users, not just
automation.

### "Create Job" shows an error but the test doesn't report the real reason

The same confirmed `impParallel` backend bug (see below) can surface as
**two different dialogs** depending on the exact app build: the older
generic "There is a technical issue" text, or (as of the 2026-08-10
binary) a dedicated `Error` dialog showing the raw backend message
(`body.impParallel: Input should be a valid string`).
`InitialLoadPage.create_job()` checks for both and raises a clear
assertion either way — if a future build changes this dialog's text
again, extend that check rather than letting it silently pass through
(which previously caused a *different*, confusing test to fail later with
an unrelated-looking navigation timeout, because the undetected dialog
was still open and blocking the next click).

### Config Tables' Upgrade/Edit sub-tab click silently lands back on "Add"

Confirmed live (2026-08-10): `test_checkpoint_table_upgrade_delete_structure`
and `test_heartbeat_table_edit_delete_structure` both started failing with
`waiting for get_by_text("Table Name").first` timing out - the aria
snapshot on failure showed the toolbar's `radio "Add" [checked]` instead
of the tab the test had just clicked. This is the exact same
reverts-to-default-tab race `select_stable_tab` was built for, but
CheckpointTable's and HeartBeatTable's sub-tab toolbars share radio names
("Add"/"Delete") between the two sections, so `select_stable_tab`'s
page-wide `get_by_role(name=...)` isn't safe here - use
`BasePage.select_stable_tab_scoped(scope_locator, name)` instead, passing
the section's own toolbar locator (see `_checkpoint_toolbar()` /
`_heartbeat_toolbar()` in `pages/config_tables_page.py`).

Also worth knowing if you touch this again: a live DOM dump confirmed
these particular toolbars are the newer `oj-c-buttonset-single` Core Pack
component, not the legacy widget `select_stable_tab` was originally
written against - their button labels use build-hashed classes
(`BaseButtonStyles_styles_inputLabel__<hash>`), not `label.oj-button-
label`, and the underlying `input[type=radio]` sits in a visually-hidden
wrapper (`tabindex="-1"`). `select_stable_tab_scoped` clicks a plain
`label` element matched by visible text for this reason - reusing
`label.oj-button-label` here finds zero elements and the click just
times out after 30s with no retry ever happening.

**Follow-up (2026-08-11): missed a fourth tab.** The initial fix only
scoped-fixed Upgrade/Delete/Edit and left `open_checkpoint_view_tab()`
on the old unscoped `.click(force=True)`. This surfaced as
`test_view_checkpoint_table` failing with a confusing "table name not
in dropdown" error - the real problem was the click landing back on
"Add" (whose plain textbox has no table dropdown at all), only found
by screenshotting the failure and seeing "Add" highlighted instead of
"View". If a test that touches a CheckpointTable/HeartBeatTable sub-tab
fails in a way that looks like missing data, screenshot it first and
check which tab is actually selected before assuming it's a data or
locator problem - grep this file for `open_checkpoint_` /
`open_heartbeat_` to confirm all four now use
`select_stable_tab_scoped`.

### Homogeneous Initial Load has a new "Enable Zero DownTime" switch

Confirmed live 2026-08-10 (full-GUI audit): a new `switch "Enable Zero
DownTime"` now renders above "Choose Deployment Name" on the Homogeneous
Initial Load DataSource step - not present before this session's
app-binary update. Ties to the same Zero DownTime feature whose missing
`conn.db` column (`dep_priv_url`) caused a real backend error earlier
(see above). It's off by default and doesn't affect the existing test
flow - `select_source_deployment`/`select_source` use role+name lookups,
which don't care about the new element's position - so nothing broke,
but no test exercises the switch itself yet
(`InitialLoadLocators.ENABLE_ZERO_DOWNTIME_SWITCH`). Worth a real test
once the feature is stable enough to exercise safely.

### Full-GUI audit (2026-08-10): everything else confirmed unchanged

After the Compare Pad removal and Config Tables tab-select fixes above,
a full live walkthrough of all 16 top-level nav items (aria snapshot of
every screen, cross-checked against every `locators/*.py` file) found
**no further drift** - Dashboard, Dataflow, Manage, Designer, Conflict
Resolution, Analyze Objects, Analyze Trails, Setup (all sub-tabs),
Troubleshoot, LogFile, both Initial Load screens + their Monitor
screens, Assessment, and Monitor all match their current locators and
page-object expectations exactly. The nav tree itself is unchanged (16
items, same names/order). If a future audit is needed, redo this rather
than assuming - the app has drifted mid-project more than once already
this project.

### The left navigation drawer suddenly can't find any tree items

`NavigationPage.open_navigation_menu()`'s hamburger button **toggles**
the drawer rather than only opening it, and the drawer stays open across
in-app navigation. Calling it a second time when the drawer is already
open closes it instead, and every subsequent `treeitem` lookup then times
out. The fixture already guards this (`if not tree.is_visible(): click`)
— if you're calling nav-open logic directly instead of through the
existing page-object methods, check for the same collapse-on-second-click
behavior (the `Assessment` parent tree item has the identical toggle
behavior for its own sub-items).

### A "Create Job" / "Add Extract Pump" / similar submit hangs or shows a generic error

Check the test/page-object comments first — several of these are
**confirmed real backend bugs**, not test issues, found via direct network
response capture:

- Homogeneous Initial Load's `create_job()` (`pages/initial_load_page.py`)
  raises a clear `AssertionError` if the app's "There is a technical
  issue" dialog appears — a real `POST /api/v2/datapump/export` 422
  because the app sends `impParallel` as a number instead of a string.
  **Unresolved discrepancy (2026-08-10), theory confirmed 2026-08-11**:
  the user reports this works when testing manually, but automated runs
  through `test_create_homogeneous_initial_load` kept hitting the
  identical 422 (`body.impParallel: Input should be a valid string`) -
  reconfirmed on three separate automated runs across two days. The
  "Enable Zero DownTime" switch theory (below) is now **structurally
  confirmed, not just plausible**: toggling it on live (without
  submitting - this screen creates real, undeletable infra, so this was
  checked non-destructively) visibly changes the DataSource step:
  - "Export Options" and "Import Options" both become disabled/greyed
    out (the classic DataPump export/import path this bug lives in is
    no longer part of the flow at all)
  - a new **"Checkpoint Table"** field appears next to Target Deployment
    (combobox + a "+" add button) - a GoldenGate-checkpoint-style field,
    strongly suggesting Zero DownTime mode does the initial load via
    live CDC/replication rather than a DataPump export/import job
  - "Create Job" becomes available directly on the DataSource step
    instead of after configuring Export/Import Options

  This is consistent with the user's manual test simply never routing
  through the buggy `POST /api/v2/datapump/export` call at all when
  Zero DownTime is on - not a different, "already-fixed" version of the
  same call. **Not yet built out**: this is a materially different flow
  (new required field, no confirmed value for it in `config.yaml` yet,
  and - like the plain flow - creates real infrastructure with no
  delete path) - rewiring `test_create_homogeneous_initial_load` onto it
  needs the user to confirm the Checkpoint Table value to use before
  it's exercised for real. Until then this remains the correct,
  now-confirmed explanation for the discrepancy, just not yet reflected
  in the test itself.
- Designer's Extract Pump submission (`add_extract_pump` in
  `pages/designer_page.py`) can hang on a "Creating Network Pump" progress
  dialog indefinitely — a real `405` on `POST
  .../undefined/api/v2/pump/add` (a literal `undefined` in the URL).
  **Scope clarified by the user**: a Network Pump is only involved for a
  **Remote Trail** delivery — a **Local Trail** doesn't need Extract
  Pump at all, so pipelines built with Local Trail delivery sidestep
  this bug entirely. This is still a real bug worth reporting on the
  Remote Trail path, but as of 2026-08-11 it's **not currently blocking
  any test** - see the config-staleness entry below for why
  `test_add_classic_replicat_apply`/`test_add_integrated_extract_capture`
  were hitting it at all. **Reproduced again manually 2026-08-11** (same
  405/`undefined` URL), this time also showing two Chrome console
  warnings on the same `AddExtract_layer` dialog - "Blocked aria-hidden
  on an element because its descendant retained focus" - fired for both
  the wizard's own train-step label and the underlying capture diagram.
  Non-fatal, doesn't affect automation, but worth including in the same
  bug report: the dialog/overlay marks its background `aria-hidden` true
  without moving focus out of it first, a real (if minor) a11y bug
  living in the same dialog as the 405.

### Designer tests failing on "Next"/"OK" timeouts was a stale config value, not the known creation-branch bugs

2026-08-11: both `test_add_integrated_extract_capture` and
`test_add_classic_replicat_apply` started failing on what looked like
the already-documented real backend bugs above (`GlobalProgressDialog_
layer` stuck overlay, Extract Pump 405). **It wasn't that** - `config.
yaml`'s `designer.extract_name`/`replicat_name` (`EXDEMO1`/`RLP2`) were
stale. The user confirmed `EXDEMO1` was deleted and `EXDEMO3` created
in its place - same rebuild pattern as the 2026-07-31 EXDEMO1/RLP2
rename documented in the migdb-framework-state memory, just not caught
until these tests' idempotency checks (`is_extract_listed`/
`is_replicat_listed`) correctly reported "not listed" for a name that
genuinely no longer exists, sent both tests into the real,
no-delete-flow creation branch, and *that* path is what hit the known
bugs above - the tests weren't wrong to fail, they were being sent down
a path they should never have needed to take.

Confirmed via Monitor (`EXDEMO3`/`RLP4`, both healthy - Lag 0s) before
updating config, not guessed. Also bumped `is_extract_listed`/
`is_replicat_listed`'s default timeout from 5000ms to 15000ms while
investigating (Monitor is a live-data screen, same "Fetching..." lag
class as other screens) - keep that change even though it wasn't the
actual root cause here, since a real timing false-negative on these
two checks would be worse than on a plain structure check (it sends a
test into real infrastructure creation, not just a failed assertion).

**Lesson**: this environment has now renamed its Extract/Replicat
pipeline at least twice in this project's lifetime. If a Designer test
fails on a wizard step that "shouldn't" be running (Add Source
Deployment, Add Extract Pump, etc. - anything past the idempotency
check), check Monitor for the current real names before assuming it's
one of the known creation-branch bugs recurring.

If a submit-related test fails with one of these signatures, it's a
product bug to report, not something to fix from the test side.

### Assessment job "stalls" mid-run — RESOLVED 2026-08-11, was three separate test-side issues, no real backend bug involved

The user reported Assessment always completes fine manually, while 5+
independent automated attempts across two sessions all appeared to
"stall" at 89-92%. Fully root-caused and fixed - all three parts were
test-framework issues, not a product bug:

**Issue #1: `open_assessment_job()` was picking a stale, wrong job.**
It took `.last` out of an unfiltered `[role='row']` locator against a
"Select Assessment" list that accumulates **25+ jobs across days of
testing** ("25 or more matches found" shown live). The dropdown doesn't
render that whole list at once, so `.last` was landing on whatever
historical job happened to be rendered last - not the job the test had
just created. Confirmed live: after a run kicked off
`SOURCECDB_20260811124209`, the combobox ended up showing
`SOURCECDB_20260810163016` (a job from the day before) instead. **Fix**:
`open_assessment_job()` now types `f"{alias}_{today's date}"` into the
combobox before reading rows, narrowing 25+ entries down to a small,
fully-rendered, chronologically-ascending set, so `.last` reliably lands
on the newest job.

**Issue #2: the "Running Assessment" dialog's progress is a client-side
loading animation, not a real backend status indicator - and it was
being misread as a stall.** Proven two ways: (a) a live diagnostic that
polled the dialog every 10s on a freshly-created job showed genuine
progress and a close within 20s (50% -> 93% -> closed) - not stuck; (b)
selecting a job from **over a day earlier** (`SOURCECDB_20260810020127`,
long since settled either way) re-triggered the exact same "Running
Assessment... N of M steps... X%" animation from scratch, and it also
eventually closed on its own (confirmed via a 90s no-force-close wait)
to reveal the fully completed report. A job that finished a full day ago
cannot still be "running" - this is a report-loading UI animation that
replays every time an assessment is selected, regardless of the job's
real age/state. It just needs to be waited out, not treated as a
progress signal. **Fix**: `verify_assessment_completed()` now calls
`wait_for_dialog_to_close("Running Assessment", timeout=300000)` instead
of checking `get_by_role("progressbar").to_have_count(0)` (which doesn't
correspond to this dialog's plain-text progress display at all) followed
by finishing checks that only had Playwright's unstated default 5s
timeout. The previously-seen "stalled at 89-92%" screenshots were this
animation caught mid-replay by a test that gave up checking too early -
not the job's real state.

**Issue #3 (separate, unrelated to the stall): Export JSON/Export PDF
buttons.** Once #1 and #2 were fixed, a new but consistent failure
appeared: the completed report page has no "Export JSON"/"Export PDF"
buttons anywhere - confirmed for both a freshly-completed job and one
settled over a day earlier, the entire page has exactly 2 buttons in the
whole DOM ("Start Here", "ORACLE admin"). **User confirmed this is an
intentional app change**, not a bug. `verify_assessment_completed()` no
longer checks for these; `AssessmentLocators.EXPORT_JSON_BUTTON`/
`EXPORT_PDF_BUTTON` are kept, marked STALE, in case the app reverts
this.

**Verified fully fixed**: `test_pre_migration_assessment` passes clean,
first attempt, no reruns needed (`1 passed in 62.40s`, 2026-08-11).

### Connections' Add DB tab has lost several field labels, not just Secretstore Alias

Originally reported as only the `textbox "Secretstore Alias"` field on
the **Add DB** sub-tab (Edit DB/Delete DB are unaffected either way).
A fresh live run (2026-08-11) showed it's broader than that: on Add DB,
**Secretstore Alias, Database UserName, and Password** textboxes and
the OneP User Secrets section's **UserName, Password, and Role**
combobox have all lost their accessible names - only "Connect String"
still has one. `ConnectionsPage.verify_screen_structure()` now uses
DOM-order position (`get_by_role("textbox")`/`get_by_role("combobox")`
+ `.nth()`) for the unlabeled fields instead of role+name lookups,
which can never match them. The stale role+name locators are kept in
`connections_locators.py`, marked STALE, in case the app reverts this.

A second, unrelated bug was hiding behind the first: `CONNECT_STRING_
TEXTBOX`'s expected name (`"Connect String hostname:dbport/dbservice"`)
was never actually the field's accessible name - that full string is
the *visible label* (a separate text node), and the textbox's real
accessible name is just `"hostname:dbport/dbservice"`. Since Playwright
name-matching checks substring-of-actual-name (not the reverse), the
longer search string could never match the shorter real name. Fixed
the locator to match live - `test_connections_screen_structure` now
passes cleanly.

### A whole screen's structure check fails on a different assertion each run

Confirmed live 2026-08-11 across four screens in a single regression
run: Login (`ORACLE admin` behind "Refreshing Secure Vault"), Dashboard
("Process Lag" behind a stale progress placeholder - see below),
Config Tables (`HeartBeatTable` heading, then later `Add HeartbeatTable`
button, behind "Fetching credential domains" in different runs), and
Supplemental Logging (`Add Trandata` behind "Fetching credential
domains") all failed with the default 5s `expect()` timeout - each on
a *different* check within the same method depending on exactly when
the transient loading dialog happened to still be up. This isn't a
single fixable race - the app now has this class of unpredictable-
duration loading dialog on more screens/more often than before, and it
can land on any assertion in a sequence, not just the first. The fix
applied throughout `pages/login_page.py`, `pages/dashboard_page.py`,
`pages/config_tables_page.py`, `pages/supplemental_logging_page.py`,
and `pages/connections_page.py`: give **every** check in an affected
`verify_*` method the same generous timeout (15-20s) rather than just
the first one, since patching one assertion at a time just moves the
failure to the next one on the next run (confirmed this happened
twice while fixing Config Tables).

### Dashboard's "Process Lag" card intermittently times out even when visible

Confirmed live 2026-08-11: `get_by_text("Process Lag")` (the shared
`expect_visible_by_text` helper's default substring match) can match a
different, permanently-hidden element instead of the real card title -
a `<p class="global-progress-text">Fetching process lag data</p>`
loading placeholder contains "process lag" as a case-insensitive
substring, sits earlier in DOM order, and `.first` locks onto it. The
assertion then waits its full timeout for that always-hidden element
to become visible and never reaches the real, already-visible card.
`DashboardPage.verify_dashboard_cards()` now uses `exact=True` for
this reason - same underlying class of issue as the duplicate-element
problems documented above, just manifesting as a wrong substring match
instead of a strict-mode violation.

### Checkpoint table View dropdown intermittently never opens, even though the data is correct

`test_view_checkpoint_table` failed twice in automated runs with the
Table Name dropdown appearing empty for `config.yaml`'s
`checkpoint_table_name` (`ORCLPDB.C##MIGDB.CKPTS`, alias
`TARGETDB_ROOT`) - looked like a stale config value after the
2026-08-10 infra changes. **It wasn't**: confirmed two ways this was a
false alarm - (1) the user reproduced it manually seconds later with a
screenshot showing the exact same value populating fine, and (2) a
direct `SELECT owner, table_name FROM dba_tables` against the target
DB (`192.168.77.42`, ORCLPDB) confirmed `C##MIGDB.CKPTS` genuinely
exists right now. The config value was correct the whole time.

Root cause: `select_lazy_combobox` (`pages/base_page.py`) only
force-clicked the combobox once before waiting for the option text -
same dropped-click-event class of bug already fixed for the
searchselect widget family via `select_stable_combobox`, just not yet
applied to this "oj-c-*" combobox family. Added the same retry-the-
click pattern (`retries=4`, capped per-attempt timeout so a raised
`settle_timeout` override can't balloon into minutes).

**Lesson for next time**: when an automated result contradicts a
manual one, verify against a third, independent source (direct DB
query here) before trusting either - two out of the three "unresolved
discrepancy" issues logged this session (`impParallel`, Assessment) are
still open precisely because that third source hasn't been available
yet. Don't update `config.yaml` off an automated failure alone when a
retry-based UI bug is equally plausible.

**SSH access to the target DB host now works**: `192.168.77.42`,
user `oracle` - earlier attempts this project failed on username
guesses (`opc`/`ec2-user`/`root`) rather than a real access problem.
Password auth via `paramiko` (no `sshpass` available on this host).
`sqlplus` is at `/u01/app/oracle/product/19.0.0/dbhome_1/bin/sqlplus`,
`ORACLE_SID=orcltgt`.

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
  Jenkins credentials (see `docs/CI_CD.md`). Locally, if you don't export those
  two variables, you're using whatever is in `config.yaml`, unchanged from
  before. `.env` exists at the repo root but is empty and unused — the
  framework doesn't read it (no `python-dotenv` call anywhere), so setting
  values there does nothing; export real shell environment variables
  instead. Every other screen's test data (vault aliases, schema/PDB
  names, etc.) has no secret-backed override and still lives only in
  `config.yaml` — treat that file as sensitive despite it being tracked in
  git.
