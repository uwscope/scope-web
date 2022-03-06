from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Union


@dataclass(frozen=True)
class CognitoClientConfig:
    """
    Configuration for a AWS Cognito User Pool.

    Excludes internal fields that a client should not access.
    """

    poolid: str
    clientid: str

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return CognitoClientConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return CognitoClientConfig(
            poolid=config_dict["poolid"],
            clientid=config_dict["clientid"],
        )


CognitoConfig = CognitoClientConfig
