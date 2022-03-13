"""
In addition to its standard set properties,
a put to scope.database.patient.activities must maintain the scheduled activities.
"""

import datetime
import pytest
import pytz
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.testing.fixtures_database_temp_patient


@pytest.mark.skip("all tests still WIP")

# TODO: Needs to test "POST" and "PUT" both.


def test_activity_maintains_scheduled_activities(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_factory: Callable[[], dict],
):
    """
    Test that the scheduled activities are maintained.

    The actual logic of scheduling specific activities is tested elsewhere.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake activity to use as template
    fake_activity = data_fake_activity_factory()
    stored_activity = scope.database.patient.activities.post_activity(
        collection=patient_collection,
        activity=fake_activity,
    )
    stored_activity = data_fake_activity_factory

    # Remove assignment of the activity
    fake_activity.update(
        {
            "assigned": False,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity(
        collection=patient_collection,
        set_id=stored_activity.inserted_set_id,
        activity=fake_activity,
    )

    # Determine what scheduled activities already exist
    existing_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    if not existing_scheduled_activities:
        existing_scheduled_activities = []

    # Assign the activity
    fake_activity.update(
        {
            "assigned": True,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
            "frequency": scope.enums.ScheduledItemFrequency.Weekly.value,
        }
    )
    patient_unsafe_utils.unsafe_update_activity(
        collection=patient_collection,
        set_id=activity_id,
        activity=fake_activity,
    )

    # Ensure we now obtain new scheduled activities
    new_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    new_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in new_scheduled_activities
        if scheduled_activity_current not in existing_scheduled_activities
    ]
    assert len(new_scheduled_activities) > 0

    # Remove assignment of the activity
    fake_activity.update(
        {
            "assigned": False,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_activity(
        collection=patient_collection,
        set_id=activity_id,
        activity=fake_activity,
    )

    # Ensure there are no pending scheduled activities
    # Because pending logic is already tested,
    # this confirms cancellation while being robust to an item created in this test which is now in the past
    existing_scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
    )
    if not existing_scheduled_activities:
        existing_scheduled_activities = []

    existing_scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in existing_scheduled_activities
        if scheduled_activity_current[scope.database.patient.activities.SEMANTIC_SET_ID]
        == activity_id
    ]

    pending_scheduled_activities = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=existing_scheduled_activities,
        after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
    )

    assert len(pending_scheduled_activities) == 0
