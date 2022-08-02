import copy
import pymongo.database

import scope.database.collection_utils
import scope.database.patient.patient_profile
import scope.database.patients
import scope.schema
import scope.schema_utils as schema_utils


def test_patient_create_get_delete(
    database_client: pymongo.database.Database,
):
    """
    Test that creates and deletes a patient.
    """

    # Create patient
    created_patient_identity = scope.database.patients.create_patient(
        database=database_client,
        patient_name="TEST NAME",
        patient_mrn="TEST MRN",
    )

    try:
        schema_utils.assert_schema(
            data=created_patient_identity,
            schema=scope.schema.patient_identity_schema,
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


def test_patient_ensure_collection_delete(
    database_client: pymongo.database.Database,
):
    """
    Test creation of a patient collection then deletion without ever creating an identity.
    """

    patient_id = "invalid"
    patient_collection_name = scope.database.patients._patient_collection_name(
        patient_id=patient_id
    )

    # Confirm the collection does not already exist
    assert patient_collection_name not in database_client.list_collection_names()

    # Create the collection underlying a patient
    patient_collection = scope.database.patients.ensure_patient_collection(
        database=database_client,
        patient_id=patient_id,
    )

    try:
        # Confirm the collection now exists
        assert patient_collection_name in database_client.list_collection_names()

        # Confirm patient collection sentinel document now exists
        sentinel_document = scope.database.collection_utils.get_singleton(
            collection=patient_collection,
            document_type="sentinel",
        )
        assert sentinel_document is not None
    finally:
        # Delete patient
        result = scope.database.patients.delete_patient(
            database=database_client,
            patient_id=patient_id,
            destructive=True,
        )
        assert result

    # Confirm the collection no longer exists
    assert patient_collection_name not in database_client.list_collection_names()


def test_patient_ensure_reentrant(
    database_client: pymongo.database.Database,
):
    """
    Test that each step in patient creation is reentrant.
    """

    patient_id = "invalid"
    patient_name = "invalid"
    patient_mrn = "invalid"

    try:
        # Do each step multiple times in multiple passes
        patient_collection = scope.database.patients.ensure_patient_collection(
            database=database_client,
            patient_id=patient_id,
        )

        # Outer loop over steps
        for _ in range(3):
            # Create the patient collection
            for _ in range(3):
                patient_collection = scope.database.patients.ensure_patient_collection(
                    database=database_client,
                    patient_id=patient_id,
                )

            # Ensure necessary documents
            for _ in range(3):
                scope.database.patients.ensure_patient_documents(
                    database=database_client,
                    patient_collection=patient_collection,
                    patient_id=patient_id,
                    patient_name=patient_name,
                    patient_mrn=patient_mrn,
                )

            # Create the patient identity document.
            for _ in range(3):
                patient_identity_document = (
                    scope.database.patients.ensure_patient_identity(
                        database=database_client,
                        patient_collection=patient_collection,
                        patient_id=patient_id,
                        patient_name=patient_name,
                        patient_mrn=patient_mrn,
                    )
                )
    finally:
        # Delete patient
        result = scope.database.patients.delete_patient(
            database=database_client,
            patient_id=patient_id,
            destructive=True,
        )
        assert result


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
        patient_name="TEST NAME",
        patient_mrn="TEST MRN",
    )

    try:
        schema_utils.assert_schema(
            data=created_patient_identity,
            schema=scope.schema.patient_identity_schema,
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
