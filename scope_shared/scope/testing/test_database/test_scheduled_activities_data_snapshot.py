"""
In addition to its standard set properties,
a put to scope.database.patient.activites and scope.database.patient.values must maintain data snapshot property in the scheduled activities.
"""

import copy
import datetime
import pytest
import pytz
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.activity_schedules
import scope.database.patient.scheduled_activities
import scope.database.patient.values
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient

from scope.database.scheduled_item_utils import _localized_datetime


def test_scheduled_activities_maintains_data_snapshot(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_factory: Callable[[], dict],
    data_fake_activity_schedule_factory: Callable[[], dict],
    data_fake_scheduled_activity_factory: Callable[[], dict],
    data_fake_value_factory: Callable[[], dict],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake value and store in db
    fake_value = data_fake_value_factory()
    fake_value_post_result = scope.database.patient.values.post_value(
        collection=patient_collection, value=fake_value
    )
    assert fake_value_post_result.inserted_count == 1
    inserted_fake_value = fake_value_post_result.document

    # Obtain fake activity, ensure it references the fake value, and store in db
    fake_activity = data_fake_activity_factory()
    fake_activity.update(
        {
            scope.database.patient.values.SEMANTIC_SET_ID: inserted_fake_value[
                scope.database.patient.values.SEMANTIC_SET_ID
            ],
        }
    )
    scope.schema_utils.assert_schema(
        data=fake_activity,
        schema=scope.schema.activity_schema,
        expected_valid=True,
    )
    fake_activity_post_result = scope.database.patient.activities.post_activity(
        collection=patient_collection, activity=fake_activity
    )
    assert fake_activity_post_result.inserted_count == 1
    inserted_fake_activity = fake_activity_post_result.document

    # Create an activity schedule, ensure it is in the future, ensure it references the fake activity, and store in db
    fake_activity_schedule = {
        "_type": scope.database.patient.activity_schedules.DOCUMENT_TYPE,
        scope.database.patient.activities.SEMANTIC_SET_ID: inserted_fake_activity[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ],
        "date": date_utils.format_date(
            datetime.date.today() + datetime.timedelta(days=10)
        ),
        "timeOfDay": 9,
        "hasReminder": False,
        "hasRepetition": False,
        "editedDateTime": date_utils.format_datetime(
            pytz.utc.localize(datetime.datetime.now())
        ),
    }
    scope.schema_utils.assert_schema(
        data=fake_activity_schedule,
        schema=scope.schema.activity_schedule_schema,
        expected_valid=True,
    )
    fake_activity_schedule_post_result = (
        scope.database.patient.activity_schedules.post_activity_schedule(
            collection=patient_collection,
            activity_schedule=fake_activity_schedule,
        )
    )
    assert fake_activity_schedule_post_result.inserted_count == 1
    inserted_fake_activity_schedule = fake_activity_schedule_post_result.document

    # Insertion of the activity schedule should create exactly one matching scheduled activity document
    scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection,
        )
    )
    scheduled_activities = [
        scheduled_activity_current
        for scheduled_activity_current in scheduled_activities
        if scheduled_activity_current[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ]
        == inserted_fake_activity_schedule[
            scope.database.patient.activity_schedules.SEMANTIC_SET_ID
        ]
    ]
    assert len(scheduled_activities) == 1
    original_scheduled_activity = scheduled_activities[0]

    # The snapsot in that scheduled activity should match our fields
    assert (
        original_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.values.DOCUMENT_TYPE]
        == inserted_fake_value
    )
    assert (
        original_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activities.DOCUMENT_TYPE]
        == inserted_fake_activity
    )
    assert (
        original_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activity_schedules.DOCUMENT_TYPE]
        == inserted_fake_activity_schedule
    )

    # Create another scheduled activity in the past
    fake_scheduled_activity_in_past = copy.deepcopy(original_scheduled_activity)
    del fake_scheduled_activity_in_past["_id"]
    del fake_scheduled_activity_in_past["_set_id"]
    del fake_scheduled_activity_in_past[
        scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
    ]
    del fake_scheduled_activity_in_past["_rev"]
    fake_scheduled_activity_in_past.update(
        {
            "dueDate": date_utils.format_date(
                datetime.date.today() - datetime.timedelta(days=10)
            ),
            "dueDateTime": date_utils.format_datetime(
                _localized_datetime(
                    date=datetime.date.today() - datetime.timedelta(days=10),
                    time_of_day=fake_scheduled_activity_in_past["dueTimeOfDay"],
                    timezone=pytz.timezone("US/Pacific"),
                )
            ),
        }
    )
    scope.schema_utils.assert_schema(
        data=fake_scheduled_activity_in_past,
        schema=scope.schema.scheduled_activity_schema,
        expected_valid=True,
    )
    fake_scheduled_activity_in_past_post_result = (
        scope.database.patient.scheduled_activities.post_scheduled_activity(
            collection=patient_collection,
            scheduled_activity=fake_scheduled_activity_in_past,
        )
    )
    assert fake_scheduled_activity_in_past_post_result.inserted_count == 1
    fake_scheduled_activity_in_past = (
        fake_scheduled_activity_in_past_post_result.document
    )

    # A change to the underlying value should result in a change to the snapshot

    # Update the value
    updated_fake_value = copy.deepcopy(inserted_fake_value)
    updated_fake_value.update(
        {
            "name": data_fake_value_factory()["name"],
        }
    )
    del updated_fake_value["_id"]
    updated_fake_value_put_result = scope.database.patient.values.put_value(
        collection=patient_collection,
        value=updated_fake_value,
        set_id=updated_fake_value[scope.database.patient.values.SEMANTIC_SET_ID],
    )
    assert updated_fake_value_put_result.inserted_count == 1
    updated_fake_value = updated_fake_value_put_result.document

    # The old and new value must not be the same
    assert inserted_fake_value != updated_fake_value

    # Get the current scheduled activity
    updated_scheduled_activity = (
        scope.database.patient.scheduled_activities.get_scheduled_activity(
            collection=patient_collection,
            set_id=original_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
        )
    )

    # The new value should be present
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.values.DOCUMENT_TYPE]
        == updated_fake_value
    )

    # But still the previous activity and activity schedule
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activities.DOCUMENT_TYPE]
        == inserted_fake_activity
    )
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activity_schedules.DOCUMENT_TYPE]
        == inserted_fake_activity_schedule
    )

    # A change to the underlying activity should result in a change to the snapshot

    # Update the activity
    updated_fake_activity = copy.deepcopy(inserted_fake_activity)
    updated_fake_activity.update(
        {
            "name": data_fake_activity_factory()["name"],
        }
    )
    del updated_fake_activity["_id"]
    updated_fake_activity_put_result = scope.database.patient.activities.put_activity(
        collection=patient_collection,
        activity=updated_fake_activity,
        set_id=updated_fake_activity[scope.database.patient.activities.SEMANTIC_SET_ID],
    )
    assert updated_fake_activity_put_result.inserted_count == 1
    updated_fake_activity = updated_fake_activity_put_result.document

    # The old and new activity must not be the same
    assert inserted_fake_activity != updated_fake_activity

    # Get the current scheduled activity
    updated_scheduled_activity = (
        scope.database.patient.scheduled_activities.get_scheduled_activity(
            collection=patient_collection,
            set_id=original_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
        )
    )

    # The new value and activity should be present
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.values.DOCUMENT_TYPE]
        == updated_fake_value
    )
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activities.DOCUMENT_TYPE]
        == updated_fake_activity
    )

    # But still the previous activity schedule
    assert (
        updated_scheduled_activity[
            scope.database.patient.scheduled_activities.DATA_SNAPSHOT_PROPERTY
        ][scope.database.patient.activity_schedules.DOCUMENT_TYPE]
        == inserted_fake_activity_schedule
    )

    # The scheduled activity in the past should not have changed

    updated_fake_scheduled_activity_in_past = (
        scope.database.patient.scheduled_activities.get_scheduled_activity(
            collection=patient_collection,
            set_id=fake_scheduled_activity_in_past[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
        )
    )
    assert fake_scheduled_activity_in_past == updated_fake_scheduled_activity_in_past

    # Modifying the activity schedule is not tested because that destroys / creates entire scheduled activity objects
