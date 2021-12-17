import aws_infrastructure.tasks.ssh
from dataclasses import dataclass

import scope.config


@dataclass
class TestingConfig:
    """
    Container for all of the configurations that define a testing environment.
    """
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig
    documentdb_config: scope.config.DocumentDBConfig
    database_config: scope.config.DatabaseConfig
    flask_config: scope.config.FlaskConfig
