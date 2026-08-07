import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.initial_load
def test_heterogeneous_initial_load_screen_structure(navigation, initial_load):

    navigation.open_navigation_menu()

    initial_load.open_heterogeneous_initial_load()

    initial_load.verify_heterogeneous_screen_structure()
