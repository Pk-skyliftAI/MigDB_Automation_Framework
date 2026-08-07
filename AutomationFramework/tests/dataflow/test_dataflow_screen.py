import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.dataflow
def test_dataflow_screen_structure(navigation, dataflow):

    navigation.open_navigation_menu()

    dataflow.open_dataflow()

    dataflow.verify_screen_structure()
