import scope.config
import scope.testing.testing_config

DEVELOPMENT_CONFIGS = {
    "development_local": scope.testing.testing_config.TestingConfig(
        database_config=scope.config.DatabaseConfig.load(
            config_path="../secrets/configuration/dev_database.yaml",
        ),
        flask_config=scope.config.FlaskConfig.load(
            config_path="../secrets/configuration/dev_local_flask.yaml",
        ),
    )
}

ALL_CONFIGS = DEVELOPMENT_CONFIGS
