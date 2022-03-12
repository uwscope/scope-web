import aws_infrastructure.tasks.ssh

import scope.config
import scope.testing.testing_config

INSTANCE_SSH_CONFIG = aws_infrastructure.tasks.ssh.SSHConfig.load(
    ssh_config_path="./secrets/configuration/instance_ssh.yaml",
)
DOCUMENTDB_CONFIG = scope.config.DocumentDBConfig.load(
    config_path="./secrets/configuration/documentdb.yaml",
)
DATABASE_DEV_CONFIG = scope.config.DatabaseConfig.load(
    config_path="./secrets/configuration/database_dev.yaml",
)

DATABASE_TESTING_CONFIGS = [
    scope.testing.testing_config.TestingConfig(
        name="database_dev",
        instance_ssh_config=INSTANCE_SSH_CONFIG,
        documentdb_config=DOCUMENTDB_CONFIG,
        database_config=DATABASE_DEV_CONFIG,
        flask_config=None,
    ),
]

DEVELOPMENT_TESTING_CONFIGS = [
    scope.testing.testing_config.TestingConfig(
        name="development_local",
        instance_ssh_config=INSTANCE_SSH_CONFIG,
        documentdb_config=DOCUMENTDB_CONFIG,
        database_config=DATABASE_DEV_CONFIG,
        flask_config=scope.config.FlaskConfig.load(
            config_path="./secrets/configuration/flask_dev_local.yaml",
        ),
    ),
]

UNIQUE_DOCUMENTDB_CONFIGS = [
    DOCUMENTDB_CONFIG,
]

UNIQUE_DATABASE_CONFIGS = [
    DATABASE_DEV_CONFIG,
]
