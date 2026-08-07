import os
import yaml
from pathlib import Path


class Config:
    def __init__(self):
        config_path = Path(__file__).parent / "config.yaml"

        with open(config_path, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

        self.application = self.data["application"]
        self.environment = self.data["environment"]
        self.browser = self.data["browser"]
        self.urls = self.data["urls"]
        self.credentials = self.data["credentials"]

        # Environment variables override config.yaml's plaintext values
        # when present - lets CI (or any local run) inject real
        # credentials via MIGDB_USERNAME/MIGDB_PASSWORD instead of the
        # committed file, without changing local/default behavior for
        # anyone who doesn't set them. See docs/CI_CD.md.
        if os.environ.get("MIGDB_USERNAME"):
            self.credentials["username"] = os.environ["MIGDB_USERNAME"]
        if os.environ.get("MIGDB_PASSWORD"):
            self.credentials["password"] = os.environ["MIGDB_PASSWORD"]

        self.secure_vault = self.data["secure_vault"]
        self.execution = self.data["execution"]
        self.reporting = self.data["reporting"]
        self.supplemental_logging = self.data["supplemental_logging"]
        self.designer = self.data["designer"]
        self.config_tables = self.data["config_tables"]
        self.initial_load = self.data["initial_load"]


config = Config()