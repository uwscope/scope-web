import copy
import json
from typing import List


def normalize_document(
    *,
    document: dict,
) -> dict:
    """
    Obtain a new document in normalized format.

    Creates a deep copy as part of normalization.
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
                normalized_document[key_current] = normalize_value(value=value_current)

            keys_remaining.remove(key_current)

    # And then the remaining keys, sorted for normalization
    keys_remaining = sorted(keys_remaining)
    for key_current in keys_remaining:
        normalized_document[key_current] = normalize_value(value=document[key_current])

    return normalized_document


def _normalize_documents_key(document) -> str:
    """
    Provide a consistent sort of documents.

    For efficiency, sort documents by any "_id" field.
    For robustness, sort anything by its JSON encoding.
    This is obviously inefficient, but is stable for now.
    """
    if isinstance(document, dict) and "_id" in document:
        return "_id:{}".format(document["_id"])

    return json.dumps(document, sort_keys=True)


def normalize_documents(
    *,
    documents: List[dict],
) -> List[dict]:
    """
    Obtain a new list of documents in normalized format.

    Creates a deep copy as part of normalization.
    """

    normalized_documents = []
    for document_current in documents:
        normalized_documents.append(normalize_document(document=document_current))

    normalized_documents = sorted(normalized_documents, key=_normalize_documents_key)

    return normalized_documents


def normalize_value(
    *,
    value: object,
) -> object:
    # Normalize a dict
    if isinstance(value, dict):
        return normalize_document(document=value)

    # Normalize a list where every element is a dict
    if isinstance(value, list):
        if all([isinstance(item_current, dict) for item_current in value]):
            return normalize_documents(documents=value)

    return copy.deepcopy(value)
