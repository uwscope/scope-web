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
    Test that we can get the values inventory for a patient.
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

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}".format(API_RELATIVE_PATH, patient_collection),
        ),
    )

    assert response.ok

    assert response.json() == data_fake_patient["valuesInventory"]


def test_flask_update_patient_values(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
):
    """
    Test that we can update the values inventory for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Generate a fake value inventory
    data_fake_values_inventory = data_fake_values_inventory_factory()

    # Create the patient collection and insert the documents
    patient_collection = scope.database.patients.create_patient_collection(
        database=database_client,
        patient=data_fake_patient,
    )

    # Increment the `v` version of the fake values inventory document
    data_fake_values_inventory["v"] = data_fake_patient["valuesInventory"]["v"] + 1

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient using the _id
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}".format(API_RELATIVE_PATH, patient_collection),
        ),
        json=data_fake_values_inventory,
    )
    assert response.ok
    assert response.json() == data_fake_values_inventory


def test_flask_update_patient_values_duplicate(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_values_inventory_factory: Callable[[], dict],
):
    """
    Test that we cannot update the values inventory for a patient with the same `v` version number.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Generate a fake value inventory
    data_fake_values_inventory = data_fake_values_inventory_factory()

    # Create the patient collection and insert the documents
    patient_collection = scope.database.patients.create_patient_collection(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve the same patient using the _id
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}".format(API_RELATIVE_PATH, patient_collection),
        ),
        json=data_fake_values_inventory,
    )
    assert response.status_code == 422
