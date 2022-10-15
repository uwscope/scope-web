import pytest
import random
from typing import Callable, List

import scope.schema
import scope.schema_utils


def fake_activity_schedules_factory(
    *,
    fake_activity_schedule_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake activity schedule documents.
    """

    def factory() -> List[dict]:
        fake_activity_schedules = [
            fake_activity_schedule_factory() for _ in range(random.randint(0, 5))
        ]

        return fake_activity_schedules

    return factory


@pytest.fixture(name="data_fake_activity_schedules_factory")
def fixture_data_fake_activity_schedules_factory(
    data_fake_activity_schedule_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_activity_schedules_factory.
    """

    unvalidated_factory = fake_activity_schedules_factory(
        fake_activity_schedule_factory=data_fake_activity_schedule_factory,
    )

    def factory() -> List[dict]:
        fake_activity_schedules = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activity_schedules_schema,
            data=fake_activity_schedules,
        )

        return fake_activity_schedules

    return factory
