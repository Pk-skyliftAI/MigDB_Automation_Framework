class DesignerLocators:

    DESIGNER = "Designer"

    CDC_COMPONENTS = "CDC Components"

    ADD = "ADD"

    # Default workflow diagram nodes (rendered as img elements with
    # these accessible names, confirmed against the live app's aria snapshot).
    SOURCE_DEPLOYMENT = "Source Deployment"

    SOURCE_CREDENTIAL_STORE = "Source CredentialStore"

    INTEGRATED_EXTRACT = "Integrated Extract"

    TARGET_DEPLOYMENT = "Target Deployment"

    EXTRACT_PUMP = "Extract Pump"

    TARGET_CREDENTIAL_STORE = "Target CredentialStore"

    CLASSIC_REPLICAT = "Classic Replicat"

    # --- Select Deployment dialog (Source/Target Deployment nodes) ---
    DEPLOYMENT_NAME_COMBOBOX = ("combobox", "Choose Deployment Name")

    # --- Select Source SecretStore dialog (Source CredentialStore node) ---
    # Plain oj-combobox pattern (not searchselect) - options render as
    # role="option".
    SRC_SECRET_DOMAIN_INPUT = "#SRCSecretDomain\\|input"
    SRC_SECRET_ALIAS_INPUT = "#SRCSecretAlias\\|input"

    # oj-searchselect pattern - duplicate-id/filter-input quirk applies,
    # options render as role="row" inside this dropdown container, not
    # role="option". Only appears once a CDB-root alias with a properly
    # registered PDB is selected as the Secret Alias above (see
    # migdb-framework-state memory for the CDC-08223 root cause this
    # depends on).
    SRC_PDB_NAME_INPUT = "#srcpdb\\|input"
    SRC_PDB_NAME_DROPDOWN = "#lovDropdown_srcpdb [role='row']:visible"

    ANALYZE_SELECTED_SCHEMAS_BUTTON = ("button", "Analyze Selected Schemas")
    TABLES_TO_EXCLUDE_HEADING = ("heading", "Tables to Exclude")

    # --- Add Integrated Extract wizard ---
    EXTRACT_NAME_LABEL = "Extract Name"
    TRAIL_NAME_LABEL = "Trail Name"

    # A second, independent PDB field required at submit time (distinct
    # widget/id from SRC_PDB_NAME_INPUT above - don't reuse one for the
    # other). oj-select-single div-based combobox; options render as
    # role="row".
    CHOOSE_PDB_COMBOBOX = ("combobox", "Choose PDB")

    ADD_INTEGRATED_EXTRACT_BUTTON = ("button", "Add Integrated Extract")

    # --- Select Target Deployment dialog (Target Deployment node) ---
    # Identical structure to Source Deployment's dialog - same
    # DEPLOYMENT_NAME_COMBOBOX locator applies.

    # --- Select Target Secrets dialog (Target CredentialStore node) ---
    # Same SRC->TGT naming convention as the source side confirmed live.
    TGT_SECRET_DOMAIN_INPUT = "#TGTSecretDomain\\|input"
    TGT_SECRET_ALIAS_COMBOBOX = ("combobox", "Choose Database Alias")

    # --- Add Extract Pump wizard (Extract Pump node) ---
    # NOTE: field labels confirmed live via a fresh "Add" dialog, but the
    # full submission was NOT exercised (see DesignerPage.add_extract_pump
    # docstring) - RLP1's real pipeline already covers this, and Pump
    # Name/Remote Trail Name likely share the same short-name character
    # limit discovered on Integrated Extract's Extract Name.
    PUMP_NAME_LABEL = "Pump Name"
    REMOTE_TRAIL_NAME_LABEL = "Remote Trail Name"
    ADD_EXTRACT_PUMP_BUTTON = ("button", "Add Extract Pump")

    # --- Add Classic Replicat wizard (Classic Replicat node) ---
    # Same caveat as Extract Pump above - structure confirmed live,
    # submission not exercised.
    REPLICAT_NAME_LABEL = "Replicat Name"
    SOURCE_EXTRACT_LABEL = "Source Extract"
    CHECKPOINT_TABLE_LABEL = "Checkpoint Table"
    ADD_CLASSIC_REPLICAT_BUTTON = ("button", "Add Classic Replicat")