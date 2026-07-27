import pytest

from config.settings import config


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.vault
def test_vault_screen_structure(navigation, setup, vault):

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_secure_vault()

    vault.verify_secure_vault_page()

    vault.verify_existing_aliases(
        config.secure_vault["existing_aliases"],
        config.secure_vault["domain"]
    )

    vault.verify_action_buttons()

    vault.verify_encryption_key()