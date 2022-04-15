import copy
from typing import List, Optional

import scope.enums
import scope.database.patients
import scope.populate.patient.rule_populate_default_data
import scope.populate.patient.rule_update_patient_identity_cognito_account
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule
import scope.testing.fake_data.fixtures_fake_provider_identity


class CreatePatient(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # If there is any patient to be created, create the first patient.
        # Later steps will use patientId, but that does not yet exist.
        if len(populate_config["patients"]["create"]) > 0:
            return _CreatePatientAction(
                patient_name=populate_config["patients"]["create"][0]["name"]
            )

        return None


class _CreatePatientAction(PopulateAction):
    patient_name: str

    def __init__(
        self,
        *,
        patient_name: str,
    ):
        self.patient_name = patient_name

    def prompt(self) -> List[str]:
        return ["Create patient '{}'".format(self.patient_name)]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the patient config
        patient_config = populate_config["patients"]["create"][0]

        # Confirm the patient name matches what we expect
        if patient_config["name"] != self.patient_name:
            raise ValueError("populate_config was modified")

        # Remove the patient from the create list
        del populate_config["patients"]["create"][0]

        # Create the patient
        patient_identity_document = scope.database.patients.create_patient(
            database=populate_context.database,
            patient_name=patient_config["name"],
            patient_mrn=patient_config["MRN"],
        )

        # Update the patient config
        patient_config.update(
            {
                "patientId": patient_identity_document[
                    scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
                ],
            }
        )

        # Specify follow-up actions
        actions = patient_config.get("actions", [])

        # All new patients require default data
        actions = actions + [
            scope.populate.patient.rule_populate_default_data.ACTION_NAME,
        ]

        # New patients with an account must have identity updated for that account.
        # Note the account might not exist yet,
        # but queue up the action and rely on rules to create the account first.
        if "account" in patient_config:
            actions = actions + [
                scope.populate.patient.rule_update_patient_identity_cognito_account.ACTION_NAME
            ]

        # Store the updated actions
        patient_config["actions"] = actions

        # Add the created patient to the config
        populate_config["patients"]["existing"].append(patient_config)

        return populate_config
