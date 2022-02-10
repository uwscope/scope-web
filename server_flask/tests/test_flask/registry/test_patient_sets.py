import copy
import http
from dataclasses import dataclass
from typing import Callable, List
from urllib.parse import urljoin

import pytest
import requests
import scope.config
import scope.database.collection_utils
import scope.database.patient.case_reviews
import scope.database.patient.sessions
import scope.testing.fixtures_database_temp_patient
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@dataclass(frozen=True)
class ConfigTestPatientSet:
    name: str
    document_factory_fixture_set: str
    document_factory_fixture_set_element: str
    database_get_set_function: Callable[[...], List[dict]]
    database_get_function: Callable[[...], dict]
    database_post_function: Callable[[...], scope.database.collection_utils.PutResult]
    database_put_function: Callable[[...], scope.database.collection_utils.PutResult]
    database_document_parameter_name: str
    flask_query_set_type: str
    flask_query_set_element_type: str
    flask_response_document_set_key: str
    flask_response_document_set_element_key: str
    document_id: str


TEST_CONFIGS = [
    ConfigTestPatientSet(
        name="sessions",
        document_factory_fixture_set="data_fake_sessions_factory",
        document_factory_fixture_set_element="data_fake_session_factory",
        database_get_set_function=scope.database.patient.sessions.get_sessions,
        database_get_function=scope.database.patient.sessions.get_session,
        database_post_function=scope.database.patient.sessions.post_session,
        database_put_function=scope.database.patient.sessions.put_session,
        database_document_parameter_name="session",
        flask_query_set_type="sessions",
        flask_query_set_element_type="session",
        flask_response_document_set_key="sessions",
        flask_response_document_set_element_key="session",
        document_id="sessionId",
    ),
    ConfigTestPatientSet(
        name="case-reviews",
        document_factory_fixture_set="data_fake_case_reviews_factory",
        document_factory_fixture_set_element="data_fake_case_review_factory",
        database_get_set_function=scope.database.patient.case_reviews.get_case_reviews,
        database_get_function=scope.database.patient.case_reviews.get_case_review,
        database_post_function=scope.database.patient.case_reviews.post_case_review,
        database_put_function=scope.database.patient.case_reviews.put_case_review,
        database_document_parameter_name="case_review",
        flask_query_set_type="casereviews",
        flask_query_set_element_type="casereview",
        flask_response_document_set_key="casereviews",
        flask_response_document_set_element_key="casereview",
        document_id="reviewId",
    ),
]


QUERY_SET = "patient/{patient_id}/{query_type}"

