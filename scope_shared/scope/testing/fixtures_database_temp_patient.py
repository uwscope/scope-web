from dataclasses import dataclass
import pymongo.collection
import pymongo.database
import pytest
from typing import Callable
from typing import List

import scope.database.patients


@dataclass(frozen=True)
class DatabaseTempPatient:
    patient_id: str
    patient_document: dict
    collection: pymongo.collection.Collection


@pytest.fixture(name="database_temp_patient_factory")
def fixture_database_temp_patient_factory(
    database_client: pymongo.database.Database,
) -> Callable[[], DatabaseTempPatient]:
    """
    Fixture for temp_patient_factory.

    Provides a factory for obtaining a patient backed by a corresponding collection.
    Removes any temporary patients that are created by obtained factory.
    """

    # List of patients created by the factory
    temp_patients: List[DatabaseTempPatient] = []

    # Actual factory for obtaining a client for a temporary Collection.
    def factory() -> DatabaseTempPatient:
        temp_patient_document_create = scope.database.patients.create_patient(database=database_client)
        temp_patient = DatabaseTempPatient(
            patient_id=temp_patient_document_create["_set_id"],
            patient_document=temp_patient_document_create,
            collection=database_client.get_collection(
                name=temp_patient_document_create["collection"]
            )
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
