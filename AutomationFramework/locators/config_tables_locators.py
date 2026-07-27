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
