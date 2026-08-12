# Playwright Framework — Technical Reference

Deep technical reference for how this project actually drives Playwright:
browser lifecycle, locator strategy, waiting model, and the full
`BasePage` helper catalog. For *what* the framework tests and *how the
POM folders relate*, see [`ARCHITECTURE.md`](ARCHITECTURE.md) — this
document goes one level deeper, into the Playwright API calls themselves.

Playwright version: `1.61.0` (`requirements.txt`). API style used
throughout: **sync API** (`from playwright.sync_api import ...` /
`sync_playwright()`), not the async API — there is no `asyncio` anywhere
in this codebase.

---

## 1. Browser/Context/Page Lifecycle

Three nested `conftest.py` fixtures manage the Playwright object graph,
one full stack per test function (`scope="function"` — no session/module
reuse, so every test gets an isolated browser instance):

```
browser (function-scoped)
  └─ context (function-scoped)
       └─ page (function-scoped)
            └─ logged_in_page (function-scoped)
                 └─ <page-object fixture, e.g. vault/designer/dataflow>
```

### `browser` fixture → `utils/browser_manager.py`

```python
manager = BrowserManager(browser_name=request.config.getoption("--browser"))
browser = manager.start_browser()
```

`BrowserManager.start_browser()`:
1. Calls `sync_playwright().start()` directly (not the `with` context
   manager form) — `stop_browser()` is responsible for calling
   `self.playwright.stop()` during fixture teardown.
2. Resolves which engine to launch: **CLI `--browser` flag wins over
   `config.yaml`'s `browser.engine`** (`self.browser_name or
   config.browser["engine"]`).
3. Launches via `self.playwright.<chromium|firefox|webkit>.launch(headless=..., slow_mo=...)`,
   both read from `config.yaml`'s `browser.headless` / `browser.slow_mo` —
   there's no per-engine override, the same headless/slow_mo values apply
   to whichever engine is chosen.
4. An unrecognized `browser_name` raises `ValueError` immediately —
   there's no silent fallback to chromium.

### `context` fixture

```python
context = browser.new_context(
    record_video_dir="reports/videos" if record_video else None
)
if config.reporting.get("trace", False):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
```

- Video recording is a **context-level** setting in Playwright (not
  per-page) — `record_video_dir` must be passed to `new_context()`, which
  is why it's here and not in the `page` fixture.
- Tracing similarly starts at the context level, with all three trace
  ingredients enabled (`screenshots`, `snapshots`, `sources`) so
  `playwright show-trace` gives a full DOM+network+source replay, not just
  a screenshot filmstrip.
- Teardown stops tracing and writes it to
  `reports/traces/<test_node_name>.zip`, creating the `traces/` directory
  on demand (`Path.mkdir(parents=True, exist_ok=True)`).

### `page` fixture

```python
page = context.new_page()
request.node.page = page   # <- makes page reachable from the failure hook
```

- Stashing the `Page` object on `request.node` is **the only way**
  `pytest_runtest_makereport` (see §5) can reach it later — pytest hooks
  don't get fixture values directly.
- Teardown captures `page.video` **before** calling `page.close()` —
  Playwright doesn't finalize/name the video file until the page actually
  closes, and the handle would be stale afterward if grabbed too late.
  After close, the video is renamed from Playwright's own temp filename to
  `reports/videos/<test_node_name>.webm`.

### `logged_in_page` fixture

```python
login = LoginPage(page)
login.open_login_page()
login.login()
return page
```

Every fixture that depends on `logged_in_page` (all 20 page-object
fixtures in `conftest.py`) triggers a **fresh login on every single test**
— there is no shared/cached authenticated session across tests, by design
(matches the function-scoped browser above).

### Per-screen page-object fixtures

Each is a one-line wrapper, e.g.:
```python
@pytest.fixture
def vault(logged_in_page):
    return VaultPage(logged_in_page)
