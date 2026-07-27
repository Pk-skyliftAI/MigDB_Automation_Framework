class ConnectionsLocators:

    # Confirmed against a live aria snapshot of the Setup > Connections
    # screen (2026-07-26). Content lags a beat behind the tab selection -
    # wait for ALTER_DATABASE_SECRETS_TEXT before asserting on the rest.

    # --- Alter Database Secrets toolbar/section ---
    ADD_DB_TAB = ("radio", "Add DB")
    EDIT_DB_TAB = ("radio", "Edit DB")
    DELETE_DB_TAB = ("radio", "Delete DB")

    ALTER_DATABASE_SECRETS_TEXT = "Alter Database Secrets"

    SECRETSTORE_ALIAS_TEXTBOX = ("textbox", "Secretstore Alias")

    DATABASE_USERNAME_TEXTBOX = ("textbox", "Database UserName")

    CONNECT_STRING_TEXTBOX = (
        "textbox",
        "Connect String hostname:dbport/dbservice"
    )

    # --- Alter OneP User Secrets toolbar/section ---
    ADD_USER_TAB = ("radio", "Add User")
    EDIT_USER_TAB = ("radio", "Edit User")
    DELETE_USER_TAB = ("radio", "Delete User")

    ALTER_ONEP_USER_SECRETS_TEXT = "Alter OneP User Secrets"

    LOCAL_DEPLOYMENT_RADIO = ("radio", "Local Deployment")
    REMOTE_DEPLOYMENT_RADIO = ("radio", "Remote Deployment")

    ROLE_COMBOBOX = ("combobox", "OnePlace User Role Required Role")
