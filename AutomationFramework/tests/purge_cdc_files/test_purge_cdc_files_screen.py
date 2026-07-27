import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.purge_cdc_files
def test_purge_cdc_files_screen_structure(navigation, setup, purge_cdc_files):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_purge_cdc_files()

    purge_cdc_files.verify_screen_structure()
