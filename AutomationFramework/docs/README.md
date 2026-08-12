# MigDB Automation Framework

UI test automation for **SkyliftAI MigDB For Oracle**, a web application for
managing Oracle GoldenGate-based database migration/replication (Secure
Vault, Supplemental Logging, Config Tables, Designer capture/apply
pipelines, Initial Load, Assessment, monitoring/troubleshooting screens,
and more).

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.13 |
| Browser automation | [Playwright](https://playwright.dev/python/) (sync API) — Chromium, Firefox, or WebKit |
| Test runner | [pytest](https://docs.pytest.org/) 9.x |
| Design pattern | Page Object Model (POM) |
| Reporting | `pytest-html` (self-contained HTML report), Playwright traces/videos/screenshots |
| Retry handling | `pytest-rerunfailures` (`@pytest.mark.flaky`) |
| Parallelization | `pytest-xdist` (installed, not enabled by default — see below) |
| Test data | `Faker`, `utils/test_data.py` |
| Config | `config/config.yaml` loaded via `PyYAML` (`config/settings.py`) |

Full pinned dependency list: [`requirements.txt`](../requirements.txt).

## Prerequisites

- Python 3.13 (the committed virtualenv at `.venv/` was built against 3.13.7)
- Network access to the application under test — `config/config.yaml`'s
  `urls.base_url` currently points at a private on-prem host
  (`192.168.77.130`), **not** a publicly reachable address
- SSH key at `key/test1.pem` if you need to reach the app/DB hosts directly
  (used ad hoc for setup, not by the test suite itself)

## Setup

```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Playwright needs its browser binaries installed separately from pip
playwright install chromium firefox webkit
```

Application URL and every screen's test data (vault aliases, schema names,
PDB names, etc.) live in [`config/config.yaml`](../config/config.yaml) and
are loaded once at import time by
[`config/settings.py`](../config/settings.py). Update that file to point
the suite at a different environment.

Login credentials default to `config.yaml`'s `credentials.username` /
`credentials.password`, but can be overridden with `MIGDB_USERNAME` /
`MIGDB_PASSWORD` environment variables — this is how CI supplies real
credentials via Jenkins credentials instead of the committed file (see
[`CI_CD.md`](CI_CD.md)). Nothing else reads environment variables; an
`.env` file exists at the repo root but is empty and unused (no
`python-dotenv` call in the codebase), so values placed there are ignored
— export real shell variables instead.

## Running Tests Locally

All commands run from the project root, with the virtualenv active.

```bash
# Full suite
pytest

# One marker (see docs/TEST_CASES.md for the full marker list)
pytest -m smoke
pytest -m regression

# One folder / file
pytest tests/vault/
pytest tests/designer/test_designer.py

# Override the browser (chromium is the config.yaml default)
pytest --browser=firefox
pytest --browser=webkit
```

`pytest.ini` sets these defaults for every run (`addopts`): verbose output
(`-v`), live stdout (`-s`), short tracebacks (`--tb=short`), and a
self-contained HTML report written to `reports/html/report.html`.

### Headless vs. headed

`config.yaml`'s `browser.headless` flag (default `true`) controls this —
there is no CLI flag for it. Set it to `false` locally to watch a run.

### Reports & artifacts

Everything lands under `reports/` (git-ignored):

| Path | Content |
|---|---|
| `reports/html/report.html` | Main pytest-html report |
| `reports/screenshots/` | Auto-captured on any test failure (`conftest.py`'s `pytest_runtest_makereport` hook) |
| `reports/videos/` | Per-test recordings, if `reporting.video: true` in config.yaml |
| `reports/traces/` | Playwright trace `.zip` files, if `reporting.trace: true` in config.yaml |
| `reports/logs/` | Logger output (`utils/logger.py`) |

## Running Tests in CI

See [`CI_CD.md`](CI_CD.md) for the Jenkins pipeline, its triggers, and why
it runs on self-hosted infrastructure rather than a cloud runner.

## More Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Page Object Model layout and how the pieces fit together
- [`PLAYWRIGHT_FRAMEWORK.md`](PLAYWRIGHT_FRAMEWORK.md) — technical reference: browser/context/page lifecycle, locator strategy, the full waiting/retry model, and the complete `BasePage` method catalog
- [`TEST_CASES.md`](TEST_CASES.md) — every test suite, what it covers, and its markers
- [`CI_CD.md`](CI_CD.md) — pipeline triggers, stages, and artifact locations
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — common setup/run problems and fixes
- [`../RUNBOOK.md`](../RUNBOOK.md) — step-by-step operational procedures: run, monitor, debug, and maintain the suite
