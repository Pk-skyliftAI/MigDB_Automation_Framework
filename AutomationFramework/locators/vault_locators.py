class VaultLocators:

    # Confirmed against a live aria snapshot of the Secure Vault
    # "Add User" screen (2026-07-21), and against a screenshot of the
    # same screen (2026-07-24).

    # --- Action tabs (rendered as radios, not buttons) ---
    ADD_USER_TAB = ("radio", "Add User")
    EDIT_USER_TAB = ("radio", "Edit User")
    DELETE_USER_TAB = ("radio", "Delete User")
    BULK_ADD_TAB = ("radio", "Bulk Add")

    EXISTING_DOMAIN_RADIO = ("radio", "Existing Secure Vault Domain")

    # --- Section headings ---
    VIEW_SECURE_VAULT_HEADING = ("heading", "View Secure Vault")
    ENCRYPTION_KEY_HEADING = ("heading", "Encryption Key")
    MANAGE_SECURE_VAULT_HEADING = ("heading", "Manage Secure Vault")

    # --- Form fields ---
    DOMAIN_COMBOBOX = ("combobox", "Secure Vault Domain")

    ALIAS_TEXTBOX = ("textbox", "Secure Vault Alias")

    USERNAME_TEXTBOX = (
        "textbox",
        "User Name dbusername@dbhostname:dbport/servicename"
    )

    PASSWORD_TEXTBOX = ("textbox", "Password")

    ADD_USER_BUTTON = ("button", "Add User")

    SUCCESS_DIALOG = ("heading", "Add User")

    SUCCESS_MESSAGE = "added successfully to MigDB SecureVault."

    OK_BUTTON = ("button", "OK")

    # --- Encryption key ---
    MASTER_KEY = "ENCRYPTION_MASTERKEY"

    # --- Delete User tab ---
    # Confirmed against a live aria snapshot of the Secure Vault
    # "Delete User" screen (2026-07-26).

    DELETE_ALIAS_COMBOBOX = ("combobox", "Secure Vault Alias")

    DELETE_USERNAME_COMBOBOX = ("combobox", "User Name")

    DELETE_USER_BUTTON = ("button", "Delete User")

    DELETE_CONFIRM_DIALOG = ("dialog", "Delete Secure Vault Domain User")

    YES_BUTTON = ("button", "Yes")

    DELETING_USER_DIALOG = ("dialog", "Deleting User")

    DELETE_SUCCESS_DIALOG = ("heading", "Delete User")

    DELETE_SUCCESS_MESSAGE = "deleted successfully from MigDB SecureVault."

    REFRESHING_VAULT_DIALOG = ("dialog", "Refreshing Secure Vault")