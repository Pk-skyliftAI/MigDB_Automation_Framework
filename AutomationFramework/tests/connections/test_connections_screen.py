import pytest


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.connections
def test_connections_screen_structure(navigation, setup, connections):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_connections()

    connections.verify_screen_structure()
