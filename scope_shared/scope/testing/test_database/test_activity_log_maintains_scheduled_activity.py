"""
In addition to its standard set properties,
a put to scope.database.patient.activity_logs must maintain the scheduled activity.
"""

import pytest
from typing import Callable

import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.scheduled_activities
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_activity_log_post_maintains_scheduled_activity(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_scheduled_activity_factory: Callable[[], dict],
    data_fake_activity_log_factory: Callable[[], dict],
):
    """
    Test that the scheduled activity is maintained.

    The actual logic of scheduling specific activities is tested elsewhere.
    This test just ensures that it sees the collection being manipulated.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake scheduled activity to use as template
    fake_scheduled_activity = data_fake_scheduled_activity_factory()

    # Ensure it is not completed
    fake_scheduled_activity.update({"completed": False})

    # Post the scheduled activity
    scheduled_activity_post_result = (
        scope.database.patient.scheduled_activities.post_scheduled_activity(
            collection=patient_collection,
            scheduled_activity=fake_scheduled_activity,
        )
    )
    assert scheduled_activity_post_result.inserted_count == 1
    fake_scheduled_activity = scheduled_activity_post_result.document

    # Post a corresponding log
    fake_activity_log = data_fake_activity_log_factory()
    fake_activity_log.update(
        {
            scope.database.patient.scheduled_activities.SEMANTIC_SET_ID: fake_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ]
        }
    )
    activity_log_post_result = scope.database.patient.activity_logs.post_activity_log(
        collection=patient_collection, activity_log=fake_activity_log
    )
    assert activity_log_post_result.inserted_count == 1

    # Confirm the scheduled activity is now completed
    updated_scheduled_activity = (
        scope.database.patient.scheduled_activities.get_scheduled_activity(
            collection=patient_collection,
            set_id=fake_scheduled_activity[
                scope.database.patient.scheduled_activities.SEMANTIC_SET_ID
            ],
        )
    )
    assert updated_scheduled_activity["completed"]
