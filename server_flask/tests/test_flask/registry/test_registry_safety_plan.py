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
API_QUERY_PATH = "safety"

# TODO: James to Review
pytest.skip("Not reviewed", allow_module_level=True)

# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient_safety_plan(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test to get the safety plan for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

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

    assert response.json() == data_fake_patient["safetyPlan"]

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_patient_safety_plan(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_safety_plan_factory: Callable[[], dict],
):
    """
    Test that we can update the safety plan for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Generate a fake safety plan
    data_fake_safety_plan = data_fake_safety_plan_factory()

    # Create the patient collection and insert the documents
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_safety_plan,
    )
    assert response.ok

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_patient_safety_plan_duplicate(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we cannot update the safety plan for a patient with the same `_rev` version number.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Remove `_id` and decrement `_rev` from safety plan document.
    data_fake_safety_plan = data_fake_patient["safetyPlan"]
    data_fake_safety_plan["_rev"] -= 1
    data_fake_safety_plan.pop("_id")

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_safety_plan,
    )
    assert response.status_code == 422

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_patient_safety_plan_latest(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_safety_plan_factory: Callable[[], dict],
):
    """
    Test that we get the latest safety plan for a patient.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Create the patient collection and insert the documents
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Generate a fake safety plan
    data_fake_safety_plan = data_fake_safety_plan_factory()

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
        json=data_fake_safety_plan,
    )

    # GET the safety plan document
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
    )

    assert response.ok

    response_json = response.json()

    # Confirm if the response matches the latest `_rev`
    data_fake_safety_plan["_rev"] += 1
    response_json.pop("_id")
    assert response_json == data_fake_safety_plan

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )
