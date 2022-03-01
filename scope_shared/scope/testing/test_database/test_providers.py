import copy
from typing import Callable

import pymongo.database
import scope.database.providers
import scope.schema
import scope.schema_utils as schema_utils


def test_provider_create_get_delete(
    database_client: pymongo.database.Database,
    data_fake_provider_identity_factory: Callable[[], dict],
):
    """
    Test that creates and deletes a provider.
    """

    data_fake_provider = data_fake_provider_identity_factory()

    # Create provider
    created_provider_identity = scope.database.providers.create_provider(
        database=database_client,
        name=data_fake_provider["name"],
        role=data_fake_provider["role"],
    )

    try:
        schema_utils.assert_schema(
            data=created_provider_identity,
            schema=scope.schema.provider_identity_schema,
        )

        # Confirm get provider identity via _set_id
        retrieved_identity_document = scope.database.providers.get_provider_identity(
            database=database_client,
            provider_id=created_provider_identity["_set_id"],
        )
        assert retrieved_identity_document == created_provider_identity

        # Confirm get provider identity via semantic set id
        retrieved_identity_document = scope.database.providers.get_provider_identity(
            database=database_client,
            provider_id=created_provider_identity[
                scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
            ],
        )
        assert retrieved_identity_document == created_provider_identity

        # Confirm provider identity in list of provider identities
        provider_identities = scope.database.providers.get_provider_identities(
            database=database_client
        )
        assert created_provider_identity in provider_identities

    finally:
        # Delete provider
        result = scope.database.providers.delete_provider(
            database=database_client,
            provider_id=created_provider_identity["_set_id"],
            destructive=True,
        )
        assert result

    # Confirm get provider identity now fails
    retrieved_identity_document = scope.database.providers.get_provider_identity(
        database=database_client,
        provider_id=created_provider_identity["_set_id"],
    )
    assert retrieved_identity_document is None

    # Confirm provider identity not in list of provider identities
    provider_identities = scope.database.providers.get_provider_identities(
        database=database_client
    )
    if provider_identities:
        assert created_provider_identity not in provider_identities


def test_provider_delete_nonexistent(
    database_client: pymongo.database.Database,
):
    """
    Test that attempts to delete a provider that does not exist.
    """

    # Attempting to delete should fail
    result = scope.database.providers.delete_provider(
        database=database_client,
        provider_id="invalid",
        destructive=True,
    )
    assert not result


def test_provider_identity_update(
    database_client: pymongo.database.Database,
    data_fake_provider_identity_factory: Callable[[], dict],
):
    """
    Test updating a provider identity.
    """

    data_fake_provider = data_fake_provider_identity_factory()

    # Create provider
    created_provider_identity = scope.database.providers.create_provider(
        database=database_client,
        name=data_fake_provider["name"],
        role=data_fake_provider["role"],
    )
    created_provider_id = created_provider_identity[
        scope.database.providers.PROVIDER_IDENTITY_SEMANTIC_SET_ID
    ]

    try:
        schema_utils.assert_schema(
            data=created_provider_identity,
            schema=scope.schema.provider_identity_schema,
        )

        # Modify the identity
        modified_provider_identity = copy.deepcopy(created_provider_identity)
        modified_provider_identity["name"] = "MODIFIED NAME"
        del modified_provider_identity["_id"]

        result = scope.database.providers.put_provider_identity(
            database=database_client,
            provider_id=created_provider_id,
            provider_identity=modified_provider_identity,
        )

        assert result.inserted_count == 1
        assert result.document["_rev"] == 2
    finally:
        scope.database.providers.delete_provider(
            database=database_client,
            provider_id=created_provider_id,
            destructive=True,
        )
