import pytest

from config.settings import config
from locators.supplemental_logging_locators import SupplementalLoggingLocators


@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.supplemental_logging
def test_enable_schema_trandata(navigation, setup, supplemental_logging):

    domain = config.secure_vault["domain"]
    cdb_alias = config.supplemental_logging["default_cdb"]
    # The "Vault Alias" field on the trandata form relabels to "Choose
    # PDB(in CDB Mode)" once a CDB-root alias is selected above it, and
    # needs its own PDB-level alias to see PDB-local schemas.
    pdb_alias = config.supplemental_logging["pdb_alias"]
    schema = config.supplemental_logging["trandata_schema"]

    navigation.open_navigation_menu()

    setup.open_setup()

    setup.open_supplemental_logging()

    supplemental_logging.verify_page_loaded()

    supplemental_logging.select_cdb(cdb_alias)

    # Add Trandata
    supplemental_logging.open_add_trandata_tab()

    supplemental_logging.select_trandata_target(domain, pdb_alias, schema)

    supplemental_logging.submit_add_trandata()

    supplemental_logging.verify_trandata_result(
        SupplementalLoggingLocators.ENABLE_RESULT_DIALOG,
        schema,
        SupplementalLoggingLocators.ENABLED_STATUS
    )

    # View Trandata
    supplemental_logging.open_view_trandata_tab()

    supplemental_logging.select_trandata_target(domain, pdb_alias, schema)

    supplemental_logging.submit_view_trandata()

    supplemental_logging.verify_trandata_result(
        SupplementalLoggingLocators.VIEW_RESULT_DIALOG,
        schema,
        SupplementalLoggingLocators.ENABLED_STATUS
    )

    # Delete Trandata - restores the schema to its original disabled
    # state so the test cleans up after itself.
    supplemental_logging.open_delete_trandata_tab()

    supplemental_logging.select_trandata_target(domain, pdb_alias, schema)

    supplemental_logging.submit_delete_trandata()

    supplemental_logging.verify_trandata_result(
        SupplementalLoggingLocators.DISABLE_RESULT_DIALOG,
        schema,
        SupplementalLoggingLocators.DISABLED_STATUS
    )
