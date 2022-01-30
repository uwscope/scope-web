import copy
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
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_patient_profile_factory: Callable[
        [],
        dict,
    ],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document = data_fake_patient_profile_factory()

    # Store the document
    scope.database.patient.patient_profile.put_patient_profile(
        collection=temp_patient.collection,
        patient_profile=document,
    )

    # Retrieve the document via Flask
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
    )
    assert response.ok

    # Confirm it matches expected document, with addition of an "_id" and a "_rev"
    document_retrieved = response.json()
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    assert document == document_retrieved


def test_get_patient_profile_invalid(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving an invalid document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()

    # Retrieve an invalid patient
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id="invalid"),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # Retrieve a valid patient for which there is no document
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_put_patient_profile(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_patient_profile_factory: Callable[
        [],
        dict,
    ],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing a document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document = data_fake_patient_profile_factory()

    # Store a document via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored = response.json()
    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_rev" in document_stored
    del document_stored["_rev"]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = scope.database.patient.patient_profile.get_patient_profile(
        collection=temp_patient.collection,
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    assert document == document_retrieved


def test_put_patient_profile_invalid(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_patient_profile_factory: Callable[
        [],
        dict,
    ],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an invalid document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()

    # Invalid document that does not match any schema
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json={
            "_invalid": "invalid",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_id"
    document = data_fake_patient_profile_factory()
    document["_id"] = "invalid"
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_put_patient_profile_update(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_patient_profile_factory: Callable[
        [],
        dict,
    ],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an updated document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document = data_fake_patient_profile_factory()

    # Store a document via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored = response.json()

    # To store an updated document, remove the "_id"
    document_update = copy.deepcopy(document_stored)
    del document_update["_id"]

    # Store an update via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document_update,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_updated = response.json()

    assert document_stored["_id"] != document_updated["_id"]
    assert document_stored["_rev"] != document_updated["_rev"]

    # Retrieve the document
    document_retrieved = scope.database.patient.patient_profile.get_patient_profile(
        collection=temp_patient.collection,
    )

    # Confirm it matches updated document
    assert document_retrieved["_id"] == document_updated["_id"]
    assert document_retrieved["_rev"] == document_updated["_rev"]


def test_put_patient_profile_update_invalid(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_patient_profile_factory: Callable[
        [],
        dict,
    ],  # dict is patient profile document
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an invalid updated document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document = data_fake_patient_profile_factory()

    # Store a document
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored_rev1 = response.json()

    # Store an update
    document_update = copy.deepcopy(document_stored_rev1)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document_update,
    )
    assert response.ok

    # Attempting to store the original document should fail, result in a duplicate on "_rev" == 1
    document_update = copy.deepcopy(document)

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document_update,
    )

    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" == 2
    document_conflict = response.json()
    assert document_conflict["_rev"] == 2

    # Attempting to store the "_rev" == 1 document should fail, result in a duplicate on "_rev" == 2
    document_update = copy.deepcopy(document_stored_rev1)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PATH.format(patient_id=temp_patient.patient_id),
        ),
        json=document_update,
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" == 2
    document_conflict = response.json()
    assert document_conflict["_rev"] == 2
