from dataclasses import dataclass
from pathlib import Path
import ruamel.yaml
from typing import Union


@dataclass(frozen=True)
class FlaskConfig:
    """
    Configuration for a Flask instance.

    Includes internal fields the instance will use to configure itself.
    """

    baseurl: str


@dataclass(frozen=True)
class FlaskClientConfig:
    """
    Configuration for a Flask client.

    Excludes internal fields that a client should not access.
    """

    baseurl: str
