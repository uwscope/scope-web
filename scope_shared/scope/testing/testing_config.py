from dataclasses import dataclass

import scope.config


@dataclass
class TestingConfig:
    """
    Container for all of the configurations that define a testing environment.
    """
    flask_config: scope.config.FlaskConfig
