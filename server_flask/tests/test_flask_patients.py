import pymongo.database
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.database.patients
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


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
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all patients
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/",
        ),
    )
    assert response.ok

    # "patients" is a list
    response_patients = response.json()["patients"]

    # Ensure list includes our fake patient
    assert data_fake_patient in response_patients


def test_flask_get_patient(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a patient via object ID.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient using the _id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/{}".format(data_fake_patient["_id"]),
        ),
    )
    assert response.ok

    # Ensure body of response is our fake patient
    assert response.json() == data_fake_patient


def test_flask_get_patient_nonexistent(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a patient via object ID.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Attempt to retrieve the patient using the _id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/{}".format(data_fake_patient["_id"]),
        ),
    )
    assert response.status_code == 404  # Not Found
