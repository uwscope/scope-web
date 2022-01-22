import aws_infrastructure.tasks.ssh
from invoke import task
from pathlib import Path
from typing import Union

import scope.config
import scope.database.initialize


def task_initialize(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(instance_ssh_config_path)
    documentdb_config = scope.config.DocumentDBConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseConfig.load(database_config_path)

    @task
    def initialize(context):
        """
        Initialize the {} database.
        """

        scope.database.initialize.initialize(
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
            database_config=database_config,
        )

    initialize.__doc__ = initialize.__doc__.format(database_config.name)

    return initialize


def task_reset(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(instance_ssh_config_path)
    documentdb_config = scope.config.DocumentDBConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseConfig.load(database_config_path)

    @task
    def reset(context):
        """
        Reset and initialize the {} database.
        """

        scope.database.initialize.reset(
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
            database_config=database_config,
        )

    reset.__doc__ = reset.__doc__.format(database_config.name)

    return reset
