class TroubleshootLocators:

    # Confirmed against a live aria snapshot of the Troubleshoot screen
    # (2026-08-06). This screen is a large Integrated Extract/Replicat
    # healthcheck dashboard with ~15 similar "No data to display"
    # tables - only the distinguishing top-level structure is asserted
    # here (mode toolbar, tab strip, key controls, a representative
    # sample of section headings), not every single table.

    INTEGRATED_EXTRACT_TAB = ("radio", "Integrated Extract")
    INTEGRATED_REPLICAT_TAB = ("radio", "Integrated Replicat")
    CLASSIC_REPLICAT_TAB = ("radio", "Classic Replicat")
    PARALLEL_REPLICAT_TAB = ("radio", "Parallel Replicat")

    HEALTHCHECK_TEXT = "Integrated Extract Healthcheck"

    OVERVIEW_TAB = ("tab", "Overview")
    CAPTURE_PROCESSES_TAB = ("tab", "Capture Processes")
    LOGMINER_DETAILS_TAB = ("tab", "LogMiner Details")
    LOGMINER_MEMORY_TAB = ("tab", "LogMiner Memory")

    DATABASE_NAME_COMBOBOX = (
        "combobox",
        "Required Database Name Choose CDB (in CDB Mode)"
    )

    GET_DETAILS_BUTTON = ("button", "Get Details")

    DATABASE_DETAILS_TABLE = ("application", "Database Details")

    CAPTURE_PROCESSES_TABLE = ("application", "Capture Processes")

    LOGMINER_DETAILS_TABLE = ("application", "LogMiner Details")
