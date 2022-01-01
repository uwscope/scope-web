import aws_infrastructure.tasks.ssh

import scope.config
import scope.testing.testing_config

INSTANCE_SSH_CONFIG = aws_infrastructure.tasks.ssh.SSHConfig.load(
    ssh_config_path="./secrets/configuration/instance_ssh.yaml",
)

DOCUMENTDB_CONFIG = scope.config.DocumentDBConfig.load(
    config_path="./secrets/configuration/documentdb.yaml",
)

DEV_DATABASE_CONFIG = scope.config.DatabaseConfig.load(
    config_path="./secrets/configuration/dev_database.yaml",
)

DEVELOPMENT_CONFIGS = {
    "development_local": scope.testing.testing_config.TestingConfig(
        instance_ssh_config=INSTANCE_SSH_CONFIG,
        documentdb_config=DOCUMENTDB_CONFIG,
        database_config=DEV_DATABASE_CONFIG,
        flask_config=scope.config.FlaskConfig.load(
            config_path="./secrets/configuration/dev_local_flask.yaml",
        ),
    ),
}

ALL_CONFIGS = DEVELOPMENT_CONFIGS

UNIQUE_DOCUMENTDB_CONFIGS = [
    DOCUMENTDB_CONFIG,
]

UNIQUE_DATABASE_CONFIGS = [
    DEV_DATABASE_CONFIG,
]
