class SupplementalLoggingLocators:

    # Page
    CHOOSE_CDB = "Choose CDB(in CDB Mode)"
    DATABASE_CHECKS = "Database Checks"

    # Toolbar
    ADD_TRANDATA = ("radio", "Add Trandata")
    VIEW_TRANDATA = ("radio", "View Trandata")
    DELETE_TRANDATA = ("radio", "Delete Trandata")

    # Choose CDB combobox handled by BasePage.select_cdb_combobox()
    # (shared with Assessment - same DOM id "dbdet" on both screens).

    ENABLE_DISABLE_TRANDATA_HEADING = ("heading", "Enable/Disable Trandata")

    # --- Add/View/Delete Trandata form (identical fields on all three
    # tabs) - confirmed against live aria snapshots (2026-07-26) ---

    # "Vault Domain" combobox briefly carries a "Loading domains" suffix
    # in its accessible name while its options fetch asynchronously, so
    # exact=True is used as the settle signal (it only matches once the
    # suffix clears).
    VAULT_DOMAIN_COMBOBOX = ("combobox", "Vault Domain")

    VAULT_ALIAS_COMBOBOX = (
        "combobox",
        "Vault Alias Choose PDB(in CDB Mode)"
    )

    # The Schema Name field is another oj-select-single (like the CDB
    # combobox): a duplicate hidden-template shares its id, and once
    # opened a separate filter <input> (a different id) takes over
    # keyboard input; options render as role="row" inside a grid.
    SCHEMA_NAME_INPUT_ID = "schema|input"
    SCHEMA_NAME_FILTER_INPUT_ID = "oj-searchselect-filter-schema|input"
    SCHEMA_NAME_DROPDOWN_ID = "lovDropdown_schema"

    ADD_SCHEMA_TRANDATA_BUTTON = ("button", "Add SchemaTrandata")
    VIEW_SCHEMA_TRANDATA_BUTTON = ("button", "View SchemaTrandata")
    DELETE_SCHEMA_TRANDATA_BUTTON = ("button", "Delete SchemaTrandata")

    DELETE_CONFIRM_DIALOG = ("dialog", "Delete Supplemental Logging")
    YES_BUTTON = ("button", "Yes")

    ENABLE_RESULT_DIALOG = ("dialog", "Enable Supplemental Logging")
    VIEW_RESULT_DIALOG = ("dialog", "View Supplemental Logging")
    DISABLE_RESULT_DIALOG = ("dialog", "Disable Supplemental Logging")

    OK_BUTTON = ("button", "OK")

    ENABLED_STATUS = "Enabled"
    DISABLED_STATUS = "Disabled"