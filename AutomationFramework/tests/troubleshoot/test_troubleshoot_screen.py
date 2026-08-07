import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.troubleshoot
def test_troubleshoot_screen_structure(navigation, troubleshoot):

    navigation.open_navigation_menu()

    troubleshoot.open_troubleshoot()

    troubleshoot.verify_screen_structure()
