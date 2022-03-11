"""
In addition to its standard singleton properties,
a put to scope.database.patient.patient_profile must maintain the patient identity.
"""

import copy
import pymongo.database
from typing import Callable

import scope.database.patient.patient_profile
import scope.database.patients
import scope.testing.fixtures_database_temp_patient


def test_patient_profile_maintains_identity(
    database_client: pymongo.database.Database,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain and modify a patient profile
    existing_profile_document = (
        scope.database.patient.patient_profile.get_patient_profile(
            collection=patient_collection,
        )
    )

    assert existing_profile_document["name"] != "modified name"
    assert existing_profile_document["MRN"] != "modified MRN"

    modified_profile_document = copy.deepcopy(existing_profile_document)
    modified_profile_document["name"] = "modified name"
    modified_profile_document["MRN"] = "modified MRN"
    del modified_profile_document["_id"]

    scope.database.patient.patient_profile.put_patient_profile(
        database=database_client,
        collection=patient_collection,
        patient_id=temp_patient.patient_id,
        patient_profile=modified_profile_document,
    )

    # Confirm corresponding fields were also modified in patient identity
    modified_identity = scope.database.patients.get_patient_identity(
        database=database_client,
        patient_id=temp_patient.patient_id,
    )

    assert modified_identity["name"] == modified_profile_document["name"]
    assert modified_identity["MRN"] == modified_profile_document["MRN"]
