import copy
import datetime
from typing import List, Optional, Union
import pymongo.collection


import scope.database.collection_utils
import scope.database.patient.activities
import scope.database.patient.values
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.schema


DOCUMENT_TYPE = "scheduledActivity"
SEMANTIC_SET_ID = "scheduledActivityId"
DATA_SNAPSHOT_PROPERTY = "dataSnapshot"


def _build_data_snapshot(
    *,
    collection: pymongo.collection.Collection,
    scheduled_activity: dict,
) -> dict:

    data_snapshot = copy.deepcopy(scheduled_activity.get(DATA_SNAPSHOT_PROPERTY, None))

    activity_id = data_snapshot[scope.database.patient.activities.DOCUMENT_TYPE][
        scope.database.patient.activities.SEMANTIC_SET_ID
    ]

    value_id = None
    value_document = data_snapshot.get(
        scope.database.patient.values.DOCUMENT_TYPE, None
    )
    if value_document:
        value_id = value_document[scope.database.patient.values.SEMANTIC_SET_ID]

    # Update activity
    data_snapshot.update(
        {
            scope.database.patient.activities.DOCUMENT_TYPE: scope.database.patient.activities.get_activity(
                collection=collection, set_id=activity_id
            )
        }
    )

    # Update value if value_id is not None
    if value_id:
        data_snapshot.update(
            {
                scope.database.patient.values.DOCUMENT_TYPE: scope.database.patient.values.get_value(
                    collection=collection, set_id=value_id
                )
            }
        )

    return data_snapshot


def delete_scheduled_activity(
    *,
    collection: pymongo.collection.Collection,
    set_id: str,
    rev: int,
) -> scope.database.collection_utils.SetPutResult:
    """
    Delete "scheduled-activity" document.
    """

    return scope.database.collection_utils.delete_set_element(
        collection=collection,
        document_type=DOCUMENT_TYPE,
        set_id=set_id,
        rev=rev,
    )


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

    return scheduled_activities


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

    return scheduled_activity


def maintain_scheduled_activities_data_snapshot(
    *,
    collection: pymongo.collection.Collection,
    maintenance_datetime: datetime.datetime,
) -> Union[List[scope.database.collection_utils.SetPutResult], None]:

    # Compute pending scheduled activities
    pending_scheduled_activities = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=get_scheduled_activities(
            collection=collection,
        ),
        after_datetime=maintenance_datetime,
    )

    if not pending_scheduled_activities:
        return

    scheduled_activities_pending_update = []
    for scheduled_activity_current in pending_scheduled_activities:
        # Calculate a new value for data snapshot
        new_data_snapshot = _build_data_snapshot(
            collection=collection,
            scheduled_activity=scheduled_activity_current,
        )

        # If data snapshot changed, update scheduled activity and add it to pending update list
        if new_data_snapshot != scheduled_activity_current.get(
            DATA_SNAPSHOT_PROPERTY, None
        ):
            scheduled_activity_current.update(
                {DATA_SNAPSHOT_PROPERTY: new_data_snapshot}
            )
            scheduled_activities_pending_update.append(scheduled_activity_current)

    if not scheduled_activities_pending_update:
        return

    # Issue the updates for scheduled activities in pending update list
    scheduled_activity_put_results = []
    for scheduled_activity_current in scheduled_activities_pending_update:
        del scheduled_activity_current["_id"]
        scheduled_activity_put_results.append(
            put_scheduled_activity(
                collection=collection,
                set_id=scheduled_activity_current[SEMANTIC_SET_ID],
                scheduled_activity=scheduled_activity_current,
            )
        )

    return scheduled_activity_put_results


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
