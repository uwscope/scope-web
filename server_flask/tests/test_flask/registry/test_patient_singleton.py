import copy
from dataclasses import dataclass
import http
import pymongo.database
import pytest
import requests
from typing import Callable, Optional
from urllib.parse import urljoin

import scope.config
import scope.database.collection_utils as collection_utils
import scope.database.patient
import scope.database.patient_unsafe_utils
import scope.testing.fixtures_database_temp_patient
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@dataclass(frozen=True)
class ConfigTestPatientSingletonOptions:
    # When a test executes, the singleton document will already exist.
    # This will impact an expected "initial" put,
    # and will also impact expectation that an initial get would fail.
    # Initial patient creation includes creation of multiple singletons,
    # so this option allows adjustment to testing based on that.
    singleton_will_already_exist: bool = False


@dataclass(frozen=True)
class ConfigTestPatientSingleton:
    name: str
    document_factory_fixture: str
    database_get_function: Callable[[...], Optional[dict]]
    database_unsafe_update_function: Callable[
        [...], scope.database.collection_utils.PutResult
    ]
    database_unsafe_update_document_parameter: str
    flask_query_type: str
    flask_document_key: str
    options: ConfigTestPatientSingletonOptions = ConfigTestPatientSingletonOptions()


TEST_CONFIGS = [
    ConfigTestPatientSingleton(
        name="clinicalhistory",
        document_factory_fixture="data_fake_clinical_history_factory",
        database_get_function=scope.database.patient.get_clinical_history,
        database_unsafe_update_function=scope.database.patient_unsafe_utils.unsafe_update_clinical_history,
        database_unsafe_update_document_parameter="clinical_history",
        flask_query_type="clinicalhistory",
        flask_document_key="clinicalhistory",
        options=ConfigTestPatientSingletonOptions(
            singleton_will_already_exist=True,
        ),
    ),
    ConfigTestPatientSingleton(
        name="profile",
        document_factory_fixture="data_fake_patient_profile_factory",
        database_get_function=scope.database.patient.get_patient_profile,
        database_unsafe_update_function=scope.database.patient_unsafe_utils.unsafe_update_clinical_history,
        database_unsafe_update_document_parameter="clinical_history",
        flask_query_type="profile",
        flask_document_key="profile",
        options=ConfigTestPatientSingletonOptions(
            singleton_will_already_exist=True,
        ),
    ),
    ConfigTestPatientSingleton(
        name="safetyplan",
        document_factory_fixture="data_fake_safety_plan_factory",
        database_get_function=scope.database.patient.get_safety_plan,
        database_unsafe_update_function=scope.database.patient_unsafe_utils.unsafe_update_safety_plan,
        database_unsafe_update_document_parameter="safety_plan",
        flask_query_type="safetyplan",
        flask_document_key="safetyplan",
        options=ConfigTestPatientSingletonOptions(
            singleton_will_already_exist=True,
        ),
    ),
    ConfigTestPatientSingleton(
        name="valuesinventory",
        document_factory_fixture="data_fake_values_inventory_factory",
        database_get_function=scope.database.patient.values_inventory.get_values_inventory,
        database_unsafe_update_function=scope.database.patient_unsafe_utils.unsafe_update_values_inventory,
        database_unsafe_update_document_parameter="values_inventory",
        flask_query_type="valuesinventory",
        flask_document_key="valuesinventory",
        options=ConfigTestPatientSingletonOptions(
            singleton_will_already_exist=True,
        ),
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

    # Put a document to be retrieved
    if not config.options.singleton_will_already_exist:
        document = document_factory()
        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                config.database_unsafe_update_document_parameter: document,
            }
        )
        assert result.inserted_count

    # Retrieve the document directly via database
    document_database = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Retrieve the document via Flask
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
    assert response.ok
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
    # but fail if nobody has created the document
    if not config.options.singleton_will_already_exist:
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

    query = QUERY_SINGLETON.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )

    # Attempt to post a singleton
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

    if config.options.singleton_will_already_exist:
        # This test targets a put of a document that does not already exist,
        # and so it is not well-defined when the document already exists.
        return

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture)

    # Put a document via Flask
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
    assert "_rev" in document_stored
    del document_stored["_id"]
    del document_stored["_rev"]

    assert document == document_stored

    # Retrieve the document from the database
    document_retrieved = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Confirm it matches expected document
    assert document_retrieved is not None
    assert "_id" in document_retrieved
    assert "_rev" in document_retrieved
    del document_retrieved["_id"]
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

    # Put a document to be retrieved
    if not config.options.singleton_will_already_exist:
        document = document_factory()
        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                config.database_unsafe_update_document_parameter: document,
            }
        )
        assert result.inserted_count

    # Retrieve the document directly via database
    document_database = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # To store an updated document, remove the "_id"
    document_update = copy.deepcopy(document_database)
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

    assert document_database["_id"] != document_updated["_id"]
    assert document_database["_rev"] != document_updated["_rev"]

    # Retrieve the document again
    document_database = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Confirm it matches updated document
    assert document_updated["_id"] == document_database["_id"]
    assert document_updated["_rev"] == document_database["_rev"]


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

    # Put a document to be retrieved
    if not config.options.singleton_will_already_exist:
        document = document_factory()
        result = config.database_unsafe_update_function(
            **{
                "collection": temp_patient.collection,
                config.database_unsafe_update_document_parameter: document,
            }
        )
        assert result.inserted_count

    # Retrieve the document directly via database
    document_database = config.database_get_function(
        **{
            "collection": temp_patient.collection,
        }
    )

    # Attempting to store the same document without any "_rev" should fail,
    # because it will result in a duplicate on "_rev" == 1
    document_update = copy.deepcopy(document_database)
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

    # Attempting to store the previous document should fail,
    # because it will result a conflict on that same "_rev"
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
