import pytest

from config.settings import config


@pytest.mark.regression
@pytest.mark.designer
def test_add_classic_replicat_apply(navigation, designer):

    designer_config = config.designer

    replicat_name = designer_config["replicat_name"]

    navigation.open_navigation_menu()

    designer.open_monitor()

    # Creating an Extract Pump + Classic Replicat stands up real,
    # persistent GoldenGate processes with no confirmed delete flow, same
    # as Integrated Extract - this test is idempotent: only build the
    # full apply-side pipeline once, then just verify it stays running on
    # every subsequent run.
    if not designer.is_replicat_listed(replicat_name):

        navigation.open_navigation_menu()

        designer.open_designer()

        designer.add_target_deployment(designer_config["deployment_name"])

        designer.add_target_credential_store(
            domain=config.secure_vault["domain"],
            alias=designer_config["target_alias"],
            db_name=designer_config["target_db_name"],
            pdb_name=designer_config["target_pdb_name"]
        )

        designer.add_extract_pump(
            pump_name=designer_config["pump_name"],
            remote_trail_name=designer_config["remote_trail_name"]
        )

        designer.add_classic_replicat(
            replicat_name=replicat_name,
            source_extract=designer_config["pump_name"],
            checkpoint_table=designer_config["checkpoint_table"]
        )

        navigation.open_navigation_menu()

        designer.open_monitor()

    designer.verify_replicat_running(replicat_name)
