import http
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.database.collection_utils as collection_utils
import scope.schema
import scope.testing.fixtures_database_temp_patient
import scope.testing.schema
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

QUERY_PATIENTS = "patients"
QUERY_PATIENT = "patient/{patient_id}"


def test_patients_get(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving patients.
    """

    session = flask_session_unauthenticated_factory()

    created_ids = [database_temp_patient_factory().patient_id for _ in range(5)]

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATIENTS,
        ),
    )
    assert response.ok

    assert "patients" in response.json()
    patient_documents = response.json()["patients"]
    for patient_document_current in patient_documents:
        scope.testing.schema.assert_schema(
            data=patient_document_current,
            schema=scope.schema.patient_schema,
            expected_valid=True,
        )

    retrieved_ids = [
        patient_document_current["identity"]["identityId"]
        for patient_document_current in patient_documents
    ]
    assert all(patient_id in retrieved_ids for patient_id in created_ids)

    scope.testing.schema.assert_schema(
        data=response.json()["patients"],
        schema=scope.schema.patients_schema,
        expected_valid=True,
    )


def test_patient_get(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a patients
    """

    session = flask_session_unauthenticated_factory()

    created_id = database_temp_patient_factory().patient_id

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATIENT.format(patient_id=created_id),
        ),
    )
    assert response.ok

    assert "patient" in response.json()
    patient_document = response.json()["patient"]
    scope.testing.schema.assert_schema(
        data=patient_document,
        schema=scope.schema.patient_schema,
        expected_valid=True,
    )

    assert created_id == patient_document["identity"]["identityId"]


def test_patient_get_invalid(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test non-existent patient yields 404.
    """

    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATIENT.format(patient_id="invalid"),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATIENT.format(patient_id=collection_utils.generate_set_id()),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND
