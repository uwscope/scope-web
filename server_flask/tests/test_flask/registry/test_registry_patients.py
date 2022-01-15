from typing import Callable
from urllib.parse import urljoin

import pymongo.database
import pytest
import requests
import scope.config
import scope.database.patients
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_all_patients(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a list of patients.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all patients
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/",
        ),
    )
    assert response.ok
    assert response.status_code == 200

    for v in data_fake_patient.values():
        # Convert `bson.objectid.ObjectId` to `str`
        if "_id" in v:
            v["_id"] = str(v["_id"])

    for v in data_fake_patient["sessions"]:
        v["_id"] = str(v["_id"])

    for v in data_fake_patient["caseReviews"]:
        v["_id"] = str(v["_id"])

    # "patients" is a list
    response_patients = response.json()["patients"]

    # Ensure list includes our fake patient
    assert data_fake_patient in response_patients

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a patient via patient collection name.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient by sending its collection name
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format(patient_collection_name),
        ),
    )
    assert response.ok
    assert response.status_code == 200

    for v in data_fake_patient.values():
        # Convert `bson.objectid.ObjectId` to `str`
        if "_id" in v:
            v["_id"] = str(v["_id"])

    for v in data_fake_patient["sessions"]:
        v["_id"] = str(v["_id"])

    for v in data_fake_patient["caseReviews"]:
        v["_id"] = str(v["_id"])

    # Ensure body of response is our fake patient
    assert response.json() == data_fake_patient

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient_nonexistent(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that we get a 404 if we try to get a non-existant patient.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Attempt to retrieve the patient using the _id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format("patient_nonexistant"),
        ),
    )
    assert response.status_code == 404  # Not Found


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_create_patient(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can create a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient using the _id
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/",
        ),
        json=data_fake_patient,
    )

    assert response.status_code == 200

    # Ensure body of response is our fake patient collection name
    assert response.json() == patient_collection_name

    # scope.database.patients.delete_patient(
    #    database=database_client,
    #    patient_collection_name=patient_collection_name,
    # )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_patient_405(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we get a 405 if we try to update patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    for v in data_fake_patient.values():
        # Convert `bson.objectid.ObjectId` to `str`
        if "_id" in v:
            v["_id"] = str(v["_id"])
    for v in data_fake_patient["sessions"]:
        v["_id"] = str(v["_id"])
    for v in data_fake_patient["caseReviews"]:
        v["_id"] = str(v["_id"])

    # Update the same patient by sending its collection name
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "patients/{}".format(patient_collection_name),
        ),
        json=data_fake_patient,
    )
    assert response.status_code == 405

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )
