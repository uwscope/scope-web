from dataclasses import dataclass

import scope.config


@dataclass
class TestingConfig:
    flask_config: scope.config.FlaskConfig


DEVELOPMENT_CONFIGS = {
    "development_local": TestingConfig(
        flask_config=scope.config.FlaskConfig(
            baseurl="http://127.0.0.1:4000",
        )
    )
}

ALL_CONFIGS = DEVELOPMENT_CONFIGS
