from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import List
from typing import Union


@dataclass(frozen=True)
class DocumentDBConfig:
    """
    Configuration for a DocumentDB cluster.

    Includes internal fields used for configuration.
    """

    admin_user: str
    admin_password: str
    endpoint: str
    hosts: List[str]
    port: int

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return DocumentDBConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return DocumentDBConfig(
            admin_user=config_dict["admin_user"],
            admin_password=config_dict["admin_password"],
            endpoint=config_dict["endpoint"],
            hosts=config_dict["hosts"],
            port=config_dict["port"],
        )


@dataclass(frozen=True)
class DocumentDBClientConfig:
    """
    Configuration for a DocumentDB cluster.

    Excludes internal fields that a client should not access.
    """

    endpoint: str
    hosts: List[str]
    port: int

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return DocumentDBClientConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return DocumentDBClientConfig(
            endpoint=config_dict["endpoint"],
            hosts=config_dict["hosts"],
            port=config_dict["port"],
        )
