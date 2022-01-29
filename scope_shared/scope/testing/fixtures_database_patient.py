import pymongo.database
import pytest
from typing import Callable
from typing import List

import scope.database.patients


@pytest.fixture(name="database_temp_patient_factory")
def fixture_database_temp_patient_factory(
    database_client: pymongo.database.Database,
) -> Callable[[], dict]:  # dict is a patient document
    """
    Fixture for temp_patient_factory.

    Provides a factory for obtaining a patient backed by a corresponding collection.
    Removes any temporary patients that are created by obtained factory.
    """

    # List of patients created by the factory
    temp_patients: List[dict] = []

    # Actual factory for obtaining a client for a temporary Collection.
    def factory() -> dict:  # dict is a patient document
        temp_patient_create = scope.database.patients.create_patient(database=database_client)
        temp_patients.append(temp_patient_create)

        return temp_patient_create

    yield factory

    # Remove any created patients
    for temp_patient_delete in temp_patients:
        scope.database.patients.delete_patient(
            database=database_client,
            patient_id=temp_patient_delete["_set_id"],
            destructive=True,
        )
