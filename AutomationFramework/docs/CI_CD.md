# CI/CD

## Status

Until this workflow was added, this repository had **no CI/CD pipeline** —
the git history and repo contents show no `.github/workflows/`,
`Jenkinsfile`, or any other pipeline config; tests were run manually via
`pytest` from a local/on-prem shell. GitHub Actions is now wired up at
[`.github/workflows/tests.yml`](../.github/workflows/tests.yml).

## Why a Self-Hosted Runner Is Required

`config/config.yaml`'s `urls.base_url` points at `192.168.77.130` — a
private, on-prem address. The database hosts the tests indirectly depend on
(source/target Oracle instances) are similarly private. **A GitHub-hosted
runner cannot reach any of this** — it runs on GitHub's public cloud with no
route into that network. The workflow is configured with `runs-on:
self-hosted`, and must run on a machine that has network access to
`192.168.77.130` (this test server, or another host on the same network).

### Registering the self-hosted runner

From the repository's GitHub page: **Settings → Actions → Runners → New
self-hosted runner**, then follow GitHub's generated download/configure/run
commands on the target machine. Install it as a service
(`./svc.sh install && ./svc.sh start` on Linux) so it survives reboots and
picks up jobs automatically.

## Triggers

Defined in `.github/workflows/tests.yml`:

| Trigger | Behavior |
|---|---|
| `push` to `main` | Runs `pytest -m smoke` |
| `pull_request` targeting `main` | Runs `pytest -m smoke` |
| `workflow_dispatch` (manual, "Run workflow" button) | Runs `pytest -m "<marker>" --browser=<browser>`, both provided as inputs at trigger time (default marker: `regression`, default browser: `chromium`) |

## Stages

Single job, `test`, running on `self-hosted`:

1. **Checkout** — `actions/checkout@v4`
2. **Set up Python** — `actions/setup-python@v5`, Python 3.13
3. **Install dependencies** — `pip install -r requirements.txt`
4. **Install Playwright browsers** — `playwright install chromium firefox
   webkit` (pip alone does not install the browser binaries)
5. **Run tests** — `pytest -m smoke` on automatic triggers, or the
   user-supplied marker/browser on manual dispatch
6. **Upload artifacts** — always runs (`if: always()`), even on failure

## Where Reports/Artifacts Are Published

Locally and in CI, `pytest.ini`'s `addopts` writes a self-contained HTML
report to `reports/html/report.html`; `conftest.py`'s fixtures/hooks add
screenshots on failure, and optionally video/trace recordings (gated by
`config.yaml`'s `reporting.video` / `reporting.trace` flags). All of it
lands under `reports/` (git-ignored locally).

In CI, the whole `reports/` directory is uploaded as a workflow artifact
named `test-reports-<run id>` (`actions/upload-artifact@v4`, 14-day
retention), downloadable from the workflow run's summary page in GitHub's
UI.

## Credentials

The application login is read from `config.yaml`'s `credentials` section by
default, but `config/settings.py` overrides `username`/`password` with the
`MIGDB_USERNAME`/`MIGDB_PASSWORD` environment variables when they're set,
falling back to `config.yaml` otherwise — so local runs are unaffected
either way. The workflow injects both as job-level `env` from
`${{ secrets.MIGDB_USERNAME }}` / `${{ secrets.MIGDB_PASSWORD }}`.

**One-time setup**: in the repo's **Settings → Secrets and variables →
Actions**, add `MIGDB_USERNAME` and `MIGDB_PASSWORD` as repository secrets.
Until they're added, the workflow silently falls back to whatever
`config.yaml` contains in the checked-out commit (both env vars resolve to
empty strings, which the settings.py check treats as "not set").

Every other screen's test data (vault aliases, schema/PDB names,
checkpoint table names, etc.) still lives only in the committed
`config/config.yaml` — none of that is secret-backed, since it's
environment topology rather than a credential.
