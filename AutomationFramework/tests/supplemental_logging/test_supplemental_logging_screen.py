import pytest
from config.settings import config


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.supplemental_logging
def test_supplemental_logging_screen(

    navigation,
    setup,
    supplemental_logging

):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_supplemental_logging()

    supplemental_logging.verify_page_loaded()

    supplemental_logging.select_cdb(
        config.supplemental_logging["default_cdb"]
    )

    supplemental_logging.verify_action_buttons()