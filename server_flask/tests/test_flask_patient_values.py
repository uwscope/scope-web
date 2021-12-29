from typing import Callable
from urllib.parse import urljoin

import pymongo.database
import requests
import scope.config
import scope.database.patients

import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

API_RELATIVE_PATH = "patient/values/"


def test_flask_get_patient_values(
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

    # Create the patient collection and insert the documents
    patient_collection = scope.database.patients.create_patient_collection(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all patients
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}".format(API_RELATIVE_PATH, patient_collection),
        ),
    )

    assert response.ok

    assert response.json() == data_fake_patient["valuesInventory"]


"""
def test_flask_update_patient_values(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):

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
            "patients/{}".format(data_fake_patient["_id"]),
        ),
    )
    assert response.ok

    # Ensure body of response is our fake patient
    assert response.json() == data_fake_patient
"""
