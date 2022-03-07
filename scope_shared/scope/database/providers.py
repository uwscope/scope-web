import pymongo.database
import scope.database.collection_utils as collection_utils
from typing import List, Optional

import scope.database.collection_utils

PROVIDER_IDENTITY_COLLECTION = "providers"

PROVIDER_IDENTITY_DOCUMENT_TYPE = "providerIdentity"
PROVIDER_IDENTITY_SEMANTIC_SET_ID = "providerId"


def create_provider(
    *,
    database: pymongo.database.Database,
    name: str,
    role: str,
) -> dict:
    """
    Create a provider. This includes:
    - Finally, create and return the provider identity document.
    """

    provider_identity_collection = database.get_collection(PROVIDER_IDENTITY_COLLECTION)

    # Obtain a unique ID for the provider
    provider_id = scope.database.collection_utils.generate_set_id()

    # Ensure this provider id does not already exist
    if (
        scope.database.providers.get_provider_identity(
            database=database, provider_id=provider_id
        )
        is not None
    ):
        raise ValueError('Provider "{}" already exists'.format(provider_id))

    # Atomically store the provider identity document.
    # Do this last, because it means all other steps have already succeeded.
    provider_identity_document = {
        "_type": scope.database.providers.PROVIDER_IDENTITY_DOCUMENT_TYPE,
        "name": name,
        "role": role,
    }
    result = scope.database.collection_utils.put_set_element(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
        semantic_set_id=PROVIDER_IDENTITY_SEMANTIC_SET_ID,
        set_id=provider_id,
        document=provider_identity_document,
    )
    provider_identity_document = result.document

    return provider_identity_document


def delete_provider(
    *,
    database: pymongo.database.Database,
    provider_id: str,
    destructive: bool,
):
    """
    Delete a provider identity.
    """

    if not destructive:
        raise NotImplementedError()

    provider_identity_collection = database.get_collection(PROVIDER_IDENTITY_COLLECTION)

    # Confirm the provider exists.
    provider_identity_document = scope.database.collection_utils.get_set_element(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
        set_id=provider_id,
    )
    if provider_identity_document is None:
        return False

    # Atomically delete the identity first, then delete all other traces of the provider.
    scope.database.collection_utils.delete_set_element(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
        set_id=provider_id,
        destructive=destructive,
    )

    return True


def get_provider_identity(
    *,
    database: pymongo.database.Database,
    provider_id: str,
) -> Optional[dict]:
    """
    Retrieve a provider identity document.
    """

    provider_identity_collection = database.get_collection(PROVIDER_IDENTITY_COLLECTION)

    return scope.database.collection_utils.get_set_element(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
        set_id=provider_id,
    )


def put_provider_identity(
    *,
    database: pymongo.database.Database,
    provider_id: str,
    provider_identity: dict,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put a provider identity document.
    """

    provider_identity_collection = database.get_collection(PROVIDER_IDENTITY_COLLECTION)

    return scope.database.collection_utils.put_set_element(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
        semantic_set_id=PROVIDER_IDENTITY_SEMANTIC_SET_ID,
        set_id=provider_id,
        document=provider_identity,
    )


def get_provider_identities(
    *,
    database: pymongo.database.Database,
) -> Optional[List[dict]]:
    """
    Retrieve all provider identity documents.
    """

    provider_identity_collection = database.get_collection(PROVIDER_IDENTITY_COLLECTION)

    return scope.database.collection_utils.get_set(
        collection=provider_identity_collection,
        document_type=PROVIDER_IDENTITY_DOCUMENT_TYPE,
    )
