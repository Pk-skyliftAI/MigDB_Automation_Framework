import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.config_tables
def test_config_tables_screen_structure(navigation, setup, config_tables):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_config_tables()

    config_tables.verify_screen_structure()
