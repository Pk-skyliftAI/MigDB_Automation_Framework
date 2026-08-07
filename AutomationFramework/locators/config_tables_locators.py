class ConfigTablesLocators:

    # Confirmed against a live aria snapshot of the Setup > Config Tables
    # screen (2026-07-26). Content lags a beat behind the tab selection -
    # wait for CHECKPOINT_TABLE_HEADING before asserting on the rest.

    CHECKPOINT_TABLE_HEADING = ("heading", "CheckpointTable")

    HEARTBEAT_TABLE_HEADING = ("heading", "HeartBeatTable")

    # --- Distinctive text (avoids ambiguous locators - "Add" radio and
    # "Choose Vault Alias" combobox each appear once in both sections) ---

    CHECKPOINT_TABLENAME_TEXT = "Checkpoint TableName"

    DIRECTION_TEXT = "UniDirectional or Bi-Directional"

    PARTITIONED_TEXT = "PARTITIONED"

    FREQUENCY_TEXT = "Frequency in Seconds"

    RETENTION_TEXT = "Retention Time in days"

    PURGE_FREQUENCY_TEXT = "Purge Frequency in days"

    ADD_HEARTBEAT_TABLE_BUTTON = ("button", "Add HeartbeatTable")

    # --- CheckpointTable Add flow ---

    ADD_CHECKPOINT_BUTTON = ("button", "Add")

    # --- CheckpointTable sub-tabs and View flow ---

    CHECKPOINT_VIEW_TAB = "View"

    CHECKPOINT_UPGRADE_TAB = "Upgrade"

    CHECKPOINT_DELETE_TAB = "Delete"

    CHECKPOINT_VAULT_ALIAS_COMBOBOX = ("combobox", "Choose Vault Alias")

    VIEW_BUTTON = ("button", "View")

    UPGRADE_BUTTON = ("button", "Upgrade")

    CHECKPOINT_DELETE_BUTTON = ("button", "Delete")

    CHECKPOINT_RESULT_DIALOG = ("dialog", "Checkpoint Table")

    # Upgrade/Delete forms share an identical field layout (Vault Domain,
    # Vault Alias, Table Name) - confirmed via a live aria snapshot of
    # both tabs (2026-08-05) - only the submit button label differs.
    CHECKPOINT_TABLE_NAME_TEXT = "Table Name"

    # --- HeartBeatTable sub-tabs ---

    HEARTBEAT_ADD_TAB = "Add"

    HEARTBEAT_EDIT_TAB = "Edit"

    HEARTBEAT_DELETE_TAB = "Delete"

    SAVE_HEARTBEAT_BUTTON = ("button", "Save HeartbeatTable")

    DELETE_HEARTBEAT_BUTTON = ("button", "Delete HeartbeatTable")
