import aws_infrastructure.tasks.ssh
import contextlib
from invoke import task
from pathlib import Path
from typing import Union

import scope.config
import scope.database.initialize
import scope.documentdb.client


def _initialize(
    *,
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
    database_config: scope.config.DatabaseConfig,
):
    """
    Initialize a database, bringing it from non-existent to our expected state (e.g., it will pass all tests).

    Initialization should be idempotent.
    """

    with contextlib.ExitStack() as context_manager:
        # Connect as cluster admin for database initialization
        documentdb_client_admin = scope.documentdb.client.documentdb_client_admin(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            host=documentdb_config.endpoint,
            port=documentdb_config.port,
            direct_connection=True,
            tls_insecure=True,
            admin_user=documentdb_config.admin_user,
            admin_password=documentdb_config.admin_password,
        )

        scope.database.initialize.ensure_database_exists(
            documentdb_client_admin=documentdb_client_admin,
            database_config=database_config,
        )

    with contextlib.ExitStack() as context_manager:
        # Connect as database user for continued initialization
        database = scope.documentdb.client.documentdb_client_database(
            context_manager=context_manager,
            instance_ssh_config=instance_ssh_config,
            host=documentdb_config.endpoint,
            port=documentdb_config.port,
            direct_connection=True,
            tls_insecure=True,
            database_name=database_config.name,
            user=database_config.user,
            password=database_config.password,
        )

        scope.database.initialize.ensure_database_initialized(database=database)


def task_initialize(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseConfig.load(database_config_path)

    @task
    def initialize(context):
        """
        Initialize the {} database.
        """

        _initialize(
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
            database_config=database_config,
        )

    initialize.__doc__ = initialize.__doc__.format(database_config.name)

    return initialize
