from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Union


@dataclass(frozen=True)
class DatabaseConfig:
    """
    Configuration for a database.
    """

    name: str
    user: str
    password: str

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return DatabaseConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return DatabaseConfig(
            name=config_dict["name"],
            user=config_dict["user"],
            password=config_dict["password"],
        )
