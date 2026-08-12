class InitialLoadLocators:

    # Homogeneous (Oracle->Oracle) Initial Load - confirmed against a
    # live walkthrough of Setup's sibling "Homogeneous Initial Load" /
    # "Homo Initial Load Monitor" nav items (2026-07-29). There is a
    # separate "Hetrogeneous Initial Load" pair for cross-platform
    # migrations, not used here since this environment is Oracle-only.
    NAV_ITEM = "Homogeneous Initial Load"
    MONITOR_NAV_ITEM = "Homo Initial Load Monitor"

    # New field confirmed live 2026-08-10 (post app-binary update),
    # not previously present - sits above Choose Deployment Name on the
    # DataSource step. Ties to the same "Zero DownTime" feature whose
    # missing conn.db column (dep_priv_url) caused a real backend error
    # earlier this session (see docs/TROUBLESHOOTING.md). Off by
    # default and not required for the existing flow -
    # select_source_deployment/select_source use role+name lookups so
    # this new element's position doesn't affect them - not yet
    # exercised by any test.
    ENABLE_ZERO_DOWNTIME_SWITCH = ("switch", "Enable Zero DownTime")

    DEPLOYMENT_NAME_COMBOBOX = ("combobox", "Choose Deployment Name")

    # Lists vault aliases (not domains). Selecting a CDB-root alias here
    # (e.g. SOURCECDB_ROOT) silently defaults the Source Database
    # Details grid to Oracle's PDB$SEED rather than any real PDB - use a
    # PDB-level alias directly (e.g. SOURCEPDB) instead.
    SOURCE_ALIAS_COMBOBOX = ("combobox", "Choose CDB(in CDB Mode)")

    # These three only appear once a PDB-level source alias is selected
    # above (async, ~5-6s+ with no visible loading indicator).
    SOURCE_PDB_NAME_COMBOBOX = ("combobox", "Choose PDB Name")
    EXPORT_MODE_COMBOBOX = ("combobox", "Choose Export Mode")
    SCHEMA_NAME_COMBOBOX = ("combobox", "Choose Schema Name")

    # Disabled until a schema is chosen above; once enabled it has a
    # strict 4-character max length (GoldenGate-style short-name limit,
    # same family as Designer's 8-char Extract Name limit).
    LOAD_NAME_TEXTBOX = ("textbox", "Load Name")

    # Analyze Selected Schemas only enables once: alias+PDB+schema+Load
    # Name are all set AND the Source Database Details grid row is
    # explicitly clicked (row click alone, before Load Name has a valid
    # value, does not register).
    ANALYZE_SCHEMAS_BUTTON = ("button", "Analyze Selected Schemas")

    TARGET_DEPLOYMENT_COMBOBOX = ("combobox", "Choose Target Deployment")

    # Target's CDB/PDB alias combobox has NO accessible name at all -
    # positional lookup only (it's the last combobox on the page once
    # Target Deployment is chosen). Lists vault aliases directly (e.g.
    # TargetDB) - no separate PDB field like the source side has.

    # Import Options (target/DataPump import) and Export Options
    # (source/DataPump export) are separate dialogs, each gated behind
    # their own button that only enables once its side's row is
    # selected. Both share an identical required "Directory Name"
    # combobox (an Oracle DIRECTORY object, e.g. DATA_PUMP_DIR) that
    # MUST be set and Saved before "Create Job" enables - this is the
    # actual gate, not the row selections themselves.
    IMPORT_OPTIONS_BUTTON = ("button", "Import Options")
    EXPORT_OPTIONS_BUTTON = ("button", "Export Options")
    DIRECTORY_NAME_COMBOBOX = ("combobox", "Directory Name")
    SAVE_BUTTON = ("button", "Save")

    IMPORT_OPTIONS_DIALOG_TEXT = "DataPump Import Options"
    EXPORT_OPTIONS_DIALOG_TEXT = "DataPump Export Options"

    CREATE_JOB_BUTTON = ("button", "Create Job")

    # ---------------------------------------------------------
    # Heterogeneous Initial Load - confirmed against a live aria
    # snapshot (2026-08-06). Structurally similar to Homogeneous's
    # DataSource step but with extra fields (Secret Domain/Secret Alias
    # instead of a plain CDB combobox, Gather Metadata switch, Load
    # Options radiogroup, a table-exclusion picker section) - kept as
    # its own screen-structure check rather than reusing Homogeneous's
    # locators, since the two forms diverge past the first few fields.
    HETERO_NAV_ITEM = "Hetrogeneous Initial Load"

    HETERO_MAIN_HEADING = ("heading", "Initial Load")

    HETERO_SECRET_DOMAIN_COMBOBOX = ("combobox", "Required Secret Domain")

    HETERO_SECRET_ALIAS_COMBOBOX = (
        "combobox",
        "Required Secret Alias Choose CDB(in CDB Mode)"
    )

    HETERO_GATHER_METADATA_SWITCH = ("switch", "Gather Metadata")

    HETERO_LOAD_OPTIONS_RADIOGROUP = ("radiogroup", "Load Options")

    HETERO_TARGET_DEPLOYMENT_COMBOBOX = (
        "combobox",
        "Choose Target Deployment"
    )

    HETERO_CHECKPOINT_TABLE_COMBOBOX = ("combobox", "Checkpoint Table")

    HETERO_DEFER_START_SWITCH = ("switch", "Defer Start")

    HETERO_CREATE_JOB_BUTTON = ("button", "Create Job")

    HETERO_EXCLUDE_TABLES_HEADING = (
        "heading",
        "Select the tables to exclude from Initail Load"
    )

    HETERO_SEARCH_TABLES_TEXTBOX = ("textbox", "Search tables")

    # ---------------------------------------------------------
    # Hetro Initial Load Monitor - confirmed live 2026-08-06. Note the
    # nav item text ("Hetro Initial Load Monitor") differs from the
    # screen's own heading text ("Hetrogeneous Initial Load Monitor") -
    # two distinct strings, not a typo.
    # ---------------------------------------------------------
    HETRO_MONITOR_NAV_ITEM = "Hetro Initial Load Monitor"

    HETRO_MONITOR_HEADING = ("heading", "Hetrogeneous Initial Load Monitor")

    SELECT_LOAD_GROUP_COMBOBOX = (
        "combobox",
        "Select the Initial Load Group"
    )

    HETRO_MONITOR_ACTIONS_BUTTON = ("button", "Actions")

    # ---------------------------------------------------------
    # Homo Initial Load Monitor - confirmed live 2026-08-06. Shares the
    # same "Select the Initial Load Group" combobox as Hetro's monitor.
    # ---------------------------------------------------------
    HOMO_MONITOR_HEADING = ("heading", "Initial Load Monitor")

    RESUMABLE_TASKS_TABLE = ("application", "Resumable Tasks")