QUERY_SET_ELEMENT = "patient/{patient_id}/{query_type}/{set_id}"


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_get(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture_set)

    # Store the documents
    documents = document_factory()

    for document in documents:
        result = config.database_post_function(
            **{
                "collection": temp_patient.collection,
                config.database_document_parameter_name: document,
            }
        )
        assert result.inserted_count == 1

    # Retrieve the set via Flask
    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_type,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok

    # Confirm it matches expected documents, with addition of an "_id", "_rev", and "_set_id"
    documents_retrieved = response.json()[config.flask_response_document_set_key]
    for document_retrieved in documents_retrieved:
        assert "_id" in document_retrieved
        del document_retrieved["_id"]
        assert "_rev" in document_retrieved
        del document_retrieved["_rev"]
        assert "_set_id" in document_retrieved
        del document_retrieved["_set_id"]

    assert len(documents) == len(documents_retrieved)

    # NOTE: @James: Is there a need to update `normalize_document` in collection_utils to avoid sorting.
    assert sorted(documents, key=lambda d: d[config.document_id]) == sorted(
        documents_retrieved, key=lambda d: d[config.document_id]
    )


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_get_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a set for invalid patient.
    """

    session = flask_session_unauthenticated_factory()

    # Retrieve an invalid patient via Flask
    query = QUERY_SET.format(
        patient_id="invalid",
        query_type=config.flask_query_set_type,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_post(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test adding a document to set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Store a document via Flask
    document = document_factory()
    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_type,
    )
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id", "_rev", and a "_set_id"
    document_stored = response.json()[config.flask_response_document_set_element_key]
    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_rev" in document_stored
    del document_stored["_rev"]
    assert "_set_id" in document_stored
    del document_stored["_set_id"]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document[config.document_id],
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]
    assert "_set_id" in document_retrieved
    del document_retrieved["_set_id"]

    assert document == document_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_post_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Invalid document that does not match any schema
    document = document_factory()
    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_type,
    )
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            "_invalid": "invalid",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_id"

    document["_id"] = "invalid"
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_put_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that put is not allowd on set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()

    # Retrieve an invalid patient via Flask
    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_type,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.status_code == 405


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_get(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Store the documents
    document = document_factory()

    result = config.database_post_function(
        **{
            "collection": temp_patient.collection,
            config.database_document_parameter_name: document,
        }
    )
    assert result.inserted_count == 1

    # Retrieve the set element via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=result.document[config.document_id],
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok

    # Confirm it matches expected document, with addition of an "_id", "_rev", and "_set_id"
    document_retrieved = response.json()[config.flask_response_document_set_element_key]
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]
    assert "_set_id" in document_retrieved
    del document_retrieved["_set_id"]

    assert document == document_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_put(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an element in set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Update a document via Flask
    document = document_factory()
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document[config.document_id],
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id", "_rev", and a "_set_id"
    document_stored = response.json()[config.flask_response_document_set_element_key]
    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_rev" in document_stored
    del document_stored["_rev"]
    assert "_set_id" in document_stored
    del document_stored["_set_id"]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document[config.document_id],
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]
    assert "_set_id" in document_retrieved
    del document_retrieved["_set_id"]

    assert document == document_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_put_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test updating an invalid element in set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Invalid document that does not match any schema
    document = document_factory()
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document[config.document_id],
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            "_invalid": "invalid",
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_id"

    document["_id"] = "invalid"
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_put_update(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an updated element in set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Store a document via Flask
    document = document_factory()
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document[config.document_id],
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id", "_rev", and "_set_id"
    document_stored = response.json()[config.flask_response_document_set_element_key]

    # To store an updated document, remove the "_id"
    document_update = copy.deepcopy(document_stored)
    del document_update["_id"]

    # Store an update via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document_update,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id", "_rev", and a "_set_id"
    document_updated = response.json()[config.flask_response_document_set_element_key]

    assert document_stored["_id"] != document_updated["_id"]
    assert document_stored["_rev"] != document_updated["_rev"]
    assert document_stored["_rev"] + 1 == document_updated["_rev"]
    assert document_stored["_set_id"] == document_updated["_set_id"]

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document_stored[config.document_id],
        }
    )

    # Confirm it matches updated document
    assert document_retrieved["_id"] == document_updated["_id"]
    assert document_retrieved["_rev"] == document_updated["_rev"]


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_put_update_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSet,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an updated element in set.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Store a document via Flask
    document = document_factory()
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document[config.document_id],
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id", "_rev", and "_set_id"
    document_stored_rev1 = response.json()[
        config.flask_response_document_set_element_key
    ]

    # Store an update that will be assigned "_rev" == 2
    document_update = copy.deepcopy(document_stored_rev1)
    del document_update["_id"]

    # Store an update via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document_update,
    )
    assert response.ok

    # Attempting to store the original document should fail, result in a duplicate on "_rev" == 1
    document_update = copy.deepcopy(document)
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document_update,
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" == 2
    document_conflict = response.json()[config.flask_response_document_set_element_key]
    assert document_conflict["_rev"] == 2

    # Attempting to store the "_rev" == 1 document should fail, result in a duplicate on "_rev" == 2
    document_update = copy.deepcopy(document_stored_rev1)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document_update,
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" == 2
    document_conflict = response.json()[config.flask_response_document_set_element_key]
    assert document_conflict["_rev"] == 2
