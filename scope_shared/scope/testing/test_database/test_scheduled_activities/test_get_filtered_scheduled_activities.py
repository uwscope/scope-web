import datetime
from typing import Callable, List

import pytest
import scope.database.collection_utils as collection_utils
import scope.database.date_utils as date_utils
import scope.database.patient.activities
import scope.database.patient.scheduled_activities
import scope.schema
import scope.schema_utils as schema_utils


def _dummy_inserted_activity(
    fake_activity_factory: Callable[[], dict],
) -> dict:
    activity = fake_activity_factory()
    # Assume activity has just been inserted into db using POST
    # create_scheduled_activities method needs activity to have its SEMANTIC_SET_ID
    activity[
        scope.database.patient.activities.SEMANTIC_SET_ID
    ] = collection_utils.generate_set_id()

    return activity


def _filtered_scheduled_activities_assertions(
    scheduled_activities: List[dict],
    activity: dict,
) -> None:
    schema_utils.assert_schema(
        data=scheduled_activities,
        schema=scope.schema.scheduled_activities_schema,
    )
    for scheduled_activity_current in scheduled_activities:
        assert not scheduled_activity_current["completed"]
        assert scheduled_activity_current["dueType"] == "Exact"
        assert (
            scheduled_activity_current[
                scope.database.patient.activities.SEMANTIC_SET_ID
            ]
            == activity[scope.database.patient.activities.SEMANTIC_SET_ID]
        )
        assert (
            date_utils.parse_datetime(scheduled_activity_current["dueDate"])
            > datetime.datetime.today()
        )


@pytest.mark.parametrize(
    "activity_method",
    [("post", "put")],
)
def test_get_filtered_scheduled_activities(
    data_fake_activity_factory: Callable[[], dict],
    activity_method: str,
):
    activity = _dummy_inserted_activity(
        fake_activity_factory=data_fake_activity_factory,
    )

    scheduled_activities = (
        scope.database.patient.scheduled_activities.create_scheduled_activities(
            activity=activity,
            activity_method=activity_method,
        )
    )

    filtered_scheduled_activities = scope.database.patient.scheduled_activities.filter_scheduled_activities(
        all_scheduled_activities=scheduled_activities,  # NOTE: These are not ALL the stored scheduled activities
        activity=activity,
    )

    _filtered_scheduled_activities_assertions(
        activity=activity,
        scheduled_activities=filtered_scheduled_activities,
    )
