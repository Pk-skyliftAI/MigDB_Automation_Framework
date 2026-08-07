import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.compare_pad
def test_compare_pad_configure_navigation(navigation, compare_pad):

    navigation.open_navigation_menu()

    compare_pad.open_compare_pad_configure()

    compare_pad.verify_navigated("Configure")


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.compare_pad
def test_compare_pad_monitor_navigation(navigation, compare_pad):

    navigation.open_navigation_menu()

    compare_pad.open_compare_pad_monitor()

    compare_pad.verify_navigated("Monitor")
