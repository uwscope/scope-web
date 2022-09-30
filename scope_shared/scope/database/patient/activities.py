import copy
import datetime
from typing import List, Optional
import pymongo.collection
import pytz

import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_activities
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.schema
import scope.schema_utils as schema_utils


DOCUMENT_TYPE = "activity"
SEMANTIC_SET_ID = "activityId"


def get_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "activity" documents.
    """

    return scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )


def get_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "activity" document.
    """

    return scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )


def post_activity(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "activity" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=activity,
    )


def put_activity(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "activity" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity,
    )
