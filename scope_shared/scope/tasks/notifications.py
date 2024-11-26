import aws_infrastructure.tasks.ssh
import boto3
import contextlib
from invoke import task
import json
from pathlib import Path
import pymongo
import random
from typing import Union

import scope.config
import scope.database.initialize
import scope.database.patient
import scope.database.patients
import scope.documentdb.client

import scope.populate
import scope.schema
import scope.schema_utils


def _is_cognito_account_disabled(*, cognito_id: str) -> bool:
    # def _reset_cognito_password(
    #     *,
    #     database: pymongo.database.Database,
    #     cognito_config: scope.config.CognitoClientConfig,
    #     account_config: dict,  # Subset of a patient config or a provider config
    # ) -> None:
    #     # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    #     # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    #     boto_session = boto3.Session()
    #     boto_userpool = boto_session.client("cognito-idp")
    #
    #     reset_account_name = account_config["accountName"]
    #     reset_temporary_password = generate_temporary_password()
    #
    #     boto_userpool.admin_set_user_password(
    #         UserPoolId=cognito_config.poolid,
    #         Username=reset_account_name,
    #         Password=reset_temporary_password,
    #         Permanent=False,
    #     )
    #
    #     # Put the temporary password in the config
    #     account_config["temporaryPassword"] = reset_temporary_password

    return random.choice([True, False])


def _patient_email_notification(
    *,
    patient_identity: dict,
    patient_collection: pymongo.collection.Collection,
):
    # Profile contains other information
    patient_profile = scope.database.patient.get_patient_profile(
        collection=patient_collection
    )

    # Use a summary string for patient output
    patient_identity_summary = "{} - {}".format(
        patient_identity["patientId"],
        patient_profile["name"],
    )

    # Determine whether the patient Cognito account has been disabled.
    if _is_cognito_account_disabled(
        cognito_id=patient_identity["cognitoAccount"]["cognitoId"]
    ):
        return ("Cognito Account Disabled", patient_identity_summary)

    # Identify document contains the cognitoAccount
    print(json.dumps(patient_identity, indent=2))

    print(json.dumps(patient_profile, indent=2))

    return ("Reached End of Function", patient_identity_summary)


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

        # Store state about results
        results_combined = {}

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

            # Iterate over every patient
            patients = scope.database.patients.get_patient_identities(database=database)
            for patient_identity_current in patients:
                patient_collection_current = database.get_collection(
                    patient_identity_current["collection"]
                )

                result_current = _patient_email_notification(
                    patient_identity=patient_identity_current,
                    patient_collection=patient_collection_current,
                )

                results_existing = results_combined.get(result_current[0], [])
                results_existing.append(result_current[1])
                results_combined[result_current[0]] = results_existing

        print(json.dumps(results_combined, indent=2))

    email_notifications.__doc__ = email_notifications.__doc__.format(
        database_config.name
    )

    return email_notifications
