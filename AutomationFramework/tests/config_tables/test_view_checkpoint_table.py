import pytest

from config.settings import config


@pytest.mark.regression
@pytest.mark.config_tables
def test_view_checkpoint_table(navigation, setup, config_tables):

    checkpoint_config = config.config_tables

    domain = checkpoint_config["checkpoint_domain"]
    alias = checkpoint_config["checkpoint_alias"]
    table_name = checkpoint_config["checkpoint_table_name"]

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_config_tables()

    config_tables.open_checkpoint_view_tab()

    config_tables.view_checkpoint_table(domain, alias, table_name)

    config_tables.verify_checkpoint_table_result(table_name)
