# CI/CD

## Status

Test runs are automated via **Jenkins**, defined in
[`Jenkinsfile`](../Jenkinsfile) at the repo root. Jenkins is self-hosted at
`http://192.168.77.215:8080`, job **`MigDB-Automation-Tests`**, with the
pipeline agent running directly on the box that also hosts Jenkins itself
(`agent any` — the Jenkinsfile comment notes "Jenkins master IS odb in this
setup").

## Why Self-Hosted Is Required

`config/config.yaml`'s `urls.base_url` points at `192.168.77.130` — a
private, on-prem address. The database hosts the tests indirectly depend on
(source/target Oracle instances) are similarly private. A cloud-hosted CI
runner would have no route into that network, so Jenkins runs on
infrastructure that already has access.

## Triggers & Behavior

The `Run tests` stage inspects `currentBuild.getBuildCauses()` to decide
what to run, so the **same pipeline** behaves differently depending on how
it was started:

| Trigger | Cause string | Behavior |
|---|---|---|
| Nightly cron (`triggers { cron('0 2 * * *') }`) | `TimerTrigger` | `pytest -m regression` — full unattended nightly run |
| Manually started from Jenkins UI ("Build with Parameters") | `UserIdCause` | `pytest -m "<MARKER>" --browser=<BROWSER>` using the build's `MARKER`/`BROWSER` parameters |
| Anything else (e.g. an SCM webhook push) | (falls through) | `pytest -m smoke` |

**Build parameters** (set when triggering manually):
- `MARKER` — string, defaults to `regression`
- `BROWSER` — choice of `chromium` / `firefox` / `webkit`, defaults to `chromium`

## Stages

1. **Checkout** — `checkout scm` (pulls the configured Git repo/branch)
2. **Install dependencies** — inside `AutomationFramework/`: creates a
   `venv` with `python3.12 -m venv venv`, activates it, upgrades `pip`, then
   `pip3 install -r requirements.txt`
3. **Install Playwright browsers** — `playwright install chromium firefox webkit`
   (pip alone doesn't install the browser binaries)
4. **Run tests** — one of the three commands above, depending on trigger cause

## Where Reports/Artifacts Are Published

`pytest.ini`'s `addopts` writes a self-contained HTML report to
`reports/html/report.html`; `conftest.py`'s fixtures/hooks add screenshots
on failure, and optionally video/trace recordings (gated by
`config.yaml`'s `reporting.video` / `reporting.trace` flags).

The `post { always { ... } }` block archives everything under
`AutomationFramework/reports/**` as a Jenkins build artifact
(`allowEmptyArchive: true`, so a run that produces no reports doesn't fail
the archive step) — downloadable from the build's page in the Jenkins UI.

## Credentials

The application login is read from `config.yaml`'s `credentials` section by
default, but `config/settings.py` overrides `username`/`password` with the
`MIGDB_USERNAME`/`MIGDB_PASSWORD` environment variables when they're set,
falling back to `config.yaml` otherwise — so local runs are unaffected
either way (see [`README.md`](README.md)).

The Jenkinsfile's `environment` block binds these from **Jenkins'
credential store**, not repo secrets:

```groovy
environment {
    MIGDB_USERNAME = credentials('migdb-username')
    MIGDB_PASSWORD = credentials('migdb-password')
}
```

**One-time setup**: in Jenkins, **Manage Jenkins → Credentials**, add two
"Secret text" credentials with IDs exactly `migdb-username` and
`migdb-password`. Jenkins masks matching values in console output
automatically (visible in build logs as `Masking supported pattern matches
of $MIGDB_USERNAME or $MIGDB_PASSWORD`).

Every other screen's test data (vault aliases, schema/PDB names,
checkpoint table names, etc.) still lives only in the committed
`config/config.yaml` — none of that is secret-backed, since it's
environment topology rather than a credential.

## Note on GitHub Actions

This repo briefly carried a parallel `.github/workflows/tests.yml` GitHub
Actions workflow targeting a self-hosted runner. It has been removed in
favor of the Jenkins pipeline above, which was already live and covering
the same triggers (push/PR-equivalent via webhook, manual dispatch with
marker/browser params, and nightly scheduled regression) — running both
would have executed the same suite twice against the same on-prem
environment for no benefit.
