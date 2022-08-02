"""
In addition to its standard set properties,
a put to scope.database.patient.assessments must maintain the scheduled assessments.
"""

import datetime
import pytz
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.database.patient.scheduled_assessments
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
import scope.database.scheduled_item_utils as scheduled_item_utils
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_assessment_calculate_scheduled_assessments_to_create():
    scheduled_assessments = (
        scope.database.patient.assessments._calculate_scheduled_assessments_to_create(
            assessment_id="testAssessmentId",
            assessment={
                "assigned": True,
                "assignedDateTime": date_utils.format_datetime(
                    pytz.utc.localize(datetime.datetime(2022, 3, 12, 6))
                ),
                "frequency": scope.enums.ScheduledItemFrequency.Daily.value,
            },
            maintenance_datetime=pytz.utc.localize(datetime.datetime(2022, 3, 14, 10)),
        )
    )

    scheduled_dates = []
    scheduled_dates.extend([datetime.date(2022, 3, day) for day in range(14, 31 + 1)])
    scheduled_dates.extend([datetime.date(2022, 4, day) for day in range(1, 30 + 1)])
    scheduled_dates.extend([datetime.date(2022, 5, day) for day in range(1, 31 + 1)])
    scheduled_dates.extend([datetime.date(2022, 6, day) for day in range(1, 14 + 1)])

    assert scheduled_assessments == [
        {
            "_type": "scheduledAssessment",
            "assessmentId": "testAssessmentId",
            "completed": False,
            "dueDate": date_utils.format_date(scheduled_date_current),
            "dueTimeOfDay": 8,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime.datetime(
                        scheduled_date_current.year,
                        scheduled_date_current.month,
                        scheduled_date_current.day,
                        15,
                    )
                )
            ),
            "reminderDate": date_utils.format_date(scheduled_date_current),
            "reminderTimeOfDay": 8,
            "reminderDateTime": date_utils.format_datetime(
                pytz.utc.localize(
                    datetime.datetime(
                        scheduled_date_current.year,
                        scheduled_date_current.month,
                        scheduled_date_current.day,
                        15,
                    )
                )
            ),
        }
        for scheduled_date_current in scheduled_dates
    ]


def test_assessment_calculate_scheduled_assessments_to_delete():
    scheduled_assessments = [
        {  # Different assessmentId, should not be deleted, even in future
            "assessmentId": "differentId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 8,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 8))
            ),
            "completed": False,
        },
        {  # Past item (previous date, later time), should not be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 12)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 12, 16))
            ),
            "completed": False,
        },
        {  # Past item (same date, previous time), should not be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 8,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 8))
            ),
            "completed": False,
        },
        {  # Future item (same date, later time), already completed, should not be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": True,
        },
        {  # Future item (later date, earlier time), already completed, should not be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": True,
        },
        {  # Future item (same date, later time), should be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": False,
        },
        {  # Future item (later date, earlier time), should be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": False,
        },
    ]

    deleted_assessments = (
        scope.database.patient.assessments._calculate_scheduled_assessments_to_delete(
            assessment_id="deleteTestId",
            scheduled_assessments=scheduled_assessments,
            maintenance_datetime=pytz.utc.localize(
                datetime.datetime(2022, 3, 13, 12, 0, 0)
            ),
        )
    )

    assert deleted_assessments == [
        {  # Future item (same date, later time), should be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 3, 13)),
            "dueTimeOfDay": 16,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 3, 13, 16))
            ),
            "completed": False,
        },
        {  # Future item (later date, earlier time), should be deleted
            "assessmentId": "deleteTestId",
            "dueDate": date_utils.format_date(datetime.date(2022, 4, 1)),
            "dueTimeOfDay": 4,
            "dueDateTime": date_utils.format_datetime(
                pytz.utc.localize(datetime.datetime(2022, 4, 1, 4))
            ),
            "completed": False,
        },
    ]


def test_assessment_put_maintains_scheduled_assessments(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_assessment_factory: Callable[[], dict],
):
    """
    Test that the scheduled assessments are maintained.

    The actual logic of scheduling specific assessments is tested elsewhere.
    This test just ensures that it sees the collection being manipulated.
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
    if "dayOfWeek" in fake_assessment:
        del fake_assessment["dayOfWeek"]
    if "frequency" in fake_assessment:
        del fake_assessment["frequency"]
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment_complete=fake_assessment,
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
            "dayOfWeek": scope.enums.DayOfWeek.Monday.value,
        }
    )
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment_complete=fake_assessment,
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
    if "dayOfWeek" in fake_assessment:
        del fake_assessment["dayOfWeek"]
    if "frequency" in fake_assessment:
        del fake_assessment["frequency"]
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment_complete=fake_assessment,
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
