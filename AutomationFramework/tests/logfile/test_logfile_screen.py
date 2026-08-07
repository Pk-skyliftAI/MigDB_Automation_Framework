import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.logfile
def test_logfile_screen_structure(navigation, logfile):

    navigation.open_navigation_menu()

    logfile.open_logfile()

    logfile.verify_screen_structure()
