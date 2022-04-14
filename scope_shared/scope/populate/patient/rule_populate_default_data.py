import pymongo.database
from typing import List, Optional

import scope.database.patients
from scope.populate.types import PopulateAction, PopulateContext, PopulateRule

ACTION_NAME = "populate_default_data"


class PopulateDefaultData(PopulateRule):
    def match(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> Optional[PopulateAction]:
        # Search for any existing patient who has the desired action pending
        for patient_config_current in populate_config["patients"]["existing"]:
            actions = patient_config_current.get("actions", [])
            if ACTION_NAME in actions:
                return _PopulateDefaultDataAction(
                    patient_id=patient_config_current["patientId"],
                    patient_name=patient_config_current["name"],
                )

        return None


class _PopulateDefaultDataAction(PopulateAction):
    patient_id: str
    patient_name: str

    def __init__(
        self,
        *,
        patient_id: str,
        patient_name: str,
    ):
        self.patient_id = patient_id
        self.patient_name = patient_name

    def prompt(self) -> List[str]:
        return [
            "Populate default data for patient '{}' ({})".format(
                self.patient_name,
                self.patient_id,
            )
        ]

    def perform(
        self,
        *,
        populate_context: PopulateContext,
        populate_config: dict,
    ) -> dict:
        # Get the patient config
        patient_config = None
        for patient_config_current in populate_config["patients"]["existing"]:
            if patient_config_current["patientId"] == self.patient_id:
                patient_config = patient_config_current
                break

        # Confirm we found the patient
        if not patient_config:
            raise ValueError("populate_config was modified")

        # Remove the action from the pending list
        patient_config["actions"].remove(ACTION_NAME)

        # Perform the populate
        _populate_default_data(
            database=populate_context.database,
            patient_config=patient_config,
        )

        return populate_config


def _populate_default_data(
    *,
    database: pymongo.database.Database,
    patient_config: dict,
) -> None:
    """
    Populate the specific documents we want in a "new" patient.
    """

    # Get the patient ID
    patient_id = patient_config["patientId"]

    # Get the patient identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_id,
    )

    # Get the patient collection
    patient_collection = database.get_collection(
        name=patient_identity_document["collection"]
    )

    # Default population is currently None.
    # Rule left in place for future use.
