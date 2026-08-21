# Test Cases

Every test file under `tests/`, what it covers, and its `pytest` markers
(declared in `pytest.ini`). Most files hold a single test function; where a
file has more than one, both are listed.

`smoke` + `regression` are applied together on almost every test — treat
`pytest -m smoke` as "one representative test per screen" and
`pytest -m regression` as effectively the full suite. Markers with no
`smoke` tag are flows too heavy/state-changing to run in a quick smoke pass
(real form submissions, real infra creation).

Sections below follow the app's real workflow order (also how `conftest.py`'s
`pytest_collection_modifyitems` hook sorts test execution/reporting — see
that file for the authoritative `MODULE_ORDER` list). **Dashboard is last on
purpose**: user-confirmed 2026-08-20 that Dashboard is the summary/final
screen in this app's real workflow (overall migration status), not a landing
page checked first.

## Authentication

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/authentication/test_login.py` | `test_login` | Valid login | `smoke`, `regression`, `login` |
| `tests/authentication/test_invalid_login.py` | `test_invalid_login` | Invalid credentials rejected | `smoke`, `regression`, `login`, `negative` |
| `tests/authentication/test_logout.py` | `test_logout` | Logout flow | `smoke`, `regression`, `logout` |

## Navigation

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/navigation/test_navigation.py` | `test_navigation` | All 17 top-level nav tree items are present | `smoke`, `regression`, `navigation` |

## Secure Vault

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/vault/test_vault_screen_structure.py` | `test_vault_screen_structure` | Secure Vault screen layout | `smoke`, `regression`, `vault` |
| `tests/vault/test_add_source_db_alias.py` | `test_add_database_alias` | Add + delete a database alias (full round trip, self-cleaning) | `smoke`, `regression`, `vault` |
| `tests/vault/test_delete_source_db_alias.py` | `test_delete_database_alias` | Delete-alias flow in isolation | `smoke`, `regression`, `vault` |

## Assessment

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/assessment/test_pre_migration_assessment.py` | `test_pre_migration_assessment` | Create Job + Monitor Job | `smoke`, `regression`, `assessment`, `flaky` |

## Setup > Supplemental Logging

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/supplemental_logging/test_supplemental_logging_screen.py` | `test_supplemental_logging_screen` | Screen structure | `smoke`, `regression`, `supplemental_logging` |
| `tests/supplemental_logging/test_enable_schema_trandata.py` | `test_enable_schema_trandata` | Add → View → Delete Trandata (real DB supplemental logging, self-cleaning) | `smoke`, `regression`, `supplemental_logging` |

## Setup > Parameter File / Connections / Purge CDC Files

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/parameter_file/test_parameter_file_screen.py` | `test_parameter_file_screen_structure` | Screen structure | `smoke`, `regression`, `parameter_file` |
| `tests/connections/test_connections_screen.py` | `test_connections_screen_structure` | Screen structure (Alter Database Secrets / Alter OneP User Secrets) | `smoke`, `regression`, `connections` |
| `tests/purge_cdc_files/test_purge_cdc_files_screen.py` | `test_purge_cdc_files_screen_structure` | Screen structure | `smoke`, `regression`, `purge_cdc_files` |

## Setup > Config Tables

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/config_tables/test_config_tables_screen.py` | `test_config_tables_screen_structure` | Screen structure (CheckpointTable + HeartBeatTable) | `smoke`, `regression`, `config_tables` |
| `tests/config_tables/test_add_checkpoint_table.py` | `test_add_checkpoint_table` | Real checkpoint table creation (not idempotent — see docstring) | `regression`, `config_tables`, `flaky` |
| `tests/config_tables/test_view_checkpoint_table.py` | `test_view_checkpoint_table` | View an existing checkpoint table | `regression`, `config_tables` |
| `tests/config_tables/test_checkpoint_table_upgrade_delete_structure.py` | `test_checkpoint_table_upgrade_delete_structure` | Upgrade/Delete tab structure only (deliberately doesn't submit — acts on the real checkpoint table backing a live replicat) | `regression`, `config_tables`, `flaky` |
| `tests/config_tables/test_heartbeat_table_edit_delete_structure.py` | `test_heartbeat_table_edit_delete_structure` | HeartBeatTable Edit/Delete tab structure only | `regression`, `config_tables`, `flaky` |

## Designer

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/designer/test_designer.py` | `test_designer` | Designer screen loads | `smoke`, `regression`, `designer` |
| `tests/designer/test_integrated_extract_capture.py` | `test_add_integrated_extract_capture` | Capture-side pipeline: Source Deployment → Source CredentialStore → Integrated Extract (idempotent build-once) | `regression`, `designer` |
| `tests/designer/test_classic_replicat_apply.py` | `test_add_classic_replicat_apply` | Apply-side pipeline: Target Deployment → Target CredentialStore → Extract Pump → Classic Replicat (idempotent build-once) | `regression`, `designer` |

