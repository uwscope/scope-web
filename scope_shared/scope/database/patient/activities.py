import copy
import datetime
from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_activities
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

    activity_set_post_result = scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=activity,
    )
    scope.database.patient.scheduled_activities.create_and_post_scheduled_activities(
        collection=collection,
        activity=activity_set_post_result.document,
        weeks=12,  # ~ 3 months
        activity_method="post",
    )

    return activity_set_post_result


def put_activity(
    *,
    collection: pymongo.collection.Collection,
    activity: dict,
    set_id: str,
) -> scope.database.collection_utils.SetPutResult:
    """
    Put "activity" document.
    """

    activity_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=activity,
    )
    activity = activity_set_put_result.document

    scope.database.patient.scheduled_activities.get_filter_and_put_scheduled_activities(
        collection=collection,
        activity=activity,
    )

    # Create and post scheduled activities.
    scope.database.patient.scheduled_activities.create_and_post_scheduled_activities(
        collection=collection,
        activity=activity,
        weeks=12,  # ~ 3 months
        activity_method="put",
    )

    return activity_set_put_result
