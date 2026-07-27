import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.parameter_file
def test_parameter_file_screen_structure(navigation, setup, parameter_file):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_parameter_file()

    parameter_file.verify_screen_structure()
