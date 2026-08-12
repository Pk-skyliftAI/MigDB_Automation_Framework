# RUNBOOK — MigDB Automation Framework

Operational guide for running, monitoring, debugging, and maintaining this
test suite. If you're new to this project, start at section 2.

---

## 1. Environment Overview

**Application under test**: `MIGDB for Oracle` (`config/config.yaml` →
`application.name`), a web app for managing Oracle GoldenGate-based
database migration/replication (Secure Vault, Supplemental Logging, Config
Tables, Designer capture/apply pipelines, Initial Load, Assessment,
monitoring/troubleshooting screens).

**Environment this suite currently points at**: `QA`
(`config/config.yaml` → `environment.name`), app URL
`http://192.168.77.130:8080/?ojr=signin`
(`config/config.yaml` → `urls.base_url`) — a **private, on-prem address**.

**Why self-hosted CI is required**: The app host, and the source/target
Oracle databases it depends on, all live on this same private on-prem
network. A cloud-hosted CI runner (GitHub-hosted, etc.) has no route into
it. Everything — local runs and CI — must execute from a machine on that
network.

```
Your laptop  ─┐
               ├─► Jenkins (192.168.77.215:8080, self-hosted agent)
CI trigger  ───┘         │
                          ▼
              http://192.168.77.130:8080  (MIGDB app)
                          │
                          ▼
        Source/Target Oracle DBs (private on-prem hosts)
```

If you can't reach `192.168.77.130:8080` from where you're running pytest,
nothing in this suite will work — check that before debugging anything else
(`curl -I http://192.168.77.130:8080/?ojr=signin`).

---

## 2. First-Time Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/Pk-skyliftAI/MigDB_Automation_Framework.git
cd MigDB_Automation_Framework/AutomationFramework

# 2. Check out main (or the feature branch you're assigned)
git checkout main
```

**Python version**: CI (Jenkins) builds its venv with `python3.12`
(`Jenkinsfile` → `python3.12 -m venv venv`). Match that locally to avoid
surprises, even though `3.13` also works (verified against this repo).

```bash
python3.12 --version   # should print Python 3.12.x
# If it's missing, install Python 3.12 through your OS package manager first.
```

```bash
# 3. Create and activate a virtualenv
python3.12 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 4. Install dependencies (exact pinned versions)
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Install Playwright's browser binaries (pip alone does not do this)
playwright install chromium firefox webkit
```

**Environment variables / secrets**:

| Variable | Required? | What it's for | Where to get it |
|---|---|---|---|
| `MIGDB_USERNAME` | Optional locally | Overrides `config.yaml`'s `credentials.username` | Ask your team lead / app owner — see section 9 |
| `MIGDB_PASSWORD` | Optional locally | Overrides `config.yaml`'s `credentials.password` | Same as above |

If you don't set these, the suite falls back to the plaintext
`admin` / `Welcome1` already committed in `config/config.yaml`
(`credentials.username` / `credentials.password`) — fine for local QA-env
runs, nothing further to configure.

`.env` exists at the repo root but is **empty and unused** — nothing in
this codebase reads it (no `python-dotenv` call anywhere), so don't bother
putting values there.

**Verify the setup worked**:

```bash
pytest -m smoke -k test_login
```

Expect `1 passed` and a browser (headless, per `config.yaml`'s
`browser.headless: true`) launching, logging into `192.168.77.130:8080`,
and succeeding. If this fails, work through section 6 before anything else.

---

## 3. Running Tests

All commands run from `AutomationFramework/` with the venv active.

```bash
# Full suite (37 tests — testpaths = tests, per pytest.ini)
pytest

# Smoke suite (29 of the 37 tests — fast, one per screen/critical path)
pytest -m smoke

# Regression suite (all 37 tests — every marked test carries `regression`)
pytest -m regression

# One test file
pytest tests/vault/test_add_source_db_alias.py

# One test function
pytest tests/authentication/test_login.py::test_login

# By keyword substring (matches test/function/class names)
pytest -k test_dataflow_screen_structure

