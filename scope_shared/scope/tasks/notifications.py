from __future__ import annotations

import aws_infrastructure.tasks.ssh
import boto3
import contextlib
from dataclasses import dataclass
from enum import Enum
from invoke import task
import json
from pathlib import Path
import pymongo
import random
import re
import ruamel.yaml
from typing import List, Optional, Union

import scope.config
import scope.database.initialize
import scope.database.patient
import scope.database.patients
import scope.documentdb.client
import scope.documents.document_set

import scope.populate
import scope.schema
import scope.schema_utils


class PatientEmailStatus(Enum):
    IN_PROGRESS = 0

    STOPPED_MATCHED_DENY_LIST = 1
    STOPPED_COGNITO_ACCOUNT_DISABLED = 2
    STOPPED_FAILED_ALLOW_LIST = 3

    REACHED_END_OF_FUNCTION = 10

    EMAIL_SUCCESS = 12


@dataclass(frozen=True)
class PatientEmailData:
    patient_id: str
    patient_name: str
    patient_email: str
    cognito_id: str

    status: PatientEmailStatus

    @property
    def patient_summary(self):
        # Use a summary string for patient output.
        return "{} : {} : {}".format(
            self.patient_id,
            self.patient_name,
            self.patient_email,
        )

    @classmethod
    def from_patient_data(
        cls,
        patient_id: str,
        patient_name: str,
        patient_email: str,
        cognito_id: str,
    ):
        return PatientEmailData(
            patient_id=patient_id,
            patient_name=patient_name,
            patient_email=patient_email,
            cognito_id=cognito_id,
            status=PatientEmailStatus.IN_PROGRESS,
        )

    @classmethod
    def from_status(
        cls,
        current: PatientEmailData,
        status: PatientEmailStatus,
    ):
        return PatientEmailData(
            patient_id=current.patient_id,
            patient_name=current.patient_name,
            patient_email=current.patient_email,
            cognito_id=current.cognito_id,
            status=status,
        )


def _filter_allowlist(
    *,
    allowlist_email_reminder: List[str],
    destination_email: str,
) -> bool:
    # A destination_email must match an element of this list to be allowed.
    for allow_current in allowlist_email_reminder:
        if re.fullmatch(allow_current, destination_email):
            return True

    return False


def _filter_cognito_account_disabled(*, cognito_id: str) -> bool:
    """
    Filter based on whether a Cognito account is disabled.
    :param cognito_id:
    :return: true if enabled, false if disabled.
    """

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
    return True


def _filter_denylist(
    *,
    denylist_email_reminder: List[str],
    patient_email_data: PatientEmailData,
) -> bool:
    """
    Filter based on whether a patient appears in the deny list.
    A patient that matches any element of this list will be denied.
    Matching is by name, patient_id, or email.
    """
    for block_current in denylist_email_reminder:
        if re.fullmatch(block_current, patient_email_data.patient_id):
            return False
        if re.fullmatch(block_current, patient_email_data.patient_name):
            return False
        if re.fullmatch(block_current, patient_email_data.patient_email):
            return False

    return True


def _apply_filter_patient_email_data(
    *,
    patient_email_data: PatientEmailData,
    denylist_email_reminder: List[str],
) -> PatientEmailData:
    """
    Apply all filtering criteria.
    """

    # Filter if the patient appears in a deny list.
    if not _filter_denylist(
        denylist_email_reminder=denylist_email_reminder,
        patient_email_data=patient_email_data,
    ):
        return PatientEmailData.from_status(
            current=patient_email_data,
            status=PatientEmailStatus.STOPPED_MATCHED_DENY_LIST,
        )

    # Filter if the patient Cognito account has been disabled.
    if not _filter_cognito_account_disabled(
        cognito_id=patient_email_data.cognito_id,
    ):
        return PatientEmailData.from_status(
            current=patient_email_data,
            status=PatientEmailStatus.STOPPED_COGNITO_ACCOUNT_DISABLED,
        )

    return patient_email_data


