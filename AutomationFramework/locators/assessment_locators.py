class AssessmentLocators:

    # Confirmed against a live aria snapshot of the Assessment > Create
    # Job and Assessment > Monitor Job screens (2026-07-26).

    # --- Navigation (parent tree item with Create Job / Monitor Job
    # children, unlike Setup's flat treeitem) ---
    ASSESSMENT_NAV_ITEM = "Assessment"
    CREATE_JOB_NAV_ITEM = "Create Job"
    MONITOR_JOB_NAV_ITEM = "Monitor Job"

    # --- Create Job screen ---
    RUN_ASSESSMENT_BUTTON = ("button", "Run Assessment")

    # Clicking Run Assessment reliably shows this dialog immediately,
    # but it is a false negative: the job continues running in the
    # background and completes successfully seconds later (confirmed
    # against the live app via Monitor Job). Dismiss it, don't fail on it.
    TECHNICAL_ISSUE_DIALOG = ("dialog", "There is a technical issue")

    # --- Monitor Job screen ---
    SELECT_ASSESSMENT_COMBOBOX = ("combobox", "Select Assessment")

    RECOMMENDED_RDS_HEADING = ("heading", "Recommended RDS Instances")
    MIGRATION_BLOCKERS_HEADING = ("heading", "Migration Blockers")
    EXPORT_JSON_BUTTON = ("button", "Export JSON")
    EXPORT_PDF_BUTTON = ("button", "Export PDF")
