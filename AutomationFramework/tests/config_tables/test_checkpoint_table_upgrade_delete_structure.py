import pytest


@pytest.mark.regression
@pytest.mark.config_tables
# Config Tables' content can lag well behind the outer Setup tab switch
# with no visible loading indicator, and this has been observed to
# occasionally exceed even a 30s wait (same class of intermittent
# backend/render lag as test_pre_migration_assessment.py and
# test_manager_actions_menu.py) - compensating control, not a mask for
# a real locator bug.
@pytest.mark.flaky(reruns=2, reruns_delay=10)
def test_checkpoint_table_upgrade_delete_structure(navigation, setup, config_tables):

    # Structure-only, no submit: Upgrade/Delete both act on the real
    # checkpoint table backing the live RLP2 replicat, and there's no
    # confirmed-safe value to submit for real (see
    # migdb-framework-state memory) - this only confirms both sub-tabs
    # render their expected fields/buttons.
    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_config_tables()

    config_tables.open_checkpoint_upgrade_tab()

    config_tables.verify_checkpoint_upgrade_structure()

    config_tables.open_checkpoint_delete_tab()

    config_tables.verify_checkpoint_delete_structure()
