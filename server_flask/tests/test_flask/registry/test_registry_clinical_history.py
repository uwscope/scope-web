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
API_QUERY_PATH = "clinicalhistory"

# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient_clinical_history(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test to get the clinical history for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # GET /patient/values/patient_{identityId}
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
    )

    for v in data_fake_patient.values():
        # Convert `bson.objectid.ObjectId` to `str`
        if "_id" in v:
            v["_id"] = str(v["_id"])

    assert response.ok

    assert response.json() == data_fake_patient["clinicalHistory"]

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_patient_clinical_history(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_clinical_history_factory: Callable[[], dict],
):
    """
    Test that we can update the clinical history for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Generate a fake clinical history
    data_fake_values_inventory = data_fake_clinical_history_factory()

    # Create the patient collection and insert the documents
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Updates the same patient's values inventory
    # PUT /patient/values/patient_{identityId} -
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_values_inventory,
    )
    assert response.ok

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_patient_clinical_history_duplicate(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we cannot update the clinical historyn for a patient with the same `_rev` version number.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Remove `_id` and decrement `_rev` from clinical history document.
    data_fake_values_inventory = data_fake_patient["clinicalHistory"]
    data_fake_values_inventory["_rev"] -= 1
    data_fake_values_inventory.pop("_id")

    # Updates the same patient's clinical history but fails with pymongo duplicate key error.
    # PUT /patient/values/patient_{identityId}
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_values_inventory,
    )
    assert response.status_code == 422

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient_clinical_history_latest(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_clinical_history_factory: Callable[[], dict],
):
    """
    Test that we get the latest clinical history for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    patient_collection_name = scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    # Generate a fake clinical history
    data_fake_clinical_history = data_fake_clinical_history_factory()

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Update the patient with new _rev
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_clinical_history,
    )

    # GET the values inventory document
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
    )

    assert response.ok

    response_values_inventory = response.json()

    # Confirm if the response matches the latest `_rev`
    data_fake_clinical_history["_rev"] += 1
    response_values_inventory.pop("_id")
    assert response_values_inventory == data_fake_clinical_history

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )
