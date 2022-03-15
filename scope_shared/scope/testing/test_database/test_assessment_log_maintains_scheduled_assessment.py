"""
In addition to its standard set properties,
a put to scope.database.patient.assessment_logs must maintain the scheduled assessment.
"""

import pytest
from typing import Callable

import scope.database.patient.assessments
import scope.database.patient.assessment_logs
import scope.database.patient.scheduled_assessments
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_assessment_log_post_maintains_scheduled_assessment(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_scheduled_assessment_factory: Callable[[], dict],
    data_fake_assessment_log_factory: Callable[[], dict],
):
    """
    Test that the scheduled assessment is maintained.

    The actual logic of scheduling specific assessments is tested elsewhere.
    This test just ensures that it sees the collection being manipulated.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    # Obtain fake scheduled assessment to use as template
    fake_scheduled_assessment = data_fake_scheduled_assessment_factory()

    # Ensure it is not completed
    fake_scheduled_assessment.update({"completed": False})

    # Put the scheduled assessment
    scheduled_assessment_post_result = (
        scope.database.patient.scheduled_assessments.post_scheduled_assessment(
            collection=patient_collection,
            scheduled_assessment=fake_scheduled_assessment,
        )
    )
    assert scheduled_assessment_post_result.inserted_count == 1
    fake_scheduled_assessment = scheduled_assessment_post_result.document

    # Post a corresponding log
    fake_assessment_log = data_fake_assessment_log_factory()
    fake_assessment_log.update(
        {
            scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID: fake_scheduled_assessment[
                scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
            ]
        }
    )
    assessment_log_post_result = (
        scope.database.patient.assessment_logs.post_assessment_log(
            collection=patient_collection, assessment_log=fake_assessment_log
        )
    )
    assert assessment_log_post_result.inserted_count == 1

    # Confirm the scheduled assessment is now completed
    updated_scheduled_assessment = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessment(
            collection=patient_collection,
            set_id=fake_scheduled_assessment[
                scope.database.patient.scheduled_assessments.SEMANTIC_SET_ID
            ],
        )
    )
    assert updated_scheduled_assessment["completed"]
