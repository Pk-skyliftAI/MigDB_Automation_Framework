import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.login
def test_login(login):

    login.open_login_page()

    login.login()

    login.verify_login_success()
