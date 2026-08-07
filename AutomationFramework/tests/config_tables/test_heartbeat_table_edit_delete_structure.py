import pytest


@pytest.mark.regression
@pytest.mark.config_tables
# Same intermittent content-lag race as
# test_checkpoint_table_upgrade_delete_structure.py - see that file's
# comment for detail.
@pytest.mark.flaky(reruns=2, reruns_delay=10)
def test_heartbeat_table_edit_delete_structure(navigation, setup, config_tables):

    # Structure-only, no submit: no HeartBeat table exists yet in this
    # environment to Edit/Delete for real, and Add (already covered by
    # test_config_tables_screen_structure's default-tab check) would
    # create a real one with no confirmed-safe values - this only
    # confirms both sub-tabs render their expected fields/buttons.
    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_config_tables()

    config_tables.open_heartbeat_edit_tab()

    config_tables.verify_heartbeat_edit_structure()

    config_tables.open_heartbeat_delete_tab()

    config_tables.verify_heartbeat_delete_structure()
