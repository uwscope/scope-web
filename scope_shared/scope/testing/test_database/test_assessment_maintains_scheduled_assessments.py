"""
In addition to its standard set properties,
a put to scope.database.patient.assessments must maintain the scheduled assessments.
"""

import datetime
import pytz
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_assessments
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_assessment_maintains_scheduled_assessments(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_assessment_factory: Callable[[], dict],
):
    """
    Test that the scheduled assessments are maintained.

    The actual logic of scheduling specific assessments is tested elsewhere.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake assessment to use as template
    fake_assessment = data_fake_assessment_factory()
    assessment_id = fake_assessment[scope.database.patient.assessments.SEMANTIC_SET_ID]

    # Remove assignment of the assessment
    fake_assessment.update(
        {
            "assigned": False,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Determine what scheduled assessments already exist
    existing_scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection
        )
    )
    if not existing_scheduled_assessments:
        existing_scheduled_assessments = []

    # Assign the assessment
    fake_assessment.update(
        {
            "assigned": True,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
            "frequency": scope.enums.ScheduledItemFrequency.Weekly.value,
        }
    )
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Ensure we now obtain new scheduled assessments
    new_scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection
        )
    )
    new_scheduled_assessments = [
        scheduled_assessment_current
        for scheduled_assessment_current in new_scheduled_assessments
        if scheduled_assessment_current not in existing_scheduled_assessments
    ]
    assert len(new_scheduled_assessments) > 0

    # Remove assignment of the assessment
    fake_assessment.update(
        {
            "assigned": False,
            "assignedDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime.utcnow())
            ),
        }
    )
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Ensure there are no pending scheduled assessments
    # Because pending logic is already tested,
    # this confirms cancellation while being robust to an item created in this test which is now in the past
    existing_scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection
        )
    )
    if not existing_scheduled_assessments:
        existing_scheduled_assessments = []

    existing_scheduled_assessments = [
        scheduled_assessment_current
        for scheduled_assessment_current in existing_scheduled_assessments
        if scheduled_assessment_current[
            scope.database.patient.assessments.SEMANTIC_SET_ID
        ]
        == assessment_id
    ]

    pending_scheduled_assessments = scheduled_item_utils.pending_scheduled_items(
        scheduled_items=existing_scheduled_assessments,
        after_datetime=pytz.utc.localize(datetime.datetime.utcnow()),
    )

    assert len(pending_scheduled_assessments) == 0
