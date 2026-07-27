import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.dashboard
def test_dashboard(navigation, dashboard):

    navigation.open_navigation_menu()

    dashboard.open_dashboard()

    dashboard.is_dashboard_loaded()

    dashboard.verify_logged_in_user()

    dashboard.verify_dashboard_cards()
