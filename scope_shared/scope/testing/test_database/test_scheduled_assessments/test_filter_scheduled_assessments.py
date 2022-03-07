import datetime
from typing import Callable, List

import pytest
import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.database.patient.scheduled_assessments
import scope.schema
import scope.schema_utils as schema_utils


def _filtered_scheduled_assessments_assertions(
    scheduled_assessments: List[dict],
    assessment: dict,
) -> None:
    schema_utils.assert_schema(
        data=scheduled_assessments,
        schema=scope.schema.scheduled_assessments_schema,
    )
    for scheduled_assessment_current in scheduled_assessments:
        assert not scheduled_assessment_current["completed"]
        assert scheduled_assessment_current["dueType"] == "Exact"
        assert (
            scheduled_assessment_current[
                scope.database.patient.assessments.SEMANTIC_SET_ID
            ]
            == assessment[scope.database.patient.assessments.SEMANTIC_SET_ID]
        )
        assert date_utils.parse_date(
            scheduled_assessment_current["dueDate"]
        ) > date_utils.parse_date(date_utils.format_date(datetime.date.today()))


def test_filter_scheduled_assessments(
    data_fake_assessment_factory: Callable[[], dict],
):
    assessment = data_fake_assessment_factory()

    scheduled_assessments = (
        scope.database.patient.scheduled_assessments.create_scheduled_assessments(
            assessment=assessment,
        )
    )

    filtered_scheduled_assessments = (
        scope.database.patient.scheduled_assessments.filter_scheduled_assessments(
            all_scheduled_assessments=scheduled_assessments,
            assessment=assessment,
        )
    )

    _filtered_scheduled_assessments_assertions(
        assessment=assessment,
        scheduled_assessments=filtered_scheduled_assessments,
    )
