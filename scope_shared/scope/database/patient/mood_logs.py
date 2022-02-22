from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils

DOCUMENT_TYPE = "moodLog"
SEMANTIC_SET_ID = "moodLogId"


def get_mood_logs(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "moodLog" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_mood_log(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "moodLog" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_mood_log(
    *,
    collection: pymongo.collection.Collection,
    mood_log: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "moodLog" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=mood_log,
    )


def put_mood_log(
    *,
    collection: pymongo.collection.Collection,
    mood_log: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "moodLog" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=mood_log,
    )