## Initial Load

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/initial_load/test_homogeneous_initial_load.py` | `test_create_homogeneous_initial_load` | Full Oracle→Oracle DataPump load job creation (idempotent build-once) | `regression`, `initial_load` |
| `tests/initial_load/test_homo_initial_load_monitor_screen.py` | `test_homo_initial_load_monitor_screen_structure` | Homogeneous monitor screen structure | `smoke`, `regression`, `initial_load` |
| `tests/initial_load/test_heterogeneous_initial_load_screen.py` | `test_heterogeneous_initial_load_screen_structure` | Heterogeneous DataSource form structure | `smoke`, `regression`, `initial_load` |
| `tests/initial_load/test_hetro_initial_load_monitor_screen.py` | `test_hetro_initial_load_monitor_screen_structure` | Heterogeneous monitor screen structure | `smoke`, `regression`, `initial_load` |

## Dataflow

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/dataflow/test_dataflow_screen.py` | `test_dataflow_screen_structure` | Dataflow (Replication flow) screen structure | `smoke`, `regression`, `dataflow` |

## Manage / Monitor

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/manage/test_manage.py` | `test_manage` | Manage screen loads | `smoke`, `regression`, `manage` |
| `tests/manage/test_manager_actions_menu.py` | `test_manager_actions_context_menu` | Manager "Actions" context menu | `regression`, `manage`, `flaky` |
| `tests/monitor/test_monitor.py` | `test_monitor` | Monitor screen (Extracts/Replicats status) | `smoke`, `regression`, `monitor` |

## Conflict Resolution / Analyze / Troubleshoot / LogFile

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/conflict_resolution/test_conflict_resolution_screen.py` | `test_conflict_resolution_screen_structure` | Automatic Conflict Detection & Resolution screen structure | `smoke`, `regression`, `conflict_resolution` |
| `tests/analyze_objects/test_analyze_objects_screen.py` | `test_analyze_objects_screen_structure` | Analyze Objects screen structure (Table/Procedure/Triggers/Function) | `smoke`, `regression`, `analyze_objects` |
| `tests/analyze_trails/test_analyze_trails_screen.py` | `test_analyze_trails_screen_structure` | Analyze Trails (Logdump/Load Balance) screen structure | `smoke`, `regression`, `analyze_trails` |
| `tests/troubleshoot/test_troubleshoot_screen.py` | `test_troubleshoot_screen_structure` | Integrated Extract healthcheck dashboard structure | `smoke`, `regression`, `troubleshoot` |
| `tests/logfile/test_logfile_screen.py` | `test_logfile_screen_structure` | LogFile screen (CDC Error Log/Report Files/Discard Files) structure | `smoke`, `regression`, `logfile` |

## Dashboard (final screen in the workflow)

| File | Test | Covers | Markers |
|---|---|---|---|
| `tests/dashboard/test_dashboard.py` | `test_dashboard` | Dashboard screen loads | `smoke`, `regression`, `dashboard` |

> **Compare Pad removed 2026-08-10**: this screen was removed from the
> application in a binary update (confirmed live — no longer present
> anywhere in the nav tree). Its tests, page object, locators, and
> fixture have been removed from this framework to match.

## Full Marker Reference

From `pytest.ini`:

`smoke`, `regression`, `sanity`, `login`, `logout`, `dashboard`,
`navigation`, `manage`, `monitor`, `designer`, `vault`,
`supplemental_logging`, `parameter_file`, `config_tables`, `connections`,
`purge_cdc_files`, `assessment`, `initial_load`, `dataflow`,
`conflict_resolution`, `analyze_objects`, `analyze_trails`, `troubleshoot`,
`logfile`, `ui`, `negative`

`flaky` above refers to `@pytest.mark.flaky(reruns=2, reruns_delay=10)`
from `pytest-rerunfailures` — used on tests that hit a documented,
non-deterministic UI render/load lag in the application itself (not a
locator bug), as a compensating control rather than a fix.
