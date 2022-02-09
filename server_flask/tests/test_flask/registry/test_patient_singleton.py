import copy
import http
from dataclasses import dataclass
from pprint import pprint
from typing import Callable
from urllib.parse import urljoin

import pymongo.collection
import pytest
import requests
import scope.config
import scope.database.collection_utils
import scope.database.patient.clinical_history
import scope.database.patient.patient_profile
import scope.database.patient.safety_plan
import scope.database.patient.values_inventory
import scope.database.patients
import scope.testing.fixtures_database_temp_patient
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS


@dataclass(frozen=True)
class ConfigTestPatientSingleton:
    name: str
    document_factory_fixture_name: str
    database_get_function: Callable[[...], dict]
    database_put_function: Callable[[...], scope.database.collection_utils.PutResult]
    database_put_function_document_parameter_name: str
    flask_query_type: str
    flask_response_document_key: str


TEST_CONFIGS = [
    ConfigTestPatientSingleton(
        name="profile",
        document_factory_fixture_name="data_fake_patient_profile_factory",
        database_get_function=scope.database.patient.patient_profile.get_patient_profile,
        database_put_function=scope.database.patient.patient_profile.put_patient_profile,
        database_put_function_document_parameter_name="patient_profile",
        flask_query_type="profile",
        flask_response_document_key="profile",
    ),
    ConfigTestPatientSingleton(
        name="safetyplan",
        document_factory_fixture_name="data_fake_safety_plan_factory",
        database_get_function=scope.database.patient.safety_plan.get_safety_plan,
        database_put_function=scope.database.patient.safety_plan.put_safety_plan,
        database_put_function_document_parameter_name="safety_plan",
        flask_query_type="safetyplan",
        flask_response_document_key="safetyplan",
    ),
    ConfigTestPatientSingleton(
        name="clinicalhistory",
        document_factory_fixture_name="data_fake_clinical_history_factory",
        database_get_function=scope.database.patient.clinical_history.get_clinical_history,
        database_put_function=scope.database.patient.clinical_history.put_clinical_history,
        database_put_function_document_parameter_name="clinical_history",
        flask_query_type="clinicalhistory",
        flask_response_document_key="clinicalhistory",
    ),
    # TODO: Commented because database PUT takes way too much time.
    # ConfigTestPatientSingleton(
    #     name="valuesinventory",
    #     document_factory_fixture_name="data_fake_values_inventory_factory",
    #     database_get_function=scope.database.patient.values_inventory.get_values_inventory,
    #     database_put_function=scope.database.patient.values_inventory.put_values_inventory,
    #     database_put_function_document_parameter_name="values_inventory",
    #     flask_query_type="valuesinventory",
    #     flask_response_document_key="valuesinventory",
    # ),
]


QUERY = "patient/{patient_id}/{query_type}"


@pytest.mark.parametrize(
    ["config"],
    [[config] for config in TEST_CONFIGS],
    ids=[config.name for config in TEST_CONFIGS],
)
def test_patient_singleton_get(
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
    Test retrieving a document.
    """

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture_name)

    # Store the document
    document = document_factory()
    result = config.database_put_function(
        **{
            "collection": temp_patient.collection,
            config.database_put_function_document_parameter_name: document,
        }
    )
    assert result.inserted_count == 1

    # Retrieve the document via Flask
    query = QUERY.format(
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

    # Confirm it matches expected document, with addition of an "_id" and a "_rev"
    document_retrieved = response.json()[config.flask_response_document_key]
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
    query = QUERY.format(
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
    query = query.format(
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
    query = query.format(
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

    temp_patient = database_temp_patient_factory()
    session = flask_session_unauthenticated_factory()
    document_factory = request.getfixturevalue(config.document_factory_fixture_name)

    # Store a document via Flask
    document = document_factory()
    query = QUERY.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored = response.json()[config.flask_response_document_key]
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
    document_factory = request.getfixturevalue(config.document_factory_fixture_name)

    # Invalid document that does not match any schema
    query = QUERY.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
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
    document = document_factory()
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
    document_factory = request.getfixturevalue(config.document_factory_fixture_name)

    # Store a document via Flask
    document = document_factory()
    query = QUERY.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored = response.json()[config.flask_response_document_key]

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

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_updated = response.json()[config.flask_response_document_key]

    assert document_stored["_id"] != document_updated["_id"]
    assert document_stored["_rev"] != document_updated["_rev"]

    # Retrieve the document
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
    document_factory = request.getfixturevalue(config.document_factory_fixture_name)

    # Store a document via Flask
    document = document_factory()
    query = QUERY.format(
        patient_id=temp_patient.patient_id,
        query_type=config.flask_query_type,
    )
    response = session.put(
        url=urljoin(
            flask_client_config.baseurl,
            query,
        ),
        json=document,
    )
    assert response.ok

    # Response body includes the stored document, with addition of an "_id" and a "_rev"
    document_stored_rev1 = response.json()[config.flask_response_document_key]

    # Store an update that will be assigned "_rev" == 2
    document_update = copy.deepcopy(document_stored_rev1)
    del document_update["_id"]

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
    document_conflict = response.json()[config.flask_response_document_key]
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
    document_conflict = response.json()[config.flask_response_document_key]
    assert document_conflict["_rev"] == 2
