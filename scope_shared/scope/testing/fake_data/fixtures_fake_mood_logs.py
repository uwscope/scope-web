import pytest
import random
from typing import Callable, List

import scope.database.document_utils as document_utils
import scope.schema
import scope.schema_utils
import scope.testing.fake_data.fake_utils as fake_utils


def fake_mood_logs_factory(
    *,
    fake_mood_log_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Obtain a factory that will generate a list of fake mood log documents.
    """

    def factory() -> List[dict]:
        fake_mood_logs = [fake_mood_log_factory() for _ in range(random.randint(1, 5))]

        return fake_mood_logs

    return factory


@pytest.fixture(name="data_fake_mood_logs_factory")
def fixture_data_fake_mood_logs_factory(
    data_fake_mood_log_factory: Callable[[], dict],
) -> Callable[[], List[dict]]:
    """
    Fixture for data_fake_mood_logs_factory.
    """

    unvalidated_factory = fake_mood_logs_factory(
        fake_mood_log_factory=data_fake_mood_log_factory,
    )

    def factory() -> List[dict]:
        fake_mood_logs = unvalidated_factory()

        scope.schema_utils.xfail_for_invalid_schema(
            schema=scope.schema.mood_logs_schema,
            data=fake_mood_logs,
        )

        return fake_mood_logs

    return factory
