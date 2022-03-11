"""
In addition to its standard set properties,
a put to scope.database.patient.assessments must maintain the scheduled assessments.
"""

import copy
import datetime
import pytz
from typing import Callable

import scope.database.date_utils as date_utils
import scope.database.patient.scheduled_assessments
import scope.database.patients
import scope.database.patient_unsafe_utils as patient_unsafe_utils
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
    fake_assessment.update({
        "assigned": False,
        "assignedDateTime": date_utils.format_datetime(pytz.utc.localize(datetime.datetime.utcnow())),
    })
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Ensure there are no scheduled assessments
    scheduled_assessments = scope.database.patient.scheduled_assessments.get_scheduled_assessments(
        collection=patient_collection
    )
    if scheduled_assessments:
        scheduled_assessments = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_assessments
            if scheduled_assessment_current[scope.database.patient.assessments.SEMANTIC_SET_ID] == assessment_id
        ]
        assert len(scheduled_assessments) == 0

    # Assign the assessment
    fake_assessment.update({
        "assigned": True,
        "assignedDateTime": date_utils.format_datetime(pytz.utc.localize(datetime.datetime.utcnow())),
        "frequency": scope.enums.ScheduledItemFrequency.Weekly.value
    })
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Ensure we now obtain scheduled assessments
    scheduled_assessments = scope.database.patient.scheduled_assessments.get_scheduled_assessments(
        collection=patient_collection
    )
    scheduled_assessments = [
        scheduled_assessment_current
        for scheduled_assessment_current in scheduled_assessments
        if scheduled_assessment_current[scope.database.patient.assessments.SEMANTIC_SET_ID] == assessment_id
    ]
    assert len(scheduled_assessments) > 0

    # Remove assignment of the assessment
    fake_assessment.update({
        "assigned": False,
        "assignedDateTime": date_utils.format_datetime(pytz.utc.localize(datetime.datetime.utcnow())),
    })
    patient_unsafe_utils.unsafe_update_assessment(
        collection=patient_collection,
        set_id=assessment_id,
        assessment=fake_assessment,
    )

    # Ensure there are no scheduled assessments
    scheduled_assessments = scope.database.patient.scheduled_assessments.get_scheduled_assessments(
        collection=patient_collection
    )
    if scheduled_assessments:
        scheduled_assessments = [
            scheduled_assessment_current
            for scheduled_assessment_current in scheduled_assessments
            if scheduled_assessment_current[scope.database.patient.assessments.SEMANTIC_SET_ID] == assessment_id
        ]
        assert len(scheduled_assessments) == 0
