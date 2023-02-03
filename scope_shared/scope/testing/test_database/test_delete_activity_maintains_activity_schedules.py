"""
A delete to scope.database.patient.activities must delete the associated activity schedules.
"""

import datetime
from typing import Callable, List

import scope.database.collection_utils as collection_utils
import scope.database.patient.activity_schedules
import scope.database.patient.activities
import scope.database.patient.values
import scope.database.patients
import scope.enums
import scope.schema
import scope.schema_utils
import scope.testing.fixtures_database_temp_patient


def test_delete_activity_maintains_activity_schedules(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_activity_factory: Callable[[], dict],
    data_fake_activity_schedules_factory: Callable[[], List[dict]],
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

    # Obtain fake activity schedules, update their "activityId", and insert them into db.
    fake_activity_schedules_with_activity_id = data_fake_activity_schedules_factory()
    for _fake_activity_schedule in fake_activity_schedules_with_activity_id:
        _fake_activity_schedule.update(
            {"activityId": inserted_fake_activity["activityId"]}
        )
        _fake_activity_schedule_post_result = (
            scope.database.patient.activity_schedules.post_activity_schedule(
                collection=patient_collection,
                activity_schedule=_fake_activity_schedule,
            )
        )
        assert _fake_activity_schedule_post_result.inserted_count == 1

    # Get activity schedules matching "activityId"
    activity_schedules_matching_activity_id = [
        activity_schedule_current
        for activity_schedule_current in scope.database.patient.activity_schedules.get_activity_schedules(
            collection=patient_collection
        )
        if activity_schedule_current.get("activityId")
        == inserted_fake_activity["activityId"]
    ]
    assert len(activity_schedules_matching_activity_id) == len(
        fake_activity_schedules_with_activity_id
    )

    # Delete activity
    delete_activity_put_result = scope.database.patient.activities.delete_activity(
        collection=patient_collection,
        set_id=inserted_fake_activity[
            scope.database.patient.activities.SEMANTIC_SET_ID
        ],
        rev=inserted_fake_activity.get("_rev"),
    )
    assert delete_activity_put_result.inserted_count == 1

    # Get the inserted fake activity, assert it is gone
    get_fake_activity = scope.database.patient.activities.get_activity(
        collection=patient_collection,
        set_id=inserted_fake_activity.get(
            scope.database.patient.activities.SEMANTIC_SET_ID
        ),
    )
    assert get_fake_activity is None

    # Get activity schedules matching "activityId", assert they are all gone
    activity_schedules_matching_activity_id = [
        activity_schedule_current
        for activity_schedule_current in scope.database.patient.activity_schedules.get_activity_schedules(
            collection=patient_collection
        )
        if activity_schedule_current.get("activityId")
        == inserted_fake_activity["activityId"]
    ]
    assert len(activity_schedules_matching_activity_id) == 0
