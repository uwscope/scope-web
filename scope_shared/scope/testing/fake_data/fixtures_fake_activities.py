import pytest
import random
from typing import Callable, List

import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_activities_factory(
    *,
    fake_activity_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake activity documents.
    """

    def factory() -> List[dict]:
        fake_activities = [fake_activity_factory() for _ in range(random.randint(0, 5))]

        return fake_activities

    return factory


@pytest.fixture(name="data_fake_activities_factory")
def fixture_data_fake_activities_factory(
    data_fake_activity_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_activities_factory.
    """

    unvalidated_factory = fake_activities_factory(
        fake_activity_factory=data_fake_activity_factory,
    )

    def factory() -> List[dict]:
        fake_activities = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.activities_schema,
            data=fake_activities,
        )

        return fake_activities

    return factory
