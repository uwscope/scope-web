from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "activityLog"
SEMANTIC_SET_ID = "activityLogId"


def get_activity_logs(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "activityLog" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_activity_log(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "activityLog" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_activity_log(
    *,
    collection: pymongo.collection.Collection,
    activity_log: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "activityLog" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=activity_log,
    )


def put_activity_log(
    *,
    collection: pymongo.collection.Collection,
    activity_log: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "activityLog" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity_log,
    )
