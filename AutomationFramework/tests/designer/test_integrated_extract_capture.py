import pytest

from config.settings import config


@pytest.mark.regression
@pytest.mark.designer
def test_add_integrated_extract_capture(navigation, designer):

    designer_config = config.designer

    extract_name = designer_config["extract_name"]

    navigation.open_navigation_menu()

    designer.open_monitor()

    # Creating an Integrated Extract stands up a real, persistent
    # GoldenGate process and trail file on the server - there is no
    # confirmed delete flow for it yet (unlike vault aliases), so this
    # test is idempotent: only build it once, then just verify it stays
    # running on every subsequent run rather than trying to re-add it.
    if not designer.is_extract_listed(extract_name):

        navigation.open_navigation_menu()

        designer.open_designer()

        designer.add_source_deployment(designer_config["deployment_name"])

        designer.add_source_vault(
            domain=config.secure_vault["domain"],
            alias=config.supplemental_logging["default_cdb"],
            pdb_name=designer_config["source_pdb_name"],
            schema=designer_config["capture_schema"]
        )

        designer.analyze_and_confirm_source_vault()

        designer.add_integrated_extract(
            extract_name=extract_name,
            trail_name=designer_config["trail_name"],
            pdb_name=designer_config["source_pdb_name"]
        )

        navigation.open_navigation_menu()

        designer.open_monitor()

    designer.verify_extract_running(extract_name)
