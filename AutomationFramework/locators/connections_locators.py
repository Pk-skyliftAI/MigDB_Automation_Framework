class ConnectionsLocators:

    # Confirmed against a live aria snapshot of the Setup > Connections
    # screen (2026-07-26). Content lags a beat behind the tab selection -
    # wait for ALTER_DATABASE_SECRETS_TEXT before asserting on the rest.

    # --- Alter Database Secrets toolbar/section ---
    ADD_DB_TAB = ("radio", "Add DB")
    EDIT_DB_TAB = ("radio", "Edit DB")
    DELETE_DB_TAB = ("radio", "Delete DB")

    ALTER_DATABASE_SECRETS_TEXT = "Alter Database Secrets"

    # STALE as of 2026-08-10 - kept for reference/in case the app
    # reverts. Confirmed live: the Add DB tab's Secretstore Alias and
    # Database UserName textboxes no longer expose these accessible
    # names at all (plain get_by_role("textbox", name=...) matches
    # nothing) - pages/connections_page.py now uses DOM-order position
    # instead. See docs/TROUBLESHOOTING.md.
    SECRETSTORE_ALIAS_TEXTBOX = ("textbox", "Secretstore Alias")

    DATABASE_USERNAME_TEXTBOX = ("textbox", "Database UserName")

    # Confirmed live 2026-08-11: the textbox's own accessible name is
    # just "hostname:dbport/dbservice" - "Connect String" is a separate,
    # standalone label text node next to it, not part of the field's
    # name. get_by_role(name=...) substring-matches against the
    # element's OWN accessible name only, so the old value (which was
    # longer than the real name) could never match.
    CONNECT_STRING_TEXTBOX = (
        "textbox",
        "hostname:dbport/dbservice"
    )

    # --- Alter OneP User Secrets toolbar/section ---
    ADD_USER_TAB = ("radio", "Add User")
    EDIT_USER_TAB = ("radio", "Edit User")
    DELETE_USER_TAB = ("radio", "Delete User")

    ALTER_ONEP_USER_SECRETS_TEXT = "Alter OneP User Secrets"

    LOCAL_DEPLOYMENT_RADIO = ("radio", "Local Deployment")
    REMOTE_DEPLOYMENT_RADIO = ("radio", "Remote Deployment")

    # STALE as of 2026-08-10 - see note above, same regression.
    ROLE_COMBOBOX = ("combobox", "OnePlace User Role Required Role")
