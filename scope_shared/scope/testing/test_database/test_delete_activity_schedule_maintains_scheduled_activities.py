"""
A delete to scope.database.patient.activity_schedules must delete the associated scheduled activities.
"""

import datetime
from typing import Callable

import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.activity_schedules
import scope.database.patient.scheduled_activities
import scope.database.patients
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient


def test_delete_activity_schedule_maintains_scheduled_activities(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_factory: Callable[[], dict],
    data_fake_activity_schedule_factory: Callable[[], dict],
    data_fake_value_factory: Callable[[], dict],
):
    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake activity
    fake_activity = data_fake_activity_factory()

    # If activity is associated to a value, insert the value into db.
    if scope.database.patient.values.SEMANTIC_SET_ID in fake_activity:
        fake_value = data_fake_value_factory()
        fake_value_post_result = scope.database.patient.values.post_value(
            collection=patient_collection,
            value=fake_value,
        )
        assert fake_value_post_result.inserted_count == 1
        inserted_fake_value = fake_value_post_result.document
        fake_activity.update(
            {
                scope.database.patient.values.SEMANTIC_SET_ID: inserted_fake_value[
                    scope.database.patient.values.SEMANTIC_SET_ID
                ]
            }
        )
    fake_activity_post_result = scope.database.patient.activities.post_activity(
        collection=patient_collection,
        activity=fake_activity,
    )
    assert fake_activity_post_result.inserted_count == 1
    inserted_fake_activity = fake_activity_post_result.document

    # Obtain fake activity schedule
    fake_activity_schedule = data_fake_activity_schedule_factory()
    # Ensure the date is in the future so maintenance will result in deletion
    fake_activity_schedule.update(
        {
            "date": date_utils.format_date(
                datetime.date.today() + datetime.timedelta(days=1)
            ),
            "activityId": inserted_fake_activity["activityId"],
        }
    )

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

    # Get scheduled activities matching "activityScheduleId"
    scheduled_activities_matching_activity_schedule_id = [
        scheduled_activity_current
        for scheduled_activity_current in scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
        if scheduled_activity_current.get("activityScheduleId")
        == inserted_fake_activity_schedule["activityScheduleId"]
    ]
    assert len(scheduled_activities_matching_activity_schedule_id) > 0

    # Delete activity schedule
    delete_activity_schedule_put_result = (
        scope.database.patient.activity_schedules.delete_activity_schedule(
            collection=patient_collection,
            set_id=inserted_fake_activity_schedule[
                scope.database.patient.activity_schedules.SEMANTIC_SET_ID
            ],
            rev=inserted_fake_activity_schedule.get("_rev"),
        )
    )
    assert delete_activity_schedule_put_result.inserted_count == 1

    # Get scheduled activities
    scheduled_activities_matching_activity_schedule_id = [
        scheduled_activity_current
        for scheduled_activity_current in scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection
        )
        if scheduled_activity_current.get("activityScheduleId")
        == inserted_fake_activity_schedule["activityScheduleId"]
    ]
    assert len(scheduled_activities_matching_activity_schedule_id) == 0
