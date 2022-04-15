import aws_infrastructure.tasks.ssh
import contextlib
from invoke import task
from pathlib import Path
from typing import Union

import scope.config
import scope.database.initialize
import scope.documentdb.client
import scope.populate
import scope.schema
import scope.schema_utils


def task_populate(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    cognito_config_path: Union[Path, str],
    populate_dir_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)
    cognito_config = scope.config.CognitoClientConfig.load(cognito_config_path)

    populate_dir_path = Path(populate_dir_path)

    @task
    def populate(context):
        """
        Populate the {} database with fake data.
        """

        # Obtain a database client
        with contextlib.ExitStack() as context_manager:
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

            # Perform the populate
            scope.populate.populate_from_dir(
                database=database,
                cognito_config=cognito_config,
                populate_dir_path=populate_dir_path,
            )

    populate.__doc__ = populate.__doc__.format(database_config.name)

    return populate
