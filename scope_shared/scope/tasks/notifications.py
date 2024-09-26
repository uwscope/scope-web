import contextlib
from pathlib import Path
from typing import Union
import aws_infrastructure.tasks.ssh
from invoke import task

import scope.config
import scope.database.initialize
import scope.database.patient
import scope.database.patients
import scope.documentdb.client

import scope.populate
import scope.schema
import scope.schema_utils


def task_email(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)

    @task
    def email_notifications(context):
        """
        Email patient notifications in {} database.
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

            patient_collections = scope.database.patients.get_patient_collections(
                database=database
            )

            for patient_collection in patient_collections:
                patient_profile = scope.database.patient.get_patient_profile(
                    collection=patient_collection
                )
                print(patient_profile.get("name"))

    email_notifications.__doc__ = email_notifications.__doc__.format(
        database_config.name
    )

    return email_notifications
