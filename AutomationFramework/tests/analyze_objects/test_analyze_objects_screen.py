import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.analyze_objects
def test_analyze_objects_screen_structure(navigation, analyze_objects):

    navigation.open_navigation_menu()

    analyze_objects.open_analyze_objects()

    analyze_objects.verify_screen_structure()
