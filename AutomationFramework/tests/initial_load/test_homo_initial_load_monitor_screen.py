import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.initial_load
def test_homo_initial_load_monitor_screen_structure(navigation, initial_load):

    navigation.open_navigation_menu()

    initial_load.open_homo_initial_load_monitor()

    initial_load.verify_homo_monitor_screen_structure()
