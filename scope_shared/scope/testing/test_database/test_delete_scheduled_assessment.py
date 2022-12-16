import pytest
from typing import Callable, List

import scope.database.patient.assessments
import scope.database.patient.assessment_logs
import scope.database.patient.scheduled_assessments
import scope.enums
import scope.testing.fixtures_database_temp_patient


def test_delete_scheduled_assessment(
    database_temp_patient_factory: Callable[
        [],
        scope.testing.fixtures_database_temp_patient.DatabaseTempPatient,
    ],
    data_fake_scheduled_assessments_factory: Callable[[], List[dict]],
):
    """
    Test that the scheduled assessment is deleted.
    Test that get_scheduled_assessments and get_scheduled_assessment do not return deleted documents.
    """

    temp_patient = database_temp_patient_factory()
    patient_collection = temp_patient.collection

    fake_scheduled_assessments = data_fake_scheduled_assessments_factory()

    for fake_scheduled_assessment_current in fake_scheduled_assessments:
        # Create scheduled assessment
        scheduled_assessment_post_result = (
            scope.database.patient.scheduled_assessments.post_scheduled_assessment(
                collection=patient_collection,
                scheduled_assessment=fake_scheduled_assessment_current,
            )
        )
        assert scheduled_assessment_post_result.inserted_count == 1
        scheduled_assessment_post_result_document = (
            scheduled_assessment_post_result.document
        )

        # Get via singular verb
        scheduled_assessment_get_singular_result = (
            scope.database.patient.scheduled_assessments.get_scheduled_assessment(
                collection=patient_collection,
                set_id=scheduled_assessment_post_result.inserted_set_id,
            )
        )
        assert (
            scheduled_assessment_post_result_document
            == scheduled_assessment_get_singular_result
        )

        # Get via plural verb
        scheduled_assessment_get_plural_result = (
            scope.database.patient.scheduled_assessments.get_scheduled_assessments(
                collection=patient_collection,
            )
        )
        assert (
            scheduled_assessment_post_result_document
            in scheduled_assessment_get_plural_result
        )

        # Delete them
        scheduled_assessment_delete_result = (
            scope.database.patient.scheduled_assessments.delete_scheduled_assessment(
                collection=patient_collection,
                scheduled_assessment=scheduled_assessment_post_result.document,
                set_id=scheduled_assessment_post_result.inserted_set_id,
            )
        )
        assert scheduled_assessment_delete_result.inserted_count == 1

        # Get via singular verb
        scheduled_assessment_get_result = (
            scope.database.patient.scheduled_assessments.get_scheduled_assessment(
                collection=patient_collection,
                set_id=scheduled_assessment_post_result.inserted_set_id,
            )
        )
        assert not scheduled_assessment_get_result  # returns None

        # Get via plural verb
        scheduled_assessment_get_plural_result = (
            scope.database.patient.scheduled_assessments.get_scheduled_assessments(
                collection=patient_collection,
            )
        )
        assert (
            scheduled_assessment_post_result_document
            not in scheduled_assessment_get_plural_result
        )
        for (
            scheduled_assessment_get_plural_result_current
        ) in scheduled_assessment_get_plural_result:
            assert (
                scheduled_assessment_post_result.inserted_set_id
                != scheduled_assessment_get_plural_result_current["_set_id"]
            )

    scheduled_assessments = (
        scope.database.patient.scheduled_assessments.get_scheduled_assessments(
            collection=patient_collection,
        )
    )
    if scheduled_assessments:
        for scheduled_assessment_current in scheduled_assessments:
            assert not scheduled_assessment_current.get("_deleted")
