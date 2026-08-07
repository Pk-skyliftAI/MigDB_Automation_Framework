class LogFileLocators:

    # Confirmed against a live aria snapshot of the LogFile screen
    # (2026-08-06). "Report Files" is the default sub-tab; its file
    # grid (MGR.rpt/EXDEMO1.rpt/etc) is real live data specific to
    # whatever GoldenGate processes exist on the current environment,
    # so only the grid role itself is asserted, not specific rows.

    CDC_ERROR_LOG_TAB = ("radio", "CDC Error Log")
    REPORT_FILES_TAB = ("radio", "Report Files")
    DISCARD_FILES_TAB = ("radio", "Discard Files")

    REPORT_FILES_HEADING = ("heading", "Report Files")

    SEARCH_TEXTBOX = ("textbox", "Search...")

    FILES_GRID = ("grid", "sticky group header")
