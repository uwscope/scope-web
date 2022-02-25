import copy
from dataclasses import dataclass
import http
import pymongo.database
import pytest
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.database.collection_utils as collection_utils
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.values_inventory
import scope.testing.fixtures_database_temp_patient
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@dataclass(frozen=True)
class ConfigTestPatientSingletonOptions:
    # When a test executes, the document will actually already exist.
    # This will impact an "initial" put as well as gets that are expected to fail.
    # Included because profile is created together with the patient.
    document_will_already_exist: bool = False


@dataclass(frozen=True)
class ConfigTestPatientSingleton:
    name: str
    document_factory_fixture: str
    database_get_function: Callable[[...], dict]
    flask_query_type: str
    flask_document_key: str
    options: ConfigTestPatientSingletonOptions = ConfigTestPatientSingletonOptions(
    )


TEST_CONFIGS = [
    ConfigTestPatientSingleton(
        name="clinicalhistory",
        document_factory_fixture="data_fake_clinical_history_factory",
        database_get_function=scope.database.patient.clinical_history.get_clinical_history,
        flask_query_type="clinicalhistory",
        flask_document_key="clinicalhistory",
    ),
    ConfigTestPatientSingleton(
        name="profile",
        document_factory_fixture="data_fake_patient_profile_factory",
        database_get_function=scope.database.patient.patient_profile.get_patient_profile,
        flask_query_type="profile",
        flask_document_key="profile",
        options=ConfigTestPatientSingletonOptions(
            document_will_already_exist=True,
        )
    ),
    ConfigTestPatientSingleton(
        name="safetyplan",
        document_factory_fixture="data_fake_safety_plan_factory",
        database_get_function=scope.database.patient.safety_plan.get_safety_plan,
        flask_query_type="safetyplan",
        flask_document_key="safetyplan",
    ),
    ConfigTestPatientSingleton(
        name="valuesinventory",
        document_factory_fixture="data_fake_values_inventory_factory",
        database_get_function=scope.database.patient.values_inventory.get_values_inventory,
        flask_query_type="valuesinventory",
        flask_document_key="valuesinventory",
    ),
]


QUERY_SINGLETON = "patient/{patient_id}/{query_type}"


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_get(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_client: pymongo.database.Database,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )

    if not config.options.document_will_already_exist:
        # Store a document via Flask
        document = document_factory()
        response = session.put(
            url=urljoin(
                flask_client_config.baseurl,
                query,
            ),
            json={
                config.flask_document_key: document,
            },
        )
        assert response.ok

        document_stored = response.json()[config.flask_document_key]
        assert document_stored["_rev"] == 1

    # Retrieve the document
    document_database = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Retrieve the document via Flask
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.ok

    # Obtain the document
    assert config.flask_document_key in response.json()
    document_flask = response.json()[config.flask_document_key]

    # Confirm it matches expected document
    assert document_database == document_flask


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_get_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
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

    # Retrieve an invalid patient via Flask
    query = QUERY_SINGLETON.format(
        patient_id="invalid",
        query_type=config.flask_query_type,
    )
    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    # Retrieve a valid patient but an invalid document
    query = QUERY_SINGLETON.format(
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

    # Retrieve a valid patient and a valid document,
    # but fail because we have not put that document
    if not config.options.document_will_already_exist:
        query = QUERY_SINGLETON.format(
            patient_id=temp_patient.patient_id,
            query_type=config.flask_query_type,
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
def test_patient_singleton_post_not_allowed(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test that POST is not allowed.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    # Generate a document via Flask
    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )
    document = document_factory()
    response = session.post(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document,
        },
    )
    assert response.status_code == http.HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_put(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing a document.
    """

    if config.options.document_will_already_exist:
        # This test targets a put of a document that does not already exist
        return

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    # Store a document via Flask
    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )
    document = document_factory()
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document,
        },
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored = response.json()[config.flask_document_key]
    assert "_id" in document_stored
    del document_stored["_id"]
    assert "_rev" in document_stored
    del document_stored["_rev"]

    assert document == document_stored

    # Retrieve the document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    del document_retrieved["_id"]
    assert "_rev" in document_retrieved
    del document_retrieved["_rev"]

    assert document == document_retrieved


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_put_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an invalid document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )

    # Invalid document that does not match any schema
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: {
                "invalid": "invalid",
            },
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
            config.flask_document_key: document,
        },
    )
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_put_update(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an updated document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )

    if not config.options.document_will_already_exist:
        # Store a document via Flask
        document = document_factory()
        response = session.put(
            url=urljoin(
                flask_client_config.baseurl,
                query,
            ),
            json={
                config.flask_document_key: document,
            },
        )
        assert response.ok

        document_stored = response.json()[config.flask_document_key]
        assert document_stored["_rev"] == 1

    # Obtain the current document
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # To store an updated document, remove the "_id"
    document_update = copy.deepcopy(document_retrieved)
    del document_update["_id"]

    # Store an update via Flask
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document_update,
        },
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_updated = response.json()[config.flask_document_key]

    assert document_retrieved["_id"] != document_updated["_id"]
    assert document_retrieved["_rev"] != document_updated["_rev"]

    # Retrieve the document again
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
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
def test_patient_singleton_put_update_invalid(
    request: pytest.FixtureRequest,
    config: ConfigTestPatientSingleton,
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test storing an invalid updated document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )

    # Store a document via Flask
    if not config.options.document_will_already_exist:
        document = document_factory()
        response = session.put(
            url=urljoin(
                flask_client_config.baseurl,
                query,
            ),
            json={
                config.flask_document_key: document,
            },
        )
        assert response.ok

    # Obtain the currently stored document
    document_existing = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Attempting to store the same document without any "_rev" should fail,
    # because it will result in a duplicate on "_rev" == 1
    document_update = copy.deepcopy(document_existing)
    del document_update["_id"]
    del document_update["_rev"]
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document_update,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT

    # Contents of the response should indicate the current "_rev"
    document_conflict = response.json()[config.flask_document_key]

    # Store an update that will be assigned an incremented "_rev"
    document_update = copy.deepcopy(document_conflict)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document_update,
        },
    )
    assert response.ok

    # Attempting to store the previous document should fail
    document_update = copy.deepcopy(document_conflict)
    del document_update["_id"]

    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json={
            config.flask_document_key: document_update,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
