import pytest

from config.settings import config


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.assessment
def test_pre_migration_assessment(navigation, assessment):

    alias = config.supplemental_logging["default_cdb"]

    navigation.open_navigation_menu()

    assessment.open_create_job()

    assessment.select_cdb(alias)

    assessment.run_assessment()

    navigation.open_navigation_menu()

    assessment.open_monitor_job()

    assessment.open_assessment_job(f"{alias}_")

    assessment.verify_assessment_completed()