# Override the browser (chromium is config.yaml's default)
pytest --browser=firefox
pytest --browser=webkit
```

**What each real marker means** (from `pytest.ini` → `markers`, cross-checked
against actual `@pytest.mark...` usage in `tests/`):

| Marker | Meaning | Real usage count |
|---|---|---|
| `smoke` | Fast critical-path check, one per screen | 29 tests |
| `regression` | Full suite — every test in the repo carries this | 37 tests |
| `login` / `logout` | Authentication flows | 2 / 1 |
| `dashboard`, `navigation`, `manage`, `monitor`, `designer`, `vault`, `supplemental_logging`, `parameter_file`, `config_tables`, `connections`, `purge_cdc_files`, `assessment`, `initial_load`, `dataflow`, `conflict_resolution`, `analyze_objects`, `analyze_trails`, `troubleshoot`, `logfile` | One marker per app screen/module — every test also carries the module marker matching its folder | 1–5 each |
| `negative` | Negative-path test (e.g. invalid login) | 1 test |
| `flaky` (via `pytest-rerunfailures`, not declared in `markers` but used) | Auto-reruns on failure — `reruns=2, reruns_delay=10` — used on screens with known async-render lag, **not** a mask for real bugs | 5 tests |

`sanity` and `ui` are declared in `pytest.ini` but **not currently applied
to any test** — don't rely on them existing yet.

**Common day-to-day combinations**:

```bash
# Everything for one module (e.g. Config Tables) across smoke+regression
pytest -m config_tables

# Just the smoke tests for one module
pytest -m "smoke and vault"

# Run everything except a flaky-marked test you're actively debugging
pytest -m "regression and not flaky"

# Re-run only what failed last time
pytest --lf
```

---

## 4. Running Tests via CI (Jenkins)

This repo's CI is **Jenkins only** (`Jenkinsfile` at repo root). A prior
GitHub Actions workflow was removed after Jenkins was confirmed to already
cover the same triggers — don't look for a `.github/workflows/` file.

**Jenkins job**: `MigDB-Automation-Tests` at `http://192.168.77.215:8080`

### Trigger a manual run

1. Go to `http://192.168.77.130:8080` → wait, that's the app; Jenkins is
   `http://192.168.77.215:8080`.
2. Open job **MigDB-Automation-Tests** → click **Build with Parameters**
   (left sidebar).
3. Set:
   - **MARKER** — string, e.g. `regression`, `smoke`, `vault`, `smoke and vault`
     (default: `regression`)
   - **BROWSER** — choose `chromium` / `firefox` / `webkit`
     (default: `chromium`)
4. Click **Build**.

This runs `pytest -m "<MARKER>" --browser=<BROWSER>` (`Jenkinsfile` →
`Run tests` stage, `UserIdCause` branch).

### Live logs while it's running

Job page → the new build number in **Build History** (left sidebar) →
**Console Output**. Updates in real time.

### After it finishes

Same build's page → **Build Artifacts** at the bottom (or the artifact
browser icon). The whole `AutomationFramework/reports/**` tree is archived
(`Jenkinsfile` → `post { always { archiveArtifacts ... } }`, so this
happens even on failure):

- `reports/html/report.html` — self-contained pytest-html report
- `reports/screenshots/*.png` — one per failed test
- `reports/videos/*.webm` — if `config.yaml`'s `reporting.video: true`
- `reports/traces/*.zip` — Playwright trace files, if `reporting.trace: true`
- `reports/logs/automation_<timestamp>.log` — full logger output

### Nightly scheduled run

`Jenkinsfile` → `triggers { cron('0 2 * * *') }` — fires daily at 02:00
(Jenkins server local time). This build has **no manual parameters set**,
so it takes the `TimerTrigger` branch: `pytest -m regression` (the full 37-test
suite, chromium only — `--browser` isn't passed on this path).

Results land in the same place as any other build: **Build History** on the
job page shows it (icon differs — clock/timer glyph instead of a person
icon for manual builds) → same **Console Output** / **Build Artifacts** as
above.

---

## 5. Reading and Interpreting Results

**Where things land** (all under `AutomationFramework/reports/`, git-ignored):

| Path | Content |
|---|---|
| `reports/html/report.html` | Open in any browser — pass/fail/skip per test, expandable logs |
| `reports/screenshots/<test_name>_<timestamp>.png` | Full-page capture, only on failure (`conftest.py` → `pytest_runtest_makereport`) |
| `reports/videos/<test_name>.webm` | Full run recording, if video reporting is on |
| `reports/traces/<test_name>.zip` | Open with `playwright show-trace reports/traces/<file>.zip` for a full timeline/DOM/network replay |
| `reports/logs/automation_<timestamp>.log` | Every `logger.info`/`error` call, one file per pytest process |

**A real console example** (from an actual run in this repo):

```
tests/authentication/test_login.py::test_login
------------------------------- live log setup --------------------------------
INFO     conftest:conftest.py:51 Browser launched successfully: chromium
INFO     conftest:conftest.py:73 Browser context created.
INFO     conftest:conftest.py:93 New browser page created.
PASSED
------------------------------ live log teardown -------------------------------
INFO     conftest:conftest.py:97 Closing browser page.
```

- **PASSED** appears inline right after the test body finishes (no gap) —
  because `pytest.ini`'s `addopts` includes `-s` (no output capturing), so
  logger lines interleave with pytest's own status text as shown above.
- **FAILED** replaces `PASSED`, followed by a `--tb=short` traceback and,
  separately, two log lines from the failure hook:
  ```
  ERROR    conftest:conftest.py:129 Test Failed: test_add_checkpoint_table
  ERROR    conftest:conftest.py:130 Screenshot saved: reports/screenshots/test_add_checkpoint_table_20260807_164459.png
  ```
- **SKIPPED** — none of the current 37 tests use `@pytest.mark.skip`, so
  you shouldn't see this; if you do, something unexpected marked it (check
  for a `skipif` added upstream, or a collection error being misreported).
