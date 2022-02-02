from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Optional, Union


@dataclass(frozen=True)
class FlaskConfig:
    """
    Configuration for a Flask instance.

    Includes internal fields the instance will use to configure itself.
    """

    baseurl: str
    secret_key: str
    documentdb_host: str
    documentdb_port: Optional[int]
    documentdb_directconnection: bool
    documentdb_tlsinsecure: bool
    database_name: str
    database_user: str
    database_password: str

    def encode(self) -> dict:
        result = {}
        result["baseurl"] = self.baseurl
        result["secret_key"] = self.secret_key
        result["documentdb"] = {}
        result["documentdb"]["host"] = self.documentdb_host
        if self.documentdb_port:
            result["documentdb"]["port"] = self.documentdb_port
        result["documentdb"]["directconnection"] = self.documentdb_directconnection
        result["documentdb"]["tlsinsecure"] = self.documentdb_tlsinsecure
        result["database"] = {}
        result["database"]["name"] = self.database_name
        result["database"]["user"] = self.database_user
        result["database"]["password"] = self.database_password

        return result

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return FlaskConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return FlaskConfig(
            baseurl=config_dict["baseurl"],
            secret_key=config_dict["secret_key"],
            documentdb_host=config_dict["documentdb"]["host"],
            documentdb_port=config_dict["documentdb"].get("port", None),
            documentdb_directconnection=config_dict["documentdb"]["directconnection"],
            documentdb_tlsinsecure=config_dict["documentdb"]["tlsinsecure"],
            database_name=config_dict["database"]["name"],
            database_user=config_dict["database"]["user"],
            database_password=config_dict["database"]["password"],
        )


@dataclass(frozen=True)
class FlaskClientConfig:
    """
    Configuration for a Flask client.

    Excludes internal fields that a client should not access.
    """

    baseurl: str

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return FlaskClientConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return FlaskClientConfig(
            baseurl=config_dict["baseurl"],
        )
