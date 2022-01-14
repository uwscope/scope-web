from typing import Callable

import pymongo.database
import pymongo.errors
import pytest
import scope.database.patients

# NOTE: This file can be deleted at some point. Keeping it here for reference.


@pytest.mark.skip(
    reason="fixture for fake patient data and scope.database.patients have changed"
)
def test_patients_create_get_delete(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that creates, retrieves, and deletes a patient document.
    """

    # Obtain data for a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Confirm the fake patient cannot be directly retrieved
    patient = scope.database.patients.get_patient(
        database=database_client,
        id=data_fake_patient["_id"],
    )
    assert patient is None

    # Confirm the fake patient is not in our list of patients
    patients = scope.database.patients.get_patients(
        database=database_client,
    )
    assert data_fake_patient not in patients

    # Insert the fake patient
    result = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    assert result.inserted_id == data_fake_patient["_id"]

    # Confirm the fake patient can be directly retrieved
    patient = scope.database.patients.get_patient(
        database=database_client,
        id=data_fake_patient["_id"],
    )
    assert patient is not None

    # Confirm the fake patient is in our list of patients
    patients = scope.database.patients.get_patients(
        database=database_client,
    )
    assert data_fake_patient in patients

    # Delete the fake patient
    result = scope.database.patients.delete_patient(
        database=database_client, id=data_fake_patient["_id"]
    )
    assert result.deleted_count == 1

    # Confirm the fake patient cannot be directly retrieved
    patient = scope.database.patients.get_patient(
        database=database_client,
        id=data_fake_patient["_id"],
    )
    assert patient is None

    # Confirm the fake patient is not in our list of patients
    patients = scope.database.patients.get_patients(
        database=database_client,
    )
    assert data_fake_patient not in patients


@pytest.mark.skip(
    reason="fixture for fake patient data and scope.database.patients have changed"
)
def test_patients_create_existing(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that attempts to create a patient that already exists.
    """

    # Obtain data for a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Insert the fake patient again, should fail because patient already exists
    with pytest.raises(pymongo.errors.DuplicateKeyError):
        scope.database.patients.create_patient(
            database=database_client,
            patient=data_fake_patient,
        )


@pytest.mark.skip(
    reason="fixture for fake patient data and scope.database.patients have changed"
)
def test_patients_delete_nonexistent(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that attempts to delete a patient that does not exist.
    """

    # Obtain data for a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Delete the fake patient
    result = scope.database.patients.delete_patient(
        database=database_client, id=data_fake_patient["_id"]
    )
    assert result.deleted_count == 0
