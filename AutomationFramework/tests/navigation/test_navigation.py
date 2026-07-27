import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.navigation
def test_navigation(navigation):

    navigation.open_navigation_menu()

    navigation.verify_navigation_menu()
