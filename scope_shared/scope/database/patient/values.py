from typing import List, Optional
from numpy import integer

import pymongo.collection
import scope.database.collection_utils
import scope.database.patient.activities

DOCUMENT_TYPE = "value"
SEMANTIC_SET_ID = "valueId"


def delete_value(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    rev: integer,
) -> scope.database.collection_utils.SetPutResult:
    """
    Delete "value" document.

    - Any existing activities with the deleted value must be modified to have no value.
    """
    existing_activities = scope.database.patient.activities.get_activities(
        collection=collection
    )
    if existing_activities:
        for activity in existing_activities:
            if activity.get(SEMANTIC_SET_ID) == set_id:
                del activity["_id"]
                del activity[SEMANTIC_SET_ID]
                scope.database.patient.activities.put_activity(
                    collection=collection,
                    activity=activity,
                    set_id=activity[scope.database.patient.activities.SEMANTIC_SET_ID],
                )

    return scope.database.collection_utils.delete_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        rev=rev,
    )


def get_values(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "value" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_value(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "value" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_value(
    *,
    collection: pymongo.collection.Collection,
    value: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "value" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=value,
    )


def put_value(
    *,
    collection: pymongo.collection.Collection,
    value: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "value" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=value,
    )
