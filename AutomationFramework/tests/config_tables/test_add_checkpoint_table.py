import pytest

from config.settings import config


@pytest.mark.regression
@pytest.mark.config_tables
# Same known async-load lag as the Assessment screen and Manager
# Actions menu (no visible loading indicator on the Vault Domain
# combobox, confirmed to occasionally exceed 15s under load during a
# full-suite run 2026-08-06) - compensating control, not a mask for a
# real issue.
@pytest.mark.flaky(reruns=2, reruns_delay=10)
def test_add_checkpoint_table(navigation, setup, config_tables):

    checkpoint_config = config.config_tables

    domain = checkpoint_config["checkpoint_domain"]
    alias = checkpoint_config["checkpoint_alias"]

    # The Add form wants the 2-part "SCHEMA.TABLENAME" (per its own
    # tooltip) - the View tab's fuller "PDB.SCHEMA.TABLENAME" display
    # value only exists once the table is already created.
    table_name = checkpoint_config["checkpoint_table_name"].split(".", 1)[-1]

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_config_tables()

    # Not idempotent like the extract/replicat flows - confirmed live
    # 2026-08-05 that no checkpoint table exists yet on this fresh
    # environment ("ERROR: No Checkpoint Table found" via View), and
    # the View tab's Table Name LOV only lists tables that already
    # exist, so it can't cleanly double as an idempotency check without
    # risking a long hang against a nonexistent option. Re-verify via
    # test_view_checkpoint_table.py before ever re-running this against
    # an environment that might already have the table.
    config_tables.add_checkpoint_table(domain, alias, table_name)

    config_tables.verify_add_checkpoint_result(table_name)
