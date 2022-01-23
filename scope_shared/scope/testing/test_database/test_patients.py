import pymongo.database
import scope.database.patients


def test_create_get_delete(
    database_client: pymongo.database.Database,
):
    """
    Test that creates and deletes a patient.
    """

    # Create patient
    patient_document = scope.database.patients.create_patient(database=database_client)

    # Confirm get patient
    document = scope.database.patients.get_patient(
        database=database_client,
        patient_id=patient_document["_set_id"],
    )
    assert document == patient_document

    # Confirm patient in list of patients
    patients = scope.database.patients.get_patients(database=database_client)
    assert patient_document in patients

    # Delete patient
    result = scope.database.patients.delete_patient(
        database=database_client,
        patient_id=patient_document["_set_id"],
        destructive=True,
    )
    assert result

    # Confirm get patient fails
    document = scope.database.patients.get_patient(
        database=database_client,
        patient_id=patient_document["_set_id"],
    )
    assert document is None

    # Confirm patient not in list of patients
    patients = scope.database.patients.get_patients(database=database_client)
    assert patient_document not in patients


def test_delete_nonexistent(
    database_client: pymongo.database.Database,
):
    """
    Test that attempts to delete a patient that does not exist.
    """

    # Attempting to delete should fail
    result = scope.database.patients.delete_patient(
        database=database_client,
        patient_id="invalid",
        destructive=True,
    )
    assert not result
