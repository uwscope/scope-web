import copy
from typing import List, Optional
import pymongo.collection
import pytest

import scope.database.collection_utils
import scope.database.patient.activities
import scope.schema
import scope.schema_utils as schema_utils


DOCUMENT_TYPE = "scheduledActivity"
SEMANTIC_SET_ID = "scheduledActivityId"


def get_scheduled_activities(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "scheduledAactivity" documents.
    """

    scheduled_activities = scope.database.collection_utils.get_set(
        collection=collection,
        document_type=DOCUMENT_TYPE,
    )

    if scheduled_activities:
        scheduled_activities = [
            scheduled_activity_current
            for scheduled_activity_current in scheduled_activities
            if not scheduled_activity_current.get("_deleted", False)
        ]

    return scheduled_activities


def delete_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    scheduled_activity = copy.deepcopy(scheduled_activity)

    scheduled_activity["_deleted"] = True
    del scheduled_activity["_id"]

    schema_utils.assert_schema(
        data=scheduled_activity,
        schema=scope.schema.scheduled_activity_schema,
    )

    return put_scheduled_activity(
        collection=collection,
        scheduled_activity=scheduled_activity,
        set_id=set_id,
    )


def get_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
) -> Optional[dict]:
    """
    Get "scheduleActivity" document.
    """

    scheduled_activity = scope.database.collection_utils.get_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
    )

    if scheduled_activity:
        if scheduled_activity.get("_deleted", False):
            scheduled_activity = None

    return scheduled_activity


def post_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
) -> scope.database.collection_utils.SetPostResult:
    """
    Post "scheduleActivity" document.
    """

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=scheduled_activity,
    )


def put_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "scheduleActivity" document.
    """

    return scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=scheduled_activity,
    )
