import pytest

from config.settings import config
from utils.test_data import TestData


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.vault
def test_add_database_alias(navigation, setup, vault):

    alias = TestData.unique_alias()

    alias_data = config.secure_vault["automation_alias"]

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_secure_vault()

    vault.open_add_user_tab()

    vault.add_database_alias(
        alias_name=alias,
        username=alias_data["username"],
        password=alias_data["password"],
        domain=config.secure_vault["domain"]
    )

    vault.verify_add_user_success(alias)

    vault.close_success_dialog()

    vault.refresh_secure_vault_tree(
        config.secure_vault["domain"]
    )

    vault.verify_alias_listed(alias)

    vault.delete_database_alias(
        alias_name=alias,
        username=alias_data["username"],
        domain=config.secure_vault["domain"]
    )

    vault.confirm_delete_alias()

    vault.verify_alias_not_listed(
        alias,
        config.secure_vault["domain"]
    )