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
        self.secure_vault = self.data["secure_vault"]
        self.execution = self.data["execution"]
        self.reporting = self.data["reporting"]
        self.supplemental_logging = self.data["supplemental_logging"]


config = Config()