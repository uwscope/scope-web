import aws_infrastructure.tasks.ssh
import boto3
import contextlib
from invoke import task
import json
from pathlib import Path
import pymongo
import random
import re
import ruamel.yaml
from typing import List, Union

import scope.config
import scope.database.initialize
import scope.database.patient
import scope.database.patients
import scope.documentdb.client

import scope.populate
import scope.schema
import scope.schema_utils


def _filter_blocklist(
    *,
    blocklist_email_reminder: List[str],
    patient_id: str,
    patient_name: str,
    patient_email: str,
) -> bool:
    # A blocklist item can target any of patient_id, patient_name, or patient_email.
    for block_current in blocklist_email_reminder:
        if re.fullmatch(block_current, patient_id):
            return True
        if re.fullmatch(block_current, patient_name):
            return True
        if re.fullmatch(block_current, patient_email):
            return True

    return False


def _filter_cognito_account_disabled(*, cognito_id: str) -> bool:
    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_userpool = boto_session.client("cognito-idp")

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
    blocklist_email_reminder: List[str],
    template_email_body_reminder: str,
    template_email_body_reminder_testing_header: str,
):
    # Profile contains other information.
    patient_profile = scope.database.patient.get_patient_profile(
        collection=patient_collection
    )

    # Key properties of each patient.
    patient_id = patient_identity["patientId"]
    patient_name = patient_profile["name"]
    patient_email = patient_identity["cognitoAccount"]["email"]

    # Use a summary string for patient output.
    patient_summary = "{} : {} : {}".format(
        patient_id,
        patient_name,
        patient_email,
    )

    # Filter if the patient appears in a block list.
    if _filter_blocklist(
        blocklist_email_reminder=blocklist_email_reminder,
        patient_id=patient_id,
        patient_name=patient_name,
        patient_email=patient_email,
    ):
        return {
            "patient_summary": patient_summary,
            "result": "Blocklist Matched",
        }

    # Filter if the patient Cognito account has been disabled.
    if _filter_cognito_account_disabled(
        cognito_id=patient_identity["cognitoAccount"]["cognitoId"]
    ):
        return {
            "patient_summary": patient_summary,
            "result": "Cognito Account Disabled",
        }

    # Apply an email transformation for testing mode.
    # Specify an email address here during texting.
    destination_email = None
    assert destination_email is not None
    email_body_testing_header = template_email_body_reminder_testing_header.format(
        patient_email=patient_email,
        destination_email=destination_email,
    )

    # Format an email.
    email_body = template_email_body_reminder.format(
        email_body_testing_header=email_body_testing_header,
        patient_email=patient_email,
    )

    # boto will obtain AWS context from environment variables, but will have obtained those at an unknown time.
    # Creating a boto session ensures it uses the current value of AWS configuration environment variables.
    boto_session = boto3.Session()
    boto_ses = boto_session.client("ses")

    response = boto_ses.send_email(
        Source="SCOPE Reminders <do-not-reply@uwscope.org>",
        Destination={
            "ToAddresses": [destination_email],
            # "CcAddresses": ["<email@email.org>"],
        },
        ReplyToAddresses=["do-not-reply@uwscope.org"],
        Message={
            "Subject": {
                "Data": "It's an email.",
                "Charset": "UTF-8",
            },
            "Body": {
                "Html": {
                    "Data": email_body,
                    "Charset": "UTF-8",
                }
            },
        },
    )

    print(response)

    return {
        "patient_summary": patient_summary,
        "result": "Reached End of Function",
    }


def task_email(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    blocklist_email_reminder_path: Union[Path, str],
    template_email_body_reminder_path: Union[Path, str],
    template_email_body_reminder_testing_header_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)
    blocklist_email_reminder = None
    with open(blocklist_email_reminder_path) as config_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        blocklist_email_reminder = yaml.load(config_file)
    template_email_body_reminder = None
    with open(template_email_body_reminder_path, "r") as file_template:
        template_email_body_reminder = file_template.read()
    template_email_body_reminder_testing_header = None
    with open(template_email_body_reminder_testing_header_path, "r") as file_template:
        template_email_body_reminder_testing_header = file_template.read()

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
                    blocklist_email_reminder=blocklist_email_reminder,
                    template_email_body_reminder=template_email_body_reminder,
                    template_email_body_reminder_testing_header=template_email_body_reminder_testing_header,
                )

                # Aggregrate results for output.
                results_existing = results_combined.get(result_current["result"], [])
                results_existing.append(result_current["patient_summary"])
                results_combined[result_current["result"]] = results_existing

        print(json.dumps(results_combined, indent=2))

    email_notifications.__doc__ = email_notifications.__doc__.format(
        database_config.name
    )

    return email_notifications
