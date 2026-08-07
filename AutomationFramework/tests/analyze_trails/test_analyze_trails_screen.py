import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.analyze_trails
def test_analyze_trails_screen_structure(navigation, analyze_trails):

    navigation.open_navigation_menu()

    analyze_trails.open_analyze_trails()

    analyze_trails.verify_screen_structure()
