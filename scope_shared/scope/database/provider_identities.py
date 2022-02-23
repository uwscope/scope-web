import base64
import hashlib
import uuid
from typing import List, Optional

import pymongo.database
import scope.database.collection_utils as collection_utils

PROVIDERS_COLLECTION = "providers"


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
        set_id=collection_utils.generate_set_id(),
        document=provider,
    )
    provider_document = result.document

    return provider_document