- **RERUN** — shown for any `@pytest.mark.flaky` test that failed once and
  is retrying (`pytest-rerunfailures`); only the final outcome (after up to
  2 reruns, 10s apart) counts toward the pass/fail total.

**Telling a real product bug from a flaky/infra failure**:

This framework's own automated signal is limited to the screenshot +
traceback described above — there's **no automatic network-response
capture built into `conftest.py`**. To tell the two apart, work through
this order:

1. **Check the traceback first.** A Playwright `TimeoutError` waiting on a
   specific locator usually means either a genuine app/backend issue or an
   environment-specific data mismatch (wrong alias/PDB/table name) — not
   pure flakiness. A `Locator resolved to N elements` (strict-mode
   violation) is a locator bug in the test/page-object code itself, not a
   product bug.
2. **Is it on the known-flaky list?** (see `flaky` marker table in
   section 3) — if so, and it passed on rerun, it's the app's known
   async-render lag, not a new issue.
3. **Is it one of the already-confirmed backend bugs?** Check
   `docs/TROUBLESHOOTING.md` — several submit flows (Extract Pump,
   Homogeneous Initial Load's Create Job) have **documented, confirmed
   server-side bugs** (`405`/`422` responses) reproduced via manual network
   capture (`page.on("response")` in an ad-hoc script) — if the failure
   matches one of those signatures, it's a known product bug, not a test
   regression.
4. **New signature, not on either list?** Open the trace
   (`playwright show-trace reports/traces/<test>.zip`) and replay the
   network tab yourself before concluding it's a product bug — that's how
   every bug currently documented in `docs/TROUBLESHOOTING.md` was
   confirmed.

---

## 6. Common Failure Scenarios & Fixes

**Symptom**: `playwright._impl._errors.Error: Executable doesn't exist`
**Cause**: Playwright's Python package installed via `pip`, but browser
binaries were never downloaded.
**Fix**:
```bash
playwright install chromium firefox webkit
```

---

**Symptom**: Every test times out immediately, can't even reach the login page
**Cause**: You're not on the same network as `192.168.77.130` (the app's
private on-prem address).
**Fix**: Confirm reachability before debugging anything else:
```bash
curl -I http://192.168.77.130:8080/?ojr=signin
```
If that hangs/fails, you need to be on-prem or on the Jenkins agent itself
— this cannot be fixed from the test code.

---

**Symptom**: `KeyError` at collection time, before any test runs
**Cause**: `config/settings.py`'s `Config.__init__` unconditionally reads a
fixed set of top-level keys from `config.yaml` (`application`,
`environment`, `browser`, `urls`, `credentials`, `secure_vault`,
`execution`, `reporting`, `supplemental_logging`, `designer`,
`config_tables`, `initial_load`). If any of those top-level sections was
removed/renamed in `config.yaml`, every test fails at import time.
**Fix**: Diff `config/config.yaml` against that key list; restore the
missing section.

---

