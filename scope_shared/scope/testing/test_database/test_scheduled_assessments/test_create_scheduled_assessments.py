import datetime
from typing import Callable, List

import freezegun
import pytest
import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.assessments
import scope.database.patient.scheduled_assessments
import scope.schema
import scope.schema_utils as schema_utils


def _dummy_assessment(
    fake_assessment_factory: Callable[[], dict],
    frequency: str,
    day_of_week: str,
) -> dict:
    assessment = fake_assessment_factory()
    assessment["frequency"] = frequency
    assessment["dayOfWeek"] = day_of_week
    return assessment


def _scheduled_assessments_assertions(
    assessment: dict,
    scheduled_assessments: List[dict],
) -> None:
    schema_utils.assert_schema(
        data=scheduled_assessments,
        schema=scope.schema.scheduled_assessments_schema,
    )
    for scheduled_assessment_current in scheduled_assessments:
        assert not scheduled_assessment_current["completed"]
        assert scheduled_assessment_current["dueType"] == "Exact"
        assert scheduled_assessment_current["assessmentId"] == assessment[scope.database.patient.assessments.SEMANTIC_SET_ID]


@freezegun.freeze_time("2022-03-01") # Tuesday
@pytest.mark.parametrize(
    "frequency,day_of_week,weeks,scheduled_assessment_due_dates",
    [
        (
            "Daily",
            "Monday",
            1,
            [
                "2022-03-07T00:00:00Z",
                "2022-03-08T00:00:00Z",
                "2022-03-09T00:00:00Z",
                "2022-03-10T00:00:00Z",
                "2022-03-11T00:00:00Z",
                "2022-03-12T00:00:00Z",
                "2022-03-13T00:00:00Z",
                "2022-03-14T00:00:00Z",
            ],
        ),
        (
            "Daily",
            "Tuesday",
            1,
            [
                "2022-03-01T00:00:00Z",
                "2022-03-02T00:00:00Z",
                "2022-03-03T00:00:00Z",
                "2022-03-04T00:00:00Z",
                "2022-03-05T00:00:00Z",
                "2022-03-06T00:00:00Z",
                "2022-03-07T00:00:00Z",
                "2022-03-08T00:00:00Z",
            ],
        ),
        (
            "Once a week",
            "Monday",
            3,
            [
                "2022-03-07T00:00:00Z",
                "2022-03-14T00:00:00Z",
                "2022-03-21T00:00:00Z",
                "2022-03-28T00:00:00Z",
            ],
        ),
        (
            "Every 2 weeks",
            "Friday",
            3,
            [
                "2022-03-04T00:00:00Z",
                "2022-03-18T00:00:00Z",
            ],
        ),
        (
            "Every 2 weeks",
            "Friday",
            5,
            [
                "2022-03-04T00:00:00Z",
                "2022-03-18T00:00:00Z",
                "2022-04-01T00:00:00Z",
            ],
        ),
        (
            "Every 4 weeks",
            "Friday",
            8,
            [
                "2022-03-04T00:00:00Z",
                "2022-04-01T00:00:00Z",
                "2022-04-29T00:00:00Z",
            ],
        ),
    ],
)
def test_create_scheduled_assessments(
    data_fake_assessment_factory: Callable[[], dict],
    frequency: str,
    day_of_week: str,
    weeks: int,
    scheduled_assessment_due_dates: List[str],
):

    # Freeze today's date to 1st March, 2022
    assert datetime.datetime.now() == datetime.datetime(2022, 3, 1)

    assessment = _dummy_assessment(
        fake_assessment_factory=data_fake_assessment_factory,
        frequency=frequency,
        day_of_week=day_of_week,
    )



    scheduled_assessments = (
        scope.database.patient.scheduled_assessments.create_scheduled_assessments(
            assessment=assessment,
            weeks=weeks,
        )
    )


    assert (
        [
            scheduled_assessment_current["dueDate"]
            for scheduled_assessment_current in scheduled_assessments
        ]
    ) == scheduled_assessment_due_dates

    _scheduled_assessments_assertions(
        assessment=assessment,
        scheduled_assessments=scheduled_assessments,
    )


