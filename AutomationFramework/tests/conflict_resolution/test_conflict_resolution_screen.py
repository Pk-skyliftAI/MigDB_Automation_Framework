import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.conflict_resolution
def test_conflict_resolution_screen_structure(navigation, conflict_resolution):

    navigation.open_navigation_menu()

    conflict_resolution.open_conflict_resolution()

    conflict_resolution.verify_screen_structure()
