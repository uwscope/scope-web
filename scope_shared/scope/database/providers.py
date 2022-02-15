import base64
import hashlib
import uuid
from typing import List, Optional

import pymongo.database
import scope.database.collection_utils

PROVIDERS_COLLECTION = "providers"

# TODO: Copied from database.patients._generate_patient_id.
# Maybe can be moved to a utils file.
def _generate_provider_id() -> str:
    """
    Generate a provider_id that:
    - Is guaranteed to be URL safe.
    - Is guaranteed to be compatible with MongoDB collection naming.
    - Is expected to be unique.
    """

    # Obtain uniqueness
    generated_uuid = uuid.uuid4()
    # Manage length so these don't seem obscenely long
    generated_digest = hashlib.blake2b(generated_uuid.bytes, digest_size=6).digest()
    # Obtain URL safety and MongoDB collection name compatibility.
    generated_base64 = base64.b32encode(generated_digest).decode("ascii").casefold()

    # Remove terminating "=="
    clean_generated_base64 = generated_base64.rstrip("=")

    return clean_generated_base64


def create_provider(
    *,
    collection: pymongo.collection.Collection,
    provider: dict,
) -> dict:
    """
    Create a provider document and return the provider document.
    """

    # Obtain a unique provider ID for the provider.
    # A set element with the generate_provider_id ensures the provider_id is unique.
    generated_provider_id = _generate_provider_id()

    # Store the provider document.
    result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=provider["_type"],
        set_id=generated_provider_id,
        document=provider,
    )
    provider_document = result.document

    return provider_document
