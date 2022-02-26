import copy

import pymongo.database
import scope.database.patient.patient_profile
import scope.database.patients
import scope.schema
import scope.testing.schema


def test_patient_create_get_delete(
    database_client: pymongo.database.Database,
):
    """
    Test that creates and deletes a patient.
    """

    # Create patient
    created_patient_identity = scope.database.patients.create_patient(
        database=database_client,
        name="TEST NAME",
        MRN="TEST MRN",
    )

    try:
        scope.testing.schema.assert_schema(
            data=created_patient_identity,
            schema=scope.schema.patient_identity_schema,
            expected_valid=True,
        )

        # Confirm get patient identity via _set_id
        retrieved_identity_document = scope.database.patients.get_patient_identity(
            database=database_client,
            patient_id=created_patient_identity["_set_id"],
        )
        assert retrieved_identity_document == created_patient_identity

        # Confirm get patient identity via semantic set id
        retrieved_identity_document = scope.database.patients.get_patient_identity(
            database=database_client,
            patient_id=created_patient_identity[
                scope.database.patients.PATIENT_IDENTITY_SEMANTIC_SET_ID
            ],
        )
        assert retrieved_identity_document == created_patient_identity

        # Confirm patient identity in list of patient identities
        patient_identities = scope.database.patients.get_patient_identities(
            database=database_client
        )
        assert created_patient_identity in patient_identities

        # Confirm patient profile document now exists
        retrieved_profile = scope.database.patient.patient_profile.get_patient_profile(
            collection=database_client.get_collection(
                created_patient_identity["collection"]
            )
        )
        assert retrieved_profile is not None
    finally:
        # Delete patient
        result = scope.database.patients.delete_patient(
            database=database_client,
            patient_id=created_patient_identity["_set_id"],
            destructive=True,
        )
        assert result

    # Confirm get patient identity now fails
    retrieved_identity_document = scope.database.patients.get_patient_identity(
        database=database_client,
        patient_id=created_patient_identity["_set_id"],
    )
    assert retrieved_identity_document is None

    # Confirm patient identity not in list of patient identities
    patient_identities = scope.database.patients.get_patient_identities(
        database=database_client
    )
    if patient_identities:
        assert created_patient_identity not in patient_identities


def test_patient_delete_nonexistent(
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


def test_patient_identity_update(
    database_client: pymongo.database.Database,
):
    """
    Test updating a patient identity.
    """

    # Create patient
    created_patient_identity = scope.database.patients.create_patient(
        database=database_client,
        name="TEST NAME",
        MRN="TEST MRN",
    )

    try:
        scope.testing.schema.assert_schema(
            data=created_patient_identity,
            schema=scope.schema.patient_identity_schema,
            expected_valid=True,
        )

        # Modify the identity
        modified_patient_identity = copy.deepcopy(created_patient_identity)
        modified_patient_identity["name"] = "MODIFIED NAME"
        modified_patient_identity["MRN"] = "MODIFIED MRN"
        del modified_patient_identity["_id"]

        result = scope.database.patients.put_patient_identity(
            database=database_client,
            patient_id=created_patient_identity["_set_id"],
            patient_identity=modified_patient_identity,
        )

        assert result.inserted_count == 1
        assert result.document["_rev"] == 2
    finally:
        scope.database.patients.delete_patient(
            database=database_client,
            patient_id=created_patient_identity["patientId"],
            destructive=True,
        )
