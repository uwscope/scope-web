import copy
from typing import List, Optional

import pymongo.collection
import scope.database.collection_utils
import scope.database.patient.scheduled_activities

DOCUMENT_TYPE = "activityLog"
SEMANTIC_SET_ID = "activityLogId"
DATA_SNAPSHOT_PROPERTY = "dataSnapshot"


def _maintain_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    activity_log: dict,
) -> Optional[scope.database.collection_utils.SetPutResult]:
    scheduled_activity_id = activity_log.get(
        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID, None
    )
    if not scheduled_activity_id:
        return

    scheduled_activity_document = (
        scope.database.patient.scheduled_activities.get_scheduled_activity(
            collection=collection,
            set_id=scheduled_activity_id,
        )
    )
    if not scheduled_activity_document:
        return

    scheduled_activity_document["completed"] = True
    del scheduled_activity_document["_id"]

    scheduled_activity_put_result = (
        scope.database.patient.scheduled_activities.put_scheduled_activity(
            collection=collection,
            set_id=scheduled_activity_id,
            scheduled_activity=scheduled_activity_document,
        )
    )

    return scheduled_activity_put_result


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

    maintained_scheduled_activity_set_put_result = _maintain_scheduled_activity(
        collection=collection,
        activity_log=activity_log,
    )

    updated_activity_log = copy.deepcopy(activity_log)
    if maintained_scheduled_activity_set_put_result.inserted_count == 1:
        activity_log_data_snapshot = {
            scope.database.patient.scheduled_activities.DOCUMENT_TYPE: maintained_scheduled_activity_set_put_result.document,
        }
        updated_activity_log.update(
            {
                DATA_SNAPSHOT_PROPERTY: activity_log_data_snapshot
            }
        )

    return scope.database.collection_utils.post_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        document=updated_activity_log,
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
