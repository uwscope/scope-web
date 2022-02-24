import pymongo.database
import scope.database.collection_utils as collection_utils

PROVIDER_IDENTITY_COLLECTION = "providers"

PROVIDER_IDENTITY_DOCUMENT_TYPE = "providerIdentity"
PROVIDER_IDENTITY_SEMANTIC_SET_ID = "providerId"


def create_provider(
    *,
    collection: pymongo.collection.Collection,
    provider: dict,
) -> dict:
    """
    Create a provider document and return the provider document.
    """

    # Store the provider document.
    result = collection_utils.put_set_element(
        collection=collection,
        document_type=provider["_type"],
        semantic_set_id=PROVIDER_IDENTITY_SEMANTIC_SET_ID,
        set_id=collection_utils.generate_set_id(),
        document=provider,
    )
    provider_document = result.document

    return provider_document
