import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.manage
def test_manage(navigation, manage):

    navigation.open_navigation_menu()

    manage.open_manage()

    manage.verify_manage_page()
