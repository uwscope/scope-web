import faker
import http
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.database.patients
import scope.database.patient.patient_profile
import scope.testing.fixtures_database_temp_patient
import scope.testing.fake_data.fixtures_fake_patient_profile
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


QUERY_PATH = "patient/{patient_id}/patient_profile"


def test_get_patient_profile(
    database_temp_patient_factory: Callable[[], scope.testing.fixtures_database_temp_patient.DatabaseTempPatient],
    data_fake_patient_profile_factory: Callable[[], dict],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing and retrieving a patient profile.
    """

    temp_patient = database_temp_patient_factory()
    patient_profile_document_created = data_fake_patient_profile_factory()

    # Store a patient profile
    scope.database.patient.patient_profile.put_patient_profile(
        collection=temp_patient.collection,
        patient_profile=patient_profile_document_created
    )

    # Retrieve the patient profile
    session = flask_session_unauthenticated_factory()
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
    )
    assert response.ok

    # Confirm it matches expected patient profile
    patient_profile_document_retrieved = response.json()
    del patient_profile_document_retrieved["_id"]
    del patient_profile_document_retrieved["_rev"]

    assert patient_profile_document_created == patient_profile_document_retrieved


def test_get_patient_profile_invalid(
    database_temp_patient_factory: Callable[[], scope.testing.fixtures_database_temp_patient.DatabaseTempPatient],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving an invalid patient profile.
    """

    # Retrieve an invalid patient profile
    session = flask_session_unauthenticated_factory()
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id="invalid"),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


# # @pytest.mark.skip(reason="no way of currently testing this")
# def test_flask_update_patient_profile(
#     database_client: pymongo.database.Database,
#     flask_client_config: scope.config.FlaskClientConfig,
#     flask_session_unauthenticated_factory: Callable[[], requests.Session],
#     data_fake_patient_factory: Callable[[], dict],
#     data_fake_patient_profile_factory: Callable[[], dict],
# ):
#     """
#     Test that we can update the clinical history for a patient.
#     """
#
#     # Generate a fake patient
#     data_fake_patient = data_fake_patient_factory()
#
#     # Generate a fake patien profile
#     data_fake_patient_profile = data_fake_patient_profile_factory()
#
#     # Create the patient collection and insert the documents
#     scope.database.patients.create_patient(
#         database=database_client,
#         patient=data_fake_patient,
#     )
#     patient_collection_name = scope.database.patients.collection_for_patient(
#         patient_name=data_fake_patient["identity"]["name"]
#     )
#
#     # Obtain a session
#     session = flask_session_unauthenticated_factory()
#
#     response = session.put(
#         url=urljoin(
#             flask_client_config.baseurl,
#             "{}/{}/{}".format(
#                 API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
#             ),
#         ),
#         json=data_fake_patient_profile,
#     )
#     assert response.ok
#
#     scope.database.patients.delete_patient(
#         database=database_client,
#         patient_collection_name=patient_collection_name,
#     )
#
#
# # @pytest.mark.skip(reason="no way of currently testing this")
# def test_flask_update_patient_profile_duplicate(
#     database_client: pymongo.database.Database,
#     flask_client_config: scope.config.FlaskClientConfig,
#     flask_session_unauthenticated_factory: Callable[[], requests.Session],
#     data_fake_patient_factory: Callable[[], dict],
# ):
#     """
#     Test that we cannot update the profile for a patient with the same `_rev` version number.
#     """
#
#     # Generate a fake patient
#     data_fake_patient = data_fake_patient_factory()
#
#     # Create the patient collection and insert the documents
#     scope.database.patients.create_patient(
#         database=database_client,
#         patient=data_fake_patient,
#     )
#     patient_collection_name = scope.database.patients.collection_for_patient(
#         patient_name=data_fake_patient["identity"]["name"]
#     )
#
#     # Obtain a session
#     session = flask_session_unauthenticated_factory()
#
#     # Remove `_id` and decrement `_rev` from clinical history document.
#     data_fake_patient_profile = data_fake_patient["patientProfile"]
#     data_fake_patient_profile["_rev"] -= 1
#     data_fake_patient_profile.pop("_id")
#
#     response = session.put(
#         url=urljoin(
#             flask_client_config.baseurl,
#             "{}/{}/{}".format(
#                 API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
#             ),
#         ),
#         json=data_fake_patient_profile,
#     )
#     assert response.status_code == 422
#
#     scope.database.patients.delete_patient(
#         database=database_client,
#         patient_collection_name=patient_collection_name,
#     )
#
#
# # @pytest.mark.skip(reason="no way of currently testing this")
# def test_flask_get_patient_profile_latest(
#     database_client: pymongo.database.Database,
#     flask_client_config: scope.config.FlaskClientConfig,
#     flask_session_unauthenticated_factory: Callable[[], requests.Session],
#     data_fake_patient_factory: Callable[[], dict],
#     data_fake_patient_profile_factory: Callable[[], dict],
# ):
#     """
#     Test that we get the latest profile for a patient.
#     """
#
#     # Generate a fake patient
#     data_fake_patient = data_fake_patient_factory()
#
#     # Create the patient collection and insert the documents
#     scope.database.patients.create_patient(
#         database=database_client,
#         patient=data_fake_patient,
#     )
#     patient_collection_name = scope.database.patients.collection_for_patient(
#         patient_name=data_fake_patient["identity"]["name"]
#     )
#     # Generate a fake patient profile
#     data_fake_patient_profile = data_fake_patient_profile_factory()
#
#     # Obtain a session
#     session = flask_session_unauthenticated_factory()
#
#     # Update the patient with new _rev
#     response = session.put(
#         url=urljoin(
#             flask_client_config.baseurl,
#             "{}/{}/{}".format(
#                 API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
#             ),
#         ),
#         json=data_fake_patient_profile,
#     )
#
#     # GET the values inventory document
#     response = session.get(
#         url=urljoin(
#             flask_client_config.baseurl,
#             "{}/{}/{}".format(
#                 API_RELATIVE_PATH, patient_collection_name, API_QUERY_PATH
#             ),
#         ),
#     )
#
#     assert response.ok
#
#     response_json = response.json()
#
#     # Confirm if the response matches the latest `_rev`
#     data_fake_patient_profile["_rev"] += 1
#     response_json.pop("_id")
#     assert response_json == data_fake_patient_profile
#
#     scope.database.patients.delete_patient(
#         database=database_client,
#         patient_collection_name=patient_collection_name,
#     )
