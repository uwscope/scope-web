import copy
import json
from typing import List


def normalize_document(
    *,
    document: dict,
) -> dict:
    """
    Normalize a document.
    - Creates a deep copy as part of normalization.
    - Goal of normalization is to support equality comparison.
    - Any modification (e.g., deleting a field) may require re-normalization for equality comparison.
    - Normalization is shallow, requiring any descendents are already normalized.
    """

    normalized_document = {}
    keys_remaining = list(document.keys())

    # Dictionaries preserve order, so ensure these are first
    keys_prefix = ["_id", "_type", "_set_id", "_rev"]
    for key_current in keys_prefix:
        if key_current in keys_remaining:
            value_current = document[key_current]

            if key_current == "_id":
                # Ensure _id can serialize
                normalized_document[key_current] = str(value_current)
            else:
                normalized_document[key_current] = value_current

            keys_remaining.remove(key_current)

    # And then the remaining keys, sorted for normalization
    keys_remaining = sorted(keys_remaining)
    for key_current in keys_remaining:
        normalized_document[key_current] = document[key_current]

    return normalized_document


def _normalize_documents_key(document) -> str:
    """
    Provide a consistent sort of documents, sufficient to enable list comparison.

    For efficiency, sort documents by any "_id" field.
    If all documents in a pair of lists contain "_id" fields, this will order them for comparison.
    If only some documents contain "_id" fields, they are already not equal.

    For robustness, sort any document by its JSON encoding.
    This is obviously inefficient, but is robust to any combination of fields.
    """
    if isinstance(document, dict) and "_id" in document:
        return "_id:{}".format(document["_id"])

    return json.dumps(document, sort_keys=True)


def normalize_documents(
    *,
    documents: List[dict],
) -> List[dict]:
    """
    Normalize a list of documents.
    - Creates a deep copy as part of normalization.
    - Goal of normalization is to support equality comparison.
    - Any modification (e.g., deleting a field)
      of any element of the list
      may require re-normalization for equality comparison.
    - Normalization is shallow, requiring any descendents are already normalized.
    """

    normalized_documents = []
    for document_current in documents:
        normalized_documents.append(normalize_document(document=document_current))

    normalized_documents = sorted(normalized_documents, key=_normalize_documents_key)

    return normalized_documents
