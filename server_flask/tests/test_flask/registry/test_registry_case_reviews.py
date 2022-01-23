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
API_QUERY_PATH = "casereviews"

# TODO: James to Review
pytest.skip("Not reviewed", allow_module_level=True)

# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_case_reviews(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a list of case_reviews.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )
    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    # Retrieve all case reviews
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
    for v in data_fake_patient["caseReviews"]:
        v["_id"] = str(v["_id"])

    assert data_fake_patient["caseReviews"] == response.json()

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_case_reviews_404(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that we get a 404 for non-existent patient collection.
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


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_create_case_review(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
    data_fake_case_review_factory: Callable[[], dict],
):
    """
    Test that we can create a case review.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()
    data_fake_case_review = data_fake_case_review_factory()
    data_fake_case_review["_review_id"] = "review-%d" % (
        len(data_fake_patient["caseReviews"]) + 1
    )

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    # Obtain a session
    session = flask_session_unauthenticated_factory()

    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}".format(
                API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
            ),
        ),
        json=data_fake_case_review,
    )
    assert response.ok

    response_json = response.json()
    response_json.pop("_id", None)

    assert response_json == data_fake_case_review


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_get_case_reviews_405(
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
def test_flask_get_case_review(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can get a case review using review_id.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    case_review_document = random.choice(data_fake_patient["caseReviews"])

    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}/{}".format(
                API_RELATIVE_PATH,
                patient_collection_name,
                API_QUERY_PATH,
                case_review_document["_review_id"],
            ),
        ),
    )
    assert response.status_code == 200
    response_json = response.json()
    case_review_document["_id"] = str(case_review_document["_id"])

    assert response_json == case_review_document

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )


# @pytest.mark.skip(reason="no way of currently testing this")
def test_flask_update_case_review(
    database_client: pymongo.database.Database,
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
    data_fake_patient_factory: Callable[[], dict],
):
    """
    Test that we can update a case review using review_id.
    """

    # Generate a fake patient
    data_fake_patient = data_fake_patient_factory()

    # Insert the fake patient
    scope.database.patients.create_patient(
        database=database_client,
        patient=data_fake_patient,
    )

    patient_collection_name = scope.database.patients.collection_for_patient(
        patient_name=data_fake_patient["identity"]["name"]
    )

    case_review_document = random.choice(data_fake_patient["caseReviews"])
    case_review_document.pop("_id", None)

    session = flask_session_unauthenticated_factory()

    # Retrieve the case review using review_id
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            "{}/{}/{}/{}".format(
                API_RELATIVE_PATH,
                patient_collection_name,
                API_QUERY_PATH,
                case_review_document["_review_id"],
            ),
        ),
        json=case_review_document,
    )
    assert response.status_code == 200

    case_review_document["_rev"] += 1
    response_json = response.json()
    response_json.pop("_id", None)

    assert response_json == case_review_document

    scope.database.patients.delete_patient(
        database=database_client,
        patient_collection_name=patient_collection_name,
    )