```
20 of these exist in `conftest.py`, one per screen module. A test asks for
exactly the ones it needs by fixture name — see any file under `tests/`.

---

## 2. Locator Strategy

**Role-based locators (`get_by_role`) are the default and overwhelming
majority pattern** across `locators/*.py` and `pages/*.py` — CSS selectors
and `page.locator()` are the exception, reached for only when a widget
genuinely has no meaningful accessible role/name (see §3's JET-specific
helpers).

Locator files (`locators/*_locators.py`) store **only data**, as
role/name tuples or bare text constants — no Playwright calls:
```python
# locators/dataflow_locators.py
REPLICATION_FLOW_HEADING = ("heading", "Replication flow")
```
Page objects unpack these into `get_by_role`/`expect_visible_by_role`
calls; locator files never import `playwright` themselves.

**`exact` matching defaults to `False` almost everywhere** in `base_page.py`
(`click_tree_item`, `expand_tree_item`, `expect_tree_item_visible`) —
this is a deliberate, established convention (see `ARCHITECTURE.md` and
inline comments), not an oversight. `select_stable_tab`'s `radio` locator
is a documented exception (`exact=True`), because toolbar tab names can be
short substrings of each other.

**ID-based locators exist for exactly one documented reason**: the nav
tree's `"Monitor"` accessible name collides with other tree items
(`Hetro Initial Load Monitor`, `Homo Initial Load Monitor`) —
`click_by_id`/`expect_visible_by_id` target `#<element_id>[role='treeitem']`
instead, e.g. `click_by_id("monitor")` in `pages/monitor_page.py` and
`pages/designer_page.py`.

---

## 3. Waiting & Retry Model

Three layers exist, used for different situations — **know which one
applies before adding a new wait**, since using the wrong layer is the
single most common source of flaky tests in this app (see
`docs/TROUBLESHOOTING.md`).

### Layer 1 — Playwright's built-in auto-waiting + `expect()`

The default, and what should be reached for first. Every
`expect(locator).to_be_visible(timeout=...)` call (used throughout
`base_page.py`) already polls/retries internally — no manual sleep needed
around these.

### Layer 2 — `BasePage.wait()` (blunt, whole-page)

```python
def wait(self):
    self.page.wait_for_load_state("networkidle")
```
Called after most navigation actions (`click_tree_item` + `.wait()` is
the standard pairing across nearly every page object). Coarse — waits for
network quiescence, not a specific element — appropriate right after a
full navigation, not for waiting on a specific async-loaded widget.

### Layer 3 — Purpose-built retry helpers for known JET quirks

These exist because layers 1–2 are insufficient for specific, confirmed
async-rendering behaviors in this app's Oracle JET frontend. **Use these
by name for their documented scenario rather than re-deriving a similar
fix**:

| Helper | Scenario it solves |
|---|---|
| `select_lazy_combobox(combo, option_text, settle_timeout=15000)` | Newer `oj-c-*` combobox family (e.g. Config Tables' CheckpointTable form) whose option list populates async with **zero loading indicator** — polls for the real option text instead of a fixed delay; some call sites raise `settle_timeout` to `30000` where the lag is worse |
| `select_stable_combobox(combo, option_text, retries=6, open_timeout=3000, settle_timeout=15000)` | Searchselect-family comboboxes (Choose Deployment Name, Choose CDB(in CDB Mode), Choose Target Deployment, Directory Name, …) whose `aria-expanded` **intermittently never flips true after a single click** — confirmed live 2026-08-10 this is a dropped click event, not a fixed lag (the same field opened at 5s in one run, still hadn't opened at 15s in another with no code change). Retries the click itself, same approach as `select_stable_tab` |
| `select_stable_tab(name, retries=5, stability_ms=3000, timeout=8000)` | Toolbar tabs that **silently revert to a default selection** after certain background refreshes — clicks, confirms selected, waits `stability_ms`, and re-verifies it held; retries up to 5 times before raising |
| `select_stable_tab_scoped(scope, name, retries=5, stability_ms=3000, timeout=8000)` | Same revert-to-default race as `select_stable_tab`, but for toolbars where the tab name **isn't unique page-wide** — Config Tables' CheckpointTable/HeartBeatTable sections both have "Add"/"Delete" radios, so the caller passes a container locator (e.g. `_checkpoint_toolbar()`) to scope the lookup. Also targets a plain `label` element rather than `label.oj-button-label` — confirmed live 2026-08-10 that this app's `oj-c-buttonset-single` (Core Pack) toolbars use build-hashed label classes, not the legacy class `select_stable_tab` was written against |
| `wait_for_dialog_to_close(dialog_text=None, timeout=20000)` | Transient dialogs are **permanent hidden DOM templates** (duplicate elements share the same `role="dialog"` name whether open or closed) — filters on the `:visible` CSS pseudo-class instead of the role locator's attached/hidden state, which would return instantly against the wrong (hidden) copy |

### Layer 4 — Test-level reruns (`pytest-rerunfailures`)

```python
@pytest.mark.flaky(reruns=2, reruns_delay=10)
```
The **last resort**, applied at the test level (5 tests currently, e.g.
`tests/config_tables/test_add_checkpoint_table.py`) only after the above
three layers still don't fully eliminate flakiness against a real,
shared, live environment. Not a substitute for using the right helper
above — see `docs/TROUBLESHOOTING.md` for the exact tests carrying it and
why.

### `utils/wait_utils.py` — written, but not currently wired in

`WaitUtils` provides generic wrappers (`wait_for_visible`, `wait_for_hidden`,
`wait_for_url`, `wait_for_title`, `wait_for_network_idle`, etc.) around raw
Playwright waits, each defaulting to `config.browser["timeout"]` (30000ms).
**Grep confirms zero imports of this class anywhere in `pages/` or
`tests/`** — it's not part of any current page object's actual call path.
Available if a future screen needs a generic wait outside the JET-specific
helpers above, but don't assume it's already exercised by the suite today.

---

## 4. Full `BasePage` Method Reference

Every page object in `pages/` inherits from `pages/base_page.py`. Full,
current method list:

| Method | Signature | What it does |
|---|---|---|
| `open` | `(url)` | `page.goto(url)` |
| `wait` | `()` | `page.wait_for_load_state("networkidle")` |
| `click_by_role` | `(role, name, force=False)` | `get_by_role(role, name=name).click(force=force)` |
| `fill_by_role` | `(role, name, value)` | `get_by_role(role, name=name).fill(value)` |
| `expect_visible_by_role` | `(role, name, timeout=None)` | `expect(get_by_role(...)).to_be_visible()` |
| `expect_visible_by_text` | `(text, timeout=None)` | `expect(get_by_text(text, exact=False).first).to_be_visible()` |
| `expect_visible_by_css` | `(selector, timeout=None)` | `expect(page.locator(selector)).to_be_visible()` |
| `click_tree_item` | `(name, exact=False)` | Click a `role="treeitem"` by accessible name |
| `expand_tree_item` | `(name, exact=False)` | Click, then `press("ArrowRight")` — JET trees select-on-click rather than expand-on-click |
| `expect_tree_item_visible` | `(name, exact=False)` | Visibility assertion on a `role="treeitem"` |
| `click_by_id` | `(element_id)` | Click `#<id>[role='treeitem']` — for tree items with colliding accessible names |
| `expect_visible_by_id` | `(element_id)` | Visibility assertion on the same id-scoped locator |
| `select_stable_tab` | `(name, retries=5, stability_ms=3000, timeout=8000)` | See §3, Layer 3 |
| `select_stable_tab_scoped` | `(scope, name, retries=5, stability_ms=3000, timeout=8000)` | See §3, Layer 3 |
| `select_stable_combobox` | `(combo, option_text, retries=6, open_timeout=3000, settle_timeout=15000)` | See §3, Layer 3 |
| `wait_for_dialog_to_close` | `(dialog_text=None, timeout=20000)` | See §3, Layer 3 |
| `right_click_diagram_node` | `(node_name)` | Right-clicks a `role="img"` node in Designer's JET Diagram canvas — uses accessible name, **not** pixel coordinates, because the diagram re-lays-out nodes after every configuration step |
| `select_cdb_combobox` | `(cdb_name)` | Selects a value in the shared "Choose CDB(in CDB Mode)" combobox (same DOM id `dbdet` on both Supplemental Logging and Assessment) — options render as `role="row"` inside a grid, not `role="option"`; caller must still wait for its own screen-specific settle signal afterward |
| `select_lazy_combobox` | `(combo, option_text, settle_timeout=15000)` | See §3, Layer 3 |

New page objects should check this table **before** writing new raw
`page.get_by_role(...)` interaction code — most Oracle JET quirks
encountered so far are already handled here.

---

## 5. Reporting Integration

| Mechanism | Configured by | Implementation |
|---|---|---|
| HTML report | `pytest.ini` → `addopts` (`--html=reports/html/report.html --self-contained-html`) | `pytest-html` plugin, no custom code |
| Screenshot on failure | Always on, unconditional | `conftest.py`'s `pytest_runtest_makereport` hookwrapper — fires only when `report.when == "call"` and `report.failed`, reads `item.page` (set by the `page` fixture), calls `ScreenshotManager.capture(page, item.name)` |
| Video | `config.yaml` → `reporting.video` | `context` fixture's `record_video_dir` |
| Trace | `config.yaml` → `reporting.trace` | `context` fixture's `context.tracing.start/stop` |
| Log file | Always on, unconditional | `utils/logger.py`'s `Logger.get_logger()` — one timestamped file per pytest process under `reports/logs/`, plus a console `StreamHandler`; guards against duplicate handlers on repeated `get_logger()` calls for the same name |

**A test failing during fixture *setup*** (e.g. login itself throws) never
gets a screenshot — `item.page` isn't set until the `page` fixture
actually runs, and the hook only checks `getattr(item, "page", None)`.
Check `reports/logs/` instead in that case.

---

## 6. Utility Classes — Actually Used vs. Dead Code

Not every class under `utils/` is wired into the live test path. Verified
by grep across `pages/`, `tests/`, and `conftest.py`:

| Class | File | Status |
|---|---|---|
| `Logger` | `utils/logger.py` | **Used** — every page object and `conftest.py` calls `Logger.get_logger(__name__)` |
| `ScreenshotManager` | `utils/screenshot_manager.py` | **Used** — via `conftest.py`'s failure hook. Only `ensure_directory`, `generate_filename`, and `capture` exist on this class |
| `BrowserManager` | `utils/browser_manager.py` | **Used** — by the `browser` fixture |
| `TestData` | `utils/test_data.py` | **Used** — only by `tests/vault/test_add_source_db_alias.py` and `test_delete_source_db_alias.py`, via `TestData.unique_alias()` (timestamp-suffixed alias names, avoids collisions on a real shared environment) |
| `WaitUtils` | `utils/wait_utils.py` | **Not used anywhere** — zero imports outside its own file. See §3 |
| `Assertions` | `utils/assertions.py` | **Not used anywhere** — zero imports outside its own file. **Contains a live bug if ever called**: `verify_title`/`verify_url`/`verify_visible`/`verify_text` all call `ScreenshotManager.take_screenshot(...)` on their failure path, but `ScreenshotManager` has no `take_screenshot` method (only `capture`) — invoking any of these on a real failure would raise `AttributeError` instead of the intended `AssertionError`. Fix before ever wiring this class in. |

---

## 7. Configuration Loading

`config/settings.py`'s `Config` class reads `config/config.yaml` once at
**import time** (module-level `config = Config()` at the bottom of the
file) — every module that does `from config.settings import config` gets
the same already-loaded singleton, not a fresh read per call.

`Config.__init__` unconditionally indexes a fixed set of top-level keys
(`application`, `environment`, `browser`, `urls`, `credentials`,
`secure_vault`, `execution`, `reporting`, `supplemental_logging`,
`designer`, `config_tables`, `initial_load`) — removing/renaming any of
these in `config.yaml` fails the whole suite at collection time with a
`KeyError`, before any test body runs.

`credentials.username`/`password` get overridden post-load if
`MIGDB_USERNAME`/`MIGDB_PASSWORD` are set in the environment (used by
Jenkins — see `docs/CI_CD.md`); every other config section has no
env-var override path.

---

## Assumptions & Gaps

Everything above was verified by reading the actual source files
(`conftest.py`, `pages/base_page.py`, `utils/*.py`, `config/settings.py`,
`pytest.ini`, `requirements.txt`) and cross-checked with `grep` for real
usage — not inferred from typical Playwright/POM conventions. The one
judgment call: **§6's dead-code determination** is based on grepping only
`pages/`, `tests/`, and `conftest.py` — if some other entry point outside
those three folders imports `Assertions`/`WaitUtils`, this document would
need correcting (none was found in this repo).
