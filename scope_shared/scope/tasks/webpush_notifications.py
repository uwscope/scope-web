import aws_infrastructure.tasks.ssh
import contextlib
from invoke import task
from pathlib import Path
from typing import Union

import scope.config
import scope.database.initialize
import scope.database.database_utils
import scope.database.patient
import scope.documentdb.client
import scope.notifications.messages
import scope.notifications.webpush_handler
import scope.populate
import scope.schema
import scope.schema_utils


def task_webpush_notifications(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    vapid_config_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)
    vapid_config = scope.config.VapidKeysConfig.load(vapid_config_path)

    @task
    def webpush_notifications(context):
        """
        Push the notifications.
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

            patient_collections = scope.database.database_utils.get_patient_collections(
                database=database
            )

            for patient_collection in patient_collections:
                push_subscriptions = scope.database.patient.get_push_subscriptions(
                    collection=patient_collection
                )
                daily_summary = scope.notifications.messages.compute_daily_summary(
                    collection=patient_collection
                )
                if push_subscriptions:
                    for push_subscription in push_subscriptions:
                        webpush_response = scope.notifications.webpush_handler.trigger_push_notification(
                            vapid_config=vapid_config,
                            push_subscription=push_subscription,
                            title="SCOPE Daily Summary",
                            options={"body": daily_summary},
                        )
                        print(webpush_response)
                        # TODO: Store webpush_response in database

    return webpush_notifications
