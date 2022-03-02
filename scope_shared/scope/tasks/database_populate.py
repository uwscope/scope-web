import aws_infrastructure.tasks.ssh
import contextlib
import datetime
from invoke import task
from pathlib import Path
import pymongo.database
import re
import ruamel.yaml
from typing import Union

import scope.config
import scope.database.initialize
import scope.documentdb.client
import scope.tasks.populate_fake


def populate_config_current_path(
    *,
    populate_dir_path: Path
) -> Path:
    """
    Obtain the current path for a populate config.

    This will be the config which sorts to the end.
    """

    config_paths = list(populate_dir_path.iterdir())

    filtered_config_paths = []
    for config_path_current in config_paths:
        if (
            config_path_current.is_file() and
            re.fullmatch("populate_(.*).yaml", config_path_current.name)
        ):
            filtered_config_paths.append(config_path_current)
    config_paths = filtered_config_paths

    config_paths = sorted(config_paths, reverse=True)

    return config_paths[0]


def populate_config_generate_path(
    *,
    populate_dir_path: Path
) -> Path:
    """
    Generate a path that should be used to store the current populate configuration.

    This path must have the property that more recent path sort to the end.
    """

    return Path(
        populate_dir_path,
        "populate_{}.yaml".format(
            datetime.datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%SZ")
        )
    )


def populate_from_config(
    *,
    database: pymongo.database.Database,
    populate_config: dict
) -> dict:
    """
    Populate from a provided config.

    Return a new state of the populate config.
    """

    return populate_config


def task_populate(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    populate_dir_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseConfig.load(database_config_path)

    populate_dir_path = Path(populate_dir_path)

    @task
    def populate(context):
        """
        Populate the {} database with fake data.
        """

        populate_config_path = populate_config_current_path(populate_dir_path=populate_dir_path)

        print('Using config "{}".'.format(populate_config_path.name))

        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        populate_config = yaml.load(populate_config_current_path(populate_dir_path=populate_dir_path))

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

            populate_config_update = populate_from_config(
                database=database,
                populate_config=populate_config
            )

        populate_config_update_path = populate_config_generate_path(
            populate_dir_path=populate_dir_path
        )
        with open(populate_config_update_path, "w") as f:
            yaml.dump(populate_config_update, f)

    populate.__doc__ = populate.__doc__.format(database_config.name)

    return populate