def _patient_email_reminder(
    *,
    patient_email_data: PatientEmailData,
    patient_document_set: scope.documents.document_set.DocumentSet,
    allowlist_email_reminder: List[str],
    denylist_email_reminder: List[str],
    url_base: str,
    template_email_reminder_body: str,
    testing_destination_email: Optional[str],
    template_testing_email_reminder_body_header: str,
) -> PatientEmailData:
    # Filter whether this patient receives an email.
    patient_email_data = _apply_filter_patient_email_data(
        patient_email_data=patient_email_data,
        denylist_email_reminder=denylist_email_reminder,
    )
    if patient_email_data.status != PatientEmailStatus.IN_PROGRESS:
        return patient_email_data

    # Differentiate destination email from the patient email.
    # These will be the same in production, but are differentiated in testing.
    destination_email = patient_email_data.patient_email

    # Apply transformations for testing mode.
    if testing_destination_email:
        # Because we are testing, email will instead go to the testing destination.
        destination_email = testing_destination_email
        # Because we are testing, populate the testing header.
        template_testing_email_reminder_body_header = (
            template_testing_email_reminder_body_header.format(
                destination_email=destination_email,
                patient_email=patient_email_data.patient_email,
            )
        )
    else:
        # Because we are not testing, do not apply the testing header in the email body template.
        template_testing_email_reminder_body_header = ""

    # Ensure the destination_email appears in an allow list.
    if not _filter_allowlist(
        allowlist_email_reminder=allowlist_email_reminder,
        destination_email=destination_email,
    ):
        return PatientEmailData.from_status(
            current=patient_email_data,
            status=PatientEmailStatus.STOPPED_FAILED_ALLOW_LIST,
        )

    # Format an email.
    email_body = template_email_reminder_body.format(
        testing_email_reminder_body_header=template_testing_email_reminder_body_header,
        patient_email=patient_email_data.patient_email,
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

    # print(response)

    return PatientEmailData.from_status(
        current=patient_email_data,
        status=PatientEmailStatus.EMAIL_SUCCESS,
    )


def task_email(
    *,
    instance_ssh_config_path: Union[Path, str],
    documentdb_config_path: Union[Path, str],
    database_config_path: Union[Path, str],
    allowlist_email_reminder_path: Union[Path, str],
    denylist_email_reminder_path: Union[Path, str],
    template_email_body_reminder_path: Union[Path, str],
    template_email_body_reminder_testing_header_path: Union[Path, str],
):
    instance_ssh_config = aws_infrastructure.tasks.ssh.SSHConfig.load(
        instance_ssh_config_path
    )
    documentdb_config = scope.config.DocumentDBClientConfig.load(documentdb_config_path)
    database_config = scope.config.DatabaseClientConfig.load(database_config_path)
    allowlist_email_reminder = None
    with open(allowlist_email_reminder_path, encoding="UTF-8") as config_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        allowlist_email_reminder = yaml.load(config_file)
    denylist_email_reminder = None
    with open(denylist_email_reminder_path, encoding="UTF-8") as config_file:
        yaml = ruamel.yaml.YAML(typ="safe", pure=True)
        denylist_email_reminder = yaml.load(config_file)
    template_email_body_reminder = None
    with open(template_email_body_reminder_path, "r") as file_template:
        template_email_body_reminder = file_template.read()
    template_testing_email_body_reminder_header = None
    with open(template_email_body_reminder_testing_header_path, "r") as file_template:
        template_testing_email_body_reminder_header = file_template.read()

    @task(optional=["production", "testing_destination_email"])
    def email_notifications(context, production=False, testing_destination_email=None):
        """
        Email patient notifications in {} database.
        """

        # Parameters must either:
        # - Explicitly indicate this is a production execution.
        # - Provide a testing_email address to which email will be sent.
        if production:
            if testing_destination_email:
                raise ValueError("-production does not allow -testing-email")
        else:
            if not testing_destination_email:
                raise ValueError("Provide either -production or -testing-email")

        # Determine a URL base for any links included in emails.
        url_base = None
        if database_config.name == "dev":
            url_base = "https://app.dev.uwscope.org/"
        elif database_config.name == "demo":
            url_base = "https://app.demo.uwscope.org/"
        elif database_config.name == "multicare":
            url_base = "https://app.multicare.uwscope.org/"
        elif database_config.name == "scca":
            url_base = "https://app.fredhutch.uwscope.org/"
        else:
            raise ValueError("Unknown database: {}".format(database_config.name))

        # Store state about results.
        patient_email_data_results: List[PatientEmailData] = []

        # Obtain a database client.
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

            # Iterate over every patient.
            patients = scope.database.patients.get_patient_identities(database=database)
            for patient_identity_current in patients:
                # Obtain needed documents for this patient.
                patient_collection = database.get_collection(
                    patient_identity_current["collection"]
                )
                patient_profile = scope.database.patient.get_patient_profile(
                    collection=patient_collection
                )

                result_current = _patient_email_reminder(
                    patient_email_data=PatientEmailData.from_patient_data(
                        patient_id=patient_identity_current["patientId"],
                        patient_name=patient_profile["name"],
                        patient_email=patient_identity_current["cognitoAccount"][
                            "email"
                        ],
                        cognito_id=patient_identity_current["cognitoAccount"][
                            "cognitoId"
                        ],
                    ),
                    patient_document_set=scope.documents.document_set.DocumentSet(
                        documents=patient_collection.find()
                    ),
                    allowlist_email_reminder=allowlist_email_reminder,
                    denylist_email_reminder=denylist_email_reminder,
                    url_base=url_base,
                    template_email_reminder_body=template_email_body_reminder,
                    testing_destination_email=testing_destination_email,
                    template_testing_email_reminder_body_header=template_testing_email_body_reminder_header,
                )

                # Store the result
                patient_email_data_results.append(result_current)

        for status_current in PatientEmailStatus:
            matching_results = [
                patient_email_data
                for patient_email_data in patient_email_data_results
                if patient_email_data.status == status_current
            ]

            if len(matching_results) > 0:
                print(status_current.name)
                for patient_email_data in matching_results:
                    print("  {}".format(patient_email_data.patient_summary))
                print()

        # print(json.dumps(patient_email_data_results, indent=2))

    email_notifications.__doc__ = email_notifications.__doc__.format(
        database_config.name
    )

    return email_notifications
