import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.logout
def test_logout(dashboard):

    dashboard.logout()
