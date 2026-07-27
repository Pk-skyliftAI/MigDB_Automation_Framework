import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.login
@pytest.mark.negative
def test_invalid_login(login):

    login.open_login_page()

    login.login_expecting_failure(
        username="admin",
        password="InvalidPassword123"
    )

    login.is_login_error_displayed()

    login.close_login_error()
