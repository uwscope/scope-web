import copy
import http
from dataclasses import dataclass
import pytest
import requests
from typing import Callable, List, Optional
from urllib.parse import urljoin

import scope.config
import scope.database.patient_unsafe_utils
import scope.database.collection_utils as collection_utils
import scope.database.document_utils as document_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.assessments
import scope.database.patient.assessment_logs
import scope.database.patient.case_reviews
import scope.database.patient.mood_logs
import scope.database.patient.sessions
import scope.database.patient.scheduled_activities
import scope.database.patient.scheduled_assessments
import scope.testing.fixtures_database_temp_patient
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@dataclass(frozen=True)
class ConfigTestPatientSetOptions:
    # When a test executes, provided set elements will already include a set id.
    # Elements therefore cannot be post, must instead be put.
    # Elements may also already exist, so we will apply an unsafe update.
    set_id_will_already_exist: bool = False
    # When a test executes, provided set elements will already exist.
    # This will impact expectation that an initial get would fail.
    set_element_will_already_exist: bool = False


@dataclass(frozen=True)
class ConfigTestPatientSet:
    name: str
    semantic_set_id: str
    document_factory_fixture_set: str
    document_factory_fixture_set_element: str
    database_get_set_function: Callable[[...], List[dict]]
    database_get_function: Callable[[...], dict]
    database_post_function: Optional[Callable[[...], collection_utils.SetPostResult]]
    database_unsafe_update_function: Optional[
        Callable[[...], scope.database.collection_utils.PutResult]
    ]
    database_document_parameter_name: str
    flask_query_set_type: str
    flask_document_set_key: str
    flask_query_set_element_type: str
    flask_document_set_element_key: str
    options: ConfigTestPatientSetOptions = ConfigTestPatientSetOptions()


