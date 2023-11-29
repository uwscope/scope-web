from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Union


@dataclass(frozen=True)
class VapidKeysConfig:
    """
    Configuration for vapid keys.
    """

    public_key: str
    private_key: str
    claim_email: str

    @staticmethod
    def load(config_path: Union[Path, str]):
        config_path = Path(config_path)

        with open(config_path) as config_file:
            yaml = ruamel.yaml.YAML(typ="safe", pure=True)
            config_dict = yaml.load(config_file)

        return VapidKeysConfig.parse(config_dict)

    @staticmethod
    def parse(config_dict: dict):
        return VapidKeysConfig(
            public_key=config_dict["vapid_public_key"],
            private_key=config_dict["vapid_private_key"],
            claim_email=config_dict["vapid_claim_email"],
        )