**Symptom**: A previously-passing test now times out on a specific vault
alias / PDB name / table name
**Cause**: This app's environment drifts — vault alias names, PDB names,
and checkpoint table names have all changed on the live app without a
matching code change (see the dated inline comments throughout
`config/config.yaml`, e.g. lines documenting the `TARGETDB_ROOT` →
`TARGETPDB` switch and the `ORCL` → `ORCLDB` fix).
**Fix**: Re-verify the value live in the app (Secure Vault screen) or via a
direct DB query — don't assume it's a locator/code bug before checking
`config.yaml`'s own comments for that key first.

---

**Symptom**: `strict mode violation: ... resolved to N elements`
**Cause**: Several screens render two elements with an identical
accessible role+name (e.g. Analyze Objects' two `"All Table"` grids,
Heterogeneous Initial Load's two `"Required Secret Domain"` comboboxes).
**Fix**: Use `.first`, an exact `id` via `BasePage.click_by_id`, or a
`to_have_count(2)` assertion instead of a single-match locator — see
`pages/analyze_objects_page.py` and `pages/initial_load_page.py` for the
fixed pattern.

---

**Symptom**: `AssertionError: Locator expected to be visible` on a
combobox/dropdown, intermittently
**Cause**: Several Oracle JET comboboxes (Vault Domain, Vault Alias,
Schema Name, Checkpoint Table) populate their option list asynchronously
with **no visible loading indicator**.
**Fix**: Use `BasePage.select_lazy_combobox()` (waits for real option text,
default 15s `settle_timeout`, some call sites raise it to 30000ms). If it
still fails intermittently under load, add
`@pytest.mark.flaky(reruns=2, reruns_delay=10)` — the established
compensating control already used on 5 tests (`test_add_checkpoint_table.py`
and others) — rather than chasing a longer fixed wait.

---

**Symptom**: Jenkins build stuck in the queue, never starts
**Cause**: No idle agent available.
**Fix**: See section 7 (Runner/Agent Health Checks).

---

**Symptom**: Jenkins build fails at the `Install dependencies` stage with a
credentials/masking-related error, or `MIGDB_USERNAME`/`MIGDB_PASSWORD`
come through empty
**Cause**: The Jenkins credential IDs `migdb-username` / `migdb-password`
(bound in `Jenkinsfile` → `environment { ... credentials(...) }`) don't
exist yet, or were renamed.
**Fix**: In Jenkins, **Manage Jenkins → Credentials**, confirm both IDs
exist exactly as `migdb-username` and `migdb-password` (Secret text type).

---

## 7. Runner/Agent Health Checks

Jenkins in this setup runs its pipeline agent **on the same box as the
Jenkins master itself** (`Jenkinsfile` → `agent any`, comment: *"runs
directly on odb since Jenkins master IS odb in this setup"*) — so "is the
agent up" and "is Jenkins up" are the same question here.

**Check if Jenkins is up**:
```bash
curl -I http://192.168.77.215:8080
```
A `200`/`302` response means it's reachable. You can also check the
built-in node status page: `http://192.168.77.215:8080/computer/` — the
built-in node should show no red/offline icon.

**Restart Jenkins** (run on the Jenkins host itself):
```bash
sudo systemctl status jenkins    # confirm current state first
sudo systemctl restart jenkins
```

**Escalate if it stays down**: `[CI ADMIN CONTACT]`

---

## 8. Adding or Updating Tests (Quick Reference)

**Where new test files go**: `tests/<module_name>/test_<description>.py`,
one folder per app screen/module (matches the existing 21 folders under
`tests/`). Function names start with `test_` (`pytest.ini` →
`python_functions`).

**Marker convention** — every test carries at minimum a suite marker plus
its module marker; add `smoke` only if this is meant to be a fast
critical-path check, not every regression test needs it:

```python
import pytest

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.dataflow          # module marker must already exist in pytest.ini's markers list
def test_dataflow_screen_structure(navigation, dataflow):

    navigation.open_navigation_menu()

    dataflow.open_dataflow()

    dataflow.verify_screen_structure()
```
(real example: `tests/dataflow/test_dataflow_screen.py`)

If you're introducing a brand-new module marker, add it to `pytest.ini`'s
`markers =` list first, or pytest will warn on every collection.

**Adding a locator + page object** — real example for a simple read-only
screen (`locators/dataflow_locators.py` + `pages/dataflow_page.py`):

```python
# locators/dataflow_locators.py
class DataflowLocators:
    # Confirmed against a live aria snapshot of the Dataflow screen
    # (2026-08-06). It's a passive read-only diagram/status view - just
    # a heading and a progress indicator, no interactive form.
    REPLICATION_FLOW_HEADING = ("heading", "Replication flow")
```

```python
# pages/dataflow_page.py
from pages.base_page import BasePage
from locators.dataflow_locators import DataflowLocators

class DataflowPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    def open_dataflow(self):
        self.click_tree_item("Dataflow")
        self.wait()

    def verify_screen_structure(self):
        self.expect_visible_by_role(*DataflowLocators.REPLICATION_FLOW_HEADING)
```

Then wire a fixture in `conftest.py` (module name = fixture name):
```python
@pytest.fixture
def dataflow(logged_in_page):
    return DataflowPage(logged_in_page)
```

Before writing new interaction code for a not-yet-covered widget type,
check `pages/base_page.py`'s existing helpers first
(`select_lazy_combobox`, `click_tree_item`, `expect_visible_by_role`,
`wait_for_dialog_to_close`) — most Oracle JET quirks in this app are
already handled there.

**Run just the new test before committing**:
```bash
pytest tests/dataflow/test_dataflow_screen.py -v
```

---

## 9. Credentials & Secrets Reference

| Name | Used for | Configured in |
|---|---|---|
| `MIGDB_USERNAME` | App login (overrides `config.yaml`) | Jenkins → **Manage Jenkins → Credentials**, ID `migdb-username` |
| `MIGDB_PASSWORD` | App login (overrides `config.yaml`) | Jenkins → **Manage Jenkins → Credentials**, ID `migdb-password` |

No other screen's test data (vault aliases, schema/PDB names, checkpoint
table names) is secret-backed — it all lives in plaintext in
`config/config.yaml`, since it's environment topology, not a credential.
Treat that file as sensitive anyway (it's tracked in git).

`key/` and `*.pem` (SSH keys used ad hoc for direct infra access, not by
the test suite itself) are git-ignored — request access to these
separately if your work requires SSH access to the app/DB hosts, per
section 10.

To request access to the above: `[CREDENTIAL OWNER / SECRETS MANAGER CONTACT]`

---

## 10. Escalation / Who Owns What

| Area | Contact |
|---|---|
| Application (MIGDB for Oracle) issues/bugs | `[APP OWNER NAME]` |
| Jenkins / CI infrastructure | `[CI ADMIN CONTACT]` |
| Oracle DB access (source/target hosts) | `[DBA CONTACT]` |
| This test framework / repo | `[QA LEAD / REPO OWNER NAME]` |
| Ticketing system for filing product bugs found by this suite | `[TICKETING SYSTEM / PROJECT LINK]` |
| Team chat channel for CI failures | `[SLACK/TEAMS CHANNEL]` |

---

## Assumptions & Gaps

**Verified directly against the codebase** (not assumed): `config.yaml`
contents and its dated drift-history comments, `conftest.py`'s fixtures and
failure hook, `pytest.ini`'s real marker list cross-checked against actual
`@pytest.mark` usage (37 tests, 29 smoke, 5 flaky), `Jenkinsfile`'s three
trigger-cause branches, `requirements.txt`'s pinned versions, `.env` being
empty/unused, `.gitignore`'s ignored paths, `utils/logger.py` /
`screenshot_manager.py` / `browser_manager.py` implementations, and one
full locator/page-object/test triplet (`dataflow`) used as the real
example in section 8.

**Inferred, not directly verifiable from the repo**:
- Jenkins server's OS/restart mechanism (assumed `systemctl` — a standard
  Linux Jenkins install, but not confirmed against the actual Jenkins host).
- The exact Jenkins UI click path in section 4 (based on standard Jenkins
  behavior for a parameterized job — the live UI wasn't screenshotted for
  this document).
- Python 3.12 vs 3.13: `Jenkinsfile` explicitly uses `python3.12`, while an
  earlier version of `docs/README.md` stated 3.13. Both are installed and
  working on the machine this was written on; this runbook recommends 3.12
  to match CI exactly. Worth reconciling with whoever maintains `docs/README.md`.

**Could not determine from the codebase — filled with placeholders,
please complete manually**:
- Section 7's escalation contact
- Section 9's credential-request contact
- All of section 10 (app owner, CI admin, DBA contact, QA lead, ticketing
  system, chat channel) — no team-structure information exists anywhere in
  this repo.
- Whether Jenkins runs as a systemd service, Docker container, or something
  else — confirm and correct section 7 if it's not `systemctl`.