TEST_CONFIGS = [
    ConfigTestPatientSet(
        name="activities",
        semantic_set_id=scope.database.patient.activities.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_activities_factory",
        document_factory_fixture_set_element="data_fake_activity_factory",
        database_get_set_function=scope.database.patient.activities.get_activities,
        database_get_function=scope.database.patient.activities.get_activity,
        database_post_function=scope.database.patient.activities.post_activity,
        database_unsafe_update_function=None,
        database_document_parameter_name="activity",
        flask_query_set_type="activities",
        flask_document_set_key="activities",
        flask_query_set_element_type="activity",
        flask_document_set_element_key="activity",
    ),
    ConfigTestPatientSet(
        name="activitylogs",
        semantic_set_id=scope.database.patient.activity_logs.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_activity_logs_factory",
        document_factory_fixture_set_element="data_fake_activity_log_factory",
        database_get_set_function=scope.database.patient.activity_logs.get_activity_logs,
        database_get_function=scope.database.patient.activity_logs.get_activity_log,
        database_post_function=scope.database.patient.activity_logs.post_activity_log,
        database_unsafe_update_function=None,
        database_document_parameter_name="activity_log",
        flask_query_set_type="activitylogs",
        flask_document_set_key="activitylogs",
        flask_query_set_element_type="activitylog",
        flask_document_set_element_key="activitylog",
    ),
    ConfigTestPatientSet(
        name="assessments",
        semantic_set_id=scope.database.patient.assessments.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_assessments_factory",
        document_factory_fixture_set_element="data_fake_assessment_factory",
        database_get_set_function=scope.database.patient.assessments.get_assessments,
        database_get_function=scope.database.patient.assessments.get_assessment,
        database_post_function=None,  # Assessments have fixed set IDs
        database_unsafe_update_function=scope.database.patient_unsafe_utils.unsafe_update_assessment,
        database_document_parameter_name="assessment",
        flask_query_set_type="assessments",
        flask_document_set_key="assessments",
        flask_query_set_element_type="assessment",
        flask_document_set_element_key="assessment",
        options=ConfigTestPatientSetOptions(
            set_id_will_already_exist=True,
            set_element_will_already_exist=True,
        ),
    ),
    ConfigTestPatientSet(
        name="assessmentlogs",
        semantic_set_id=scope.database.patient.assessment_logs.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_assessment_logs_factory",
        document_factory_fixture_set_element="data_fake_assessment_log_factory",
        database_get_set_function=scope.database.patient.assessment_logs.get_assessment_logs,
        database_get_function=scope.database.patient.assessment_logs.get_assessment_log,
        database_post_function=scope.database.patient.assessment_logs.post_assessment_log,
        database_unsafe_update_function=None,
        database_document_parameter_name="assessment_log",
        flask_query_set_type="assessmentlogs",
        flask_document_set_key="assessmentlogs",
        flask_query_set_element_type="assessmentlog",
        flask_document_set_element_key="assessmentlog",
    ),
    ConfigTestPatientSet(
        name="casereviews",
        semantic_set_id=scope.database.patient.case_reviews.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_case_reviews_factory",
        document_factory_fixture_set_element="data_fake_case_review_factory",
        database_get_set_function=scope.database.patient.case_reviews.get_case_reviews,
        database_get_function=scope.database.patient.case_reviews.get_case_review,
        database_post_function=scope.database.patient.case_reviews.post_case_review,
        database_unsafe_update_function=None,
        database_document_parameter_name="case_review",
        flask_query_set_type="casereviews",
        flask_document_set_key="casereviews",
        flask_query_set_element_type="casereview",
        flask_document_set_element_key="casereview",
    ),
    ConfigTestPatientSet(
        name="moodlogs",
        semantic_set_id=scope.database.patient.mood_logs.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_mood_logs_factory",
        document_factory_fixture_set_element="data_fake_mood_log_factory",
        database_get_set_function=scope.database.patient.mood_logs.get_mood_logs,
        database_get_function=scope.database.patient.mood_logs.get_mood_log,
        database_post_function=scope.database.patient.mood_logs.post_mood_log,
        database_unsafe_update_function=None,
        database_document_parameter_name="mood_log",
        flask_query_set_type="moodlogs",
        flask_document_set_key="moodlogs",
        flask_query_set_element_type="moodlog",
        flask_document_set_element_key="moodlog",
    ),
    ConfigTestPatientSet(
        name="sessions",
        semantic_set_id=scope.database.patient.sessions.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_sessions_factory",
        document_factory_fixture_set_element="data_fake_session_factory",
        database_get_set_function=scope.database.patient.sessions.get_sessions,
        database_get_function=scope.database.patient.sessions.get_session,
        database_post_function=scope.database.patient.sessions.post_session,
        database_unsafe_update_function=None,
        database_document_parameter_name="session",
        flask_query_set_type="sessions",
        flask_document_set_key="sessions",
        flask_query_set_element_type="session",
        flask_document_set_element_key="session",
    ),
    ConfigTestPatientSet(
        name="scheduledactivities",
        semantic_set_id=scope.database.patient.scheduled_activities.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_scheduled_activities_factory",
        document_factory_fixture_set_element="data_fake_scheduled_activity_factory",
        database_get_set_function=scope.database.patient.scheduled_activities.get_scheduled_activities,
        database_get_function=scope.database.patient.scheduled_activities.get_scheduled_activity,
        database_post_function=scope.database.patient.scheduled_activities.post_scheduled_activity,
        database_unsafe_update_function=None,
        database_document_parameter_name="scheduled_activity",
        flask_query_set_type="scheduledactivities",
        flask_document_set_key="scheduledactivities",
        flask_query_set_element_type="scheduledactivity",
        flask_document_set_element_key="scheduledactivity",
    ),
    ConfigTestPatientSet(
        name="scheduledassessments",
        semantic_set_id=scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID,
        document_factory_fixture_set="data_fake_scheduled_assessments_factory",
        document_factory_fixture_set_element="data_fake_scheduled_assessment_factory",
        database_get_set_function=scope.database.patient.scheduled_assessments.get_scheduled_assessments,
        database_get_function=scope.database.patient.scheduled_assessments.get_scheduled_assessment,
        database_post_function=scope.database.patient.scheduled_assessments.post_scheduled_assessment,
        database_unsafe_update_function=None,
        database_document_parameter_name="scheduled_assessment",
        flask_query_set_type="scheduledassessments",
        flask_document_set_key="scheduledassessments",
        flask_query_set_element_type="scheduledassessment",
        flask_document_set_element_key="scheduledassessment",
        options=ConfigTestPatientSetOptions(
            set_id_will_already_exist=False,
            set_element_will_already_exist=True,
        ),
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
    documents_stored = document_factory()

    for document in documents_stored:
        # Most set elements expect to be post.
        #
        # If elements already include a set ID, they expect to be put.
        if not config.options.set_id_will_already_exist:
            result = config.database_post_function(
                **{
                    "collection": temp_patient.collection,
                    config.database_document_parameter_name: document,
                }
            )
            assert result.inserted_count == 1
        else:
            assert "_set_id" in document

            result = config.database_unsafe_update_function(
                **{
                    "collection": temp_patient.collection,
                    "set_id": document["_set_id"],
                    "{}_complete".format(
                        config.database_document_parameter_name
                    ): document,
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

    # Obtain the documents
    assert config.flask_document_set_key in response.json()
    documents_retrieved = response.json()[config.flask_document_set_key]

    # Confirm they match expected documents,
    # with addition of an "_id", "_rev", "_set_id", and semantic id
    for document_retrieved in documents_retrieved:
        assert "_id" in document_retrieved
        del document_retrieved["_id"]
        assert "_rev" in document_retrieved
        del document_retrieved["_rev"]

        assert "_set_id" in document_retrieved
        if config.semantic_set_id:
            assert config.semantic_set_id in document_retrieved

        # If the provided documents already included set_id,
        # then we must preserve that for the set comparison
        if not config.options.set_id_will_already_exist:
            del document_retrieved["_set_id"]
            if config.semantic_set_id:
                del document_retrieved[config.semantic_set_id]

    # Other documents may already be present, so check those present include ours
    for document_stored_current in documents_stored:
        assert document_stored_current in documents_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_get_empty(
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
    Test retrieving an empty set for patient.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()

    if not config.options.set_element_will_already_exist:
        # Retrieve a valid patient and a valid set,
        # but get an empty list because we have not put any elements
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
        assert config.flask_document_set_key in response.json()
        assert response.json()[config.flask_document_set_key] == []


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

    temp_patient = database_temp_patient_factory()
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

    # Retrieve a valid patient but an invalid set
    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type="invalid",
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

    if config.database_post_function is None:
        # This test targets a post endpoint which will not exist
        return

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Post a new document via Flask
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
            config.flask_document_set_element_key: document,
        },
    )
    assert response.ok

    # Response body includes the stored document,
    # with addition of an "_id", "_rev", "_set_id", and semantic id
    assert config.flask_document_set_element_key in response.json()
    document_stored = response.json()[config.flask_document_set_element_key]
    document_stored_set_id = document_stored["_set_id"]

    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_set_id" in document_stored
    del document_stored["_set_id"]
    assert "_rev" in document_stored
    del document_stored["_rev"]

    if config.semantic_set_id:
        assert document_stored[config.semantic_set_id] == document_stored_set_id
        assert config.semantic_set_id in document_stored
        del document_stored[config.semantic_set_id]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document_stored_set_id,
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_set_id" in document_retrieved
    del document_retrieved["_set_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    if config.semantic_set_id:
        assert config.semantic_set_id in document_retrieved
        del document_retrieved[config.semantic_set_id]

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
    """
    Test adding an invalid document to set.
    """

    if config.database_post_function is None:
        # This test targets a post endpoint which will not exist
        return

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    query = QUERY_SET.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_type,
    )

    # Invalid document that does not match any schema
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: {
                "_invalid": "invalid",
            }
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that is not nested under the document key
    document = document_factory()
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_id"
    document = document_factory()
    document["_id"] = "invalid"
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={config.flask_document_set_element_key: document},
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_set_id"
    document = document_factory()
    document["_set_id"] = "invalid"
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={config.flask_document_set_element_key: document},
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_rev"
    document = document_factory()
    document["_rev"] = "invalid"
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={config.flask_document_set_element_key: document},
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes a semantic id
    if config.semantic_set_id:
        document = document_factory()
        document[config.semantic_set_id] = "invalid"
        response = session.post(
            url=urljoin(
                flask_client_config.baseurl,
                query,
            ),
            json={config.flask_document_set_element_key: document},
        )
        assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_put_not_allowed(
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
    Test that put is not allowed on set.
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
    assert response.status_code == http.HTTPStatus.METHOD_NOT_ALLOWED


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
    Test retrieving a set element.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    document = document_factory()

    # Most set elements expect to be post.
    #
    # If elements already include a set ID, they expect to be put.
    if not config.options.set_id_will_already_exist:
        result = config.database_post_function(
            **{
                "collection": temp_patient.collection,
                config.database_document_parameter_name: document,
            }
        )
        assert result.inserted_count == 1
    else:
        assert "_set_id" in document

        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                "set_id": document["_set_id"],
                "{}_complete".format(config.database_document_parameter_name): document,
            }
        )
        assert result.inserted_count == 1

    # Retrieve the set element via Flask
    document_set_id = result.inserted_set_id
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document_set_id,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok

    # Confirm it matches expected document,
    # with addition of an "_id", "_rev", "_set_id", and semantic id
    assert config.flask_document_set_element_key in response.json()
    document_retrieved = response.json()[config.flask_document_set_element_key]

    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    assert "_set_id" in document_retrieved
    if config.semantic_set_id:
        assert config.semantic_set_id in document_retrieved

    # If the provided documents already included set_id,
    # then we must preserve that for the set comparison
    if not config.options.set_id_will_already_exist:
        del document_retrieved["_set_id"]
        if config.semantic_set_id:
            del document_retrieved[config.semantic_set_id]

    assert document == document_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_set_element_get_invalid(
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
    Test retrieving an invalid set element.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    document = document_factory()

    # Most set elements expect to be post.
    #
    # If elements already include a set ID, they expect to be put.
    if not config.options.set_id_will_already_exist:
        result = config.database_post_function(
            **{
                "collection": temp_patient.collection,
                config.database_document_parameter_name: document,
            }
        )
        assert result.inserted_count == 1
    else:
        assert "_set_id" in document

        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                "set_id": document["_set_id"],
                "{}_complete".format(config.database_document_parameter_name): document,
            }
        )
        assert result.inserted_count == 1

    # Retrieve an invalid patient set element via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id="invalid",
        query_type=config.flask_query_set_element_type,
        set_id=result.inserted_set_id,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # Retrieve a valid patient but invalid document
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type="invalid",
        set_id=result.inserted_set_id,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # Retrieve a valid patient and a valid document
    # but fail because the set_id is wrong
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id="invalid",
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
def test_patient_set_element_post_not_allowed(
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
    Test that post is not allowed on set element.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Store a document via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=collection_utils.generate_set_id(),
    )
    document = document_factory()
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.METHOD_NOT_ALLOWED


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
    Test putting a set element.
    """

    if config.options.set_element_will_already_exist:
        # This test targets a put of a document that does not already exist,
        # and so it is not well-defined when the document already exists.
        return

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    # Generate document and potentially set_id to assign it
    document = document_factory()
    if config.options.set_id_will_already_exist:
        document_set_id = document["_set_id"]
    else:
        document_set_id = collection_utils.generate_set_id()

    # Store a document via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document_set_id,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: document,
        },
    )
    assert response.ok

    # Response body includes the stored document,
    # with addition of an "_id", "_rev", "_set_id", and semantic id
    document_stored = response.json()[config.flask_document_set_element_key]
    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_rev" in document_stored
    assert document_stored["_rev"] == 1
    del document_stored["_rev"]

    assert "_set_id" in document_stored
    assert document_stored["_set_id"] == document_set_id
    del document_stored["_set_id"]
    if config.semantic_set_id:
        assert config.semantic_set_id in document_stored
        assert document_stored[config.semantic_set_id] == document_set_id
        del document_stored[config.semantic_set_id]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document_set_id,
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    assert "_set_id" in document_retrieved
    assert document_retrieved["_set_id"] == document_set_id
    del document_retrieved["_set_id"]
    if config.semantic_set_id:
        assert config.semantic_set_id in document_retrieved
        assert document_retrieved[config.semantic_set_id] == document_set_id
        del document_retrieved[config.semantic_set_id]

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
    Test putting an invalid set element.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(
        config.document_factory_fixture_set_element
    )

    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=collection_utils.generate_set_id(),
    )

    # Invalid document that does not match any schema
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: {"_invalid": "invalid"},
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that is not nested under the document key
    document = document_factory()
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes an "_id"
    document = document_factory()
    document["_id"] = "invalid"
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: document,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes a mismatched "_set_id"
    document = document_factory()
    document["_set_id"] = "invalid"
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: document,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Invalid document that already includes a mismatched semantic id
    if config.semantic_set_id:
        document = document_factory()
        document[config.semantic_set_id] = "invalid"
        response = session.put(
            url=urljoin(
                flask_client_config.baseurl,
                query,
            ),
            json={
                config.flask_document_set_element_key: document,
            },
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

    # Most set elements expect to be post.
    #
    # If elements already include a set ID, they expect to be put.
    document = document_factory()
    if not config.options.set_id_will_already_exist:
        result = config.database_post_function(
            **{
                "collection": temp_patient.collection,
                config.database_document_parameter_name: document,
            }
        )
        assert result.inserted_count == 1
    else:
        assert "_set_id" in document

        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                "set_id": document["_set_id"],
                "{}_complete".format(config.database_document_parameter_name): document,
            }
        )
        assert result.inserted_count == 1

    document_stored = result.document
    document_stored_set_id = result.inserted_set_id

    # To store an updated document, remove the "_id"
    document_update = copy.deepcopy(document_stored)
    del document_update["_id"]

    # Store an update via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document_stored_set_id,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: document_update,
        },
    )
    assert response.ok

    # Response body includes the stored document,
    # with addition of an "_id", "_rev", "_set_id", and semantic id
    document_updated = response.json()[config.flask_document_set_element_key]

    assert document_stored["_id"] != document_updated["_id"]
    assert document_stored["_set_id"] == document_updated["_set_id"]
    assert document_stored["_rev"] != document_updated["_rev"]
    assert document_stored["_rev"] + 1 == document_updated["_rev"]

    if config.semantic_set_id:
        assert (
            document_stored[config.semantic_set_id]
            == document_updated[config.semantic_set_id]
        )

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
            "set_id": document_stored_set_id,
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

    # Most set elements expect to be post.
    #
    # If elements already include a set ID, they expect to be put.
    document = document_factory()
    if not config.options.set_id_will_already_exist:
        result = config.database_post_function(
            **{
                "collection": temp_patient.collection,
                config.database_document_parameter_name: document,
            }
        )
        assert result.inserted_count == 1
    else:
        assert "_set_id" in document

        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                "set_id": document["_set_id"],
                "{}_complete".format(config.database_document_parameter_name): document,
            }
        )
        assert result.inserted_count == 1

    document_stored = result.document
    document_stored_set_id = result.inserted_set_id

    # Store an update that will be assigned an incremented "_rev"
    document_update = copy.deepcopy(document_stored)
    del document_update["_id"]

    # Store an update via Flask
    query = QUERY_SET_ELEMENT.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_set_element_type,
        set_id=document_stored_set_id,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_set_element_key: document_update,
        },
    )
    assert response.ok
    document_updated_stored = response.json()[config.flask_document_set_element_key]

    # Attempting to store the original document should fail, result in a duplicate on "_rev"
    document_update = copy.deepcopy(document)
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={config.flask_document_set_element_key: document_update},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" is the incremented rev
    document_conflict = response.json()[config.flask_document_set_element_key]
    assert document_conflict["_rev"] == document_updated_stored["_rev"]

    # Attempting to store the stored document should fail, result in a duplicate on incremented "_rev"
    document_update = copy.deepcopy(document_stored)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={config.flask_document_set_element_key: document_update},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate that current "_rev" is the incremented rev
    document_conflict = response.json()[config.flask_document_set_element_key]
    assert document_conflict["_rev"] == document_updated_stored["_rev"]
