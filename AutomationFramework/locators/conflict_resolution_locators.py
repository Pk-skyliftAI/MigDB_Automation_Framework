class ConflictResolutionLocators:

    # Confirmed against a live aria snapshot of the Conflict Resolution
    # screen (2026-08-06).

    MAIN_HEADING = (
        "heading",
        "Automatic Conflict Detections and Resolution"
    )

    DEPLOYMENT_COMBOBOX = ("combobox", "Choose Deployment Name")

    CDB_COMBOBOX = ("combobox", "Choose CDB(in CDB Mode)")

    ANALYZE_SCHEMAS_BUTTON = ("button", "Analyze Selected Schemas")

    DB_DETAIL_TABLE = ("application", "DB Detail Table")

    AUTO_CDR_HEADING = ("heading", "Auto CDR")

    ENABLE_TAB = ("radio", "Enable")
    INFO_TAB = ("radio", "Info")
    DISABLE_TAB = ("radio", "Disable")
    EXCEPTIONS_TAB = ("radio", "Exceptions")
    TOMBSTONE_TAB = ("radio", "Tombstone")

    ENABLE_CDR_BUTTON = ("button", "Enable CDR")

    CDR_TABLE_LIST = ("application", "CDR Table List")
