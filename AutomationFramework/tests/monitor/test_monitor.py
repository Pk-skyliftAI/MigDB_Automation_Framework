import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.monitor
def test_monitor(navigation, monitor):

    navigation.open_navigation_menu()

    monitor.open_monitor()

    monitor.verify_monitor_page()
