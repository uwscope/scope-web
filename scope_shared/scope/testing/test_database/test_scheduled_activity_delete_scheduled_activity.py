import pytest
from typing import Callable, List

import scope.database.patient.activities
import scope.database.patient.activity_logs
import scope.database.patient.scheduled_activities
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_scheduled_activity_delete_scheduled_activity(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_scheduled_activities_factory: Callable[[], List[dict]],
):
    """
    Test that the scheduled activity is deleted.
    Test that get_scheduled_activities and get_scheduled_activity do not return deleted documents.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    fake_scheduled_activities = data_fake_scheduled_activities_factory()

    for fake_scheduled_activity_current in fake_scheduled_activities:
        # Create scheduled activity
        scheduled_activity_post_result = (
            scope.database.patient.scheduled_activities.post_scheduled_activity(
                collection=patient_collection,
                scheduled_activity=fake_scheduled_activity_current,
            )
        )
        assert scheduled_activity_post_result.inserted_count == 1

        # Delete them
        scheduled_activity_delete_result = (
            scope.database.patient.scheduled_activities.delete_scheduled_activity(
                collection=patient_collection,
                scheduled_activity=scheduled_activity_post_result.document,
                set_id=scheduled_activity_post_result.inserted_set_id,
            )
        )
        assert scheduled_activity_delete_result.inserted_count == 1

        scheduled_activity_get_result = (
            scope.database.patient.scheduled_activities.get_scheduled_activity(
                collection=patient_collection,
                set_id=scheduled_activity_post_result.inserted_set_id,
            )
        )
        assert not scheduled_activity_get_result  # returns None

    scheduled_activities = (
        scope.database.patient.scheduled_activities.get_scheduled_activities(
            collection=patient_collection,
        )
    )
    if scheduled_activities:
        for scheduled_activity_current in scheduled_activities:
            assert not scheduled_activity_current.get("_deleted")
