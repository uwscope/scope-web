import datetime

import aws_infrastructure.tasks.ssh
import contextlib
from invoke import task
from pathlib import Path
from typing import Optional, Union
import shutil

import scope.config
import scope.database.initialize
import scope.documentdb.client
import scope.tasks.database_populate


def _reset(
    *,
    instance_ssh_config: aws_infrastructure.tasks.ssh.SSHConfig,
    documentdb_config: scope.config.DocumentDBConfig,
    database_config: scope.config.DatabaseConfig,
    populate_reset: bool,
    populate_dir_path: Optional[Path] = None,
    populate_reset_dir_path: Optional[Path] = None,
):
    """
    Reset a database by:
    - Dropping the existing database.
    - Creating a new database.
    - Initializing that database.
    - Reseting the populate configuration.
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

        #
        # Drop the existing database
        #
        documentdb_client_admin.drop_database(name_or_database=database_config.name)

        #
        # Create a new database
        #
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

        #
        # Initialize the new database
        #
        scope.database.initialize.ensure_database_initialized(database=database)

    #
    # If requested, reset the populate configuration
    #
    if populate_reset:
        shutil.copy(
            src=Path(populate_reset_dir_path, "populate.yaml"),
            dst=Path(
                populate_dir_path,
                "populate_{}.yaml".format(
                    datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%SZ")
                ),
            ),
        )


def task_reset(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    populate_reset: bool,
    populate_dir_path: Optional[Union[Path, str]] = None,
    populate_reset_dir_path: Optional[Union[Path, str]] = None,
):
    if populate_reset:
        if populate_dir_path is None:
            raise ValueError("populate_reset requires populate_dir_path")
        if populate_reset_dir_path is None:
            raise ValueError("populate_reset requires populate_reset_dir_path")

    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseConfig.load(database_config_path)
    if populate_dir_path:
        populate_dir_path = Path(populate_dir_path)
    if populate_reset_dir_path:
        populate_reset_dir_path = Path(populate_reset_dir_path)

    @task
    def reset(context):
        """
        Reset and initialize the {} database.
        """

        database_confirm = input("Confirm database name to reset: ")
        if database_confirm != database_config.name:
            raise ValueError("Database name mismatch.")

        _reset(
            instance_ssh_config=instance_ssh_config,
            documentdb_config=documentdb_config,
            database_config=database_config,
            populate_reset=populate_reset,
            populate_dir_path=populate_dir_path,
            populate_reset_dir_path=populate_reset_dir_path,
        )

    reset.__doc__ = reset.__doc__.format(database_config.name)

    return reset
