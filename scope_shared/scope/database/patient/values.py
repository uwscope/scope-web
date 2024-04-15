import datetime
import pymongo.collection
import pytz
from typing import List, Optional

import scope.database.collection_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities


DOCUMENT_TYPE = "value"
SEMANTIC_SET_ID = "valueId"


def delete_value(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    rev: int,
) -> scope.database.collection_utils.SetPutResult:
    """
    Delete "value" document.

    - Any existing activities with the deleted value must be modified to have no value.
    - Modifying the activity will trigger updates to any ScheduledActivities that have a snapshot of this.
    """

    result = scope.database.collection_utils.delete_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        rev=rev,
    )

    if result.inserted_count == 1:
        existing_activities = scope.database.patient.activities.get_activities(
            collection=collection
        )

        for activity in existing_activities:
            if activity.get(SEMANTIC_SET_ID) == set_id:
                del activity["_id"]
                del activity[SEMANTIC_SET_ID]
                scope.database.patient.activities.put_activity(
                    collection=collection,
                    activity=activity,
                    set_id=activity[scope.database.patient.activities.SEMANTIC_SET_ID],
                )

    return result


def get_values(
    *,
    collection: pymongo.collection.Collection,
) -> Optional[List[dict]]:
    """
    Get list of "value" documents.
    """

    # patients.py/_construct_patient_document
    # currently assumes this access does nothing to retrieved documents.
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

    - Because ScheduledActivity documents may reference this activity, their snapshots must be updated.
    """

    value_set_put_result = scope.database.collection_utils.put_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        semantic_set_id=SEMANTIC_SET_ID,
        set_id=set_id,
        document=value,
    )

    if value_set_put_result.inserted_count == 1:
        scope.database.patient.scheduled_activities.maintain_scheduled_activities_data_snapshot(
            collection=collection,
            maintenance_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
        )

    return value_set_put_result
