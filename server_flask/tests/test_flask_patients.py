from typing import Callable
from urllib.parse import urljoin

import requests
import scope.config
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


def test_flask_get_all_patients(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a list of patients.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Generate a fake patient
    fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/"
        ),
        json=fake_patient,
    )
    assert response.ok

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
    assert fake_patient in response_patients


def test_flask_get_patient(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a patient via object ID.
    """

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Generate a fake patient
    fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/"
        ),
        json=fake_patient,
    )
    assert response.ok

    # Retrieve the same patient using the _id
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "patients_blueprint/{}".format(fake_patient["_id"]),
        ),
    )
    assert response.ok

    # Ensure body of response is our fake patient
    assert response.json() == fake_patient
