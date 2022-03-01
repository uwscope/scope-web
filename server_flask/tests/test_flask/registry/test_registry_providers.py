import http
import requests
from typing import Callable
from urllib.parse import urljoin

import scope.config
import scope.database.collection_utils as collection_utils
import scope.database.providers
import scope.schema
import scope.schema_utils as schema_utils
import scope.testing.fixtures_database_temp_provider
import tests.testing_config

TESTING_CONFIGS = tests.testing_config.ALL_CONFIGS

QUERY_PROVIDERS = "providers"
QUERY_PROVIDER = "provider/{provider_id}"


def test_provider_identities_get(
    database_temp_provider_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_provider.DatabaseTempProvider,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving providers.
    """

    session = flask_session_unauthenticated_factory()

    created_ids = [database_temp_provider_factory().provider_id for _ in range(5)]

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PROVIDERS,
        ),
    )
    assert response.ok

    assert "providers" in response.json()
    provider_identities = response.json()["providers"]
    for provider_identity_current in provider_identities:
        schema_utils.assert_schema(
            data=provider_identity_current,
            schema=scope.schema.provider_identity_schema,
        )

    retrieved_ids = [
        provider_identity_current[
            scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
        ]
        for provider_identity_current in provider_identities
    ]
    assert all(provider_id in retrieved_ids for provider_id in created_ids)

    schema_utils.assert_schema(
        data=response.json()["providers"],
        schema=scope.schema.provider_identities_schema,
    )


def test_provider_identity_get(
    database_temp_provider_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_provider.DatabaseTempProvider,
    ],
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test retrieving a provider.
    """

    session = flask_session_unauthenticated_factory()

    created_id = database_temp_provider_factory().provider_id

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PROVIDER.format(provider_id=created_id),
        ),
    )
    assert response.ok

    assert "provider" in response.json()
    provider_identity = response.json()["provider"]
    schema_utils.assert_schema(
        data=provider_identity,
        schema=scope.schema.provider_identity_schema,
    )

    provider_id = provider_identity[
        scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
    ]
    assert provider_id == created_id


def test_provider_identity_get_invalid(
    flask_client_config: scope.config.FlaskClientConfig,
    flask_session_unauthenticated_factory: Callable[[], requests.Session],
):
    """
    Test non-existent provider yields 404.
    """

    session = flask_session_unauthenticated_factory()

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PROVIDER.format(provider_id="invalid"),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND

    response = session.get(
        url=urljoin(
            flask_client_config.baseurl,
            QUERY_PROVIDER.format(provider_id=collection_utils.generate_set_id()),
        ),
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND
