from typing import Callable

import pymongo.database
import pymongo.errors
import pytest
import scope.database.patients


def test_documentdb_index_singleton_failure_one(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    identity_document = data_fake_patient.get("identity")
    patient_profile_document = data_fake_patient.get("patientProfile")

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=identity_document["name"]
    )

    # Get or create a patients collection
    patients_collection = database_client.get_collection(patient_collection_name)

    # Create unique index on (`type`, `v`)
    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="type_asc_rev_desc",
    )

    patients_collection.create_index(
        [
            ("_session_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        sparse=True,
        unique=True,
        name="sessionId_asc_rev_desc",
    )

    # Insertion succeeds.
    patients_collection.insert_one(document=identity_document)

    try:
        # Insertion fails.
        patients_collection.insert_one(document=patient_profile_document)
    except pymongo.errors.DuplicateKeyError as err:
        # {'index': 0, 'code': 11000, 'errmsg': 'E11000 duplicate key error collection: {patient_collection_name} index: sessionId_asc_rev_desc'}
        # print(err.details)
        # NOTE: "sessionId_asc_rev_desc" index stores "{sessionId": null}" key value pair for identity_document on insertion.

        # Insertion operation on patient_profile_document fails with "DuplicateKeyError" because its index stores {"sessionId": null}. Index "sessionId_asc_rev_desc" doesn't allow that because of uniqueness constraint.

        assert err.code == 11000

    database_client.drop_collection(patient_collection_name)


def test_documentdb_index_singleton_failure_two(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    identity_document = data_fake_patient.get("identity")
    patient_profile_document = data_fake_patient.get("patientProfile")
    patient_profile_document["_rev"] += 1
    clinical_history_document = data_fake_patient.get("clinicalHistory")
    clinical_history_document["_rev"] += 1

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=identity_document["name"]
    )

    # Get or create a patients collection
    patients_collection = database_client.get_collection(patient_collection_name)

    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="type_asc_rev_desc",
    )

    patients_collection.create_index(
        [
            ("_session_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        sparse=True,
        unique=True,
        name="sessionId_asc_rev_desc",
    )

    # Both insertions succeed.
    patients_collection.insert_one(document=identity_document)
    patients_collection.insert_one(document=patient_profile_document)
    try:
        # Insertion fails.
        patients_collection.insert_one(document=clinical_history_document)
    except pymongo.errors.DuplicateKeyError as err:
        # {'index': 0, 'code': 11000, 'errmsg': 'E11000 duplicate key error collection: patient_ade6eaddbb9e7cf7e600282c27310c8e index: sessionId_asc_rev_desc'}
        # print(err.details)
        assert err.code == 11000

    database_client.drop_collection(patient_collection_name)


def test_documentdb_index_sets_failure_one(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    identity_document = data_fake_patient.get("identity")
    patient_profile_document = data_fake_patient.get("patientProfile")
    patient_profile_document["_rev"] += 1
    session_documents = data_fake_patient.get("sessions")

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=identity_document["name"]
    )

    # Get or create a patients collection
    patients_collection = database_client.get_collection(patient_collection_name)

    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="type_asc_rev_desc",
    )

    patients_collection.create_index(
        [
            ("_session_id", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        sparse=True,
        name="sessionId_asc_rev_desc",
    )

    # Both insertions succeed.
    patients_collection.insert_one(document=identity_document)
    patients_collection.insert_one(document=patient_profile_document)
    try:
        # Insertion fails.
        patients_collection.insert_many(documents=session_documents)
    except pymongo.errors.BulkWriteError as err:
        # First element in sessions set will get inserted but the rest of the insertions fail.
        # {'writeErrors': [{'index': 1, 'code': 11000, 'errmsg': 'E11000 duplicate key error collection: {patient_collection_name} index: type_asc_rev_desc', 'op': {'type': 'session', 'sessionId': 'sessionId2', '_rev': 1, 'name': 'Luke Skywalker', '_id': ObjectId('61df9a91e1d17d81f628f650')}}], 'writeConcernErrors': [], 'nInserted': 1, 'nUpserted': 0, 'nMatched': 0, 'nModified': 0, 'nRemoved': 0, 'upserted': []}        print(err.details)
        # print(err.details)
        assert err.code == 65

    database_client.drop_collection(patient_collection_name)


def test_documentdb_index_singleton_passing(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    identity_document = data_fake_patient.get("identity")
    patient_profile_document = data_fake_patient.get("patientProfile")
    patient_profile_document["_rev"] += 1

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=identity_document["name"]
    )

    # Get or create a patients collection
    patients_collection = database_client.get_collection(patient_collection_name)

    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
        ],
        unique=True,
        name="type_asc_rev_desc",
    )

    # Both insertions succeed.
    patients_collection.insert_one(document=identity_document)
    patients_collection.insert_one(document=patient_profile_document)

    database_client.drop_collection(patient_collection_name)


def test_documentdb_index_singleton_and_sets_passing(
    database_client: pymongo.database.Database,
    data_fake_patient_factory: Callable[[], dict],
):
    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    identity_document = data_fake_patient.get("identity")
    patient_profile_document = data_fake_patient.get("patientProfile")
    session_documents = data_fake_patient.get("sessions")

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=identity_document["name"]
    )

    # Get or create a patients collection
    patients_collection = database_client.get_collection(patient_collection_name)

    patients_collection.create_index(
        [
            ("_type", pymongo.ASCENDING),
            ("_rev", pymongo.DESCENDING),
            ("_session_id", pymongo.DESCENDING),
            ("_assessment_id", pymongo.DESCENDING),
        ],
        unique=True,
        name="global_patient_index",
    )

    # All insertions succeed.
    patients_collection.insert_one(document=identity_document)
    patients_collection.insert_one(document=patient_profile_document)
    patients_collection.insert_many(documents=session_documents)

    database_client.drop_collection(patient_collection_name)
