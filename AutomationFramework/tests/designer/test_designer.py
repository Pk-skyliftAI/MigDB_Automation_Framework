import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.designer
def test_designer(navigation, designer):

    navigation.open_navigation_menu()

    designer.open_designer()

    designer.verify_designer_loaded()

    designer.verify_default_workflow()
