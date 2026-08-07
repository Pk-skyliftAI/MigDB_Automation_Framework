import pytest

from config.settings import config


@pytest.mark.regression
@pytest.mark.initial_load
def test_create_homogeneous_initial_load(navigation, initial_load):

    load_config = config.initial_load

    load_name = load_config["load_name"]

    navigation.open_navigation_menu()

    initial_load.open_homo_initial_load_monitor()

    # Creating a load job kicks off a real DataPump export/import against
    # the source and target databases - there is no confirmed delete flow
    # for it, so this test is idempotent: only build it once, then just
    # verify it stays visible in Monitor on every subsequent run.
    if not initial_load.is_load_listed(load_name):

        navigation.open_navigation_menu()

        initial_load.open_homogeneous_initial_load()

        initial_load.select_source_deployment(load_config["deployment_name"])

        initial_load.select_source(
            alias=load_config["source_alias"],
            pdb_name=load_config["source_pdb_name"],
            schema=load_config["schema"],
            load_name=load_name
        )

        initial_load.select_source_db_row(
            load_config["source_db_name"],
            load_config["source_pdb_name"]
        )

        initial_load.analyze_selected_schemas()

        initial_load.select_target(
            load_config["target_deployment_name"],
            load_config["target_alias"]
        )

        initial_load.select_target_db_row(
            load_config["target_db_name"],
            load_config["target_pdb_name"]
        )

        initial_load.configure_import_options(load_config["directory_name"])

        initial_load.configure_export_options(load_config["directory_name"])

        initial_load.create_job()

        navigation.open_navigation_menu()

        initial_load.open_homo_initial_load_monitor()

    initial_load.verify_load_completed(load_name)
