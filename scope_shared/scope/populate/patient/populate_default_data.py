import copy
import pymongo.database

import scope.database.patient
import scope.database.patients
import scope.enums
import scope.schema

ACTION_NAME = "populate_default_data"


def _ensure_valid(
    *,
    patient_config: dict,
) -> None:
    if "actions" not in patient_config:
        raise ValueError('patient_config["actions"] not found', patient_config)
    if ACTION_NAME not in patient_config["actions"]:
        raise ValueError(
            'ACTION_NAME not found in patient_config["actions"]', patient_config
        )


def populate_default_data(
    *,
    database: pymongo.database.Database,
    patient_config: dict,
) -> dict:
    # Ensure a valid setup
    _ensure_valid(patient_config=patient_config)

    # Get the patient identity document
    patient_identity_document = scope.database.patients.get_patient_identity(
        database=database,
        patient_id=patient_config["patientId"],
    )
    # Get the patient collection
    patient_collection = database.get_collection(
        name=patient_identity_document["collection"]
    )

    # Do the populating
    _populate_default_data(collection=patient_collection)

    # Mark the action complete
    updated_patient_config = copy.deepcopy(patient_config)
    updated_patient_config["actions"].remove(ACTION_NAME)

    return updated_patient_config


def _populate_default_data(
    *,
    collection: pymongo.collection.Collection,
):
    """
    Populate the specific documents we want.
    """

    #
    # Default safety plan
    #
    default_safety_plan_document = scope.database.patient.get_safety_plan(
        collection=collection,
    )
    default_safety_plan_document.update(
        {
            "assigned": True,
            # Preserve original assignedDateTime
        }
    )
    del default_safety_plan_document["_id"]
    scope.database.patient.put_safety_plan(
        collection=collection,
        safety_plan=default_safety_plan_document,
    )

    #
    # Default values inventory
    #
    default_values_inventory = scope.database.patient.get_values_inventory(
        collection=collection,
    )
    default_values_inventory.update(
        {
            "assigned": True,
            # Preserve original assignedDateTime
        }
    )
    del default_values_inventory["_id"]
    scope.database.patient.put_values_inventory(
        collection=collection,
        values_inventory=default_values_inventory,
    )

    # Default assignment of GAD-7 assessment
    default_assessment_gad7 = scope.database.patient.get_assessment(
        collection=collection,
        set_id=scope.enums.AssessmentType.GAD7.value,
    )
    default_assessment_gad7.update(
        {
            "assigned": True,
            # Preserve original assignedDateTime
            "frequency": "Every 2 weeks",
            "dayOfWeek": "Monday",
        }
    )
    del default_assessment_gad7["_id"]
    scope.database.patient.put_assessment(
        collection=collection,
        set_id=scope.enums.AssessmentType.GAD7.value,
        assessment=default_assessment_gad7,
    )

    # Default assignment of PHQ-9 assessment
    default_assessment_phq9 = scope.database.patient.get_assessment(
        collection=collection,
        set_id=scope.enums.AssessmentType.PHQ9.value,
    )
    default_assessment_phq9.update(
        {
            "assigned": True,
            # Preserve original assignedDateTime
            "frequency": "Every 2 weeks",
            "dayOfWeek": "Monday",
        }
    )
    del default_assessment_phq9["_id"]
    scope.database.patient.put_assessment(
        collection=collection,
        set_id=scope.enums.AssessmentType.PHQ9.value,
        assessment=default_assessment_phq9,
    )
