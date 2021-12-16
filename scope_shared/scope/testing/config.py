from dataclasses import dataclass
import os
from pathlib import Path
from typing import Union

import scope.config


@dataclass
class TestingConfig:
    """
    Container for all of the configurations that define a testing environment.
    """
    flask_config: scope.config.FlaskConfig


def project_relative_path(config_path: Union[Path, str]) -> Path:
    """
    Utility for computing relative path to configuration files.

    Needed because paths are used across multiple test environments with different working directories.
    """

    # Find the project root
    project_path = Path.cwd()
    while project_path.name != "scope-web":
        project_path = project_path.parent

    # Find a path from our current working directory to the root
    project_root_path = os.path.relpath(project_path, Path.cwd())

    # Combine the two in a path that goes to the project root and then to the config
    return Path(project_root_path, config_path)


DEVELOPMENT_CONFIGS = {
    "development_local": TestingConfig(
        flask_config=scope.config.FlaskConfig.load(
            config_path=project_relative_path("./secrets/configuration/dev_local_flask.yaml"),
        )
    )
}

ALL_CONFIGS = DEVELOPMENT_CONFIGS
