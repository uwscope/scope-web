from dataclasses import dataclass
import pymongo.database
import pytest
from typing import Callable
from typing import List

import scope.database.patients


@dataclass(frozen=True)
class DatabaseTempPatient:
    patient_id: str
    patient_identity: dict
    collection: pymongo.collection.Collection


@pytest.fixture(name="database_temp_patient_factory")
def fixture_database_temp_patient_factory(
    database_client: pymongo.database.Database,
    data_fake_patient_profile_factory: Callable[[], dict],
) -> Callable[[], DatabaseTempPatient]:
    """
    Fixture for database_temp_patient_factory.

    Provides a factory for obtaining a patient backed by a corresponding collection.
    Removes any temporary patients that are created by obtained factory.
    """

    # List of patients created by the factory
    temp_patients: List[DatabaseTempPatient] = []

    # Actual factory for obtaining a temporary patient.
    def factory() -> DatabaseTempPatient:
        temp_patient_profile = data_fake_patient_profile_factory()
        temp_patient_identity = scope.database.patients.create_patient(
            database=database_client,
            patient_name=temp_patient_profile["name"],
            patient_mrn=temp_patient_profile["MRN"],
        )

        temp_patient = DatabaseTempPatient(
            patient_id=temp_patient_identity["_set_id"],
            patient_identity=temp_patient_identity,
            collection=database_client.get_collection(
                name=temp_patient_identity["collection"]
            ),
        )

        temp_patients.append(temp_patient)

        return temp_patient

    yield factory

    # Remove any created patients
    for temp_patient_delete in temp_patients:
        scope.database.patients.delete_patient(
            database=database_client,
            patient_id=temp_patient_delete.patient_id,
            destructive=True,
        )
