import pytest
import random
from typing import Callable, List

import scope.schema
import scope.schema_utils


def fake_values_factory(
    *,
    fake_value_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake value documents.
    """

    def factory() -> List[dict]:
        fake_values = [fake_value_factory() for _ in range(random.randint(1, 5))]

        return fake_values

    return factory


@pytest.fixture(name="data_fake_values_factory")
def fixture_data_fake_values_factory(
    data_fake_value_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_values_factory.
    """

    unvalidated_factory = fake_values_factory(
        fake_value_factory=data_fake_value_factory,
    )

    def factory() -> List[dict]:
        fake_values = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.values_schema,
            data=fake_values,
        )

        return fake_values

    return factory
