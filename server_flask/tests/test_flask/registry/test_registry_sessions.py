import random
from typing import Callable
from urllib.parse import urljoin

import pymongo.database
import pytest
import requests
import scope.config
import scope.database.patients
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS
API_RELATIVE_PATH = "patients/"

# TODO: This could be renamed better.
API_QUERY_PATH = "sessions"

# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_sessions(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a list of sessions.
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

    # Retrieve all sessions
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
    )
    assert response.ok
    assert response.status_code == 200

    for v in data_fake_patient.values():
        # Convert `bson.objectid.ObjectId` to `str`
        if "_id" in v:
            v["_id"] = str(v["_id"])

    for fake_session in data_fake_patient["sessions"]:
        fake_session["_id"] = str(fake_session["_id"])

    assert data_fake_patient["sessions"] == response.json()

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


def test_flask_get_sessions_404(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that we can get a list of sessions.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all sessions
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, "nonexistent_patient_collection_name", API_QUERY_PATH
            ),
        ),
    )
    assert response.status_code == 404


def test_flask_create_session(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_session_factory: Callable[[], dict],
):
    """
    Test that we can create a session via patient collection name.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()
    data_fake_session = data_fake_session_factory()
    data_fake_session["_session_id"] = "session-%d" % (
        len(data_fake_patient["sessions"]) + 1
    )

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient by sending its collection name
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_session,
    )
    assert response.ok

    response_json = response.json()
    response_json.pop("_id", None)

    assert response_json == data_fake_session


def test_flask_get_sessions_405(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that we get a 405 on method that is not allowed.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all sessions
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, "nonexistent_patient_collection_name", API_QUERY_PATH
            ),
        ),
    )
    assert response.status_code == 405


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_session(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a session using session_id.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    session_document = random.choice(data_fake_patient["sessions"])

    session = flask_session_unauthenticated_factory()

    # Retrieve the session using session_id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}/{}".format(
                API_RELATIVE_PATH,
                patient_collection_name,
                API_QUERY_PATH,
                session_document["_session_id"],
            ),
        ),
    )
    assert response.status_code == 200
    response_json = response.json()
    session_document["_id"] = str(session_document["_id"])

    assert response_json == session_document

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_session(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can update a session using session_id.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    session_document = random.choice(data_fake_patient["sessions"])
    session_document.pop("_id", None)

    session = flask_session_unauthenticated_factory()

    # Retrieve the session using session_id
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}/{}".format(
                API_RELATIVE_PATH,
                patient_collection_name,
                API_QUERY_PATH,
                session_document["_session_id"],
            ),
        ),
        json=session_document,
    )
    assert response.status_code == 200

    session_document["_rev"] += 1
    response_json = response.json()
    response_json.pop("_id", None)

    assert response_json == session_document

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


def test_flask_update_session(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we get a 422 if _id exists in json.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    session_document = random.choice(data_fake_patient["sessions"])
    session_document["_id"] = str(session_document["_id"])

    session = flask_session_unauthenticated_factory()

    # Retrieve the session using session_id
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}/{}".format(
                API_RELATIVE_PATH,
                patient_collection_name,
                API_QUERY_PATH,
                session_document["_session_id"],
            ),
        ),
        json=session_document,
    )
    assert response.status_code == 422
    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )
